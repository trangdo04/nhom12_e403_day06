import json
import os
import re
from typing import Any, Dict, List
from langgraph.types import Command
from langchain_core.tools import tool

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))
HOC_PHI_MAM_NON_PATH = os.path.join(DATA_DIR, "hoc_phi_mam_non.json")
HOC_PHI_TH_PATH = os.path.join(DATA_DIR, "hocphi_th_thcs_thpt.json")
QUY_CHE_PATH = os.path.join(DATA_DIR, "quy_che_tuyen_sinh.json")
KNOWLEDGE_BASE_PATH = os.path.join(DATA_DIR, "vinschool_knowledge_base.json")


def normalize_text(text: str) -> str:
    """Normalize text for comparison.

    This function strips leading/trailing whitespace, collapses multiple
    whitespace characters into a single space, and converts text to lowercase.

    Args:
        text: The input text to normalize.

    Returns:
        The normalized text string.
    """
    return re.sub(r"\s+", " ", text.strip().lower())


def contains_any(text: str, keywords: List[str]) -> bool:
    """Check whether any keyword is present in the text.

    Args:
        text: The text to search.
        keywords: A list of keyword strings to look for.

    Returns:
        True if any keyword appears in the text; otherwise False.
    """
    return any(keyword in text for keyword in keywords)


def load_json(path: str) -> Any:
    """Load JSON data from a file path.

    Args:
        path: The path to the JSON file.

    Returns:
        The parsed JSON object.
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_locations(text: str) -> List[str]:
    """Return standardized location names found in the text.

    Args:
        text: The input text to inspect.

    Returns:
        A list of matched location names.
    """
    location_map = {
        "hà nội": "Hà Nội",
        "ha noi": "Hà Nội",
        "hải phòng": "Hải Phòng",
        "hai phong": "Hải Phòng",
        "thanh hóa": "Thanh Hóa",
        "thanh hoa": "Thanh Hóa",
        "hưng yên": "Hưng Yên",
        "hung yen": "Hưng Yên",
        "tp hcm": "Thành phố Hồ Chí Minh",
        "hcm": "Thành phố Hồ Chí Minh",
        "sài gòn": "Thành phố Hồ Chí Minh",
        "phú quốc": "Phú Quốc",
        "phu quoc": "Phú Quốc",
    }
    return [value for key, value in location_map.items() if key in text]


def filter_levels(text: str) -> List[str]:
    """Return standardized education level names found in the text.

    Args:
        text: The input text to inspect.

    Returns:
        A list of matched level names.
    """
    level_map = {
        "mầm non": "Mầm non",
        "mam non": "Mầm non",
        "tiểu học": "Tiểu học",
        "tieu hoc": "Tiểu học",
        "thcs": "THCS",
        "thpt": "THPT",
        "nâng cao": "Nâng cao",
        "nang cao": "Nâng cao",
        "chuẩn": "Chuẩn",
        "chuan": "Chuẩn",
    }
    return [value for key, value in level_map.items() if key in text]


def build_result(source: str, section: str, summary: str, details: Any) -> Dict[str, Any]:
    """Build a consistent tool result dictionary.

    Args:
        source: The source or section name for the result.
        section: The specific area or location of the result.
        summary: A short summary of the result.
        details: The detailed payload for the result.

    Returns:
        A structured result dictionary.
    """
    return {
        "source": source,
        "section": section,
        "summary": summary,
        "details": details,
    }


# ============================================================================
# TOOL 1: Search Học Phí (Tuition Fees)
# ============================================================================

@tool
def search_hoc_phi(query: str) -> dict[str, Any]:
    """Search tuition, fee, discount, and payment policy information.

    This tool searches the tuition and fee JSON datasets for matching
    information based on user query keywords, location, and education level.

    Args:
        query: The user query text.

    Returns:
        A dictionary containing the search status, the original query,
        the matched results, and the total result count.
    """
    query_normalized = normalize_text(query)
    try:
        mam_non_data = load_json(HOC_PHI_MAM_NON_PATH)
        th_data = load_json(HOC_PHI_TH_PATH)
    except Exception as e:
        return {"status": "error", "message": f"Lỗi đọc file học phí: {str(e)}", "results": []}

    results: List[Dict[str, Any]] = []
    locations = filter_locations(query_normalized)
    levels = filter_levels(query_normalized)

    is_tuition_question = contains_any(query_normalized, [
        "học phí", "hoc phi", "phí", "phí chính khóa", "hệ chuẩn", "hệ nâng cao",
        "phí bán trú", "phí xe buýt", "phí đồng phục", "phí dịch vụ", "phí phát triển trường",
        "đăng ký tuyển sinh", "ưu đãi", "miễn giảm", "chiết khấu"
    ])

    # Học phí chính khóa từ file hoc_phi_mam_non.json
    for entry in mam_non_data.get("Học phí chính khóa", []):
        if locations and not any(loc in entry.get("Địa điểm", "") for loc in locations):
            continue
        if levels and not any(level.lower() in json.dumps(entry, ensure_ascii=False).lower() for level in levels):
            continue
        if is_tuition_question or any(keyword in query_normalized for keyword in ["học phí", "phí", "hệ", "mầm non", "tiểu học", "thcs", "thpt"]):
            results.append(build_result(
                source="Học phí chính khóa",
                section=entry.get("Địa điểm", "") + " — " + entry.get("Năm học", ""),
                summary="Thông tin học phí chính khóa theo địa điểm và hệ đào tạo.",
                details=entry.get("Học phí", []),
            ))

    # Phí khác và ưu đãi từ file hoc_phi_mam_non.json
    for section_name in ["Chính sách ưu đãi và miễn giảm", "Các khoản phí khác"]:
        for entry in mam_non_data.get(section_name, []):
            if locations and not any(loc in entry.get("Địa điểm", "") for loc in locations):
                continue
            if levels and section_name == "Chính sách ưu đãi và miễn giảm" and not any(level.lower() in json.dumps(entry, ensure_ascii=False).lower() for level in levels):
                pass
            if is_tuition_question or section_name == "Chính sách ưu đãi và miễn giảm" or section_name == "Các khoản phí khác":
                results.append(build_result(
                    source=section_name,
                    section=entry.get("Địa điểm", "") + " — " + entry.get("Năm học", ""),
                    summary=entry.get("Lưu ý", ""),
                    details=entry.get("Chính sách", entry.get("Phí", [])),
                ))

    # Học phí TH-THCS-THPT
    for entry in th_data.get("categories", {}).get("hoc_phi_chinh_khoa", {}).get("hoc_phi", []):
        if locations and not any(loc in entry.get("dia_diem", "") for loc in locations):
            continue
        if levels and not any(level.lower() in json.dumps(entry, ensure_ascii=False).lower() for level in levels):
            continue
        if is_tuition_question:
            results.append(build_result(
                source="Học phí TH-THCS-THPT",
                section=entry.get("dia_diem", ""),
                summary="Thông tin học phí chính khóa theo cấp học và hệ đào tạo.",
                details={
                    "he_chuan": entry.get("he_chuan"),
                    "he_nang_cao": entry.get("he_nang_cao"),
                },
            ))

    # Các khoản khác trong file hocphi_th_thcs_thpt.json
    other_section = th_data.get("categories", {}).get("cac_khoan_phi_khac", {})
    for fee_key, fee_value in other_section.items():
        if query_normalized and any(keyword in query_normalized for keyword in ["phí", "phi", "đăng ký", "bán trú", "xe buýt", "đồng phục", "học phẩm", "phát triển", "bảo hiểm", "dịch vụ"]):
            results.append(build_result(
                source="Học phí TH-THCS-THPT",
                section=fee_key,
                summary="Thông tin khoản phí khác." ,
                details=fee_value,
            ))

    if not results:
        # Fallback: search trong toàn bộ dữ liệu
        query_lower = query.lower()
        def recursive_search(obj: Any, path: str, source: str):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if query_lower in str(key).lower() or query_lower in str(value).lower():
                        results.append({"source": source, "path": new_path, "content": value})
                    recursive_search(value, new_path, source)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_path = f"{path}[{idx}]"
                    if isinstance(item, (dict, list)):
                        recursive_search(item, new_path, source)
                    elif query_lower in str(item).lower():
                        results.append({"source": source, "path": new_path, "content": item})
        recursive_search(mam_non_data, "Mầm non", "Mầm non")
        recursive_search(th_data, "TH-THCS-THPT", "TH-THCS-THPT")

    return {
        "status": "found" if results else "not_found",
        "query": query,
        "results": results[:20],
        "total_results": len(results),
    }


# ============================================================================
# TOOL 2: Search Quy Chế Tuyển Sinh (Admissions Regulations)
# ============================================================================

@tool
def search_quy_che(query: str) -> dict[str, Any]:
    """Search admission regulations and policy information.

    This tool matches the user query against the admission regulation dataset
    and returns the most relevant category or detailed entries.

    Args:
        query: The user query text.

    Returns:
        A dictionary containing the status, the original query,
        the matched results, and the total result count.
    """
    query_normalized = normalize_text(query)
    try:
        quy_che_data = load_json(QUY_CHE_PATH)
    except Exception as e:
        return {"status": "error", "message": f"Lỗi đọc file quy chế: {str(e)}", "results": []}

    category_rules = {
        "DO_TUOI_TUYEN_SINH": ["độ tuổi", "tuổi", "năm sinh", "độ tuổi tuyển sinh"],
        "QUY_DINH_SI_SO": ["sĩ số", "si so", "sỉ số", "số lượng", "số lớp"],
        "DIEU_KIEN_DANG_KY": ["điều kiện", "điều kien", "học sinh mới", "đăng ký", "dang ky"],
        "QUY_TRINH_TUYEN_SINH": ["quy trình", "quy trinh", "tuyển sinh", "tuyen sinh", "thủ tục", "thu tuc"],
        "DU_TUYEN_DAU_VAO": ["dự tuyển", "du tuyen", "thi", "đầu vào", "dau vao"],
        "HUONG_DAN_HO_SO": ["hồ sơ", "ho so", "giấy tờ", "giay to", "nộp hồ sơ", "nop ho so"],
        "THOI_GIAN_TUYEN_SINH": ["thời gian", "thoi gian", "đợt", "dot", "lịch", "tháng"],
        "LIEN_HE": ["liên hệ", "lien he", "hotline", "email", "ứng dụng", "ung dung"],
        "CHINH_SACH_TUYEN_SINH": ["ưu tiên", "uu tien", "ưu đãi", "uu dai", "chính sách", "chinh sach"],
    }

    matched_categories = [cat for cat, keywords in category_rules.items() if contains_any(query_normalized, keywords)]
    results: List[Dict[str, Any]] = []

    if matched_categories:
        for cat in matched_categories:
            if cat in quy_che_data.get("categories", {}):
                results.append({
                    "category": cat,
                    "content": quy_che_data["categories"][cat],
                })
    else:
        # Fallback: search toàn bộ dữ liệu theo cấu trúc
        def recursive_search(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_path = f"{path}.{key}" if path else key
                    if query_normalized in key.lower() or (isinstance(value, str) and query_normalized in value.lower()):
                        results.append({"path": new_path, "key": key, "value": value})
                    recursive_search(value, new_path)
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_path = f"{path}[{idx}]"
                    if isinstance(item, (dict, list)):
                        recursive_search(item, new_path)
                    elif isinstance(item, str) and query_normalized in item.lower():
                        results.append({"path": new_path, "content": item})
        recursive_search(quy_che_data)

    return {
        "status": "found" if results else "not_found",
        "query": query,
        "results": results[:15],
        "total_results": len(results),
    }


# ============================================================================
# TOOL 3: Search Thông Tin Vinschool (General Information)
# ============================================================================

@tool
def search_thong_tin(query: str, category: str = "all") -> dict[str, Any]:
    """Search the Vinschool knowledge base for general information.

    This tool searches overview, features, achievements, or admission
    categories for matches to the user query.

    Args:
        query: The user query text.
        category: The optional category to search in.

    Returns:
        A dictionary containing the status, the original query,
        the selected category, the matched results, and the total result count.
    """
    query_normalized = normalize_text(query)
    try:
        kb_data = load_json(KNOWLEDGE_BASE_PATH)
    except Exception as e:
        return {"status": "error", "message": f"Lỗi đọc file knowledge base: {str(e)}", "results": []}

    category_aliases = {
        "overview": ["overview", "giới thiệu", "gioi thieu", "giới thieu"],
        "features": ["features", "tính năng", "tinh nang", "chương trình", "chuong trinh", "chương trinh"],
        "achievements": ["achievements", "thành tích", "thanh tich", "kết quả", "ket qua"],
        "admission": ["admission", "tuyển sinh", "tuyen sinh", "đăng ký", "dang ky"],
    }

    normalized_category = category
    if category != "all":
        for canonical, aliases in category_aliases.items():
            if category.lower() in aliases:
                normalized_category = canonical
                break

    categories_to_search = [normalized_category] if normalized_category != "all" and normalized_category in kb_data else ["overview", "features", "achievements", "admission"]
    results: List[Dict[str, Any]] = []

    for cat in categories_to_search:
        items = kb_data.get(cat, [])
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            title = item.get("title", "")
            summary = item.get("summary", "")
            details = item.get("details", "")
            if query_normalized in title.lower() or query_normalized in summary.lower() or query_normalized in details.lower():
                match_field = "title" if query_normalized in title.lower() else "summary" if query_normalized in summary.lower() else "details"
                results.append({
                    "category": cat,
                    "title": title,
                    "summary": summary,
                    "details": details,
                    "match_field": match_field,
                })

    return {
        "status": "found" if results else "not_found",
        "query": query,
        "category": normalized_category,
        "results": results,
        "total_results": len(results),
        "available_categories": ["overview", "features", "achievements", "admission"],
    }


# ============================================================================
# Danh sách tất cả các tools
# ============================================================================

tools = [search_hoc_phi, search_quy_che, search_thong_tin]
