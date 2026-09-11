const identityContext = document.querySelector("#identity-context");
const attributionPreview = document.querySelector("#attribution-preview");
const changeIdentity = document.querySelector("#change-identity");
const recordForm = document.querySelector("#record-form");
const recordOwner = document.querySelector("#record-owner");
const recordFormMessage = document.querySelector("#record-form-message");
const recordList = document.querySelector("#record-list");
const cancelEdit = document.querySelector("#cancel-edit");
const saveDraft = recordForm.querySelector('button[type="submit"]');
let selectedIdentityId = null;
let editingRecordId = null;
let records = [];

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

function apiErrorMessage(error, fallback) {
  if (Array.isArray(error.detail)) {
    return displayValidationErrors(error.detail);
  }
  if (typeof error.detail === "string") {
    return error.detail;
  }
  if (error.detail && typeof error.detail === "object") {
    const messages = [error.detail.message];
    if (error.detail.missing_fields?.length) {
      messages.push(
        `Missing required fields: ${error.detail.missing_fields
          .map((field) => displayFieldName([field]))
          .join(", ")}.`,
      );
    }
    if (error.detail.approver) {
      messages.push(error.detail.approver);
    }
    return messages.filter(Boolean).join(" ");
  }
  return fallback;
}

function disableDraftAuthoring(message) {
  recordOwner.replaceChildren();
  recordOwner.disabled = true;
  saveDraft.disabled = true;
  recordFormMessage.textContent = message;
}

async function loadContext() {
  const sessionResponse = await fetch("/api/mock-session");
  const session = await sessionResponse.json();
  if (!session.selected_identity) {
    window.location.replace("/");
    return;
  }

  const identity = session.selected_identity;
  selectedIdentityId = identity.id;
  identityContext.replaceChildren();

  const title = document.createElement("h2");
  title.textContent = identity.label;
  const roles = document.createElement("p");
  roles.textContent = `Configured roles: ${identity.roles.map(roleName).join(", ")}`;
  identityContext.append(title, roles);

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
  await loadRecords();
}

changeIdentity.addEventListener("click", async () => {
  await fetch("/api/mock-session", { method: "DELETE" });
  window.location.assign("/");
});

loadContext();

function resetForm() {
  editingRecordId = null;
  recordForm.reset();
  recordOwner.disabled = false;
  cancelEdit.hidden = true;
  saveDraft.textContent = "Save Draft";
}

function beginEdit(record) {
  editingRecordId = record.id;
  for (const field of [
    "title",
    "context",
    "decision",
    "rationale",
    "alternatives_considered",
    "consequences",
    "decision_date",
  ]) {
    recordForm.elements[field].value = record[field];
  }
  recordForm.elements.owner_id.value = record.owner.id;
  recordOwner.disabled = true;
  recordForm.elements.tags.value = record.tags.join(", ");
  cancelEdit.hidden = false;
  saveDraft.textContent = "Save changes";
  recordFormMessage.textContent = "";
  recordForm.scrollIntoView({ behavior: "smooth" });
}

async function submitDraft(record) {
  const response = await fetch(`/api/decision-records/${record.id}/submit`, {
    method: "POST",
  });
  if (!response.ok) {
    const error = await response.json();
    recordFormMessage.className = "error";
    recordFormMessage.textContent = apiErrorMessage(
      error,
      "Draft could not be submitted.",
    );
    return;
  }

  recordFormMessage.className = "";
  recordFormMessage.textContent = "Draft submitted for review.";
  resetForm();
  await loadRecords();
}

function renderRecords() {
  if (!records.length) {
    recordList.replaceChildren(
      Object.assign(document.createElement("p"), {
        textContent: "No decision records have been created.",
      }),
    );
    return;
  }

  recordList.replaceChildren(
    ...records.map((record) => {
      const card = document.createElement("article");
      card.className = "record-card";
      const title = document.createElement("h3");
      title.textContent = record.title || "Untitled Draft";
      const summary = document.createElement("p");
      summary.textContent = `${record.status} · Author: ${record.author.display_name} · Owner: ${record.owner.display_name}`;
      card.append(title, summary);

      const editable =
        record.author.id === selectedIdentityId &&
        record.status === "Draft" &&
        !record.abandoned;
      if (editable) {
        const actions = document.createElement("div");
        actions.className = "record-actions";
        const edit = document.createElement("button");
        edit.type = "button";
        edit.className = "secondary";
        edit.textContent = "Edit Draft";
        edit.addEventListener("click", () => beginEdit(record));
        const submit = document.createElement("button");
        submit.type = "button";
        submit.textContent = "Submit Draft";
        submit.addEventListener("click", () => submitDraft(record));
        actions.append(edit, submit);
        card.append(actions);
      }
      return card;
    }),
  );
}

async function loadRecords() {
  const response = await fetch("/api/decision-records");
  if (!response.ok) {
    recordList.textContent = "Decision records could not be loaded.";
    return;
  }
  records = (await response.json()).records;
  renderRecords();
}

cancelEdit.addEventListener("click", () => {
  resetForm();
  recordFormMessage.textContent = "";
});

recordForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  saveDraft.disabled = true;
  recordFormMessage.textContent = "";
  const formData = new FormData(recordForm);
  const payload = Object.fromEntries(formData.entries());
  payload.tags = payload.tags.split(",").map((tag) => tag.trim());

  try {
    const response = await fetch(
      editingRecordId
        ? `/api/decision-records/${editingRecordId}`
        : "/api/decision-records",
      {
        method: editingRecordId ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
    );
    if (!response.ok) {
      let message = "Draft could not be saved. Please try again.";
      try {
        const error = await response.json();
        message = apiErrorMessage(error, message);
      } catch {
        // Keep the generic message when the server response is not JSON.
      }
      recordFormMessage.className = "error";
      recordFormMessage.textContent = message;
      return;
    }

    resetForm();
    recordFormMessage.className = "";
    recordFormMessage.textContent = "Draft saved.";
    await loadRecords();
  } finally {
    saveDraft.disabled = false;
  }
});
