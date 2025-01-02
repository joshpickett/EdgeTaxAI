import pytest
from unittest.mock import Mock, patch
from ..routes.gig_routes import gig_routes
from ..utils.gig_platform_processor import GigPlatformProcessor


@pytest.fixture
def app():
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(gig_routes)
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class TestGigRoutes:
    def test_connect_platform_success(self, client):
        with patch("requests.get") as mock_request:
            mock_request.return_value.status_code = 200
            response = client.get("/gig/connect/uber")
            assert response.status_code == 302  # Redirect to OAuth URL

    def test_connect_platform_invalid(self, client):
        response = client.get("/gig/connect/invalid_platform")
        assert response.status_code == 400
        assert "error" in response.json

    def test_oauth_callback_success(self, client):
        data = {"user_id": 123, "platform": "uber", "code": "test_code"}
        response = client.post("/gig/callback", json=data)
        assert response.status_code == 200
        assert "message" in response.json

    def test_list_connections_success(self, client):
        response = client.get("/gig/connections?user_id=123")
        assert response.status_code == 200
        assert "connections" in response.json

    @patch.object(GigPlatformProcessor, "sync_platform_data")
    def test_sync_platform_data(self, mock_sync, client):
        mock_sync.return_value = {"status": "success"}
        response = client.post("/gig/sync/uber", json={"user_id": 123})
        assert response.status_code == 200
        assert response.json["status"] == "success"

    def test_get_earnings_success(self, client):
        response = client.get("/gig/earnings?user_id=123")
        assert response.status_code == 200
        assert isinstance(response.json, dict)

    def test_fetch_data_success(self, client):
        response = client.get("/gig/fetch-data?user_id=123&platform=uber")
        assert response.status_code == 200
        assert "data" in response.json

    def test_refresh_token_success(self, client):
        data = {"user_id": 123, "platform": "uber"}
        response = client.post("/refresh-token", json=data)
        assert response.status_code == 200
        assert "message" in response.json

    def test_exchange_token_success(self, client):
        data = {"platform": "uber", "code": "test_code"}
        response = client.post("/gig/exchange-token", json=data)
        assert response.status_code == 200
        assert "access_token" in response.json

    @patch("requests.post")
    def test_platform_oauth_flow(self, mock_post, client):
        # Test complete OAuth flow
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "test_token"}

        # Step 1: Connect
        connect_response = client.get("/gig/connect/uber")
        assert connect_response.status_code == 302

        # Step 2: Callback
        callback_response = client.post(
            "/gig/callback",
            json={"user_id": 123, "platform": "uber", "code": "test_code"},
        )
        assert callback_response.status_code == 200

    def test_error_handling(self, client):
        # Test various error scenarios
        responses = [
            client.get("/gig/connect/invalid"),
            client.post("/gig/callback", json={}),
            client.get("/gig/connections"),
            client.get("/gig/fetch-data"),
        ]

        for response in responses:
            assert response.status_code in [400, 401, 404, 500]
            assert "error" in response.json

    @patch("redis.Redis")
    def test_rate_limiting(self, mock_redis, client):
        mock_redis.return_value.get.return_value = b"101"  # Over limit
        response = client.get("/gig/connect/uber")
        assert response.status_code == 429
