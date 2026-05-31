"""Neo4j knowledge graph client."""
from neo4j import GraphDatabase, Driver
from typing import Optional, List, Dict, Any
from app.config import settings
import structlog

logger = structlog.get_logger()

_driver: Optional[Driver] = None


def get_driver() -> Driver:
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


def close_driver():
    global _driver
    if _driver:
        _driver.close()
        _driver = None


class Neo4jRepository:
    def __init__(self):
        self.driver = get_driver()

    def create_context_node(self, ctx: Dict[str, Any]) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (c:ContextObject {id: $id})
                SET c.title = $title,
                    c.source_type = $source_type,
                    c.project = $project,
                    c.owner = $owner,
                    c.risk_level = $risk_level,
                    c.importance = $importance,
                    c.created_at = $created_at
                """,
                **ctx,
            )

    def create_person_node(self, person: Dict[str, Any]) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (p:Person {id: $id})
                SET p.name = $name,
                    p.role = $role,
                    p.email = $email,
                    p.department = $department
                """,
                **person,
            )

    def create_project_node(self, project: Dict[str, Any]) -> None:
        with self.driver.session() as session:
            session.run(
                """
                MERGE (proj:Project {id: $id})
                SET proj.name = $name,
                    proj.description = $description,
                    proj.status = $status
                """,
                **project,
            )

    def create_relationship(
        self, source_id: str, target_id: str, rel_type: str, weight: float = 1.0
    ) -> None:
        cypher = f"""
            MATCH (a {{id: $source_id}})
            MATCH (b {{id: $target_id}})
            MERGE (a)-[r:{rel_type.upper()}]->(b)
            SET r.weight = $weight
        """
        with self.driver.session() as session:
            session.run(cypher, source_id=source_id, target_id=target_id, weight=weight)

    def get_full_graph(self) -> Dict[str, List[Dict]]:
        with self.driver.session() as session:
            nodes_result = session.run(
                "MATCH (n) RETURN n.id AS id, labels(n)[0] AS label, properties(n) AS props LIMIT 500"
            )
            nodes = [
                {"id": r["id"], "label": r["label"], "properties": dict(r["props"])}
                for r in nodes_result
                if r["id"]
            ]

            edges_result = session.run(
                """
                MATCH (a)-[r]->(b)
                RETURN a.id AS source, b.id AS target, type(r) AS rel, r.weight AS weight
                LIMIT 1000
                """
            )
            edges = [
                {
                    "source": r["source"],
                    "target": r["target"],
                    "relationship": r["rel"],
                    "weight": r["weight"] or 1.0,
                }
                for r in edges_result
                if r["source"] and r["target"]
            ]
        return {"nodes": nodes, "edges": edges}

    def get_node_neighborhood(self, node_id: str, depth: int = 2) -> Dict[str, List[Dict]]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (n {id: $node_id})-[r*1..$depth]-(m)
                WITH collect(DISTINCT n) + collect(DISTINCT m) AS all_nodes,
                     collect(DISTINCT r) AS all_rels
                UNWIND all_nodes AS node
                WITH collect(DISTINCT {id: node.id, label: labels(node)[0], props: properties(node)}) AS nodes,
                     all_rels
                RETURN nodes,
                       [rel IN all_rels |
                        {source: startNode(rel).id, target: endNode(rel).id,
                         rel: type(rel), weight: rel.weight}
                       ] AS edges
                """,
                node_id=node_id,
                depth=depth,
            )
            row = result.single()
            if not row:
                return {"nodes": [], "edges": []}
            return {
                "nodes": [
                    {"id": n["id"], "label": n["label"], "properties": dict(n["props"])}
                    for n in row["nodes"]
                    if n["id"]
                ],
                "edges": [
                    {
                        "source": e["source"],
                        "target": e["target"],
                        "relationship": e["rel"],
                        "weight": e["weight"] or 1.0,
                    }
                    for e in row["edges"]
                    if e["source"] and e["target"]
                ],
            }

    def find_related_context(self, context_id: str) -> List[str]:
        """Return IDs of context objects related to the given one."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:ContextObject {id: $id})-[*1..2]-(related:ContextObject)
                RETURN DISTINCT related.id AS id LIMIT 20
                """,
                id=context_id,
            )
            return [r["id"] for r in result]

    def get_project_context_ids(self, project_name: str) -> List[str]:
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:ContextObject)
                WHERE toLower(c.project) CONTAINS toLower($project_name)
                RETURN c.id AS id LIMIT 100
                """,
                project_name=project_name,
            )
            return [r["id"] for r in result]

    def create_schema_indexes(self) -> None:
        queries = [
            "CREATE INDEX IF NOT EXISTS FOR (c:ContextObject) ON (c.id)",
            "CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.id)",
            "CREATE INDEX IF NOT EXISTS FOR (proj:Project) ON (proj.id)",
            "CREATE INDEX IF NOT EXISTS FOR (c:ContextObject) ON (c.project)",
            "CREATE INDEX IF NOT EXISTS FOR (c:ContextObject) ON (c.source_type)",
        ]
        with self.driver.session() as session:
            for q in queries:
                session.run(q)
