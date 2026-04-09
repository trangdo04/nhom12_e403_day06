import requests
import json
import sys

def test_stream():
    url = "http://127.0.0.1:8000/api/chat/stream"
    payload = {"message": "cho hỏi độ tuổi lớp 1", "session_id": "test"}
    headers = {"Content-Type": "application/json"}
    
    with requests.post(url, json=payload, headers=headers, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)

if __name__ == "__main__":
    test_stream()
