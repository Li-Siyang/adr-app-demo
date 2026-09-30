const identityContext = document.querySelector("#identity-context");
const attributionPreview = document.querySelector("#attribution-preview");
const changeIdentity = document.querySelector("#change-identity");
const tagForm = document.querySelector("#tag-form");
const tagName = document.querySelector("#tag-name");
const tagFormMessage = document.querySelector("#tag-form-message");
const createTagButton = tagForm.querySelector('button[type="submit"]');
const recordForm = document.querySelector("#record-form");
const recordOwner = document.querySelector("#record-owner");
const recordTags = document.querySelector("#record-tags");
const recordFormMessage = document.querySelector("#record-form-message");
const saveDraft = recordForm.querySelector('button[type="submit"]');
const requiredFields = [...recordForm.querySelectorAll("[required]")];
const tagFilter = document.querySelector("#tag-filter");
const recordList = document.querySelector("#record-list");
const recordListMessage = document.querySelector("#record-list-message");
const decisionMessage = document.querySelector("#decision-message");
const transferMessage = document.querySelector("#transfer-message");
const replacementMessage = document.querySelector("#replacement-message");
const archiveMessage = document.querySelector("#archive-message");
const cancelEdit = document.querySelector("#cancel-edit");

let availableTags = [];
let availableOwners = [];
let latestRecordRequest = 0;
let selectedIdentityId = null;
let selectedCanDecideProposals = false;
let selectedIsAdministrator = false;
let selectedPermissionsLoaded = false;
let editingRecordId = null;
let editingOwnerId = null;
let editingStatus = null;
const pendingArchivalIds = new Set();
const archivalDisabledControls = new Map();

function lockRecordControls(recordId) {
  const card = document.getElementById(`record-card-${recordId}`);
  const controls = card
    ? [...card.querySelectorAll("button, select")].filter((control) => !control.disabled)
    : [];
  for (const control of controls) {
    control.disabled = true;
  }
  archivalDisabledControls.set(recordId, controls);
}

function unlockRecordControls(recordId) {
  for (const control of archivalDisabledControls.get(recordId) || []) {
    control.disabled = false;
  }
  archivalDisabledControls.delete(recordId);
}

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

async function loadTags() {
  const response = await fetch("/api/tags");
  if (!response.ok) {
    throw new Error("Available tags could not be loaded.");
  }
  const collection = await response.json();
  updateTagOptions(collection.tags);
}

async function createTag(event) {
  event.preventDefault();
  createTagButton.disabled = true;
  tagFormMessage.className = "";
  tagFormMessage.textContent = "";

  try {
    const response = await fetch("/api/tags", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: tagName.value }),
    });
    if (!response.ok) {
      let message = "Tag could not be created.";
      try {
        message = apiErrorMessage(await response.json(), message);
      } catch {
        // Keep the generic message when the server response is not JSON.
      }
      tagFormMessage.className = "error";
      tagFormMessage.textContent = message;
      return;
    }

    const createdTag = await response.json();
    updateTagOptions([createdTag.name]);
    tagForm.reset();
    tagFormMessage.textContent =
      `Tag "${createdTag.name}" is available for record association.`;
  } catch {
    tagFormMessage.className = "error";
    tagFormMessage.textContent =
      "Tag could not be created. Please try again.";
  } finally {
    createTagButton.disabled = false;
  }
}

function disableDraftAuthoring(message) {
  recordOwner.replaceChildren();
  recordOwner.disabled = true;
  saveDraft.disabled = true;
  recordFormMessage.textContent = message;
}

function setEditingMode(isEditing) {
  for (const field of requiredFields) {
    field.required = !isEditing;
  }
  recordOwner.disabled = isEditing;
}

function resetForm() {
  editingRecordId = null;
  editingOwnerId = null;
  editingStatus = null;
  recordForm.reset();
  setEditingMode(false);
  cancelEdit.hidden = true;
  saveDraft.textContent = "Save Draft";
}

function beginEdit(record) {
  editingRecordId = record.id;
  editingOwnerId = record.owner.id;
  editingStatus = record.status;
  setEditingMode(true);
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
  recordOwner.value = editingOwnerId;
  for (const option of recordTags.options) {
    option.selected = record.tags.includes(option.value);
  }
  cancelEdit.hidden = false;
  saveDraft.textContent = "Save changes";
  recordFormMessage.textContent = "";
  recordForm.scrollIntoView({ behavior: "smooth" });
}

async function submitDraft(record, submitButton) {
  submitButton.disabled = true;
  let response;
  try {
    response = await fetch(`/api/decision-records/${record.id}/submit`, {
      method: "POST",
    });
  } catch {
    submitButton.disabled = false;
    recordFormMessage.className = "error";
    recordFormMessage.textContent =
      "Draft could not be submitted. Please try again.";
    return;
  }

  if (!response.ok) {
    let message = "Draft could not be submitted.";
    try {
      message = apiErrorMessage(await response.json(), message);
    } catch {
      // Keep the generic message when the server response is not JSON.
    }
    submitButton.disabled = false;
    recordFormMessage.className = "error";
    recordFormMessage.textContent = message;
    return;
  }

  recordFormMessage.className = "";
  recordFormMessage.textContent = "Draft submitted for review.";
  resetForm();
  // loadRecords reports refresh failures in the list message, so a failed
  // refresh cannot overwrite the completed-submission confirmation above.
  await loadRecords(tagFilter.value);
}

async function decideProposal(record, outcome, decisionButton) {
  decisionButton.disabled = true;
  decisionMessage.className = "";
  decisionMessage.textContent = "";
  try {
    const response = await fetch(
      `/api/decision-records/${record.id}/decision`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ outcome }),
      },
    );
    if (!response.ok) {
      let message = `Proposal could not be ${outcome.toLowerCase()}.`;
      try {
        message = apiErrorMessage(await response.json(), message);
      } catch {
        // Keep the generic message when the server response is not JSON.
      }
      decisionMessage.className = "error";
      decisionMessage.textContent = message;
      decisionButton.disabled = false;
      return;
    }

    decisionMessage.textContent = `Proposal ${outcome.toLowerCase()}.`;
    await loadRecords(tagFilter.value);
  } catch {
    decisionMessage.className = "error";
    decisionMessage.textContent =
      `Proposal could not be ${outcome.toLowerCase()}. Please try again.`;
    decisionButton.disabled = false;
  }
}

async function transferOwner(record, ownerSelect, transferButton) {
  transferButton.disabled = true;
  transferMessage.className = "";
  transferMessage.textContent = "";
  try {
    const response = await fetch(
      `/api/decision-records/${record.id}/owner`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ owner_id: ownerSelect.value }),
      },
    );
    if (!response.ok) {
      let message = "Ownership could not be transferred.";
      try {
        message = apiErrorMessage(await response.json(), message);
      } catch {
        // Keep the generic message when the server response is not JSON.
      }
      transferMessage.className = "error";
      transferMessage.textContent = message;
      transferButton.disabled = false;
      return;
    }
    transferMessage.textContent = "Record ownership transferred.";
    await loadRecords(tagFilter.value);
  } catch {
    transferMessage.className = "error";
    transferMessage.textContent =
      "Ownership could not be transferred. Please try again.";
    transferButton.disabled = false;
  }
}

async function createReplacement(record, replacementButton) {
  replacementButton.disabled = true;
  replacementMessage.className = "";
  replacementMessage.textContent = "";
  try {
    const response = await fetch(
      `/api/decision-records/${record.id}/replacements`,
      { method: "POST" },
    );
    if (!response.ok) {
      let message = "Replacement version could not be created.";
      try {
        message = apiErrorMessage(await response.json(), message);
      } catch {
        // Keep the generic message when the server response is not JSON.
      }
      replacementMessage.className = "error";
      replacementMessage.textContent = message;
      replacementButton.disabled = false;
      return;
    }
    replacementMessage.textContent = "Replacement Draft created.";
    await loadRecords(tagFilter.value);
  } catch {
    replacementMessage.className = "error";
    replacementMessage.textContent =
      "Replacement version could not be created. Please try again.";
    replacementButton.disabled = false;
  }
}

async function abandonReplacement(record, abandonButton) {
  abandonButton.disabled = true;
  replacementMessage.className = "";
  replacementMessage.textContent = "";
  try {
    const response = await fetch(
      `/api/decision-records/${record.id}/abandon`,
      { method: "POST" },
    );
    if (!response.ok) {
      let message = "Replacement Draft could not be abandoned.";
      try {
        message = apiErrorMessage(await response.json(), message);
      } catch {
        // Keep the generic message when the server response is not JSON.
      }
      replacementMessage.className = "error";
      replacementMessage.textContent = message;
      abandonButton.disabled = false;
      return;
    }
    replacementMessage.textContent =
      "Replacement Draft retained and marked Abandoned.";
    await loadRecords(tagFilter.value);
  } catch {
    replacementMessage.className = "error";
    replacementMessage.textContent =
      "Replacement Draft could not be abandoned. Please try again.";
    abandonButton.disabled = false;
  }
}

async function changeArchival(record) {
  const action = record.archived ? "restore" : "archive";
  if (action === "archive" && editingRecordId === record.id) {
    recordFormMessage.className = "error";
    recordFormMessage.textContent =
      "Save or cancel your edits before archiving this record.";
    recordFormMessage.scrollIntoView({ behavior: "smooth" });
    return;
  }
  if (pendingArchivalIds.has(record.id)) {
    return;
  }
  pendingArchivalIds.add(record.id);
  lockRecordControls(record.id);
  archiveMessage.className = "";
  archiveMessage.textContent = "";
  try {
    const response = await fetch(
      `/api/decision-records/${record.id}/${action}`,
      { method: "POST" },
    );
    if (!response.ok) {
      let message = `Record could not be ${action}d.`;
      try {
        message = apiErrorMessage(await response.json(), message);
      } catch {
        // Keep the generic message when the server response is not JSON.
      }
      archiveMessage.className = "error";
      archiveMessage.textContent = message;
      return;
    }
    archiveMessage.textContent = record.archived
      ? "Record restored."
      : "Record archived and retained.";
    await loadRecords(tagFilter.value);
  } catch {
    archiveMessage.className = "error";
    archiveMessage.textContent =
      `Record could not be ${action}d. Please try again.`;
  } finally {
    pendingArchivalIds.delete(record.id);
    unlockRecordControls(record.id);
  }
}

async function navigateToRecord(recordId, event) {
  event.preventDefault();
  const cardId = `record-card-${recordId}`;
  if (!document.getElementById(cardId)) {
    tagFilter.value = "";
    await loadRecords();
  }

  const card = document.getElementById(cardId);
  if (card) {
    window.location.hash = cardId;
    card.scrollIntoView({ behavior: "smooth" });
  }
}

function renderRecords(records, allRecords = records) {
  recordList.replaceChildren(
    ...records.map((record) => {
      const article = document.createElement("article");
      article.className = "record-card";
      article.id = `record-card-${record.id}`;

      const title = document.createElement("h3");
      title.textContent = record.title || "Untitled Draft";
      const details = document.createElement("p");
      details.textContent =
        `${record.status}${record.abandoned ? " (Abandoned)" : ""} | ` +
        `${record.archived ? "Archived | " : ""}` +
        `Author: ${record.author.display_name} | ` +
        `Owner: ${record.owner.display_name} | ` +
        `Decision date: ${record.decision_date}`;
      const tags = document.createElement("p");
      tags.textContent = `Tags: ${record.tags.join(", ")}`;
      article.append(title, details, tags);

      const original = allRecords.find(
        (candidate) => candidate.id === record.replaces_record_id,
      );
      const linkedReplacements = (record.replacement_record_ids || [])
        .map((replacementId) =>
          allRecords.find((candidate) => candidate.id === replacementId),
        )
        .filter(Boolean);
      if (original || linkedReplacements.length) {
        const links = document.createElement("p");
        links.className = "version-links";
        if (original) {
          const link = document.createElement("a");
          link.href = `#record-card-${original.id}`;
          link.textContent = `Version of: ${original.title}`;
          link.addEventListener("click", (event) =>
            navigateToRecord(original.id, event),
          );
          links.append(link);
        }
        for (const replacement of linkedReplacements) {
          if (links.childNodes.length) {
            links.append(document.createTextNode(" | "));
          }
          const link = document.createElement("a");
          link.href = `#record-card-${replacement.id}`;
          link.textContent =
            `Replacement: ${replacement.title} (${replacement.status}` +
            `${replacement.abandoned ? ", Abandoned" : ""})`;
          link.addEventListener("click", (event) =>
            navigateToRecord(replacement.id, event),
          );
          links.append(link);
        }
        article.append(links);
      }

      const activeReplacement = allRecords.some(
        (candidate) =>
          candidate.replaces_record_id === record.id &&
          ["Draft", "Proposed"].includes(candidate.status) &&
          !candidate.abandoned,
      );
      if (selectedPermissionsLoaded && selectedIsAdministrator) {
        const blockedByProposedReplacement =
          record.status === "Accepted" &&
          allRecords.some(
            (candidate) =>
              candidate.replaces_record_id === record.id &&
              candidate.status === "Proposed" &&
              !candidate.abandoned,
          );
        if (record.archived || !blockedByProposedReplacement) {
          const archival = document.createElement("button");
          archival.type = "button";
          archival.textContent = record.archived ? "Restore record" : "Archive record";
          archival.setAttribute(
            "aria-label",
            `${archival.textContent}: ${record.title || "Untitled Draft"} (${record.id})`,
          );
          archival.addEventListener("click", () => changeArchival(record));
          article.append(archival);
        }
      }
      if (
        selectedPermissionsLoaded &&
        selectedIsAdministrator &&
        !record.archived &&
        record.status === "Accepted" &&
        !activeReplacement
      ) {
        const create = document.createElement("button");
        create.type = "button";
        create.textContent = "Create replacement Draft";
        create.addEventListener("click", () => createReplacement(record, create));
        article.append(create);
      }
      if (
        selectedPermissionsLoaded &&
        selectedIsAdministrator &&
        !record.archived &&
        record.replaces_record_id &&
        record.status === "Draft" &&
        !record.abandoned
      ) {
        const abandon = document.createElement("button");
        abandon.type = "button";
        abandon.textContent = "Abandon replacement Draft";
        abandon.addEventListener("click", () => abandonReplacement(record, abandon));
        article.append(abandon);
      }

      const transferable =
        selectedPermissionsLoaded &&
        (record.author.id === selectedIdentityId ||
          record.owner.id === selectedIdentityId ||
          selectedIsAdministrator) &&
        ["Draft", "Proposed"].includes(record.status) &&
        !record.archived &&
        !record.abandoned;
      if (transferable && availableOwners.length) {
        const actions = document.createElement("div");
        actions.className = "record-actions";
        const label = document.createElement("label");
        label.textContent = "New owner ";
        const ownerSelect = document.createElement("select");
        ownerSelect.setAttribute("aria-label", `New owner for ${record.title}`);
        ownerSelect.replaceChildren(
          ...availableOwners
            .filter((owner) => owner.id !== record.owner.id)
            .map((owner) => {
              const option = document.createElement("option");
              option.value = owner.id;
              option.textContent = owner.label;
              return option;
            }),
        );
        const transfer = document.createElement("button");
        transfer.type = "button";
        transfer.textContent = "Transfer ownership";
        transfer.addEventListener("click", () =>
          transferOwner(record, ownerSelect, transfer),
        );
        label.append(ownerSelect);
        actions.append(label, transfer);
        article.append(actions);
      }

      const editable =
        record.author.id === selectedIdentityId &&
        ["Draft", "Proposed"].includes(record.status) &&
        !record.archived &&
        !record.abandoned;
      if (editable) {
        const actions = document.createElement("div");
        actions.className = "record-actions";
        const edit = document.createElement("button");
        edit.type = "button";
        edit.className = "secondary";
        edit.textContent =
          record.status === "Proposed" ? "Edit proposal" : "Edit Draft";
        edit.addEventListener("click", () => beginEdit(record));
        actions.append(edit);
        if (record.status === "Draft" && !original?.archived) {
          const submit = document.createElement("button");
          submit.type = "button";
          submit.textContent = "Submit Draft";
          submit.addEventListener("click", () => submitDraft(record, submit));
          actions.append(submit);
        }
        article.append(actions);
      }
      if (record.status === "Proposed" && !record.archived && selectedCanDecideProposals) {
        const actions = document.createElement("div");
        actions.className = "record-actions";
        for (const outcome of ["Accepted", "Rejected"]) {
          const decide = document.createElement("button");
          decide.type = "button";
          decide.textContent = outcome === "Accepted"
            ? "Accept proposal"
            : "Reject proposal";
          decide.addEventListener("click", () =>
            decideProposal(record, outcome, decide),
          );
          actions.append(decide);
        }
        article.append(actions);
      }
      if (pendingArchivalIds.has(record.id)) {
        const controls = [...article.querySelectorAll("button, select")];
        for (const control of controls) {
          control.disabled = true;
        }
        archivalDisabledControls.set(record.id, controls);
      }
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
  const selectedRecordTags = new Set(
    [...recordTags.selectedOptions].map((option) => option.value),
  );
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
  recordTags.replaceChildren(
    ...availableTags.map((tag) => {
      const option = document.createElement("option");
      option.value = tag;
      option.textContent = tag;
      option.selected = selectedRecordTags.has(tag);
      return option;
    }),
  );
}

async function loadRecords(tag = "") {
  const requestId = ++latestRecordRequest;
  recordListMessage.textContent = "Loading decision records...";
  try {
    const response = await fetch("/api/decision-records");
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
    const records = tag
      ? collection.records.filter((record) => record.tags.includes(tag))
      : collection.records;
    renderRecords(records, collection.records);
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
  selectedIdentityId = identity.id;
  identityContext.replaceChildren();

  const title = document.createElement("h2");
  title.textContent = identity.label;
  const roles = document.createElement("p");
  roles.textContent = `Configured roles: ${identity.roles.map(roleName).join(", ")}`;
  identityContext.append(title, roles);

  const permissionResponse = await fetch("/api/governance/permissions");
  if (permissionResponse.ok) {
    const permissions = await permissionResponse.json();
    selectedCanDecideProposals = permissions.designated_approver;
    selectedIsAdministrator =
      permissions.identity.roles.includes("administrator");
    selectedPermissionsLoaded = true;
  } else {
    decisionMessage.className = "error";
    decisionMessage.textContent =
      "Review permissions could not be loaded; decision actions are unavailable.";
    transferMessage.className = "error";
    transferMessage.textContent =
      "Transfer permissions could not be loaded; transfer actions are unavailable.";
  }

  try {
    await loadTags();
  } catch {
    tagFormMessage.className = "error";
    tagFormMessage.textContent =
      "Available tags could not be loaded; tag association is unavailable.";
  }
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
  availableOwners = identities;
  recordOwner.replaceChildren(
    ...identities.map((owner) => {
      const option = document.createElement("option");
      option.value = owner.id;
      option.textContent = owner.label;
      return option;
    }),
  );
  if (editingOwnerId !== null) {
    recordOwner.value = editingOwnerId;
  }
  setEditingMode(editingRecordId !== null);
  saveDraft.disabled = false;
  await loadRecords(tagFilter.value);
}

changeIdentity.addEventListener("click", async () => {
  await fetch("/api/mock-session", { method: "DELETE" });
  window.location.assign("/");
});

loadContext();

tagFilter.addEventListener("change", () => {
  loadRecords(tagFilter.value);
});

tagForm.addEventListener("submit", createTag);

cancelEdit.addEventListener("click", () => {
  resetForm();
  recordFormMessage.textContent = "";
});

recordForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  saveDraft.disabled = true;
  recordFormMessage.textContent = "";
  const restartedReview = editingStatus === "Proposed";
  const formData = new FormData(recordForm);
  const payload = Object.fromEntries(formData.entries());
  payload.tags = [...recordTags.selectedOptions].map((option) => option.value);

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

    updateTagOptions(payload.tags);
    resetForm();
    recordFormMessage.className = "";
    recordFormMessage.textContent = restartedReview
      ? "Proposal changes saved. It returned to Draft and must be resubmitted for review."
      : "Draft saved.";
    await loadRecords(tagFilter.value);
  } finally {
    saveDraft.disabled = false;
  }
});
