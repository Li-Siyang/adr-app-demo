const identityContext = document.querySelector("#identity-context");
const attributionPreview = document.querySelector("#attribution-preview");
const changeIdentity = document.querySelector("#change-identity");
const recordForm = document.querySelector("#record-form");
const recordOwner = document.querySelector("#record-owner");
const recordFormMessage = document.querySelector("#record-form-message");
const saveDraft = recordForm.querySelector('button[type="submit"]');
const tagFilter = document.querySelector("#tag-filter");
const recordList = document.querySelector("#record-list");
const recordListMessage = document.querySelector("#record-list-message");

let availableTags = [];
let latestRecordRequest = 0;

function roleName(role) {
  return role
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function displayFieldName(location) {
  const fieldName = location[location.length - 1];
  if (typeof fieldName !== "string") {
    return "Draft";
  }

  return fieldName
    .replaceAll("_", " ")
    .replace(/\b\w/g, (character) => character.toUpperCase());
}

function displayValidationErrors(details) {
  return details
    .map((item) => `${displayFieldName(item.loc)}: ${item.msg}`)
    .join(" ");
}

function disableDraftAuthoring(message) {
  recordOwner.replaceChildren();
  recordOwner.disabled = true;
  saveDraft.disabled = true;
  recordFormMessage.textContent = message;
}

function renderRecords(records) {
  recordList.replaceChildren(
    ...records.map((record) => {
      const article = document.createElement("article");
      article.className = "record-card";

      const title = document.createElement("h3");
      title.textContent = record.title;
      const details = document.createElement("p");
      details.textContent =
        `${record.status} | Owner: ${record.owner.display_name} | ` +
        `Decision date: ${record.decision_date}`;
      const tags = document.createElement("p");
      tags.textContent = `Tags: ${record.tags.join(", ")}`;
      article.append(title, details, tags);
      return article;
    }),
  );
  recordListMessage.textContent =
    records.length === 0 ? "No decision records found." : "";
}

function updateTagOptions(tags) {
  const discoveredTags = [...new Set(tags)].sort();
  availableTags = [...new Set([...availableTags, ...discoveredTags])].sort();
  const selectedTag = tagFilter.value;
  const allTagsOption = document.createElement("option");
  allTagsOption.value = "";
  allTagsOption.textContent = "All tags";
  tagFilter.replaceChildren(
    allTagsOption,
    ...availableTags.map((tag) => {
      const option = document.createElement("option");
      option.value = tag;
      option.textContent = tag;
      return option;
    }),
  );
  tagFilter.value = selectedTag;
}

async function loadRecords(tag = "") {
  const requestId = ++latestRecordRequest;
  recordListMessage.textContent = "Loading decision records...";
  const query = tag ? `?tag=${encodeURIComponent(tag)}` : "";
  try {
    const response = await fetch(`/api/decision-records${query}`);
    if (requestId !== latestRecordRequest) {
      return;
    }
    if (!response.ok) {
      recordList.replaceChildren();
      recordListMessage.textContent = "Decision records could not be loaded.";
      return;
    }

    const collection = await response.json();
    if (requestId !== latestRecordRequest) {
      return;
    }
    updateTagOptions(collection.records.flatMap((record) => record.tags));
    renderRecords(collection.records);
  } catch {
    if (requestId === latestRecordRequest) {
      recordList.replaceChildren();
      recordListMessage.textContent = "Decision records could not be loaded.";
    }
  }
}

async function loadContext() {
  const sessionResponse = await fetch("/api/mock-session");
  const session = await sessionResponse.json();
  if (!session.selected_identity) {
    window.location.replace("/");
    return;
  }

  const identity = session.selected_identity;
  identityContext.replaceChildren();

  const title = document.createElement("h2");
  title.textContent = identity.label;
  const roles = document.createElement("p");
  roles.textContent = `Configured roles: ${identity.roles.map(roleName).join(", ")}`;
  identityContext.append(title, roles);

  await loadRecords();

  const attributionResponse = await fetch("/api/attribution-preview");
  if (attributionResponse.ok) {
    const attribution = await attributionResponse.json();
    attributionPreview.textContent = attribution.message;
  } else {
    attributionPreview.textContent = "Attribution context could not be loaded.";
  }

  const identitiesResponse = await fetch("/api/mock-identities");
  if (!identitiesResponse.ok) {
    disableDraftAuthoring(
      "Owner options could not be loaded. Draft creation is unavailable.",
    );
    return;
  }

  const identities = await identitiesResponse.json();
  recordOwner.replaceChildren(
    ...identities.map((owner) => {
      const option = document.createElement("option");
      option.value = owner.id;
      option.textContent = owner.label;
      return option;
    }),
  );
  recordOwner.disabled = false;
  saveDraft.disabled = false;
}

changeIdentity.addEventListener("click", async () => {
  await fetch("/api/mock-session", { method: "DELETE" });
  window.location.assign("/");
});

loadContext();

tagFilter.addEventListener("change", () => {
  loadRecords(tagFilter.value);
});

recordForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  saveDraft.disabled = true;
  recordFormMessage.textContent = "";
  const formData = new FormData(recordForm);
  const payload = Object.fromEntries(formData.entries());
  payload.tags = payload.tags.split(",").map((tag) => tag.trim());

  try {
    const response = await fetch("/api/decision-records", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      let message = "Draft could not be saved. Please try again.";
      try {
        const error = await response.json();
        message = Array.isArray(error.detail)
          ? displayValidationErrors(error.detail)
          : error.detail || message;
      } catch {
        // Keep the generic message when the server response is not JSON.
      }
      recordFormMessage.textContent = message;
      return;
    }

    updateTagOptions(payload.tags);
    recordForm.reset();
    recordFormMessage.className = "";
    recordFormMessage.textContent = "Draft saved.";
    await loadRecords(tagFilter.value);
  } finally {
    saveDraft.disabled = false;
  }
});
