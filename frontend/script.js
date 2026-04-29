const chatHistory = document.getElementById("chat-history");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");

const API_URL = "http://localhost:8000/chat";

function addMessage(text, sender) {
  const message = document.createElement("div");
  message.classList.add("message", sender);
  message.textContent = text;
  chatHistory.appendChild(message);
  chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage(pergunta) {
  const response = await fetch(API_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pergunta })
  });

  if (!response.ok) {
    throw new Error("Falha na comunicação com o backend.");
  }

  return response.json();
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const pergunta = userInput.value.trim();
  if (!pergunta) {
    return;
  }

  addMessage(pergunta, "user");
  userInput.value = "";

  try {
    const data = await sendMessage(pergunta);
    addMessage(data.resposta, "bot");
  } catch (error) {
    addMessage("Não foi possível obter resposta no momento.", "bot");
  }
});

addMessage(
  "Olá! Sou a assistente acadêmica virtual. Pergunte sobre matrícula, trancamento, documentos ou prazos.",
  "bot"
);
