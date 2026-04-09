"""Dùng LLM để trích xuất age và area từ câu hỏi tự nhiên."""
from services.llm import call_llm_json


EXTRACT_PROMPT = """Bạn là trợ lý phân tích câu hỏi tuyển sinh.

Từ đoạn văn sau, hãy trích xuất thông tin:
- "age": tuổi của học sinh (số nguyên, null nếu không đề cập)
- "area": khu vực/địa điểm người dùng quan tâm (chuỗi, null nếu không đề cập)
- "intent": một trong ["ask_program", "ask_campus", "ask_tuition", "ask_apply", "ask_policy", "general", "unclear"]

Câu hỏi: "{message}"

Chỉ trả về JSON thuần, không giải thích:
{{"age": ..., "area": ..., "intent": "..."}}
"""


def extract_info(message: str) -> dict:
    prompt = EXTRACT_PROMPT.format(message=message)
    result = call_llm_json(prompt)
    return {
        "age": result.get("age"),
        "area": result.get("area"),
        "intent": result.get("intent", "general"),
    }
