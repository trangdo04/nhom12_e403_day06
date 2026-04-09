"""
ReAct Agent tư vấn tuyển sinh Vinschool
Sử dụng LangGraph prebuilt agent với các tools tìm kiếm thông tin
"""

import os
import json
import time
import warnings
from typing import Annotated
from dotenv import load_dotenv

# An cac canh bao Pydantic Serialization noi bo (khong anh huong chuc nang)
warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from langchain.agents import create_agent
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage, HumanMessage

from .tools import search_hoc_phi, search_quy_che, search_thong_tin


# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)


# ============================================================================
# Initialize LLM (Sử dụng OpenAI)
# ============================================================================

def get_llm():
    """Khởi tạo LLM dựa trên LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "gemini").strip().lower()

    if provider == "gemini":
        google_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            raise ValueError("GEMINI_API_KEY/GOOGLE_API_KEY không được set. Vui lòng thêm vào .env")
        return ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite-preview",
            temperature=0.7,
            api_key=google_api_key,
        )

    if provider == "openai":
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY không được set. Vui lòng thêm vào .env")
        return ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key=openai_api_key,
        )

    raise ValueError(f"LLM_PROVIDER không hợp lệ: {provider}. Hãy chọn 'gemini' hoặc 'openai'.")


# ============================================================================
# Load System Prompt
# ============================================================================

def load_system_prompt():
    """Tải system prompt từ file"""
    prompt_path = os.path.join(
        os.path.dirname(__file__),
        "../prompts/system-prompt.txt"
    )
    
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Lỗi tải system prompt: {e}")
        # Return default prompt nếu không tìm thấy file
        return """Bạn là một chuyên gia tư vấn tuyển sinh của Vinschool.
Hãy sử dụng các tools để tìm kiếm thông tin và cung cấp tư vấn chi tiết.
Luôn sử dụng tiếng Việt và thân thiện với khách hàng."""


# ============================================================================
# Create ReAct Agent
# ============================================================================

def create_advisor_agent():
    """
    Tạo ReAct agent tư vấn tuyển sinh
    
    Returns:
        graph: Compiled LangGraph agent
    """
    llm = get_llm()
    system_prompt = load_system_prompt()
    
    # Định nghĩa các tools
    tools = [search_hoc_phi, search_quy_che, search_thong_tin]
    
    # Tạo ReAct agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
    )
    
    return agent


# ============================================================================
# Agent Invocation - Synchronous
# ============================================================================

def invoke_advisor(query: str, conversation_history: list = None, max_retries: int = 2) -> dict:
    """
    Gọi agent tư vấn tuyển sinh (Synchronous)
    
    Args:
        query: Câu hỏi từ người dùng
        conversation_history: Lịch sử hội thoại (list messages)
        max_retries: Số lần thử lại khi bị rate limit tạm thời
    
    Returns:
        dict với các trường:
        - response: Câu trả lời từ agent
        - messages: Toàn bộ messages trong conversation
        - tool_calls: Danh sách tools được gọi
        - error: Thông báo lỗi (nếu có)
    """
    agent = create_advisor_agent()
    
    # Chuẩn bị messages
    messages = conversation_history or []
    messages.append(HumanMessage(content=query))
    
    # Invoke agent với retry cho rate limit tạm thời
    state = {"messages": messages}
    last_error = None

    for attempt in range(max_retries + 1):
        try:
            result = agent.invoke(state)

            # Extract response
            response_message = result["messages"][-1]
            content = response_message.content if hasattr(response_message, 'content') else ""

            # Xu ly ca hai truong hop: content la string hoac list of parts
            # (cac model Gemini moi hon tra ve list [{"type": "text", "text": "..."}])
            if isinstance(content, list):
                response_text = "".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                ).strip()
            elif isinstance(content, str):
                response_text = content
            else:
                response_text = str(content)

            # Track tool calls
            tool_calls = []
            for msg in result["messages"]:
                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                    tool_calls.extend([call.get('name', 'unknown') for call in msg.tool_calls])

            return {
                "response": response_text,
                "messages": result["messages"],
                "tool_calls": tool_calls,
                "error": None,
            }

        except Exception as e:
            err_str = str(e)
            last_error = e

            # Hết quota ngày — không retry
            if "RESOURCE_EXHAUSTED" in err_str and "limit: 0" in err_str:
                quota_msg = (
                    "[QUOTA HET] API key da het quota cho hom nay.\n"
                    "Giai phap:\n"
                    "  1. Lay API key moi tai: https://aistudio.google.com/app/apikey\n"
                    "  2. Cap nhat GEMINI_API_KEY trong backend/.env\n"
                    "  3. Hoac doi den 7:00 sang ngay mai (reset theo UTC)"
                )
                return {
                    "response": quota_msg,
                    "messages": messages,
                    "tool_calls": [],
                    "error": "QUOTA_EXHAUSTED",
                }

            # Rate limit hoac loi mang tam thoi — retry sau vai giay
            is_rate_limit = "RESOURCE_EXHAUSTED" in err_str
            is_network_err = "ReadError" in err_str or "WinError 10053" in err_str or "ConnectionReset" in err_str
            if (is_rate_limit or is_network_err) and attempt < max_retries:
                wait_sec = 15 * (attempt + 1)
                reason = "Rate limit" if is_rate_limit else "Loi mang"
                print(f"[{reason}] Thu lai sau {wait_sec}s... (lan {attempt + 1}/{max_retries})")
                time.sleep(wait_sec)
                continue

            # Loi khac — nem ra ngay
            raise

    raise last_error

# Global in-memory store for session history
GLOBAL_SESSIONS = {}
MAX_HISTORY_TURNS = 3 # 3 pairs of Human + AI messages

def get_session_history(session_id: str) -> list:
    return GLOBAL_SESSIONS.get(session_id, []).copy()

def save_session_history(session_id: str, human_msg: str, ai_msg: str):
    if session_id not in GLOBAL_SESSIONS:
        GLOBAL_SESSIONS[session_id] = []
    
    # We store the base messages
    from langchain_core.messages import HumanMessage, AIMessage
    GLOBAL_SESSIONS[session_id].append(HumanMessage(content=human_msg))
    GLOBAL_SESSIONS[session_id].append(AIMessage(content=ai_msg))
    
    # Cap history based on MAX_HISTORY_TURNS * 2 (each turn = 1 human + 1 AI msg)
    if len(GLOBAL_SESSIONS[session_id]) > MAX_HISTORY_TURNS * 2:
        GLOBAL_SESSIONS[session_id] = GLOBAL_SESSIONS[session_id][-(MAX_HISTORY_TURNS * 2):]

def run_agent(message: str, session_id: str = "anonymous") -> dict:
    """Hàm wrapper để tương thích với main.py với lưu vết history."""
    history = get_session_history(session_id)
    result = invoke_advisor(message, history)
    
    # Cập nhật lịch sử
    if result and result.get("response") and result.get("error") != "QUOTA_EXHAUSTED":
        save_session_history(session_id, message, result["response"])
        
    return result


# ============================================================================
# Agent Invocation - Streaming (cho chat UI)
# ============================================================================

def invoke_advisor_stream(query: str, session_id: str = "anonymous"):
    """
    Gọi agent với streaming (tối ưu cho chat UI) có lưu lịch sử 3 tin nhắn gần nhất
    
    Args:
        query: Câu hỏi từ người dùng
        session_id: ID phiên hội thoại để lưu vết context
    
    Yields:
        Streaming events trực tiếp từ agent
    """
    agent = create_advisor_agent()
    
    messages = get_session_history(session_id)
    messages.append(HumanMessage(content=query))
    
    state = {"messages": messages}
    full_ai_response = ""
    
    # Stream events
    for event in agent.stream(state, stream_mode="messages"):
        chunk = event[0] if isinstance(event, tuple) else event
        if hasattr(chunk, "type") and chunk.type not in ("tool", "human") and not getattr(chunk, "tool_call_chunks", None):
            content = getattr(chunk, "content", "")
            if isinstance(content, str):
                full_ai_response += content
            elif isinstance(content, list):
                text = "".join(
                    p.get("text", "") if isinstance(p, dict) else str(p)
                    for p in content
                )
                full_ai_response += text
                
        yield event

    if full_ai_response:
        save_session_history(session_id, query, full_ai_response)


# ============================================================================
# Conversation Manager - Quản lý hội thoại
# ============================================================================

class ConversationManager:
    """Quản lý hội thoại với agent"""
    
    def __init__(self):
        self.messages = []
        self.agent = create_advisor_agent()
    
    def add_user_message(self, content: str):
        """Thêm tin nhắn từ người dùng"""
        self.messages.append(HumanMessage(content=content))
    
    def get_agent_response(self) -> str:
        """Lấy phản hồi từ agent"""
        state = {"messages": self.messages}
        result = self.agent.invoke(state)
        
        # Cập nhật messages với kết quả mới
        self.messages = result["messages"]
        
        # Return agent's response (tin nhắn cuối cùng)
        last_message = self.messages[-1]
        return last_message.content if hasattr(last_message, 'content') else str(last_message)
    
    def chat(self, user_message: str) -> str:
        """
        Thực hiện một lượt hội thoại
        
        Args:
            user_message: Tin nhắn từ người dùng
        
        Returns:
            Phản hồi từ agent
        """
        self.add_user_message(user_message)
        return self.get_agent_response()
    
    def clear_history(self):
        """Xóa lịch sử hội thoại"""
        self.messages = []
    
    def get_history(self):
        """Lấy toàn bộ lịch sử hội thoại"""
        return self.messages


# ============================================================================
# Main - Test agent
# ============================================================================

if __name__ == "__main__":
    print("Vinschool Admissions Advisor - Testing")
    print("=" * 60)
    
    # Test 1: Single invocation
    print("\nTest 1: Single query")
    result = invoke_advisor("Toi muon biet ve do tuoi tuyen sinh lop 1")
    print("\nAgent Response:")
    print(result["response"])
    if result.get("error") == "QUOTA_EXHAUSTED":
        print("\n[!] De chay lai: cap nhat API key trong backend/.env")
    elif result["tool_calls"]:
        print(f"\nTools duoc su dung: {result['tool_calls']}")
    
    if result.get("error"):
        print("\n[SKIP] Bo qua Test 2 do API key het quota.")
    else:
        # Test 2: Conversation Manager
        print("\n" + "=" * 60)
        print("Test 2: Multi-turn conversation")
        manager = ConversationManager()
        
        questions = [
            "Vinschool co nhung chuong trinh dac biet nao?",
            "Ho so can thiet la gi de tuyen sinh tieu hoc?",
            "Hoc phi bao nhieu?"
        ]
        
        for q in questions:
            print(f"\nUser: {q}")
            response = manager.chat(q)
            print(f"\nAgent: {response}")
            print("-" * 60)
