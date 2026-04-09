from dotenv import load_dotenv
import os
import sys

# Thêm backend vào sys.path để có thể chạy uvicorn từ thư mục gốc
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)

load_dotenv(os.path.join(backend_dir, ".env"))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import logging
import json
from datetime import datetime
from pathlib import Path

from agent.agent import run_agent, invoke_advisor_stream

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vinschool Admissions Copilot API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOG_FILE = Path(os.path.join(backend_dir, "logs/interactions.jsonl"))
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


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
        result = run_agent(req.message, session_id=req.session_id)

        # Chuẩn hóa response theo format frontend kỳ vọng
        response_text = result.get("response", "")

        # Nếu quota hết, trả về thông báo thân thiện
        if result.get("error") == "QUOTA_EXHAUSTED":
            response_text = (
                "Xin lỗi, hệ thống đang tạm thời gián đoạn. "
                "Vui lòng liên hệ hotline 18006511 để được hỗ trợ trực tiếp."
            )

        api_response = {
            "response": response_text,
            "data": {
                "age": None,
                "area": None,
                "level": None,
                "campuses": [],
            },
            "cta": [
                {"label": "Xem học phí", "url": "https://vinschool.edu.vn/hoc-phi"},
                {"label": "Đăng ký tuyển sinh", "url": "https://vinschool.edu.vn/dang-ky"},
                {"label": "Liên hệ tư vấn", "url": "https://vinschool.edu.vn/lien-he"},
            ],
        }

        _log_interaction(req.session_id, req.message, api_response)
        return api_response
    except Exception as e:
        logger.error(f"Agent error: {e}")
        raise HTTPException(status_code=500, detail="Lỗi xử lý, vui lòng thử lại.")


@app.post("/api/chat/stream")
def chat_stream(req: ChatRequest):
    """Streaming endpoint — trả về text từng chunk qua SSE."""
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message không được để trống")

    def generate():
        try:
            full_text = ""
            for event in invoke_advisor_stream(req.message, session_id=req.session_id):
                if isinstance(event, tuple) and len(event) == 2:
                    chunk, metadata = event
                    
                    if hasattr(chunk, "type") and chunk.type in ("tool", "human"):
                        continue
                        
                    if hasattr(chunk, "tool_call_chunks") and chunk.tool_call_chunks:
                        continue

                    content = getattr(chunk, "content", "")
                    if isinstance(content, str) and content:
                        data = json.dumps({"delta": content}, ensure_ascii=False)
                        yield f"data: {data}\n\n"
                    elif isinstance(content, list):
                        text = "".join(
                            p.get("text", "") if isinstance(p, dict) else str(p)
                            for p in content
                        )
                        if text:
                            data = json.dumps({"delta": text}, ensure_ascii=False)
                            yield f"data: {data}\n\n"
            # Gửi event done kèm CTA
            done_payload = json.dumps({
                "done": True,
                "cta": [
                    {"label": "Xem học phí", "url": "https://vinschool.edu.vn/hoc-phi"},
                    {"label": "Đăng ký tuyển sinh", "url": "https://vinschool.edu.vn/dang-ky"},
                    {"label": "Liên hệ tư vấn", "url": "https://vinschool.edu.vn/lien-he"},
                ],
            }, ensure_ascii=False)
            yield f"data: {done_payload}\n\n"
        except Exception as e:
            logger.error(f"Stream error: {e}")
            err = json.dumps({"error": str(e)}, ensure_ascii=False)
            yield f"data: {err}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


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
        "level": result.get("data", {}).get("level"),
        "campuses": [c["name"] for c in result.get("data", {}).get("campuses", [])],
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
