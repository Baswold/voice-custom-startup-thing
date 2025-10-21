"""
Test cases for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db
from app.models import Base
import tempfile
import os


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user():
    """Create a test user and return credentials"""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    response = client.post("/api/users/register", json=user_data)
    assert response.status_code == 201

    # Login to get token
    login_response = client.post("/api/users/login", json={
        "email": user_data["email"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]
    return {
        "data": user_data,
        "token": token,
        "user_id": login_response.json()["user"]["id"]
    }


class TestHealth:
    """Test health check endpoint"""

    def test_health_check(self):
        """Test that health check returns OK"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
        assert "version" in response.json()


class TestAuth:
    """Test authentication endpoints"""

    def test_register_user(self):
        """Test user registration"""
        user_data = {
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "password123",
            "full_name": "New User"
        }
        response = client.post("/api/users/register", json=user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["username"] == user_data["username"]
        assert "id" in data
        assert "hashed_password" not in data  # Password should not be returned

    def test_register_duplicate_email(self, test_user):
        """Test that duplicate email registration fails"""
        user_data = {
            "email": test_user["data"]["email"],
            "username": "differentusername",
            "password": "password123"
        }
        response = client.post("/api/users/register", json=user_data)
        assert response.status_code == 400

    def test_register_duplicate_username(self, test_user):
        """Test that duplicate username registration fails"""
        user_data = {
            "email": "different@example.com",
            "username": test_user["data"]["username"],
            "password": "password123"
        }
        response = client.post("/api/users/register", json=user_data)
        assert response.status_code == 400

    def test_login_success(self, test_user):
        """Test successful login"""
        response = client.post("/api/users/login", json={
            "email": test_user["data"]["email"],
            "password": test_user["data"]["password"]
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data

    def test_login_wrong_password(self, test_user):
        """Test login with wrong password"""
        response = client.post("/api/users/login", json={
            "email": test_user["data"]["email"],
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        response = client.post("/api/users/login", json={
            "email": "nonexistent@example.com",
            "password": "password"
        })
        assert response.status_code == 401

    def test_get_current_user(self, test_user):
        """Test getting current user profile"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.get("/api/users/me", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["data"]["email"]
        assert data["username"] == test_user["data"]["username"]

    def test_get_current_user_unauthorized(self):
        """Test getting user without auth"""
        response = client.get("/api/users/me")
        assert response.status_code == 403  # No auth header

    def test_get_current_user_invalid_token(self):
        """Test getting user with invalid token"""
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/api/users/me", headers=headers)
        assert response.status_code == 401


class TestVoiceProfiles:
    """Test voice profile endpoints"""

    def test_list_voices_empty(self, test_user):
        """Test listing voices when user has none"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.get("/api/voices", headers=headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_upload_voice_unauthorized(self):
        """Test uploading voice without auth"""
        response = client.post("/api/voices/upload")
        assert response.status_code == 403

    def test_get_nonexistent_voice(self, test_user):
        """Test getting voice that doesn't exist"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.get("/api/voices/999", headers=headers)
        assert response.status_code == 404


class TestJobs:
    """Test job endpoints"""

    def test_list_jobs_empty(self, test_user):
        """Test listing jobs when user has none"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.get("/api/jobs", headers=headers)

        assert response.status_code == 200
        assert response.json() == []

    def test_get_nonexistent_job(self, test_user):
        """Test getting job that doesn't exist"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.get("/api/jobs/999", headers=headers)
        assert response.status_code == 404


class TestSynthesis:
    """Test synthesis endpoints"""

    def test_synthesize_unauthorized(self):
        """Test synthesis without auth"""
        response = client.post("/api/synthesize", json={
            "voice_profile_id": 1,
            "text": "Hello world"
        })
        assert response.status_code == 403

    def test_synthesize_nonexistent_voice(self, test_user):
        """Test synthesis with nonexistent voice"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.post("/api/synthesize", json={
            "voice_profile_id": 999,
            "text": "Hello world"
        }, headers=headers)
        assert response.status_code == 404

    def test_synthesize_empty_text(self, test_user):
        """Test synthesis with empty text"""
        headers = {"Authorization": f"Bearer {test_user['token']}"}
        response = client.post("/api/synthesize", json={
            "voice_profile_id": 1,
            "text": ""
        }, headers=headers)
        assert response.status_code == 422  # Validation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
