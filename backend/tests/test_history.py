import requests
import json
import time

def test_history():
    url = "http://127.0.0.1:8000/api/chat"
    base_headers = {"Content-Type": "application/json"}
    
    # Message 1
    p1 = {"message": "Xin chào, tôi quan tâm Vinschool", "session_id": "test_hist_1"}
    r1 = requests.post(url, json=p1, headers=base_headers)
    print("M1:", r1.json().get('response'))
    time.sleep(1)
    
    # Message 2
    p2 = {"message": "Tôi vừa hỏi bạn gì vậy?", "session_id": "test_hist_1"}
    r2 = requests.post(url, json=p2, headers=base_headers)
    print("M2:", r2.json().get('response'))

if __name__ == "__main__":
    test_history()
