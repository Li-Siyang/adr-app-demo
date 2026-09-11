const identityContext = document.querySelector("#identity-context");
const attributionPreview = document.querySelector("#attribution-preview");
const changeIdentity = document.querySelector("#change-identity");
const recordForm = document.querySelector("#record-form");
const recordOwner = document.querySelector("#record-owner");
const recordFormMessage = document.querySelector("#record-form-message");
const saveDraft = recordForm.querySelector('button[type="submit"]');

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
      const error = await response.json();
      recordFormMessage.textContent = Array.isArray(error.detail)
        ? displayValidationErrors(error.detail)
        : error.detail;
      return;
    }

    recordForm.reset();
    recordFormMessage.className = "";
    recordFormMessage.textContent = "Draft saved.";
  } finally {
    saveDraft.disabled = false;
  }
});
