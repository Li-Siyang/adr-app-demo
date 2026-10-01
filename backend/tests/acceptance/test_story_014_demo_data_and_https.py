from collections.abc import Iterator
from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


class DataNoticeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.notice_visible = False
        self.notice_text: list[str] = []
        self._in_notice = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        if tag == "section":
            attributes = dict(attrs)
            if "notice" in attributes.get("class", "").split():
                self._in_notice = True
                self.notice_visible = "hidden" not in attributes

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self._in_notice:
            self._in_notice = False

    def handle_data(self, data: str) -> None:
        if self._in_notice:
            self.notice_text.append(data)


@pytest.mark.parametrize(
    "path",
    ("/", "/app"),
    ids=("identity-entry", "record-create-edit"),
)
def test_tc_014_01_data_notice_is_visible_on_required_surfaces(
    tmp_path,
    path: str,
) -> None:
    with TestClient(create_app(tmp_path / "audit.sqlite3")) as client:
        response = client.get(path)

    assert response.status_code == 200
    parser = DataNoticeParser()
    parser.feed(response.text)

    assert parser.notice_visible
    notice = " ".join(" ".join(parser.notice_text).split()).lower()
    assert "demo or synthetic data" in notice
    assert "real internal confidential information" in notice
    assert "regulated personal information" in notice
    assert "health information" in notice


@pytest.fixture
def production_client(monkeypatch, tmp_path) -> Iterator[TestClient]:
    monkeypatch.setenv("APP_ENV", "production")
    with TestClient(
        create_app(tmp_path / "audit.sqlite3"),
        follow_redirects=False,
    ) as client:
        yield client


def test_tc_014_02_production_redirects_page_and_api_traffic_to_https(
    production_client: TestClient,
) -> None:
    for path in ("/app", "/api/mock-identities"):
        response = production_client.get(path)

        assert response.status_code == 307
        assert response.headers["location"] == f"https://testserver{path}"


def test_tc_014_02_production_serves_page_and_api_over_https(tmp_path) -> None:
    with TestClient(
        create_app(tmp_path / "audit.sqlite3", environment="production"),
        base_url="https://testserver",
    ) as client:
        page = client.get("/app")
        api = client.get("/api/mock-identities")

    assert page.status_code == 200
    assert api.status_code == 200


def test_tc_014_02_development_keeps_page_and_api_available_over_http(
    tmp_path,
) -> None:
    with TestClient(
        create_app(tmp_path / "audit.sqlite3", environment="development")
    ) as client:
        page = client.get("/app")
        api = client.get("/api/mock-identities")

    assert page.status_code == 200
    assert api.status_code == 200
