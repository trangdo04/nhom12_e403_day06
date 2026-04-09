import os
import json
import google.generativeai as genai
from openai import OpenAI

PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" hoặc "openai"


def _call_gemini(prompt: str) -> str:
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)
    return response.text


def _call_openai(prompt: str) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    return response.choices[0].message.content


def call_llm(prompt: str) -> str:
    if PROVIDER == "openai":
        return _call_openai(prompt)
    return _call_gemini(prompt)


def call_llm_json(prompt: str) -> dict:
    """Gọi LLM và parse kết quả JSON."""
    raw = call_llm(prompt)
    # Xóa markdown code block nếu có
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}
