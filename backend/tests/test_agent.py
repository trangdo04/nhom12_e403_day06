import os
from unittest.mock import ANY, MagicMock, patch

import pytest

from agent.agent import create_advisor_agent, get_llm, invoke_advisor, run_agent


def test_get_llm_gemini(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")

    with patch("agent.agent.ChatGoogleGenerativeAI") as mock_gemini:
        mock_instance = MagicMock()
        mock_gemini.return_value = mock_instance

        llm = get_llm()

        mock_gemini.assert_called_once_with(
            model="gemini-3.1-flash-lite-preview",
            temperature=0.7,
            api_key="test-gemini-key",
        )
        assert llm is mock_instance


def test_get_llm_openai(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-openai-key")

    with patch("agent.agent.ChatOpenAI") as mock_openai:
        mock_instance = MagicMock()
        mock_openai.return_value = mock_instance

        llm = get_llm()

        mock_openai.assert_called_once_with(
            model="gpt-4o-mini",
            temperature=0.7,
            api_key="test-openai-key",
        )
        assert llm is mock_instance


def test_get_llm_invalid_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "invalid_provider")

    with pytest.raises(ValueError, match="LLM_PROVIDER không hợp lệ"):
        get_llm()


def test_create_advisor_agent_uses_tools_and_system_prompt(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini-key")

    with patch("agent.agent.get_llm", return_value="fake-llm") as mock_get_llm, patch(
        "agent.agent.create_agent"
    ) as mock_create_agent:
        mock_create_agent.return_value = MagicMock()

        agent = create_advisor_agent()

        mock_get_llm.assert_called_once()
        mock_create_agent.assert_called_once_with(
            model="fake-llm",
            tools=[ANY, ANY, ANY],
            system_prompt=ANY,
        )
        assert agent is mock_create_agent.return_value


def test_invoke_advisor_returns_response_and_tool_calls(monkeypatch):
    fake_agent = MagicMock()
    fake_agent.invoke.return_value = {
        "messages": [MagicMock(content="Hello"), MagicMock(content="Hi")]
    }

    with patch("agent.agent.create_advisor_agent", return_value=fake_agent):
        result = invoke_advisor("Xin chào")

    assert result["response"] == "Hi"
    assert result["messages"] == fake_agent.invoke.return_value["messages"]
    assert result["tool_calls"] == []


def test_run_agent_wrapper(monkeypatch):
    fake_result = {"response": "OK"}

    with patch("agent.agent.invoke_advisor", return_value=fake_result) as mock_invoke:
        result = run_agent("Xin chào")

    mock_invoke.assert_called_once_with("Xin chào", None)
    assert result == fake_result
