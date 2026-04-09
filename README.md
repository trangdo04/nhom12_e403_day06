# Vinschool Admissions Copilot

AI chatbot tư vấn tuyển sinh Vinschool — giúp phụ huynh tìm **chương trình** và **cơ sở** phù hợp với con chỉ trong vài câu hỏi.

---

## Tính năng

- Tích hợp **ReAct Agent** cho phép LLM tự động suy luận và tra cứu tool\n- Trải nghiệm mượt mà với **Streaming response** (nhận và gõ chữ thời gian thực)\n- Nhận câu hỏi tự nhiên (tiếng Việt) về tuyển sinh
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
│   └── data/
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

---

## Luồng hoạt động của Agent (Backend)

Hệ thống sử dụng mô hình **ReAct Agent** (Reasoning and Acting) kết hợp **LangGraph** (cấu hình trong `backend/agent/agent.py`).
- **Tiếp nhận Context**: Nhận lịch sử hội thoại 3 tin nhắn gần nhất (Session history) để đảm bảo hiểu thông suốt ngũ cảnh.
- **Suy luận (Reasoning)**: Phân tích câu hỏi của phụ huynh (Ví dụ: "Học phí lớp 1 khoảng bao nhiêu?") nhờ sự trợ giúp của LLM (Google Gemini Flash Lite / OpenAI).
- **Hành động (Acting)**: Tự động quyết định gọi linh hoạt các tools cung cấp sẵn (`search_hoc_phi`, `search_quy_che`, `search_thong_tin`) để tra cứu thông tin định tuyến nội bộ.
- **Phản hồi**: Khớp dữ kiện tìm được, sinh ra câu trả lời dạng văn bản (Streaming) song song đi kèm các thông số trích xuất thô (ví dụ: cấp học, địa chỉ cơ sở) phản hồi về cho Frontend.

---

## Kiến trúc Giao diện UI/UX (Frontend)

Module Front-end sử dụng **Next.js 15 & Tailwind CSS**, đặt mục tiêu tối ưu trải nghiệm người dùng (UX) và tối giản UI:
- **Chat Widget Responsive**: Khung chatbot được thiết kế dạng nút nổi (Floating Widget). Thiết kế `calc(100vw)` tự động thích ứng với mọi giao diện mobile siêu nhỏ (iPhone SE, Galaxy Fold) để tránh hiện tượng tràn viền.
- **Trải nghiệm Streaming Siêu mượt**: 
  - Khóa (disable) tự động khung nhập liệu trong khi AI đang trả lời - ngăn rủi ro Race Condition / Overlapping Streams làm hỏng chuỗi hội thoại.
  - Fix triệt để lỗi loại bỏ khoảng trắng của Gemini để chữ in rõ ràng. Tích hợp cuộn màn hình (`Auto-Scroll`) mềm mại khi tin nhắn tự động dài ra.
  - Ngăn chặn lỗi đẩy tin nhắn sai bởi bộ gõ (Telex/IME keyboard) khi thao tác với phím Enter.
- **Các Module chức năng riêng**: Hệ thống hiển thị độc lập **Result Card** dành riêng cho thông tin cơ sở và cấp học, kết hợp **Quick Replies** và **CTA Buttons** (Xem học phí, Đăng ký ngay) để lôi kéo hiệu suất chuyển đổi cho tư vấn viên.

---

## Giám sát (Monitoring) với LangSmith

Mọi đường đi nước bước (Chain Logic), số lần chạy Tool, độ trễ mạng và số lượng Token tiêu thụ đều được tích hợp tự động lên log nền tảng **LangSmith**.  

Để kích hoạt hệ thống Tracking (đã cấu hình sẵn), bạn chỉ cần bật các biến môi trường trong tệp `backend/.env`:

```bash
export LANGSMITH_TRACING=true
export LANGSMITH_ENDPOINT=https://api.smith.langchain.com
export LANGSMITH_API_KEY=your_langsmith_api_key_here
export LANGSMITH_PROJECT="ai_thuc_chien_lab06"
```
Thông qua Dashboard của LangSmith, nhà phát triển có thể chẩn đoán (Debug) chi tiết xem Agent đang "Suy nghĩ" (`Thoughts`) gì và tại sao lại dùng/không dùng các công cụ (Tools) nào đó.
