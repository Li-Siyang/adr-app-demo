import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest


STATIC = Path(__file__).resolve().parents[1] / "app" / "static"
CHROME = next(
    (
        browser
        for browser in (
            shutil.which("chrome"),
            shutil.which("chromium"),
            shutil.which("google-chrome"),
            shutil.which("msedge"),
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        )
        if browser and Path(browser).is_file()
    ),
    None,
)


@pytest.mark.skipif(CHROME is None, reason="Chrome is required for the UI regression")
def test_archive_warning_and_in_flight_card_lock():
    fixture = """
<script>
const record = {
  id: "one", title: "First", status: "Draft", archived: false,
  abandoned: false, tags: [], author: {id: "admin", display_name: "Admin"},
  owner: {id: "admin", display_name: "Admin"},
  decision_date: "2026-01-01", replacement_record_ids: [],
};
const other = {
  ...record, id: "two", title: "Second",
};
let resolveArchive;
let archiveRequests = 0;
let pauseLists = 0;
const pendingLists = [];
window.fetch = async (url, options = {}) => {
  if (url === "/api/mock-session") return reply({selected_identity: {
    id: "admin", label: "Admin", roles: ["administrator"],
  }});
  if (url === "/api/governance/permissions")
    return reply({identity: {roles: ["administrator"]}, designated_approver: false});
  if (url === "/api/tags") return reply({tags: []});
  if (url === "/api/mock-identities") return reply([{id: "admin", label: "Admin"}]);
  if (url === "/api/attribution-preview") return reply({message: "Admin"});
  if (url === "/api/decision-records") {
    if (pauseLists) {
      pauseLists--;
      return new Promise((resolve) => { pendingLists.push(resolve); });
    }
    return reply({records: [record, other]});
  }
  if (url === "/api/decision-records/one/archive") {
    archiveRequests++;
    return new Promise((resolve) => { resolveArchive = resolve; });
  }
  throw new Error(`Unexpected request: ${url} ${options.method}`);
};
function reply(body, ok = true) {
  return {ok, json: async () => body};
}
function button(id, name) {
  return [...document.querySelectorAll(`#record-card-${id} button`)]
    .find((item) => item.textContent === name);
}
async function ready() {
  for (let i = 0; i < 100 && !button("one", "Archive record"); i++)
    await new Promise((resolve) => setTimeout(resolve, 10));
  if (!button("one", "Archive record")) throw new Error("Records did not load");
}
async function check() {
  await ready();
  button("one", "Edit Draft").click();
  document.querySelector('#record-form [name="title"]').value = "Unsaved";
  button("one", "Archive record").click();
  const message = document.querySelector("#record-form-message");
  if (!message.textContent.includes("Save or cancel") ||
      !message.classList.contains("error") ||
      archiveRequests !== 0 ||
      document.querySelector('#record-form [name="title"]').value !== "Unsaved")
    throw new Error("Edit warning did not preserve the form and prevent archive");
  document.querySelector("#cancel-edit").click();
  if (message.textContent) throw new Error("Cancel did not clear warning");

  button("one", "Archive record").click();
  if (archiveRequests !== 1 ||
      [...document.querySelectorAll("#record-card-one button, #record-card-one select")]
        .some((control) => !control.disabled) ||
      button("two", "Edit Draft").disabled)
    throw new Error("In-flight lock affected wrong controls");
  document.querySelector("#tag-filter").dispatchEvent(new Event("change"));
  await new Promise((resolve) => setTimeout(resolve, 20));
  if (!button("one", "Edit Draft").disabled || button("two", "Edit Draft").disabled)
    throw new Error("Refresh lost the per-record lock");
  resolveArchive(reply({detail: "Not allowed"}, false));
  await new Promise((resolve) => setTimeout(resolve, 20));
  if (button("one", "Edit Draft").disabled || button("one", "Archive record").disabled)
    throw new Error("Failed archive did not release controls");

  button("one", "Archive record").click();
  record.archived = true;
  pauseLists = 2;
  resolveArchive(reply({}));
  await new Promise((resolve) => setTimeout(resolve, 20));
  document.querySelector("#tag-filter").dispatchEvent(new Event("change"));
  await new Promise((resolve) => setTimeout(resolve, 20));
  pendingLists.shift()(reply({records: [record, other]}));
  await new Promise((resolve) => setTimeout(resolve, 20));
  if (!button("one", "Edit Draft").disabled ||
      !button("one", "Archive record").disabled)
    throw new Error("Superseded archive refresh unlocked stale card");
  pendingLists.shift()(reply({records: [record, other]}));
  await new Promise((resolve) => setTimeout(resolve, 20));
  if (button("one", "Edit Draft") || !button("one", "Restore record") ||
      button("one", "Restore record").disabled)
    throw new Error("Successful archive did not refresh available actions");
  document.body.dataset.result = "passed";
}
setTimeout(() => check().catch((error) => {
  document.body.dataset.result = `failed: ${error.message}`;
}), 0);
</script>
"""
    html = (STATIC / "app.html").read_text(encoding="utf-8")
    html = html.replace('<script src="/static/app.js" defer></script>', fixture)
    html = html.replace("</body>", f"<script>{(STATIC / 'app.js').read_text(encoding='utf-8')}</script></body>")
    with tempfile.TemporaryDirectory() as directory:
        page = Path(directory) / "index.html"
        page.write_text(html, encoding="utf-8")
        result = subprocess.run(
            [
                CHROME, "--headless", "--disable-gpu", "--no-first-run",
                "--no-default-browser-check", "--virtual-time-budget=3000",
                "--dump-dom", page.as_uri(),
            ],
            capture_output=True, text=True, timeout=30, check=True,
            env={**os.environ, "CHROME_LOG_FILE": str(Path(directory) / "chrome.log")},
        )
    assert 'data-result="passed"' in result.stdout, result.stdout[-1500:]
