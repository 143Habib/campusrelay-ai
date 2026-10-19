from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app


@pytest.fixture
def client(tmp_path: Path):
    settings = Settings(db_path=tmp_path / "tests.db",app_env="test",enable_demo_data=True)
    with TestClient(create_app(settings)) as c:
        yield c


@pytest.fixture
def staff(client):
    result = client.post('/api/auth/login',json={'email':'staff@campusrelay.demo','password':'Staff@2026!'})
    assert result.status_code == 200, result.text
    return client, {'X-CSRF-Token': result.json()['csrf_token']}


@pytest.fixture
def student(client):
    result = client.post('/api/auth/login',json={'email':'student@campusrelay.demo','password':'Student@2026!'})
    assert result.status_code == 200, result.text
    return client, {'X-CSRF-Token': result.json()['csrf_token']}


@pytest.fixture
def admin(client):
    result = client.post('/api/auth/login',json={'email':'admin@campusrelay.demo','password':'Admin@2026!'})
    assert result.status_code == 200, result.text
    return client, {'X-CSRF-Token': result.json()['csrf_token']}
