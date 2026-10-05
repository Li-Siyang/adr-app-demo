"""TEST-001 v2.2 TC-016-01/03: real README-started local app at capacity.

No production fixtures, browser substitutions, or response-time assertions.
Browser timeouts are harness liveness guards, not performance criteria.
"""

from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import httpx
import pytest
from websockets.sync.client import connect


BACKEND = Path(__file__).resolve().parents[2]
ADMIN = "lee-admin-approver"
MEMBER = "maya-member"
OTHER = "arun-approver"
PREFIX = "/api/decision-records"
TAG = "story016-exact"
BROWSERS = {
    "chrome": Path(os.environ.get("PROGRAMFILES", "")) / "Google" / "Chrome"
    / "Application" / "chrome.exe",
    "edge": Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Microsoft" / "Edge"
    / "Application" / "msedge.exe",
}


def port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def request(client, method, path, payload=None, expected=200):
    response = client.request(method, path, json=payload)
    assert response.status_code == expected, (
        method, path, response.status_code, response.text
    )
    return response.json() if response.content else None


def select(client, identity):
    selected = request(client, "POST", "/api/mock-session", {"identity_id": identity})
    assert selected["selected_identity"]["id"] == identity


def payload(title, tags=None):
    return {
        "title": title, "context": "Synthetic capacity decision context.",
        "decision": "Use the integrated local demonstration.",
        "rationale": "Retain synthetic evidence of all approved workflows.",
        "alternatives_considered": "Synthetic alternative.",
        "consequences": "Retained synthetic decision.",
        "owner_id": OTHER, "decision_date": "2026-10-05",
        "tags": tags or [TAG, "story016-common"],
    }


def draft(client, title, tags=None, actor=MEMBER):
    select(client, actor)
    result = request(client, "POST", PREFIX, payload(title, tags), 201)
    assert result["status"] == "Draft" and result["author"]["id"] == actor
    assert result["owner"]["id"] == OTHER
    return result


def action(client, record, operation, actor=ADMIN, data=None, expected=200):
    select(client, actor)
    return request(client, "POST", f"{PREFIX}/{record['id']}/{operation}", data, expected)


def get(client, record):
    return request(client, "GET", f"{PREFIX}/{record['id']}")


def proposed(client, title):
    record = draft(client, title)
    return action(client, record, "submit", MEMBER)


def accepted(client, title):
    return action(client, proposed(client, title), "decision", data={"outcome": "Accepted"})


def replacement(client, original):
    return action(client, original, "replacements", expected=201)


@pytest.fixture(scope="module")
def local(tmp_path_factory):
    work = tmp_path_factory.mktemp("story016-local")
    base = f"http://127.0.0.1:{port()}"
    log_path = work / "uvicorn.log"
    with log_path.open("w") as log:
        server = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--reload",
             "--host", "127.0.0.1", "--port", base.rsplit(":", 1)[1]],
            cwd=BACKEND, stdout=log, stderr=subprocess.STDOUT,
            env={**os.environ, "WATCHFILES_FORCE_POLLING": "true"},
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        try:
            with httpx.Client(base_url=base, timeout=60) as client:
                deadline = time.monotonic() + 30
                while True:
                    assert server.poll() is None, log_path.read_text()
                    try:
                        ready = client.get("/")
                        if ready.status_code == 200:
                            break
                    except httpx.ConnectError:
                        pass
                    assert time.monotonic() < deadline, log_path.read_text()
                    time.sleep(0.1)
                identities = request(client, "GET", "/api/mock-identities")
                assert len(identities) == len({i["id"] for i in identities}) == 25
                assert all(i["is_mock"] and "Mock User" in i["label"] for i in identities)
                select(client, ADMIN)
                baseline_events = request(client, "GET", "/api/audit-events")["events"]
                (work / "audit-baseline.json").write_text(
                    json.dumps([event["id"] for event in baseline_events]),
                    encoding="utf-8",
                )
                request(client, "POST", "/api/approvers", {"identity_id": ADMIN})
                for index in range(25):
                    author = identities[index]["id"]
                    for offset in range(38):
                        record = draft(client, f"Synthetic {index:02}-{offset:02}", actor=author)
                        state = offset % 5
                        if state:
                            record = action(client, record, "submit", author)
                        if index == 0 and offset == 1:
                            select(client, author)
                            request(client, "PUT", f"{PREFIX}/{record['id']}",
                                    {"rationale": "Synthetic review-restart fixture."})
                            record = action(client, record, "submit", author)
                        if state in (2, 3, 4):
                            record = action(client, record, "decision",
                                            data={"outcome": "Rejected" if state == 3 else "Accepted"})
                        if offset == 36:
                            record = action(client, record, "decision", data={"outcome": "Accepted"})
                            rep = replacement(client, record)
                            action(client, rep, "submit")
                            action(client, rep, "decision", data={"outcome": "Accepted"})
                        if offset == 37:
                            rep = replacement(client, record)
                            action(client, rep, "abandon")
                        if offset % 10 == 0:
                            record = action(client, record, "archive")
                records = request(client, "GET", PREFIX)["records"]
                assert len(records) == len({r["id"] for r in records}) == 1000
                assert len({r["author"]["id"] for r in records}) == 25
                counts = Counter(r["status"] for r in records)
                assert counts == {
                    "Draft": 225, "Proposed": 175, "Accepted": 400,
                    "Rejected": 175, "Superseded": 25,
                }
                assert sum(r["archived"] for r in records) == 100
                assert sum(r["abandoned"] for r in records) == 25
                assert sum(r["replaces_record_id"] is not None for r in records) == 50
                print("CAPACITY_BASELINE", json.dumps({
                    "identities": 25, "records": 1000, "authors": 25,
                    "states": counts, "archived": 100, "abandoned": 25,
                    "linked_replacements": 50, "base_url": base,
                }))
                yield client, work, identities
                print("CAPACITY_FINAL", len(request(client, "GET", PREFIX)["records"]))
        finally:
            if os.name == "nt":
                subprocess.run(
                    ["powershell", "-NoProfile", "-Command",
                     f"Get-CimInstance Win32_Process -Filter 'ParentProcessId = {server.pid}' "
                     "| ForEach-Object { Stop-Process -Id $_.ProcessId -ErrorAction SilentlyContinue }; "
                     f"Stop-Process -Id {server.pid} -ErrorAction SilentlyContinue"],
                    capture_output=True, check=True,
                )
            else:
                server.terminate()
            server.wait(timeout=15)


def test_tc_016_01_identity_content_submission_and_review(local):
    """AC-002/004-008/023/024/029/043/044 at >=1000 records."""
    client, _, identities = local
    for identity in identities:
        select(client, identity["id"])
        assert request(client, "GET", "/api/mock-session")["selected_identity"] == identity
        assert request(client, "GET", "/api/attribution-preview")["actor"] == identity
    for field in payload("Required content"):
        missing = payload("Required content")
        del missing[field]
        if field != "tags":
            denied = client.post(PREFIX, json=missing)
            assert denied.status_code == 422 and field in denied.text
    select(client, ADMIN)
    request(client, "DELETE", f"/api/approvers/{ADMIN}")
    record = draft(client, "Submission guards")
    for field in ("title", "context", "decision", "rationale",
                  "alternatives_considered", "consequences", "tags"):
        empty = [] if field == "tags" else ""
        request(client, "PUT", f"{PREFIX}/{record['id']}", {field: empty})
        error = action(client, record, "submit", MEMBER, expected=422)
        assert field in error["detail"]["missing_fields"]
        assert "approver" in json.dumps(error).lower()
        request(client, "PUT", f"{PREFIX}/{record['id']}", {field: payload("Submission guards")[field]})
    select(client, ADMIN)
    request(client, "POST", "/api/approvers", {"identity_id": ADMIN})
    permissions = request(client, "GET", "/api/governance/permissions")["permissions"]
    assert {"create_replacements", "accept_proposals", "archive_records"}.issubset(permissions)
    record = action(client, record, "submit", MEMBER)
    for outcome in ("Accepted", "Rejected"):
        action(client, record, "decision", MEMBER, {"outcome": outcome}, 403)
    select(client, MEMBER)
    edited = request(client, "PUT", f"{PREFIX}/{record['id']}", {"title": "Review restarted"})
    assert edited["status"] == "Draft"
    action(client, edited, "decision", ADMIN, {"outcome": "Accepted"}, 409)
    action(client, edited, "submit", MEMBER)
    action(client, edited, "decision", ADMIN, {"outcome": "Accepted"})
    for outcome in ("Accepted", "Rejected"):
        own = draft(client, f"Self {outcome}", actor=ADMIN)
        own = action(client, own, "submit")
        assert action(client, own, "decision", data={"outcome": outcome})["status"] == outcome
    select(client, MEMBER)
    created_tag = request(client, "POST", "/api/tags", {"name": "story016-created"}, 201)
    assert created_tag["name"] in request(client, "GET", "/api/tags")["tags"]
    tagged = draft(client, "Associated tags", ["story016-created", TAG])
    assert tagged["tags"] == ["story016-created", TAG]


def test_tc_016_01_ownership_versions_retention_and_role_matrix(local):
    """AC-003/009-014/020-021/025-026/030/038-039/045-047."""
    client, _, identities = local
    record = draft(client, "Ownership matrix")
    for state in ("Draft", "Proposed"):
        for actor, owner in ((MEMBER, ADMIN), (ADMIN, OTHER), (OTHER, MEMBER)):
            result = action(client, record, "owner", actor, {"owner_id": owner})
            assert result["owner"]["id"] == owner and result["author"]["id"] == MEMBER
        action(client, record, "owner", "mock-user-05", {"owner_id": ADMIN}, 403)
        if state == "Draft":
            action(client, record, "submit", MEMBER)
    original = accepted(client, "Version governance")
    retained = [original]
    first = replacement(client, original)
    action(client, original, "replacements", expected=409)
    action(client, first, "abandon", MEMBER, expected=403)
    abandoned = action(client, first, "abandon")
    assert abandoned["abandoned"] and abandoned["status"] == "Draft"
    assert get(client, original)["status"] == "Accepted"
    assert first["id"] in get(client, original)["replacement_record_ids"]
    retained.append(abandoned)
    second = replacement(client, original)
    action(client, second, "submit")
    action(client, original, "archive", expected=409)
    rejected = action(client, second, "decision", data={"outcome": "Rejected"})
    retained.append(rejected)
    third = replacement(client, original)
    action(client, third, "submit")
    new = action(client, third, "decision", data={"outcome": "Accepted"})
    assert get(client, original)["status"] == "Superseded"
    assert new["replaces_record_id"] == original["id"]
    retained[0] = get(client, original)
    retained.extend([new, draft(client, "Ordinary retained Draft"), proposed(client, "Retained proposal")])
    for actor in identities:
        select(client, actor["id"])
        for item in retained:
            before = get(client, item)
            if item["status"] in ("Accepted", "Rejected", "Superseded") or item["abandoned"]:
                assert client.put(f"{PREFIX}/{item['id']}", json={"title": "Mutation"}).status_code in (403, 409)
                assert client.post(f"{PREFIX}/{item['id']}/owner", json={"owner_id": OTHER}).status_code in (403, 409)
            assert client.delete(f"{PREFIX}/{item['id']}").status_code == 405
            assert client.put(f"{PREFIX}/{item['id']}", json={"deleted": True}).status_code == 422
            assert get(client, item) == before
    for item in retained:
        if not item["abandoned"]:
            action(client, item, "abandon", expected=409)
        before = get(client, item)
        archived = action(client, item, "archive")
        assert archived["archived"] and archived["status"] == before["status"]
        assert item["id"] in {r["id"] for r in request(client, "GET", PREFIX, )["records"]}
        restored = action(client, item, "restore")
        assert restored == before
    for operation, item in (("archive", new), ("replacements", new), ("abandon", abandoned)):
        action(client, item, operation, MEMBER, expected=403)
    action(client, new, "archive")
    action(client, new, "restore", MEMBER, expected=403)
    action(client, new, "restore")
    for actor in (ADMIN, MEMBER, OTHER):
        select(client, actor)
        assert client.put(f"{PREFIX}/{abandoned['id']}", json={"abandoned": False}).status_code == 422
        assert client.post(f"{PREFIX}/{abandoned['id']}/submit").status_code in (403, 409)
    departed = draft(client, "Retained departed author")
    select(client, OTHER)
    assert client.put(f"{PREFIX}/{departed['id']}", json={"title": "Departure grants no edit"}).status_code == 403
    action(client, departed, "owner", OTHER, {"owner_id": ADMIN})
    select(client, ADMIN)
    assert client.put(f"{PREFIX}/{departed['id']}", json={"title": "No extra edit"}).status_code == 403
    assert get(client, departed)["author"]["id"] == MEMBER
    for actor in (MEMBER, OTHER):
        select(client, actor)
        assert client.post("/api/approvers", json={"identity_id": actor}).status_code == 403
        assert client.delete(f"/api/approvers/{ADMIN}").status_code == 403
    select(client, ADMIN)
    assert client.post("/api/approvers", json={"identity_id": ADMIN}).status_code == 200
    assert client.post("/api/approvers", json={"identity_id": MEMBER}).status_code == 200
    assert client.delete(f"/api/approvers/{MEMBER}").status_code == 200


def test_tc_016_01_discovery_comments_audit_and_concurrency(local):
    """AC-013/015-016/018-019/033-034 plus concurrent transitions/deletion."""
    client, work, _ = local
    target = draft(client, "Exact discovery", ["story016-filter"])
    draft(client, "Not an exact match", ["story016-filter-longer"])
    action(client, target, "archive")
    found = client.get(PREFIX, params={"tag": "story016-filter"}).json()["records"]
    assert [r["id"] for r in found] == [target["id"]] and found[0]["archived"]
    all_tagged = client.get(PREFIX, params={"tag": TAG}).json()["records"]
    assert {"Draft", "Proposed", "Accepted", "Rejected", "Superseded"}.issubset({r["status"] for r in all_tagged})
    assert any(r["archived"] for r in all_tagged)
    select(client, MEMBER)
    comment = request(client, "POST", f"{PREFIX}/{target['id']}/comments", {"content": "Synthetic discussion"}, 201)
    assert comment["author"]["id"] == MEMBER and comment in get(client, target)["comments"]
    select(client, OTHER)
    request(client, "DELETE", f"{PREFIX}/{target['id']}/comments/{comment['id']}", expected=403)
    select(client, MEMBER)
    with ThreadPoolExecutor(max_workers=2) as pool:
        deleted = list(pool.map(lambda _: client.delete(f"{PREFIX}/{target['id']}/comments/{comment['id']}"), range(2)))
    assert all(r.status_code in (200, 409) for r in deleted)
    comments = get(client, target)["comments"]
    assert len(comments) == 1 and comments[0]["content"] == "[deleted]"
    proposal = proposed(client, "One concurrent outcome")
    select(client, ADMIN)
    with ThreadPoolExecutor(max_workers=2) as pool:
        outcomes = list(pool.map(lambda outcome: client.post(
            f"{PREFIX}/{proposal['id']}/decision", json={"outcome": outcome}), ("Accepted", "Rejected")))
    assert sorted(r.status_code for r in outcomes) == [200, 409]
    events = request(client, "GET", "/api/audit-events")["events"]
    baseline_ids = set(json.loads((work / "audit-baseline.json").read_text(encoding="utf-8")))
    events = [event for event in events if event["id"] not in baseline_ids]
    expected = {"approver_designation_changed", "lifecycle_transitioned",
                "record_archived", "record_restored", "replacement_draft_abandoned",
                "ownership_transferred", "comment_deleted"}
    assert expected.issubset({event["event_type"] for event in events})
    for event in events:
        assert event["actor"]["id"] and event["occurred_at"] and event["changes"]
        assert "expires_at" not in event
    for kind, actor in (("comment_deleted", MEMBER), ("replacement_draft_abandoned", ADMIN)):
        event = next(e for e in events if e["event_type"] == kind)
        assert event["actor"]["id"] == actor
        path = f"/api/audit-events/{event['id']}"
        assert client.delete(path).status_code == 405
        assert client.put(path, json={"expires_at": "2026-10-06"}).status_code == 405
        assert request(client, "GET", path) == request(client, "GET", path) == event
    transitions = {
        (change["before"], change["after"])
        for event in events
        if event["event_type"] == "lifecycle_transitioned"
        for change in event["changes"]
        if change["field"] == "status"
    }
    required = {
        ("Draft", "Proposed"), ("Proposed", "Draft"),
        ("Proposed", "Accepted"), ("Proposed", "Rejected"),
        ("Accepted", "Superseded"),
    }
    assert required.issubset(transitions), {
        "missing_lifecycle_audit": sorted(required - transitions),
        "actual_transitions": sorted(transitions, key=lambda pair: (str(pair[0]), str(pair[1]))),
    }


def test_tc_016_01_submission_audit_attribution_and_retention(local):
    """AC-013/033: submission is itself an attributed, retained transition."""
    client, _, _ = local
    record = draft(client, "Audited submission at capacity")
    submitted = action(client, record, "submit", MEMBER)
    assert submitted["status"] == "Proposed"
    events = request(client, "GET", f"{PREFIX}/{record['id']}/audit-events")["events"]
    expected_change = {"field": "status", "before": "Draft", "after": "Proposed"}
    matches = [e for e in events if expected_change in e["changes"]]
    assert len(matches) == 1, {
        "record_id": record["id"], "expected_change": expected_change,
        "actual_events": events, "record_status": get(client, record)["status"],
    }
    assert matches[0]["actor"]["id"] == MEMBER and matches[0]["occurred_at"]
    assert request(client, "GET", f"/api/audit-events/{matches[0]['id']}") == matches[0]


class Browser:
    def __init__(self, executable, work):
        self.debug_port = port()
        self.process = subprocess.Popen(
            [str(executable), "--headless", "--disable-gpu", "--no-first-run",
             "--no-default-browser-check", "--remote-allow-origins=*",
             f"--remote-debugging-port={self.debug_port}", f"--user-data-dir={work}"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        self.connection = None
        self.connection_context = None
        self.command_id = 0

    def __enter__(self):
        try:
            with httpx.Client(timeout=2) as client:
                deadline = time.monotonic() + 30
                while True:
                    assert self.process.poll() is None, "Browser exited before DevTools readiness"
                    try:
                        self.version = client.get(f"http://127.0.0.1:{self.debug_port}/json/version").json()
                        targets = client.get(f"http://127.0.0.1:{self.debug_port}/json/list").json()
                        target = next((t for t in targets if t["type"] == "page"), None)
                        if target:
                            break
                    except httpx.ConnectError:
                        pass
                    assert time.monotonic() < deadline, "Browser DevTools unavailable"
                    time.sleep(0.1)
            self.connection_context = connect(
                target["webSocketDebuggerUrl"], origin="http://localhost"
            )
            self.connection = self.connection_context.__enter__()
            self.command("Page.enable")
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *_):
        if self.connection:
            self.connection_context.__exit__(None, None, None)
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=10)

    def command(self, method, params=None):
        self.command_id += 1
        self.connection.send(json.dumps({"id": self.command_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self.connection.recv(timeout=60))
            if message.get("id") == self.command_id:
                assert "error" not in message, message
                return message["result"]

    def evaluate(self, expression):
        result = self.command("Runtime.evaluate", {"expression": expression, "returnByValue": True, "awaitPromise": True})
        assert "exceptionDetails" not in result, result
        return result["result"].get("value")

    def wait(self, expression):
        deadline = time.monotonic() + 60
        while not self.evaluate(expression):
            assert time.monotonic() < deadline, expression
            time.sleep(0.1)

    def click(self, record_id, text):
        card = f"document.getElementById('record-card-{record_id}')"
        self.wait(f"{card} && [...{card}.querySelectorAll('button')].some(b=>b.textContent==={json.dumps(text)}&&!b.disabled)")
        self.evaluate(f"[...{card}.querySelectorAll('button')].find(b=>b.textContent==={json.dumps(text)}).click()")


NOTICE = """(() => {
  const n=document.querySelector('section.notice');
  if (!n || !n.getBoundingClientRect().height) return false;
  const t=n.innerText.toLowerCase();
  return ['demo or synthetic data','real internal confidential information',
    'regulated personal information','health information'].every(p=>t.includes(p))
    && getComputedStyle(n).visibility==='visible';
})()"""


def test_tc_016_03_readme_local_browser_workflows(local):
    """All UI workflows locally; API-only administration is exercised above."""
    client, work, _ = local
    executable = BROWSERS["chrome"]
    assert executable.is_file(), "TEST_ENVIRONMENT: Chrome unavailable for local E2E"
    with Browser(executable, work / "local-chrome-profile") as browser:
        print("LOCAL_BROWSER", json.dumps(browser.version))
        run_ui_workflows(browser, client)


def run_ui_workflows(browser, client):
    base = str(client.base_url).rstrip("/")
    browser.command("Page.navigate", {"url": base})
    browser.wait("document.querySelectorAll('#identity-list button').length===25")
    assert browser.evaluate(NOTICE)
    assert "not authentication" in browser.evaluate("document.body.innerText").lower()
    browser.evaluate(f"[...document.querySelectorAll('#identity-list button')].find(b=>b.textContent.includes('Lee')).click()")
    browser.wait("location.pathname==='/app' && document.querySelector('#record-owner').options.length===25")
    browser.wait("document.querySelectorAll('#record-list article').length>=1000")
    assert browser.evaluate(NOTICE)
    tag = f"ui-{browser.debug_port}"
    browser.evaluate(f"document.querySelector('#tag-name').value={json.dumps(tag)}; document.querySelector('#tag-form button').click()")
    browser.wait(f"[...document.querySelector('#record-tags').options].some(o=>o.value==={json.dumps(tag)})")
    data = payload(f"Synthetic UI {tag}", [tag, TAG])
    browser.evaluate(f"""(() => {{
      const f=document.querySelector('#record-form'), d={json.dumps(data)};
      for (const [k,v] of Object.entries(d)) if(k!=='tags') f.elements[k].value=v;
      for(const o of f.elements.tags.options) o.selected=d.tags.includes(o.value);
      f.querySelector('button[type=submit]').click();
    }})()""")
    browser.wait(f"[...document.querySelectorAll('#record-list h3')].some(h=>h.textContent==={json.dumps(data['title'])})")
    record = next(r for r in request(client, "GET", PREFIX)["records"] if r["title"] == data["title"])
    assert record["author"]["id"] == ADMIN and set(record["tags"]) == set(data["tags"])
    rid = record["id"]
    browser.click(rid, "Edit Draft")
    browser.wait("!document.querySelector('#cancel-edit').hidden")
    assert browser.evaluate(NOTICE)
    browser.evaluate("document.querySelector('#record-form').elements.rationale.value='Synthetic UI edit'; document.querySelector('#record-form button[type=submit]').click()")
    browser.wait("document.querySelector('#cancel-edit').hidden")
    browser.click(rid, "Submit Draft")
    browser.wait(f"document.getElementById('record-card-{rid}').innerText.includes('Proposed')")
    browser.click(rid, "Edit proposal")
    browser.wait("!document.querySelector('#cancel-edit').hidden")
    browser.evaluate("document.querySelector('#record-form').elements.decision.value='Synthetic review restart'; document.querySelector('#record-form button[type=submit]').click()")
    browser.wait(f"document.getElementById('record-card-{rid}').innerText.includes('Draft')")
    browser.click(rid, "Transfer ownership")
    browser.wait("document.querySelector('#transfer-message').textContent==='Record ownership transferred.'")
    browser.click(rid, "Submit Draft")
    browser.wait(f"document.getElementById('record-card-{rid}').innerText.includes('Proposed')")
    browser.click(rid, "Accept proposal")
    browser.wait(f"document.getElementById('record-card-{rid}').innerText.includes('Accepted')")
    browser.click(rid, "Create replacement Draft")
    browser.wait("document.querySelector('#replacement-message').textContent==='Replacement Draft created.' && !document.querySelector('#record-list-message').textContent")
    rep = get(client, record)["replacement_record_ids"][-1]
    browser.click(rep, "Abandon replacement Draft")
    browser.wait(f"document.getElementById('record-card-{rep}').innerText.includes('Abandoned')")
    browser.click(rep, "Archive record")
    browser.wait(f"document.getElementById('record-card-{rep}').innerText.includes('Archived')")
    browser.click(rep, "Restore record")
    browser.wait(f"!document.getElementById('record-card-{rep}').innerText.includes('Archived')")
    assert get(client, {"id": rep})["abandoned"]
    browser.click(rid, "Create replacement Draft")
    browser.wait("document.querySelector('#replacement-message').textContent==='Replacement Draft created.' && !document.querySelector('#record-list-message').textContent")
    rep2 = get(client, record)["replacement_record_ids"][-1]
    browser.click(rep2, "Submit Draft")
    browser.wait(f"document.getElementById('record-card-{rep2}').innerText.includes('Proposed')")
    browser.click(rep2, "Reject proposal")
    browser.wait(f"document.getElementById('record-card-{rep2}').innerText.includes('Rejected')")
    browser.click(rid, "Create replacement Draft")
    browser.wait("document.querySelector('#replacement-message').textContent==='Replacement Draft created.' && !document.querySelector('#record-list-message').textContent")
    rep3 = get(client, record)["replacement_record_ids"][-1]
    browser.click(rep3, "Submit Draft")
    browser.wait(f"document.getElementById('record-card-{rep3}').innerText.includes('Proposed')")
    browser.click(rep3, "Accept proposal")
    browser.wait(f"document.getElementById('record-card-{rid}').innerText.includes('Superseded')")
    browser.evaluate(f"document.querySelector('#tag-filter').value={json.dumps(tag)}; document.querySelector('#tag-filter').dispatchEvent(new Event('change'))")
    browser.wait("!document.querySelector('#record-list-message').textContent")
    assert browser.evaluate("document.querySelectorAll('#record-list article').length") == 4
    browser.evaluate(f"document.querySelector('#record-card-{rep3} .version-links a').click()")
    browser.wait(f"location.hash==='#record-card-{rid}'")
    browser.evaluate(f"document.querySelector('#record-card-{rid} .version-links a[href=\"#record-card-{rep}\"]').click()")
    browser.wait(f"location.hash==='#record-card-{rep}'")
    browser.evaluate(f"document.querySelector('#record-card-{rid} .comment-form textarea').value='Synthetic UI comment'")
    browser.click(rid, "Add comment")
    browser.wait(f"document.getElementById('record-card-{rid}').innerText.includes('Synthetic UI comment')")
    browser.click(rid, "Delete comment")
    browser.wait(f"document.getElementById('record-card-{rid}').innerText.includes('[deleted]')")
    browser.evaluate(f"document.querySelector('#record-card-{rid} summary').click()")
    browser.wait(f"document.querySelector('#record-card-{rid} .record-history ol').innerText.includes('Changed by')")
    history = browser.evaluate(f"document.querySelector('#record-card-{rid} .record-history ol').innerText")
    assert "Rationale" in history
    browser.click(rid, "Archive record")
    browser.wait(f"document.getElementById('record-card-{rid}').innerText.includes('Archived')")
    browser.click(rid, "Restore record")
    browser.wait(f"!document.getElementById('record-card-{rid}').innerText.includes('Archived')")
    assert get(client, record)["status"] == "Superseded"
    assert browser.evaluate("[...document.querySelectorAll('#record-list button')].every(b=>!/^Delete record/.test(b.textContent))")
    browser.evaluate("document.querySelector('#change-identity').click()")
    browser.wait("location.pathname==='/' && document.querySelectorAll('#identity-list button').length===25")
    assert browser.evaluate(NOTICE)
    assert "Status: Draft -> Proposed" in history, {
        "missing_ui_history": "Draft -> Proposed", "actual_history": history,
    }
