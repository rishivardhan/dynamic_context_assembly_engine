"""Project relevance scoring — boosts context from the same project as the query."""
import re
from typing import Optional, List
from difflib import SequenceMatcher


class ProjectRelevanceScorer:
    """
    Scores context items by how closely they match the detected project context.

    Matching strategy (in priority order):
    1. Exact project name match: 1.0
    2. Partial / fuzzy match above threshold: 0.5 – 0.9
    3. No detected project (query is project-agnostic): 0.5 (neutral)
    4. No match: 0.1
    """

    FUZZY_THRESHOLD = 0.6

    def score(
        self,
        context_project: str,
        detected_project: Optional[str],
    ) -> tuple[float, str]:
        if not detected_project:
            return 0.5, "No project detected — neutral score"

        ctx_lower = context_project.lower().strip()
        det_lower = detected_project.lower().strip()

        if ctx_lower == det_lower:
            return 1.0, f"Exact match: '{context_project}'"

        if det_lower in ctx_lower or ctx_lower in det_lower:
            return 0.85, f"Substring match: '{context_project}' ~ '{detected_project}'"

        ratio = SequenceMatcher(None, ctx_lower, det_lower).ratio()
        if ratio >= self.FUZZY_THRESHOLD:
            normalized = 0.5 + (ratio - self.FUZZY_THRESHOLD) / (1.0 - self.FUZZY_THRESHOLD) * 0.35
            return normalized, f"Fuzzy match ({ratio:.2f}): '{context_project}' ~ '{detected_project}'"

        return 0.1, f"No match: '{context_project}' vs '{detected_project}'"

    def detect_project(self, query: str, known_projects: List[str]) -> Optional[str]:
        """Extract the most likely project name from a natural language query."""
        query_lower = query.lower()
        best_match: Optional[str] = None
        best_score = 0.0

        for proj in known_projects:
            proj_lower = proj.lower()
            if proj_lower in query_lower:
                return proj

            ratio = SequenceMatcher(None, query_lower, proj_lower).ratio()
            words = proj_lower.split()
            word_hits = sum(1 for w in words if w in query_lower and len(w) > 3)
            combined = ratio * 0.4 + (word_hits / max(len(words), 1)) * 0.6

            if combined > best_score and combined > 0.3:
                best_score = combined
                best_match = proj

        return best_match
