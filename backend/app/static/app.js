const identityContext = document.querySelector("#identity-context");
const attributionPreview = document.querySelector("#attribution-preview");
const changeIdentity = document.querySelector("#change-identity");

function roleName(role) {
  return role
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
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
}

changeIdentity.addEventListener("click", async () => {
  await fetch("/api/mock-session", { method: "DELETE" });
  window.location.assign("/");
});

loadContext();

