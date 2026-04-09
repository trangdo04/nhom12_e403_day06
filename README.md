# Vinschool Admissions Copilot

AI chatbot tư vấn tuyển sinh Vinschool — giúp phụ huynh tìm **chương trình** và **cơ sở** phù hợp với con chỉ trong vài câu hỏi.

---

## Tính năng

- Nhận câu hỏi tự nhiên (tiếng Việt) về tuyển sinh
- Tự động xác định cấp học phù hợp theo độ tuổi
- Gợi ý cơ sở Vinschool theo khu vực
- Sinh câu trả lời tự nhiên bằng LLM (Gemini / OpenAI)
- Hiển thị nút CTA: xem học phí, đăng ký, liên hệ

---

## Cấu trúc dự án

```
Nhom12-E403-Day06/
├── backend/                        # Python + FastAPI
│   ├── main.py                     # API server (3 endpoints)
│   ├── requirements.txt
│   ├── .env.example                # Mẫu biến môi trường
│   ├── agent/
│   │   ├── agent.py                # Điều phối toàn bộ flow
│   │   ├── extractor.py            # LLM trích xuất tuổi, khu vực, intent
│   │   ├── rules.py                # Rule: tuổi → cấp học, khu vực → cơ sở
│   │   └── responder.py            # LLM sinh câu trả lời tự nhiên
│   ├── services/
│   │   └── llm.py                  # Wrapper gọi Gemini hoặc OpenAI
│   └── data/
│       └── knowledge_base.json     # Dữ liệu: cơ sở, chương trình, CTA
│
└── frontend/                       # Next.js 15 + Tailwind CSS
    ├── app/
    │   ├── layout.tsx
    │   ├── page.tsx                # Trang chính
    │   └── globals.css
    ├── components/
    │   ├── ChatWidget.tsx          # Nút chat nổi góc phải màn hình
    │   ├── ChatWindow.tsx          # Cửa sổ chat, quản lý state
    │   ├── MessageBubble.tsx       # Bubble tin nhắn user / assistant
    │   ├── QuickReplies.tsx        # Gợi ý câu hỏi nhanh
    │   └── ResultCard.tsx          # Card kết quả + nút CTA
    ├── services/
    │   └── api.ts                  # Gọi backend, log hành vi
    └── .env.example
```

---

## Cài đặt và chạy local

### Yêu cầu

- Python 3.10+
- Node.js 18+
- Gemini API Key (miễn phí tại [aistudio.google.com](https://aistudio.google.com/app/apikey))

---

### Backend

```bash
# 1. Activate virtual environment
venv\Scripts\activate          # Windows
# hoặc: source venv/bin/activate   # macOS/Linux

# 2. Cài dependencies
pip install -r backend/requirements.txt

# 3. Tạo file .env
cp backend/.env.example backend/.env
# Mở backend/.env và điền GEMINI_API_KEY

# 4. Chạy server
uvicorn backend.main:app --reload --port 8000
```

API sẵn sàng tại `http://localhost:8000`

---

### Frontend

```bash
# 1. Cài dependencies
cd frontend
npm install

# 2. Tạo file biến môi trường
cp .env.example .env.local
# Mặc định trỏ về http://localhost:8000, không cần sửa khi chạy local

# 3. Chạy dev server
npm run dev
```

Mở trình duyệt tại `http://localhost:3000`

