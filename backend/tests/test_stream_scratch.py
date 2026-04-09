import sys
import os
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.append(backend_dir)
from agent.agent import create_advisor_agent
from langchain_core.messages import HumanMessage

def test_stream():
    agent = create_advisor_agent()
    state = {"messages": [HumanMessage(content="Chào")]}
    for event in agent.stream(state, stream_mode="messages"):
        print(repr(event), type(event))

if __name__ == "__main__":
    test_stream()
