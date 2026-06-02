from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from groq import Groq
import os

app = FastAPI()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

SYSTEM_PROMPT = """
Eres el asistente virtual de "El Correo", un restaurante colombiano en Cali.
Tu nombre es Camilo y hablas de forma amable, cálida y natural.

INFORMACIÓN DEL RESTAURANTE:
- Nombre: El Correo
- Dirección: Calle 1 # 2-3, Cali
- Teléfono: 317 750 8039
- Horarios:
  • Lunes a viernes: 12:00 pm - 9:00 pm
  • Sábados: 11:00 am - 10:00 pm
  • Domingos: 11:00 am - 8:00 pm
  • Lunes: CERRADO

MENÚ:
Entradas:
- Patacones con hogao: $12.000
- Empanadas (3 unidades): $9.000
- Sopa del día: $10.000

Platos principales:
- Bandeja paisa completa: $28.000
- Sancocho de gallina: $22.000
- Pollo asado con papas: $24.000
- Chuleta de cerdo: $26.000
- Cazuela de fríjoles: $18.000

Postres:
- Arroz con leche: $7.000
- Mazamorra con panela: $6.000
- Brownie con helado: $10.000

Bebidas:
- Jugo natural (lulo, maracuyá, mora, guanábana): $7.000
- Limonada de coco: $9.000
- Gaseosa: $5.000
- Agua: $3.000

PARA RESERVAS:
- El cliente debe indicar: nombre, número de personas, fecha y hora
- Confirmar que la disponibilidad se validará y se les avisará por este mismo chat

REGLAS:
- Responde SIEMPRE en español
- Sé conciso, máximo 4-5 líneas por respuesta
- No inventes precios ni platos que no estén en el menú
- Si el cliente quiere hablar con una persona real, dile que escriba "HUMANO"
- Usa emojis con moderación (máximo 2 por mensaje)
"""

conversations: dict[str, list] = {}

class ChatRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
async def chat(req: ChatRequest):
    if req.session_id not in conversations:
        conversations[req.session_id] = []

    conversations[req.session_id].append({
        "role": "user",
        "content": req.message
    })

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            *conversations[req.session_id]
        ],
        max_tokens=500
    )

    bot_reply = response.choices[0].message.content

    conversations[req.session_id].append({
        "role": "assistant",
        "content": bot_reply
    })

    return {"reply": bot_reply}

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>El Correo — Bot Nivel 3</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #f0f2f5; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
    .container { width: 400px; height: 680px; background: white; border-radius: 16px; box-shadow: 0 4px 24px rgba(0,0,0,0.12); display: flex; flex-direction: column; overflow: hidden; }
    .header { background: #E1306C; color: white; padding: 16px 20px; display: flex; align-items: center; gap: 12px; }
    .avatar { width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,0.3); display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .header-info h2 { font-size: 15px; font-weight: 600; }
    .header-info p { font-size: 12px; opacity: 0.85; margin-top: 2px; }
    .status-dot { width: 8px; height: 8px; background: #4ade80; border-radius: 50%; display: inline-block; margin-right: 4px; }
    .badge { font-size: 10px; background: rgba(255,255,255,0.2); padding: 2px 8px; border-radius: 99px; margin-top: 4px; display: inline-block; }
    .messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; background: #f0f2f5; }
    .msg { max-width: 78%; padding: 10px 14px; border-radius: 18px; font-size: 14px; line-height: 1.5; word-break: break-word; }
    .msg.bot { background: white; color: #1a1a1a; align-self: flex-start; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.08); }
    .msg.user { background: #E1306C; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }
    .msg.typing { background: white; color: #888; align-self: flex-start; font-style: italic; font-size: 13px; }
    .input-area { padding: 12px 16px; background: white; border-top: 1px solid #f0f0f0; display: flex; gap: 8px; align-items: center; }
    .input-area input { flex: 1; border: 1px solid #e0e0e0; border-radius: 24px; padding: 10px 16px; font-size: 14px; outline: none; }
    .input-area input:focus { border-color: #E1306C; }
    .input-area button { width: 40px; height: 40px; background: #E1306C; border: none; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; }
    .input-area button svg { fill: white; width: 18px; height: 18px; }
    .input-area button:disabled { background: #ccc; cursor: not-allowed; }
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <div class="avatar">🍽️</div>
    <div class="header-info">
      <h2>El Correo</h2>
      <p><span class="status-dot"></span>Camilo · Asistente virtual</p>
      <span class="badge">Nivel 3 · IA con Groq</span>
    </div>
  </div>
  <div class="messages" id="messages">
    <div class="msg bot">Hola! Soy Camilo, el asistente de <strong>El Correo</strong>. En que te puedo ayudar hoy?</div>
  </div>
  <div class="input-area">
    <input type="text" id="input" placeholder="Escribe tu mensaje..." autocomplete="off" />
    <button id="send-btn" onclick="sendMessage()">
      <svg viewBox="0 0 24 24"><path d="M2 21l21-9L2 3v7l15 2-15 2z"/></svg>
    </button>
  </div>
</div>
<script>
  const sessionId = 'session_' + Math.random().toString(36).slice(2);
  const messagesEl = document.getElementById('messages');
  const inputEl = document.getElementById('input');
  const btnEl = document.getElementById('send-btn');

  inputEl.addEventListener('keydown', function(e) { if (e.key === 'Enter') sendMessage(); });

  function addMsg(text, role) {
    const div = document.createElement('div');
    div.className = 'msg ' + role;
    div.innerText = text;
    messagesEl.appendChild(div);
    messagesEl.scrollTop = messagesEl.scrollHeight;
    return div;
  }

  async function sendMessage() {
    const text = inputEl.value.trim();
    if (!text) return;
    inputEl.value = '';
    btnEl.disabled = true;
    addMsg(text, 'user');
    const typing = addMsg('Escribiendo...', 'typing');
    try {
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId, message: text })
      });
      const data = await res.json();
      typing.remove();
      addMsg(data.reply, 'bot');
    } catch(e) {
      typing.remove();
      addMsg('Error al conectar. Intenta de nuevo.', 'bot');
    }
    btnEl.disabled = false;
    inputEl.focus();
  }
</script>
</body>
</html>
"""
