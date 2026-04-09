"""Rule-based mapping: tuổi → cấp học, khu vực → cơ sở."""
import json
from pathlib import Path

_KB_PATH = Path(__file__).parent.parent / "data" / "knowledge_base.json"

with open(_KB_PATH, encoding="utf-8") as f:
    KB = json.load(f)


def map_age_to_level(age: int | None) -> str | None:
    """Trả về cấp học tương ứng với tuổi, hoặc None nếu không xác định."""
    if age is None:
        return None
    for entry in KB["age_to_level"]:
        if entry["min"] <= age <= entry["max"]:
            return entry["level"]
    return None


def match_campus(area: str | None) -> list[dict]:
    """Trả về danh sách cơ sở phù hợp với khu vực người dùng nhắc đến."""
    if not area:
        return []
    area_lower = area.lower().strip()
    matched = []
    for campus in KB["campuses"]:
        for kw in campus["keywords"]:
            if kw in area_lower:
                matched.append(campus)
                break
    return matched


def get_program_info(level: str | None) -> dict | None:
    if not level:
        return None
    return KB["programs"].get(level)


def get_cta() -> dict:
    return KB["cta"]
