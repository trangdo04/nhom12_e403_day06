import json
import os
from typing import Any
from langgraph.types import Command
from langchain_core.tools import tool


# ============================================================================
# TOOL 1: Search Học Phí (Tuition Fees)
# ============================================================================

@tool
def search_hoc_phi(query: str) -> dict[str, Any]:
    """
    Tìm kiếm thông tin học phí của Vinschool.
    
    Hiện tại cơ sở dữ liệu đang trống, vui lòng liên hệ với nhà trường để
    cập nhật thông tin học phí mới nhất.
    
    Args:
        query: Từ khóa tìm kiếm (ví dụ: "học phí mầm non", "học phí tiểu học")
    
    Returns:
        dict với các trường:
        - status: "no_data" | "found"
        - message: Thông báo kết quả
        - data: Dữ liệu học phí (nếu có)
        - tips: Gợi ý liên hệ
    """
    # Hiện tại DB học phí để trống
    hoc_phi_db = {}
    
    return {
        "status": "no_data",
        "message": f"Chưa có thông tin học phí cho tìm kiếm: '{query}'",
        "data": None,
        "tips": "Vui lòng liên hệ hotline 18006511 hoặc email để được tư vấn học phí chi tiết.",
        "contact": {
            "hotline": "18006511",
            "email_mien_bac": "info.mb@vinschool.edu.vn",
            "email_mien_nam": "info.mn@vinschool.edu.vn"
        }
    }


# ============================================================================
# TOOL 2: Search Quy Chế Tuyển Sinh (Admissions Regulations)
# ============================================================================

@tool
def search_quy_che(query: str) -> dict[str, Any]:
    """
    Tìm kiếm thông tin quy chế tuyển sinh của Vinschool từ file quy_che_tuyen_sinh.json.
    
    Có thể tìm kiếm theo:
    - Độ tuổi tuyển sinh
    - Quy định cho học sinh hiện tại
    - Quy định sĩ số lớp
    - Điều kiện đăng ký
    - Quy trình tuyển sinh
    - Dự tuyển đầu vào
    - Hướng dẫn hồ sơ
    - Thời gian tuyển sinh
    
    Args:
        query: Từ khóa tìm kiếm (ví dụ: "độ tuổi mầm non", "quy trình tuyển sinh")
    
    Returns:
        dict với các trường:
        - status: "found" | "not_found"
        - query: Từ khóa tìm kiếm
        - results: Kết quả tìm kiếm (list)
        - total_results: Tổng số kết quả
    """
    quy_che_path = os.path.join(
        os.path.dirname(__file__), 
        "../../data/quy_che_tuyen_sinh.json"
    )
    
    try:
        with open(quy_che_path, 'r', encoding='utf-8') as f:
            quy_che_data = json.load(f)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi đọc file quy chế: {str(e)}",
            "results": []
        }
    
    # Chuyển đổi query thành chữ thường để tìm kiếm
    query_lower = query.lower()
    results = []
    
    # Hàm tìm kiếm đệ quy trong JSON
    def search_recursive(obj: Any, path: str = ""):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                # Tìm trong key
                if query_lower in key.lower():
                    results.append({
                        "path": new_path,
                        "key": key,
                        "value": value,
                        "type": "key_match"
                    })
                # Tìm trong value
                search_recursive(value, new_path)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                new_path = f"{path}[{idx}]"
                if isinstance(item, dict):
                    for key, value in item.items():
                        if query_lower in str(key).lower() or query_lower in str(value).lower():
                            results.append({
                                "path": new_path,
                                "content": item,
                                "type": "list_item_match"
                            })
                else:
                    if query_lower in str(item).lower():
                        results.append({
                            "path": new_path,
                            "content": item,
                            "type": "list_match"
                        })
        elif isinstance(obj, str):
            if query_lower in obj.lower():
                results.append({
                    "path": path,
                    "content": obj,
                    "type": "string_match"
                })
    
    search_recursive(quy_che_data)
    
    return {
        "status": "found" if results else "not_found",
        "query": query,
        "results": results[:10],  # Giới hạn 10 kết quả
        "total_results": len(results)
    }


# ============================================================================
# TOOL 3: Search Thông Tin Vinschool (General Information)
# ============================================================================

@tool
def search_thong_tin(query: str, category: str = "all") -> dict[str, Any]:
    """
    Tìm kiếm thông tin chung về Vinschool từ file vinschool_knowledge_base.json.
    
    Categories có sẵn:
    - "overview": Giới thiệu chung về Vinschool
    - "features": Các tính năng và chương trình
    - "achievements": Thành tích học sinh
    - "admission": Thông tin tuyển sinh
    - "all": Tất cả danh mục (mặc định)
    
    Args:
        query: Từ khóa tìm kiếm (ví dụ: "AI", "Cambridge", "học bổng")
        category: Danh mục tìm kiếm (mặc định: "all")
    
    Returns:
        dict với các trường:
        - status: "found" | "not_found"
        - query: Từ khóa tìm kiếm
        - category: Danh mục đã tìm kiếm
        - results: Danh sách kết quả (list các items chứa title, summary, details)
        - total_results: Tổng số kết quả
    """
    knowledge_base_path = os.path.join(
        os.path.dirname(__file__), 
        "../../data/vinschool_knowledge_base.json"
    )
    
    try:
        with open(knowledge_base_path, 'r', encoding='utf-8') as f:
            kb_data = json.load(f)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Lỗi đọc file knowledge base: {str(e)}",
            "results": []
        }
    
    query_lower = query.lower()
    results = []
    
    # Xác định categories để tìm kiếm
    if category == "all":
        categories_to_search = ["overview", "features", "achievements", "admission"]
    else:
        categories_to_search = [category] if category in kb_data else []
    
    # Tìm kiếm trong từng category
    for cat in categories_to_search:
        if cat not in kb_data:
            continue
        
        items = kb_data[cat]
        if not isinstance(items, list):
            continue
        
        for item in items:
            if not isinstance(item, dict):
                continue
            
            # Tìm trong title
            if "title" in item and query_lower in item["title"].lower():
                results.append({
                    "category": cat,
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "details": item.get("details", ""),
                    "match_field": "title"
                })
            # Tìm trong summary
            elif "summary" in item and query_lower in item["summary"].lower():
                results.append({
                    "category": cat,
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "details": item.get("details", ""),
                    "match_field": "summary"
                })
            # Tìm trong details
            elif "details" in item and query_lower in item["details"].lower():
                results.append({
                    "category": cat,
                    "title": item.get("title", ""),
                    "summary": item.get("summary", ""),
                    "details": item.get("details", ""),
                    "match_field": "details"
                })
    
    return {
        "status": "found" if results else "not_found",
        "query": query,
        "category": category,
        "results": results,
        "total_results": len(results),
        "available_categories": ["overview", "features", "achievements", "admission"]
    }


# ============================================================================
# Danh sách tất cả các tools
# ============================================================================

tools = [search_hoc_phi, search_quy_che, search_thong_tin]
