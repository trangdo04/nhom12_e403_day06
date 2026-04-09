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
    Tìm kiếm thông tin học phí, chính sách ưu đãi, thời hạn đóng phí của Vinschool từ cơ sở dữ liệu.
    
    Có thể tìm kiếm các thông tin như:
    - Biểu phí mầm non, tiểu học, trung học
    - Các khoản phí khác (bán trú, xe buýt, học phẩm, đồng phục...)
    - Các chính sách ưu đãi và miễn giảm
    - Quy định nộp, rút và hoàn phí
    
    Args:
        query: Từ khóa tìm kiếm (ví dụ: "học phí mầm non", "phí xe buýt", "ưu đãi", "chuyển hệ")
    
    Returns:
        dict với các trường:
        - status: "found" | "not_found" | "error"
        - query: Từ khóa tìm kiếm
        - results: Kết quả tìm kiếm (list)
        - total_results: Tổng số kết quả
    """
    mam_non_path = os.path.join(os.path.dirname(__file__), "../../data/hoc_phi_mam_non.json")
    th_path = os.path.join(os.path.dirname(__file__), "../../data/hocphi_th_thcs_thpt.json")
    
    try:
        with open(mam_non_path, 'r', encoding='utf-8') as f:
            mam_non_data = json.load(f)
        with open(th_path, 'r', encoding='utf-8') as f:
            th_data = json.load(f)
    except Exception as e:
        return {"status": "error", "message": f"Lỗi đọc file học phí: {str(e)}", "results": []}

    query_lower = query.lower()
    results = []
    
    def search_recursive(obj: Any, path: str, source: str):
        if isinstance(obj, dict):
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                if query_lower in key.lower():
                    results.append({"source": source, "path": new_path, "value": value})
                search_recursive(value, new_path, source)
        elif isinstance(obj, list):
            for idx, item in enumerate(obj):
                new_path = f"{path}[{idx}]"
                if isinstance(item, dict):
                    match = False
                    for k, v in item.items():
                        if isinstance(v, (str, int, float)) and query_lower in str(v).lower():
                            match = True
                            break
                        if query_lower in str(k).lower():
                            match = True
                            break
                    if match:
                        results.append({"source": source, "path": new_path, "content": item})
                    search_recursive(item, new_path, source)
                else:
                    if query_lower in str(item).lower():
                        results.append({"source": source, "path": new_path, "content": item})
        elif isinstance(obj, str):
            if query_lower in obj.lower():
                results.append({"source": source, "path": path, "content": obj})

    search_recursive(mam_non_data, "", "Mầm non")
    search_recursive(th_data, "", "TH-THCS-THPT")
    
    # Lọc bớt các node cha nếu nội dung quá dài có thể chiếm hết context
    final_results = []
    seen_paths = set()
    for res in results:
        # Nếu path con đã match, có thể path cha cũng match. 
        # Tạm thời cứ trả về để LLM nhặt thông tin.
        if res["path"] not in seen_paths:
            final_results.append(res)
            seen_paths.add(res["path"])
            
    return {
        "status": "found" if final_results else "not_found",
        "query": query,
        "results": final_results[:15],  # Giới hạn 15 kết quả tránh vượt limit context
        "total_results": len(final_results)
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
