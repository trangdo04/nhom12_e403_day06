from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
import json
from datetime import datetime
from pathlib import Path

from agent.agent import run_agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vinschool Admissions Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = Path("logs/interactions.jsonl")
LOG_FILE.parent.mkdir(exist_ok=True)


class ChatRequest(BaseModel):
    message: str
    session_id: str = "anonymous"


class LogRequest(BaseModel):
    session_id: str
    action: str  # "accept_cta" | "correct" | "drop_off"
    detail: str = ""


@app.get("/")
def root():
    return {"status": "ok", "service": "Vinschool Admissions Copilot"}


@app.post("/api/chat")
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message không được để trống")
    try:
        result = run_agent(req.message)
        _log_interaction(req.session_id, req.message, result)
        return result
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý, vui lòng thử lại.")


@app.post("/api/log")
def log_action(req: LogRequest):
    """Ghi lại hành vi người dùng (click CTA, sửa, rời phiên)."""
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "session_id": req.session_id,
        "action": req.action,
        "detail": req.detail,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return {"status": "logged"}


def _log_interaction(session_id: str, message: str, result: dict):
    entry = {
        "ts": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "message": message,
        "level": result["data"].get("level"),
        "campuses": [c["name"] for c in result["data"].get("campuses", [])],
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
