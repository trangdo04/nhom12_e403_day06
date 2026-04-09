"""Agent chính: kết hợp LLM extractor + rule mapping + LLM responder."""
from agent.extractor import extract_info
from agent.rules import map_age_to_level, match_campus, get_program_info, get_cta
from agent.responder import generate_response


def run_agent(message: str) -> dict:
    # 1. Trích xuất thông tin từ câu hỏi bằng LLM
    extracted = extract_info(message)
    age = extracted.get("age")
    area = extracted.get("area")
    intent = extracted.get("intent", "general")

    # 2. Rule-based mapping
    level = map_age_to_level(age)
    campuses = match_campus(area)
    program = get_program_info(level)
    cta = get_cta()

    # 3. Xây dựng CTA phù hợp với intent
    cta_list = _build_cta(intent, cta)

    # 4. Sinh câu trả lời tự nhiên bằng LLM
    response_text = generate_response(
        message=message,
        level=level,
        program=program,
        campuses=campuses,
        intent=intent,
    )

    return {
        "response": response_text,
        "data": {
            "age": age,
            "area": area,
            "level": level,
            "campuses": [{"name": c["name"], "address": c["address"], "url": c["url"]} for c in campuses],
        },
        "cta": cta_list,
    }


def _build_cta(intent: str, cta: dict) -> list[dict]:
    """Trả về CTA phù hợp theo intent."""
    if intent == "ask_tuition":
        return [cta["tuition"], cta["apply"]]
    if intent == "ask_apply":
        return [cta["apply"], cta["contact"]]
    if intent == "ask_policy":
        return [cta["policy"], cta["apply"]]
    # Mặc định: luôn có học phí + đăng ký
    return [cta["tuition"], cta["apply"], cta["contact"]]
