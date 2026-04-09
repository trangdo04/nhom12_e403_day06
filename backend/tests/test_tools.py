from agent.tools import search_hoc_phi, search_quy_che, search_thong_tin


def test_search_hoc_phi_returns_no_data():
    # LangChain @tool tạo ra StructuredTool, cần gọi qua .invoke()
    result = search_hoc_phi.invoke({"query": "học phí tiểu học"})

    assert result["status"] == "no_data"
    assert result["data"] is None
    assert "hotline" in result["contact"]
    assert result["contact"]["hotline"] == "18006511"


def test_search_quy_che_finds_known_term():
    result = search_quy_che.invoke({"query": "mầm non"})

    assert result["status"] == "found"
    assert result["total_results"] > 0
    assert any(
        "mầm non" in str(item.get("content", "")).lower()
        or "mầm non" in str(item.get("value", "")).lower()
        for item in result["results"]
    )


def test_search_quy_che_returns_not_found_for_random_query():
    result = search_quy_che.invoke({"query": "zzz_nonexistent_query_123"})

    assert result["status"] == "not_found"
    assert result["total_results"] == 0


def test_search_thong_tin_finds_ai_term_in_features():
    result = search_thong_tin.invoke({"query": "AI", "category": "features"})

    assert result["status"] == "found"
    assert result["category"] == "features"
    assert result["total_results"] > 0
    assert all(item["category"] == "features" for item in result["results"])


def test_search_thong_tin_returns_available_categories():
    result = search_thong_tin.invoke({"query": "tuyển sinh"})

    assert "available_categories" in result
    assert set(result["available_categories"]) == {"overview", "features", "achievements", "admission"}
