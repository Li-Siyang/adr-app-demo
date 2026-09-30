"""Independent browser regression for STORY-012 review findings."""

import os
import subprocess
import tempfile
from pathlib import Path

import pytest


STATIC = Path(__file__).resolve().parents[2] / "app" / "static"
CHROME = Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe")


@pytest.mark.skipif(not CHROME.is_file(), reason="Chrome unavailable")
def test_archive_edit_warning_and_pending_mutations_in_real_ui():
    mock = r"""
<script>
const first = {
  id: "first", title: "First", status: "Draft", archived: false,
  author: {id: "admin", display_name: "Admin"},
  owner: {id: "admin", display_name: "Admin"}, decision_date: "2026-09-30",
  tags: [], replacement_record_ids: [], abandoned: false,
  context: "Context", decision: "Decision", rationale: "Rationale",
  alternatives_considered: "Alternative", consequences: "Consequence",
};
const second = {...first, id: "second", title: "Second"};
let settle, actionCount = 0, edits = 0, listCount = 0;
let pauseNextList = false, releaseList;
function response(body = {}, ok = true) {
  return {ok, json: async () => body};
}
window.fetch = async (url, init = {}) => {
  if (url === "/api/mock-session") return response({selected_identity: {
    id: "admin", label: "Admin", roles: ["administrator"],
  }});
  if (url === "/api/governance/permissions") return response({
    identity: {roles: ["administrator"]}, designated_approver: false,
  });
  if (url === "/api/tags") return response({tags: []});
  if (url === "/api/mock-identities") return response([{id: "admin", label: "Admin"}]);
  if (url === "/api/attribution-preview") return response({message: "Admin"});
  if (url === "/api/decision-records") {
    listCount++;
    if (pauseNextList) {
      pauseNextList = false;
      await new Promise(resolve => { releaseList = resolve; });
    }
    return response({records: [first, second]});
  }
  if (url === "/api/decision-records/first/archive" ||
      url === "/api/decision-records/first/restore") {
    actionCount++;
    return new Promise(resolve => { settle = resolve; });
  }
  if (url === "/api/decision-records/first" && init.method === "PUT") {
    edits++;
    return response(first);
  }
  throw new Error(`Unexpected API call: ${url}`);
};
function button(id, text) {
  return [...document.querySelectorAll(`#record-card-${id} button`)]
    .find(node => node.textContent === text);
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
async function tick() {
  await new Promise(resolve => setTimeout(resolve, 20));
}
async function run() {
  for (let n = 0; !button("first", "Edit Draft") && n < 100; n++) await tick();
  assert(button("first", "Edit Draft"), "UI not initialized");
  button("first", "Edit Draft").click();
  const form = document.querySelector("#record-form");
  const notice = document.querySelector("#record-form-message");
  form.elements.title.value = "Unsaved title";
  button("first", "Archive record").click();
  assert(actionCount === 0 && form.elements.title.value === "Unsaved title",
    "Archive while editing lost changes or posted");
  assert(notice.textContent.includes("Save or cancel") &&
    notice.classList.contains("error"), "Warning missing from edit form");
  document.querySelector("#cancel-edit").click();
  assert(!notice.textContent, "Cancel did not clear warning");

  button("first", "Edit Draft").click();
  button("first", "Archive record").click();
  form.dispatchEvent(new Event("submit", {bubbles: true, cancelable: true}));
  await tick();
  assert(edits === 1 && !notice.textContent.includes("Save or cancel"),
    "Save did not replace archive warning");

  button("first", "Archive record").click();
  assert(actionCount === 1, "Archive request not sent once");
  assert([...document.querySelectorAll("#record-card-first button, #record-card-first select")]
    .every(node => node.disabled), "Record still has enabled mutation controls");
  assert(!button("second", "Edit Draft").disabled, "Other record incorrectly locked");
  document.querySelector("#tag-filter").dispatchEvent(new Event("change"));
  await tick();
  assert(button("first", "Edit Draft").disabled &&
    !button("second", "Edit Draft").disabled, "Filter refresh lost record-specific lock");
  button("first", "Edit Draft").click();
  assert(form.elements.title.value !== "First", "Locked edit started");
  settle(response({detail: "Rejected"}, false));
  await tick();
  assert(!button("first", "Edit Draft").disabled &&
    !button("first", "Archive record").disabled,
    "Failed request did not unlock card");

  button("first", "Archive record").click();
  first.archived = true;
  pauseNextList = true;
  settle(response());
  await tick();
  assert(typeof releaseList === "function" &&
    button("first", "Edit Draft").disabled, "Refresh interval not locked");
  releaseList();
  await tick();
  assert(!button("first", "Edit Draft") &&
    !button("first", "Restore record").disabled,
    "Successful archive did not update controls");
  button("first", "Restore record").click();
  assert(button("first", "Restore record").disabled, "Restore not locked");
  first.archived = false;
  settle(response());
  await tick();
  assert(!button("first", "Archive record").disabled &&
    !button("second", "Edit Draft").disabled, "Restore did not unlock");
  document.body.dataset.validation = "passed";
}
setTimeout(() => run().catch(error => {
  document.body.dataset.validation = `failed: ${error.message}`;
}), 0);
</script>
"""
    html = (STATIC / "app.html").read_text(encoding="utf-8").replace(
        '<script src="/static/app.js" defer></script>', mock
    )
    html = html.replace(
        "</body>",
        f"<script>{(STATIC / 'app.js').read_text(encoding='utf-8')}</script></body>",
    )
    with tempfile.TemporaryDirectory() as directory:
        page = Path(directory) / "index.html"
        page.write_text(html, encoding="utf-8")
        result = subprocess.run(
            [
                str(CHROME), "--headless", "--disable-gpu", "--no-first-run",
                "--no-default-browser-check", "--virtual-time-budget=5000",
                "--dump-dom", page.as_uri(),
            ],
            capture_output=True, text=True, timeout=35, check=True,
            env={**os.environ, "CHROME_LOG_FILE": str(Path(directory) / "chrome.log")},
        )
    assert 'data-validation="passed"' in result.stdout, result.stdout[-1800:]
