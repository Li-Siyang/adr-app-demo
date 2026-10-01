from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def production_client(monkeypatch, tmp_path) -> Iterator[TestClient]:
    monkeypatch.setenv("APP_ENV", "production")
    with TestClient(
        create_app(tmp_path / "audit.sqlite3"),
        follow_redirects=False,
    ) as test_client:
        yield test_client


def test_production_redirects_http_requests_to_https(
    production_client: TestClient,
) -> None:
    response = production_client.get("/")

    assert response.status_code == 307
    assert response.headers["location"] == "https://testserver/"


def test_production_serves_https_requests(tmp_path) -> None:
    app = create_app(tmp_path / "audit.sqlite3", environment="production")
    with TestClient(
        app,
        base_url="https://testserver",
    ) as client:
        response = client.get("/")

    assert response.status_code == 200


def test_development_allows_http_requests(tmp_path) -> None:
    with TestClient(
        create_app(tmp_path / "audit.sqlite3", environment="development")
    ) as client:
        response = client.get("/")

    assert response.status_code == 200


def test_app_environment_defaults_to_development(monkeypatch, tmp_path) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)

    with TestClient(create_app(tmp_path / "audit.sqlite3")) as client:
        response = client.get("/")

    assert response.status_code == 200


@pytest.mark.parametrize("environment", ("staging", ""))
def test_invalid_app_environment_fails_fast(tmp_path, environment: str) -> None:
    with pytest.raises(
        ValueError,
        match="APP_ENV must be either 'development' or 'production'",
    ):
        create_app(tmp_path / "audit.sqlite3", environment=environment)
