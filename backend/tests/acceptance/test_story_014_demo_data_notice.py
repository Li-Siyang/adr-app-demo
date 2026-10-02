from html.parser import HTMLParser
import os
from pathlib import Path
import re
import shutil
import subprocess

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


class DataNoticeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.notice_visible = False
        self.record_form_visible = False
        self.notice_text: list[str] = []
        self._in_notice = False

    def handle_starttag(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
    ) -> None:
        attributes = dict(attrs)
        if tag == "section":
            if "notice" in attributes.get("class", "").split():
                self._in_notice = True
                self.notice_visible = "hidden" not in attributes
        if tag == "form" and attributes.get("id") == "record-form":
            self.record_form_visible = "hidden" not in attributes

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self._in_notice:
            self._in_notice = False

    def handle_data(self, data: str) -> None:
        if self._in_notice:
            self.notice_text.append(data)


def _browser_executable() -> str | None:
    configured = os.environ.get("CHROME_BIN") or os.environ.get("BROWSER_BIN")
    if configured and Path(configured).is_file():
        return configured

    executable = shutil.which("chrome") or shutil.which("msedge")
    if executable:
        return executable

    if os.name == "nt":
        candidates = (
            Path(os.environ.get("PROGRAMFILES", "")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft/Edge/Application/msedge.exe",
        )
        return next((str(path) for path in candidates if path.is_file()), None)

    return None


def _assert_browser_notice_visible(tmp_path: Path, path: str) -> None:
    browser = _browser_executable()
    if browser is None:
        pytest.skip("Chrome or Edge is required for rendered notice visibility.")

    static_dir = Path(__file__).parents[2] / "app" / "static"
    html = (static_dir / ("index.html" if path == "/" else "app.html")).read_text(
        encoding="utf-8"
    )
    html = html.replace('/static/styles.css', 'styles.css')
    html = re.sub(r'<script\b[^>]*>\s*</script>', "", html)
    probe = """
<script>
(() => {
  const notice = document.querySelector("section.notice");
  let visible = Boolean(notice);
  for (let element = notice; element; element = element.parentElement) {
    const style = getComputedStyle(element);
    const bounds = element.getBoundingClientRect();
    visible = visible
      && !element.hasAttribute("hidden")
      && style.display !== "none"
      && style.visibility !== "hidden"
      && Number(style.opacity) > 0
      && bounds.width > 0
      && bounds.height > 0;
  }
  document.documentElement.dataset.noticeRenderedVisible = String(visible);
})();
</script>
"""
    html = html.replace("</body>", f"{probe}</body>")
    page = tmp_path / "notice-surface.html"
    page.write_text(html, encoding="utf-8")
    shutil.copyfile(static_dir / "styles.css", tmp_path / "styles.css")

    result = subprocess.run(
        [
            browser,
            "--headless",
            "--disable-gpu",
            "--dump-dom",
            page.as_uri(),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert 'data-notice-rendered-visible="true"' in result.stdout


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
    if path == "/app":
        assert parser.record_form_visible
    notice = " ".join(" ".join(parser.notice_text).split()).lower()
    assert "demo or synthetic data" in notice
    assert "real internal confidential information" in notice
    assert "regulated personal information" in notice
    assert "health information" in notice
    _assert_browser_notice_visible(tmp_path, path)
