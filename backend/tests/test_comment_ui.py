"""Implementation-level browser regression for comment controls in app.js."""

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
def test_comment_add_render_and_delete_controls() -> None:
    fixture = """
<script>
const identities = {
  author: {
    id: "author", label: "Author (Mock User)", display_name: "Author",
    roles: ["team-member"],
  },
  other: {
    id: "other", label: "Other (Mock User)", display_name: "Other",
    roles: ["team-member"],
  },
};
let selected = identities.author;
const record = {
  id: "one", title: "First", status: "Draft", archived: false,
  abandoned: false, tags: [], author: identities.author,
  owner: identities.author, decision_date: "2026-10-01",
  replacement_record_ids: [], comments: [],
};
let additions = 0;
let deletions = 0;
function reply(body = {}, ok = true) {
  return {ok, json: async () => body};
}
window.fetch = async (url, options = {}) => {
  if (url === "/api/mock-session")
    return reply({selected_identity: selected});
  if (url === "/api/governance/permissions")
    return reply({identity: selected, designated_approver: false});
  if (url === "/api/tags") return reply({tags: []});
  if (url === "/api/mock-identities")
    return reply(Object.values(identities));
  if (url === "/api/attribution-preview")
    return reply({message: selected.display_name});
  if (url === "/api/decision-records")
    return reply({records: [record]});
  if (url === "/api/decision-records/one/comments" &&
      options.method === "POST") {
    const payload = JSON.parse(options.body);
    if (selected.id !== "author" || payload.content !== "A reason to discuss")
      throw new Error("Comment submission lost its actor or content");
    additions++;
    record.comments.push({
      id: "comment-one", content: payload.content, author: identities.author,
      created_at: "2026-10-01T00:00:00Z", deleted: false,
    });
    return reply(record.comments[0]);
  }
  if (url === "/api/decision-records/one/comments/comment-one" &&
      options.method === "DELETE") {
    if (selected.id !== "author") throw new Error("Non-author deleted a comment");
    deletions++;
    record.comments[0] = {
      ...record.comments[0], content: "[deleted]", deleted: true,
    };
    return reply(record.comments[0]);
  }
  throw new Error(`Unexpected request: ${url} ${options.method}`);
};
function assert(condition, message) {
  if (!condition) throw new Error(message);
}
function comments() {
  return document.querySelector("#record-card-one .record-comments");
}
function deleteButton() {
  return [...comments().querySelectorAll("button")]
    .find(button => button.textContent === "Delete comment");
}
async function tick() {
  await new Promise(resolve => setTimeout(resolve, 20));
}
async function run() {
  for (let n = 0; !comments() && n < 100; n++) await tick();
  assert(comments(), "Record comments did not load");
  const form = comments().querySelector("form");
  assert(form, "Author cannot submit a top-level comment");
  form.elements.content.value = "A reason to discuss";
  form.dispatchEvent(new Event("submit", {bubbles: true, cancelable: true}));
  await tick();
  assert(additions === 1, "Comment submission did not reach the API once");
  assert(comments().querySelector("li p").textContent === "A reason to discuss",
    "Comment content did not render");
  assert(comments().querySelector(".comment-attribution").textContent.includes("Author"),
    "Comment author attribution is missing");
  assert(deleteButton(), "Author cannot delete their comment");

  selected = identities.other;
  await loadContext();
  assert(comments().querySelector("li p").textContent === "A reason to discuss",
    "Non-author cannot view the comment");
  assert(!deleteButton(), "Non-author can access author-only deletion control");
  assert(comments().querySelector("form"), "Other team member cannot comment");

  selected = identities.author;
  await loadContext();
  deleteButton().click();
  await tick();
  assert(deletions === 1, "Author deletion did not reach the API once");
  assert(comments().querySelector("li p").textContent === "[deleted]",
    "Deleted content did not render as a tombstone");
  assert(comments().querySelector(".comment-attribution").textContent.includes("Author"),
    "Soft deletion erased original attribution");
  assert(!deleteButton(), "Deleted comment can be deleted again");

  selected = identities.other;
  await loadContext();
  assert(comments().querySelector("li p").textContent === "[deleted]" &&
    !deleteButton(), "Non-author view lost the tombstone or exposed deletion");
  document.body.dataset.commentUi = "passed";
}
setTimeout(() => run().catch(error => {
  document.body.dataset.commentUi = `failed: ${error.message}`;
}), 0);
</script>
"""
    html = (STATIC / "app.html").read_text(encoding="utf-8").replace(
        '<script src="/static/app.js" defer></script>', fixture
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
                "--no-default-browser-check", "--virtual-time-budget=4000",
                "--dump-dom", page.as_uri(),
            ],
            capture_output=True, text=True, timeout=35, check=True,
            env={**os.environ, "CHROME_LOG_FILE": str(Path(directory) / "chrome.log")},
        )
    assert 'data-comment-ui="passed"' in result.stdout, result.stdout[-1800:]
