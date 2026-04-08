# SPEC Draft — Nhom12

## Track: VinUni – Vinschool

---

## 1. Problem Statement

Vinschool cung cấp đầy đủ thông tin tuyển sinh như chương trình học, cơ sở, học phí và quy chế, nhưng các thông tin này còn phân tán trên nhiều trang, khiến phụ huynh mất thời gian tìm kiếm và khó xác định bước tiếp theo.  

Đề tài đề xuất xây dựng **AI Admissions Copilot** nhằm hỗ trợ phụ huynh tra cứu thông tin tuyển sinh theo cách hội thoại, từ đó nhanh chóng xác định chương trình phù hợp, cơ sở phù hợp và hành động tiếp theo như xem học phí hoặc đăng ký tuyển sinh.

---

## 2. Canvas Draft

| | Value | Trust | Feasibility |
|---|-------|-------|-------------|
| **Phân tích** | Đối tượng chính là phụ huynh đang tìm hiểu tuyển sinh cho con. AI giúp giảm thời gian tìm kiếm, cá nhân hóa thông tin và định hướng nhanh hơn trong giai đoạn đầu của hành trình tuyển sinh. | Nếu chatbot trả lời sai về chương trình, cơ sở hoặc thông tin tuyển sinh, phụ huynh có thể mất niềm tin. Vì vậy, câu trả lời cần bám vào nguồn chính thức (luôn gắn link chính thức) và luôn có phương án chuyển sang tư vấn viên khi cần. | Hệ thống có thể triển khai bằng kiến trúc RAG dựa trên dữ liệu từ website. Chi phí thấp, thời gian phản hồi nhanh, phù hợp để xây dựng MVP trong khuôn khổ hackathon. |

### Auto hay Aug?

**Augmentation.**  
Chatbot chỉ đóng vai trò hỗ trợ tư vấn ban đầu và điều hướng thông tin; quyết định cuối cùng vẫn thuộc về phụ huynh hoặc tư vấn viên.

### Learning Signal

Hệ thống học từ hành vi thực tế của người dùng, bao gồm việc chấp nhận gợi ý, chỉnh sửa lại thông tin hoặc rời phiên sớm. Các tín hiệu này được dùng để gán nhãn tự động và cải thiện dần khả năng hiểu nhu cầu cũng như chất lượng gợi ý của hệ thống.

---

## Hướng đi chính

- **Prototype:**  
  Xây dựng chatbot tư vấn tuyển sinh theo flow ngắn, tập trung vào decision nhanh:
  1. Hỏi 2–3 câu chính: độ tuổi của học sinh, khu vực quan tâm (có thể thêm mục tiêu học tập nếu cần)  
  2. Xử lý:  
     - Mapping độ tuổi → cấp học (mầm non / tiểu học / THCS / THPT)  
     - Matching khu vực → cơ sở phù hợp  
  3. Output:  
     - Gợi ý 1–2 chương trình phù hợp  
     - Gợi ý cơ sở gần  
     - CTA rõ ràng: “xem học phí”, “xem quy chế”, “đăng ký tuyển sinh”  
  Chatbot ưu tiên trả lời ngắn gọn, có quick replies và luôn kèm nguồn chính thức.

- **Eval:**  
  - Recommendation precision (đúng chương trình/cơ sở) ≥ 85%  
  - Acceptance rate (user click CTA hoặc tiếp tục flow) ≥ 30%  
  - Correction rate (user sửa lại thông tin) ≤ 20%  
  - Latency < 4s  
  Đánh giá chủ yếu dựa trên hành vi người dùng (accept / correct / drop-off) kết hợp test nội bộ.

- **Main failure mode:**  
  1. User hỏi mơ hồ (“trường có tốt không”) → chatbot trả lời chung chung, không actionable  
  2. Mapping sai độ tuổi → cấp học → gợi ý sai chương trình  
  3. Gợi ý đúng nhưng không có CTA rõ → user không biết bước tiếp theo  

  → Hướng xử lý: luôn có bước làm rõ (clarification), validation theo độ tuổi và bắt buộc mỗi câu trả lời phải có CTA cụ thể.

---

## 4. Phân công

- **Nguyễn Bằng Anh:** Xây dựng RAG pipeline (crawl dữ liệu, chunking, retrieval) và chuẩn bị knowledge base.  
- **Bùi Trọng Anh:** Thiết kế conversation flow và phát triển chatbot logic (intent handling, prompting).  
- **Nguyễn Thị Thanh Huyền:** Xây dựng cơ chế evaluation, logging hành vi người dùng và phân tích learning signals.  
- **Đỗ Thị Thùy Trang:** Tích hợp hệ thống, xây dựng API/UI demo và triển khai prototype.  

> Tất cả thành viên cùng tham gia test, debug và tối ưu prompt/hệ thống.