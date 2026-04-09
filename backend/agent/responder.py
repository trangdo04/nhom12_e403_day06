"""Dùng LLM để sinh câu trả lời tự nhiên từ dữ liệu đã xử lý."""
from services.llm import call_llm


RESPONSE_PROMPT = """Bạn là tư vấn viên tuyển sinh Vinschool thân thiện và chuyên nghiệp.

Dữ liệu đã xử lý:
- Cấp học phù hợp: {level}
- Chương trình: {program_desc}
- Cơ sở gợi ý: {campus_names}
- Intent người dùng: {intent}

Câu hỏi gốc: "{message}"

Yêu cầu:
1. Trả lời ngắn gọn, thân thiện (2–4 câu)
2. Nếu có cấp học → đề cập rõ chương trình
3. Nếu có cơ sở → gợi ý cơ sở cụ thể
4. Kết thúc bằng gợi ý hành động tiếp theo (học phí / đăng ký / liên hệ)
5. Nếu thiếu thông tin → hỏi lại 1 câu cụ thể (tuổi hoặc khu vực)
6. Trả lời bằng tiếng Việt
"""


CLARIFY_PROMPT = """Bạn là tư vấn viên tuyển sinh Vinschool.

Người dùng hỏi: "{message}"

Câu hỏi chưa đủ thông tin để tư vấn chính xác. Hãy hỏi lại 1 câu ngắn gọn, thân thiện để làm rõ:
- Nếu chưa biết tuổi → hỏi tuổi học sinh
- Nếu chưa biết khu vực → hỏi khu vực quan tâm

Chỉ hỏi 1 điều. Trả lời bằng tiếng Việt.
"""


def generate_response(message: str, level: str, program: dict | None, campuses: list[dict], intent: str) -> str:
    if not level and not campuses:
        prompt = CLARIFY_PROMPT.format(message=message)
        return call_llm(prompt).strip()

    campus_names = ", ".join(c["name"] for c in campuses) if campuses else "chưa xác định"
    program_desc = program["description"] if program else "chưa xác định"

    prompt = RESPONSE_PROMPT.format(
        level=level or "chưa xác định",
        program_desc=program_desc,
        campus_names=campus_names,
        intent=intent,
        message=message,
    )
    return call_llm(prompt).strip()
