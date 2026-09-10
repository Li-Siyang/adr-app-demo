const identityList = document.querySelector("#identity-list");
const selectionError = document.querySelector("#selection-error");

function roleName(role) {
  return role
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

async function selectIdentity(identityId) {
  selectionError.hidden = true;
  const response = await fetch("/api/mock-session", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identity_id: identityId }),
  });

  if (!response.ok) {
    selectionError.textContent = "The Mock identity could not be selected.";
    selectionError.hidden = false;
    return;
  }

  window.location.assign("/app");
}

async function loadIdentities() {
  const response = await fetch("/api/mock-identities");
  if (!response.ok) {
    identityList.innerHTML = "<p>Mock identities could not be loaded.</p>";
    return;
  }

  const identities = await response.json();
  identityList.replaceChildren(
    ...identities.map((identity) => {
      const card = document.createElement("article");
      card.className = "identity-card";

      const title = document.createElement("h3");
      title.textContent = identity.label;

      const roles = document.createElement("p");
      roles.textContent = `Roles: ${identity.roles.map(roleName).join(", ")}`;

      const button = document.createElement("button");
      button.type = "button";
      button.textContent = `Continue as ${identity.display_name} (Mock)`;
      button.addEventListener("click", () => selectIdentity(identity.id));

      card.append(title, roles, button);
      return card;
    }),
  );
}

loadIdentities();

