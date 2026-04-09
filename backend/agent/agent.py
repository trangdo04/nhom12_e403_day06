"""
ReAct Agent tư vấn tuyển sinh Vinschool
Sử dụng LangGraph prebuilt agent với các tools tìm kiếm thông tin
"""

import os
import json
from typing import Annotated
from dotenv import load_dotenv

from langchain.google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from langchain.agents import create_agent
from langgraph.graph import MessagesState
from langchain_core.messages import BaseMessage, HumanMessage

from agent.tools import search_hoc_phi, search_quy_che, search_thong_tin


# Load environment variables
load_dotenv()


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
            model="gemini-2.5-flash-lite",
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
        print(f"⚠️  Lỗi tải system prompt: {e}")
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

def invoke_advisor(query: str, conversation_history: list = None) -> dict:
    """
    Gọi agent tư vấn tuyển sinh (Synchronous)
    
    Args:
        query: Câu hỏi từ người dùng
        conversation_history: Lịch sử hội thoại (list messages)
    
    Returns:
        dict với các trường:
        - response: Câu trả lời từ agent
        - messages: Toàn bộ messages trong conversation
        - tool_calls: Danh sách tools được gọi
    """
    agent = create_advisor_agent()
    
    # Chuẩn bị messages
    messages = conversation_history or []
    messages.append(HumanMessage(content=query))
    
    # Invoke agent
    state = {"messages": messages}
    result = agent.invoke(state)
    
    # Extract response
    response_message = result["messages"][-1]
    response_text = response_message.content if hasattr(response_message, 'content') else str(response_message)
    
    # Track tool calls
    tool_calls = []
    for msg in result["messages"]:
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            tool_calls.extend([call.get('name', 'unknown') for call in msg.tool_calls])
    
    return {
        "response": response_text,
        "messages": result["messages"],
        "tool_calls": tool_calls
    }


def run_agent(message: str, conversation_history: list = None) -> dict:
    """Hàm wrapper để tương thích với main.py."""
    return invoke_advisor(message, conversation_history)


# ============================================================================
# Agent Invocation - Streaming (cho chat UI)
# ============================================================================

def invoke_advisor_stream(query: str, conversation_history: list = None):
    """
    Gọi agent với streaming (tối ưu cho chat UI)
    
    Args:
        query: Câu hỏi từ người dùng
        conversation_history: Lịch sử hội thoại
    
    Yields:
        Streaming events trực tiếp từ agent
    """
    agent = create_advisor_agent()
    
    messages = conversation_history or []
    messages.append(HumanMessage(content=query))
    
    state = {"messages": messages}
    
    # Stream events
    for event in agent.stream(state, stream_mode="values"):
        yield event


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
    print("🤖 Vinschool Admissions Advisor - Testing")
    print("=" * 60)
    
    # Test 1: Single invocation
    print("\n📝 Test 1: Single query")
    result = invoke_advisor("Tôi muốn biết về độ tuổi tuyển sinh lớp 1")
    print("\nAgent Response:")
    print(result["response"])
    if result["tool_calls"]:
        print(f"\n🔧 Tools được sử dụng: {result['tool_calls']}")
    
    # Test 2: Conversation Manager
    print("\n" + "=" * 60)
    print("📝 Test 2: Multi-turn conversation")
    manager = ConversationManager()
    
    questions = [
        "Vinschool có những chương trình đặc biệt nào?",
        "Hồ sơ cần thiết là gì để tuyển sinh tiểu học?",
        "Học phí bao nhiêu?"
    ]
    
    for q in questions:
        print(f"\n👤 User: {q}")
        response = manager.chat(q)
        print(f"\n🤖 Agent: {response}")
        print("-" * 60)
