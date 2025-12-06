"""
SiteMind API Tests
Basic integration tests for the API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "SiteMind API"
        assert data["status"] == "running"
    
    def test_ping(self, client):
        """Test ping endpoint"""
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.json()["pong"] == True
    
    def test_health(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "services" in data


class TestWhatsAppWebhook:
    """Test WhatsApp webhook endpoints"""
    
    def test_webhook_verify(self, client):
        """Test webhook verification endpoint"""
        response = client.get("/whatsapp/webhook")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"
    
    @patch("routers.whatsapp.whatsapp_client")
    @patch("routers.whatsapp.gemini_service")
    def test_webhook_unknown_user(self, mock_gemini, mock_whatsapp, client):
        """Test webhook with unknown user"""
        mock_whatsapp.send_message = MagicMock()
        
        response = client.post(
            "/whatsapp/webhook",
            data={
                "MessageSid": "SM123",
                "From": "whatsapp:+919999999999",
                "To": "whatsapp:+14155238886",
                "Body": "Test message",
                "NumMedia": "0",
            }
        )
        
        # Should return 200 with empty response (TwiML)
        assert response.status_code == 200


class TestAdminEndpoints:
    """Test admin API endpoints"""
    
    def test_list_builders_empty(self, client):
        """Test listing builders when empty"""
        response = client.get("/admin/builders")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_list_projects_empty(self, client):
        """Test listing projects when empty"""
        response = client.get("/admin/projects")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestAnalyticsEndpoints:
    """Test analytics endpoints"""
    
    def test_dashboard_stats(self, client):
        """Test dashboard statistics"""
        response = client.get("/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_builders" in data
        assert "total_projects" in data
        assert "total_queries_today" in data


# Run with: pytest tests/test_api.py -v

