
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# OpenAI SDK v1.x
from openai import OpenAI

# --- App Setup ---
app = FastAPI(title="KIN508 Monolithic Chatbot")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- OpenAI Client ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # Allow the app to boot so the landing page can show an env var warning
    pass
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

# --- Domain System Prompt (KIN508) ---
KIN508_SYSTEM_PROMPT = """\
Eres ARK, un asistente de razonamiento clínico para la asignatura KIN508 (Disfunción Neuromusculoesquelética).
Objetivo: guiar al estudiante en el proceso de anamnesis, examen físico, hipótesis diagnósticas diferenciales,
tests de confirmación, y propuesta de intervención basada en evidencia.
Reglas:
- Sé claro, estructurado y breve cuando el estudiante te pida pasos concretos; expándete sólo si lo solicita.
- Promueve el razonamiento: pregunta por datos faltantes relevantes.
- Evita dar diagnósticos definitivos sin sustento; ofrece probabilidades y siguientes pasos.
- Incluye referencias rápidas (autor/año o guía clínica) cuando propongas intervenciones de alto impacto.
- Seguridad primero: destaca 'banderas rojas' si aparecen.
"""

# --- Schemas ---
class ChatMessage(BaseModel):
    role: str = Field(..., description="user|assistant|system")
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = "gpt-4o-mini"
    temperature: Optional[float] = 0.3
    # Optional course tag for future multi-course support
    course: Optional[str] = "KIN508"

@app.get("/", response_class=HTMLResponse)
async def landing(request: Request):
    env_ok = bool(os.getenv("OPENAI_API_KEY"))
    return templates.TemplateResponse("index.html", {"request": request, "env_ok": env_ok})

@app.post("/chat")
async def chat(req: ChatRequest):
    if client is None:
        raise HTTPException(status_code=500, detail="OPENAI_API_KEY no configurada en variables de entorno.")
    
    # Build messages: system + user history
    messages = [{"role": "system", "content": KIN508_SYSTEM_PROMPT}] + [m.dict() for m in req.messages]
    try:
        # Responses API (Assistants-style "Responses") if available; fallback to Chat Completions
        # Using Chat Completions for broad support
        completion = client.chat.completions.create(
            model=req.model,
            messages=messages,
            temperature=req.temperature,
        )
        content = completion.choices[0].message.content
        usage = getattr(completion, "usage", None)
        return JSONResponse(
            {
                "ok": True,
                "reply": content,
                "usage": getattr(usage, "model_dump", lambda: usage)() if usage else None,
                "ts": datetime.utcnow().isoformat() + "Z",
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health/diagnostics
@app.get("/health")
async def health():
    return {"status": "ok", "env_openai": bool(os.getenv("OPENAI_API_KEY"))}
