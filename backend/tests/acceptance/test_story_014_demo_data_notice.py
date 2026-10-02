from html.parser import HTMLParser
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
from urllib.request import urlopen

import pytest
from fastapi.testclient import TestClient
from websockets.sync.client import connect

from app.main import create_app


STATIC = Path(__file__).resolve().parents[2] / "app" / "static"


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
    candidates = (
        shutil.which("chrome"),
        shutil.which("chromium"),
        shutil.which("google-chrome"),
        shutil.which("msedge"),
        os.path.join(
            os.environ.get("PROGRAMFILES", ""),
            "Google",
            "Chrome",
            "Application",
            "chrome.exe",
        ),
        os.path.join(
            os.environ.get("PROGRAMFILES(X86)", ""),
            "Microsoft",
            "Edge",
            "Application",
            "msedge.exe",
        ),
    )
    return next(
        (browser for browser in candidates if browser and Path(browser).is_file()),
        None,
    )


def _cdp_command(connection, command_id: int, method: str, params: dict | None = None):
    connection.send(
        json.dumps({"id": command_id, "method": method, "params": params or {}})
    )
    while True:
        message = json.loads(connection.recv(timeout=10))
        if message.get("id") == command_id:
            assert "error" not in message, message.get("error")
            return message.get("result", {})


def _evaluate(connection, command_id: int, expression: str):
    result = _cdp_command(
        connection,
        command_id,
        "Runtime.evaluate",
        {"expression": expression, "returnByValue": True, "awaitPromise": True},
    )
    return result["result"].get("value")


def _wait_for(connection, command_id: int, expression: str, expected: str) -> None:
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if _evaluate(connection, command_id, expression) == expected:
            return
        time.sleep(0.1)
    pytest.fail(f"Timed out waiting for browser state {expected!r}.")


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


def test_tc_014_01_notice_is_visible_after_real_ui_initialization(tmp_path: Path) -> None:
    browser = _browser_executable()
    if browser is None:
        pytest.skip("Chrome, Chromium, or Edge is required for rendered notice validation.")

    with socket.socket() as server_socket:
        server_socket.bind(("127.0.0.1", 0))
        app_port = server_socket.getsockname()[1]
    with socket.socket() as debug_socket:
        debug_socket.bind(("127.0.0.1", 0))
        debug_port = debug_socket.getsockname()[1]

    server = subprocess.Popen(
        [
            sys.executable,
            "-c",
            (
                "import uvicorn; from pathlib import Path; "
                "from app.main import create_app; "
                f"uvicorn.run(create_app(Path({str(tmp_path / 'audit.sqlite3')!r})), "
                f"host='127.0.0.1', port={app_port})"
            ),
        ],
        cwd=Path(__file__).parents[2],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    chrome = None
    try:
        base_url = f"http://127.0.0.1:{app_port}"
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if server.poll() is not None:
                pytest.fail("The local application server exited before startup.")
            try:
                with urlopen(base_url, timeout=1):
                    break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("The local application server did not start.")

        profile = tmp_path / "chrome-profile"
        chrome = subprocess.Popen(
            [
                browser,
                "--headless",
                "--disable-gpu",
                "--no-first-run",
                "--no-default-browser-check",
                "--no-sandbox",
                "--remote-allow-origins=*",
                f"--remote-debugging-port={debug_port}",
                f"--user-data-dir={profile}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        version_url = f"http://127.0.0.1:{debug_port}/json/version"
        deadline = time.monotonic() + 15
        while time.monotonic() < deadline:
            if chrome.poll() is not None:
                pytest.fail("The headless browser exited before DevTools startup.")
            try:
                with urlopen(version_url, timeout=1) as response:
                    json.load(response)
                break
            except OSError:
                time.sleep(0.1)
        else:
            pytest.fail("The headless browser DevTools endpoint did not start.")

        with urlopen(f"http://127.0.0.1:{debug_port}/json/list") as response:
            targets = json.load(response)
        page_target = next(target for target in targets if target["type"] == "page")
        with connect(
            page_target["webSocketDebuggerUrl"],
            origin="http://localhost",
            additional_headers={"Origin": "http://localhost"},
            open_timeout=10,
        ) as connection:
            _cdp_command(connection, 1, "Page.enable")
            _cdp_command(connection, 2, "Runtime.enable")
            _cdp_command(
                connection,
                3,
                "Page.navigate",
                {"url": f"{base_url}/"},
            )
            _wait_for(
                connection,
                4,
                "document.querySelector('#identity-list button') ? 'ready' : 'loading'",
                "ready",
            )
            visibility = """
(() => {
  const notice = document.querySelector("section.notice");
  if (!notice) return false;
  const text = notice.innerText.toLowerCase().replace(/\\s+/g, " ");
  const requiredPhrases = [
    "demo or synthetic data",
    "real internal confidential information",
    "regulated personal information",
    "health information",
  ];
  if (!requiredPhrases.every((phrase) => text.includes(phrase))) return false;
  for (let element = notice; element; element = element.parentElement) {
    const style = getComputedStyle(element);
    const bounds = element.getBoundingClientRect();
    if (element.hasAttribute("hidden") || style.display === "none" ||
        style.visibility === "hidden" || Number(style.opacity) <= 0 ||
        bounds.width <= 0 || bounds.height <= 0) return false;
  }
  return true;
})()
"""
            assert _evaluate(connection, 5, visibility) is True
            _cdp_command(
                connection,
                6,
                "Runtime.evaluate",
                {
                    "expression": "document.querySelector('#identity-list button').click()",
                    "returnByValue": True,
                },
            )
            _wait_for(
                connection,
                7,
                "location.pathname === '/app' ? 'app' : 'navigating'",
                "app",
            )
            _wait_for(
                connection,
                8,
                "document.querySelector('#record-owner').options.length > 0 ? 'initialized' : 'loading'",
                "initialized",
            )
            assert _evaluate(connection, 9, visibility) is True
            assert _evaluate(
                connection,
                10,
                "Boolean(document.querySelector('#record-form'))",
            ) is True
            assert _evaluate(
                connection,
                11,
                "document.querySelector('#cancel-edit').hidden",
            ) is True
            assert _evaluate(
                connection,
                12,
                "!document.querySelector('#record-owner').disabled",
            ) is True

            _cdp_command(
                connection,
                13,
                "Runtime.evaluate",
                {
                    "expression": """
(() => {
  const field = document.querySelector("#tag-name");
  field.value = "story014-validation";
  document.querySelector("#tag-form").dispatchEvent(
    new Event("submit", {bubbles: true, cancelable: true})
  );
})()
""",
                    "returnByValue": True,
                },
            )
            _wait_for(
                connection,
                14,
                "document.querySelector('#record-tags option[value=\"story014-validation\"]') ? 'ready' : 'loading'",
                "ready",
            )
            _cdp_command(
                connection,
                15,
                "Runtime.evaluate",
                {
                    "expression": """
(() => {
  const form = document.querySelector("#record-form");
  form.elements.title.value = "STORY-014 notice validation record";
  form.elements.context.value = "Synthetic context for UI validation.";
  form.elements.decision.value = "Use a local demonstration.";
  form.elements.rationale.value = "Exercise the editable Draft UI.";
  form.elements.alternatives_considered.value = "No alternative.";
  form.elements.consequences.value = "The synthetic Draft is editable.";
  form.elements.owner_id.value = "maya-member";
  form.elements.decision_date.value = "2026-10-02";
  document.querySelector(
    '#record-tags option[value="story014-validation"]'
  ).selected = true;
  form.dispatchEvent(new Event("submit", {bubbles: true, cancelable: true}));
})()
""",
                    "returnByValue": True,
                },
            )
            _wait_for(
                connection,
                16,
                """[...document.querySelectorAll("#record-list h3")]
  .some((node) => node.textContent === "STORY-014 notice validation record")
    ? "created" : "creating" """,
                "created",
            )
            assert _evaluate(connection, 17, visibility) is True
            assert _evaluate(
                connection,
                18,
                "document.querySelector('#cancel-edit').hidden",
            ) is True
            _cdp_command(
                connection,
                19,
                "Runtime.evaluate",
                {
                    "expression": """
[...document.querySelectorAll("#record-list article")]
  .find((card) => card.querySelector("h3")?.textContent ===
    "STORY-014 notice validation record")
  ?.querySelector("button.secondary")?.click()
""",
                    "returnByValue": True,
                },
            )
            _wait_for(
                connection,
                20,
                "!document.querySelector('#cancel-edit').hidden ? 'editing' : 'loading'",
                "editing",
            )
            assert _evaluate(connection, 21, visibility) is True
            assert _evaluate(
                connection,
                22,
                """document.querySelector("#record-form")
  .getBoundingClientRect().height > 0 &&
  document.querySelector("#record-form").elements.title.value ===
    "STORY-014 notice validation record" &&
  document.querySelector("#record-form").querySelector(
    'button[type="submit"]'
  ).textContent === "Save changes" """,
            ) is True
    finally:
        if chrome is not None:
            chrome.terminate()
            try:
                chrome.wait(timeout=5)
            except subprocess.TimeoutExpired:
                chrome.kill()
                chrome.wait(timeout=5)
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
