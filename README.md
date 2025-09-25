
# KIN508 · Chatbot monolítico (Python) para Vercel

Monolito ligero en **FastAPI** que sirve **landing + API** en el mismo archivo (`api/index.py`).
Diseñado para Vercel Functions (Python).

## 🚀 Deploy en Vercel

1) Crea un repositorio con estos archivos.
2) En Vercel, crea un proyecto conectado a ese repo.
3) Agrega **Environment Variable**: `OPENAI_API_KEY`.
4) Deploy. Listo.

> Vercel ejecuta `api/index.py` como Function. Servimos `/` (landing), `/chat` (endpoint) y `/static/*`.

## ▶️ Local

```bash
pip install -r requirements.txt
uvicorn api.index:app --reload
# abre http://127.0.0.1:8000
```

## 📦 Estructura

```
api/index.py          # FastAPI (landing + /chat)
templates/index.html  # Landing + UI del chat
static/styles.css     # Estilos
requirements.txt
vercel.json
```

## 🧠 Prompt del sistema (KIN508)
El backend incluye un prompt diseñado para **razonamiento clínico en Disfunción Neuromusculoesquelética** con reglas de seguridad y enfoque pedagógico.

## 🔒 Persistencia
Para mantener el monolito simple en Vercel (FS efímero), la **historia de chat vive en el cliente** y se envía en cada request.
Si deseas persistencia: integra Vercel KV / Supabase / Redis externo.

## 🧩 Extensiones
- Agregar rutas por asignatura (KIN607, KIN723): duplicar prompts por curso.
- Streaming SSE: posible, pero considera límites de Functions.
- Auth (JWT), panel tutor, analíticas.
```

