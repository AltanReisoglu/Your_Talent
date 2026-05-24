const userIdInput = document.querySelector("#userId");
const sessionIdInput = document.querySelector("#sessionId");
const form = document.querySelector("#invokeForm");
const messageInput = document.querySelector("#messageInput");
const submitButton = document.querySelector("#submitButton");
const messages = document.querySelector("#messages");
const statusEl = document.querySelector("#status");
const hookTrace = document.querySelector("#hookTrace");
const threadId = document.querySelector("#threadId");

const storedUser = localStorage.getItem("finwiki.userId") || "local-user";
const storedSession = localStorage.getItem("finwiki.sessionId") || `demo-${new Date().toISOString().slice(0, 10)}`;

userIdInput.value = storedUser;
sessionIdInput.value = storedSession;

userIdInput.addEventListener("change", () => localStorage.setItem("finwiki.userId", userIdInput.value.trim()));
sessionIdInput.addEventListener("change", () => localStorage.setItem("finwiki.sessionId", sessionIdInput.value.trim()));

document.querySelectorAll("[data-prompt]").forEach((button) => {
  button.addEventListener("click", () => {
    messageInput.value = button.dataset.prompt || "";
    messageInput.focus();
  });
});

async function checkHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const data = await response.json();
    statusEl.className = "status ok";
    statusEl.lastElementChild.textContent = data.service || "Hazır";
  } catch (error) {
    statusEl.className = "status error";
    statusEl.lastElementChild.textContent = "Servis yok";
  }
}

function addMessage(kind, text, meta) {
  const item = document.createElement("article");
  item.className = `message ${kind}`;
  const metaEl = document.createElement("span");
  metaEl.className = "meta";
  metaEl.textContent = meta;
  item.append(metaEl, document.createTextNode(text));
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

function renderTrace(payload) {
  hookTrace.textContent = JSON.stringify(payload || {}, null, 2);
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  const userId = userIdInput.value.trim() || "local-user";
  const sessionId = sessionIdInput.value.trim() || "default";

  if (!message) {
    messageInput.focus();
    return;
  }

  localStorage.setItem("finwiki.userId", userId);
  localStorage.setItem("finwiki.sessionId", sessionId);

  addMessage("user", message, `${userId} / ${sessionId}`);
  messageInput.value = "";
  submitButton.disabled = true;
  submitButton.textContent = "Çalışıyor";

  try {
    const response = await fetch("/invoke", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, session_id: sessionId, message })
    });

    const text = await response.text();
    let data;
    try {
      data = JSON.parse(text);
    } catch {
      data = { response: text };
    }

    if (!response.ok) {
      const detail = data.detail || data.title || text || `HTTP ${response.status}`;
      addMessage("error", detail, "gateway error");
      return;
    }

    addMessage("agent", data.response || "(boş yanıt)", "FinWiki");
    threadId.textContent = data.thread_id || "Thread yok";
    renderTrace(data.hooks);
  } catch (error) {
    addMessage("error", String(error), "network error");
  } finally {
    submitButton.disabled = false;
    submitButton.textContent = "Gönder";
  }
});

checkHealth();
