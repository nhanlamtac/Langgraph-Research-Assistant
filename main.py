from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from apps import run_agent

# ✅ MUST BE DEFINED BEFORE `app = FastAPI()`
app = FastAPI(title="LLM Research Assistant API")

# ✅ TURN CORS ON
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # use "*" for file:// or null origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Mount static directory and templates for frontend ===
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# === Root page to serve chat UI ===
@app.get("/", response_class=HTMLResponse)
async def chat_interface(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request, "response": ""})

# === POST form submission ===
@app.post("/", response_class=HTMLResponse)
async def handle_chat(request: Request, prompt: str = Form(...)):
    response = run_agent(prompt)
    return templates.TemplateResponse("chat.html", {"request": request, "response": response, "prompt": prompt})

# === API endpoint (optional, already exists) ===
@app.post("/ask/")
async def ask_agent(prompt: str = Form(...)):
    response = run_agent(prompt)
    return {"response": response}
