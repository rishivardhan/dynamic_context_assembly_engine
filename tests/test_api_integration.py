"""Integration tests for the FastAPI endpoints.

These tests use TestClient with an in-memory SQLite database (via mocking)
to avoid requiring live PostgreSQL and Neo4j connections.
"""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))


@pytest.fixture
def client():
    """Create a test client with mocked databases."""
    with patch('app.db.postgres.engine'), \
         patch('app.db.neo4j_client.get_driver'), \
         patch('app.engines.semantic.get_model'):
        from app.main import app
        with TestClient(app) as c:
            yield c


class TestHealthEndpoint:
    def test_health_check_returns_200(self, client):
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        assert response.json()['status'] == 'healthy'

    def test_root_endpoint(self, client):
        response = client.get('/')
        assert response.status_code == 200
        data = response.json()
        assert 'name' in data
        assert 'DCAE' in data['name']


class TestQueryEndpointValidation:
    def test_empty_query_rejected(self, client):
        response = client.post('/api/v1/query', json={'query': 'ab'})
        assert response.status_code == 422

    def test_valid_query_requires_db(self, client):
        """With mocked db this will still reach the handler."""
        with patch('app.api.routes.assembler.assemble') as mock_assemble:
            mock_assemble.return_value = MagicMock(
                query="test",
                query_id="q1",
                project_detected=None,
                selected_context=[],
                assembled_prompt=MagicMock(
                    system_prompt="sys",
                    user_prompt="user",
                    context_window_used=0,
                    context_items_count=0,
                    profile_adaptation="default",
                ),
                rag_comparison=[],
                processing_time_ms=10.0,
                total_candidates=0,
            )
            response = client.post('/api/v1/query', json={'query': 'What is the status of the migration?'})
            assert response.status_code == 200


class TestAPISchemaValidation:
    def test_query_request_top_k_bounds(self, client):
        with patch('app.api.routes.assembler.assemble') as mock:
            mock.return_value = MagicMock(
                query="test", query_id="q1", project_detected=None,
                selected_context=[], assembled_prompt=MagicMock(
                    system_prompt="s", user_prompt="u",
                    context_window_used=0, context_items_count=0, profile_adaptation=""
                ),
                rag_comparison=[], processing_time_ms=1.0, total_candidates=0,
            )
            # top_k=0 should be rejected
            r = client.post('/api/v1/query', json={'query': 'test query here', 'top_k': 0})
            assert r.status_code == 422

            # top_k=51 should be rejected
            r = client.post('/api/v1/query', json={'query': 'test query here', 'top_k': 51})
            assert r.status_code == 422

            # top_k=10 should be accepted
            r = client.post('/api/v1/query', json={'query': 'test query here', 'top_k': 10})
            assert r.status_code == 200
