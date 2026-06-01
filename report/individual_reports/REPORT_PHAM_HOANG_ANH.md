# Individual Report: Lab 3 - Chatbot vs ReAct Agent

- **Student Name**: Phạm Hoàng Anh
- **Student ID**: 2A202600631
- **Date**: 2026-06-01

---

## I. Technical Contribution (15 Points)

Trong bài Lab này, tôi chịu trách nhiệm chính về mặt thiết kế công cụ (Tool Design), xây dựng cơ chế giám sát (Telemetry) và viết bộ phân tích dữ liệu tự động cho nhóm:

1. **Thiết kế và Hiện thực hóa 5 Công cụ Marketing (Phase 1):**
   - Lập trình file [marketing_tools.py](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/src/tools/marketing_tools.py) định nghĩa 5 công cụ lõi của MVP AI Marketing Agent: `analyze_product` (Phân tích sản phẩm), `discover_groups` (Tìm kiếm group), `generate_content` (Tạo nội dung marketing), `schedule_post` (Lên lịch đăng bài) và `get_analytics` (Lấy dữ liệu hiệu quả).
   - Thiết kế lược đồ tham số chi tiết dưới dạng JSON Schema tương thích OpenAI style và tối ưu hóa phần `description` của từng công cụ để LLM hiểu chính xác cách gọi hàm.

2. **Xây dựng Công cụ Phân tích Telemetry Tự động (Phase 5):**
   - Viết tập lệnh [parse_logs.py](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/parse_logs.py) ở thư mục gốc để tự động đọc toàn bộ file log dạng JSON cấu trúc từ `logs/`, phân tích và tính toán các chỉ số công nghiệp (Latency, Tokens, Steps, Success Rate) rồi xuất ra bảng so sánh trực quan cho báo cáo nhóm.

---

## II. Debugging Case Study (10 Points)

### 1. Mô tả lỗi phát hiện (Problem Description)
Trong quá trình kiểm thử Agent phiên bản đầu tiên (Agent v1) với câu lệnh marketing phức tạp gồm 5 bước, Agent đã dừng hoạt động sớm ở Step 2 và đưa ra `Final Answer` mà **không hề gọi** hai công cụ quan trọng là `generate_content` và `schedule_post`. Nó tự viết nội dung bài đăng và tự xác nhận là đã lên lịch trong suy nghĩ (Hallucinated execution).

### 2. Log minh chứng (Log Source)
Trích xuất từ file log thực tế [2026-06-01.log](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/logs/2026-06-01.log):
```json
{"timestamp": "2026-06-01T08:29:49.550749", "event": "LLM_CALL_START", "data": {"step": 1}}
{"timestamp": "2026-06-01T08:29:50.627126", "event": "TOOL_CALL", "data": {"tool": "discover_groups", "args": {"keywords": "IELTS, TOEIC"}}}
{"timestamp": "2026-06-01T08:29:50.627346", "event": "TOOL_OBSERVATION", "data": {"tool": "discover_groups", "observation": "[...]"}}
{"timestamp": "2026-06-01T08:29:50.627537", "event": "LLM_CALL_START", "data": {"step": 2}}
{"timestamp": "2026-06-01T08:29:59.814849", "event": "LLM_CALL_END", "data": {"step": 2, ...}}
{"timestamp": "2026-06-01T08:29:59.816469", "event": "AGENT_END", "data": {"steps": 2, "success": true}}
```
*Nhận xét:* Agent chỉ gọi đúng 2 tool (`analyze_product` ở Step 0 và `discover_groups` ở Step 1), sau đó nhảy thẳng tới kết thúc ở Step 2, bỏ qua hoàn toàn các bước còn lại.

### 3. Chẩn đoán nguyên nhân (Diagnosis)
Do System Prompt v1 quá chung chung và thiên về định nghĩa cấu trúc ReAct thô, chưa có các ràng buộc kỷ luật nghiêm ngặt chống hiện tượng tự vượt quyền (Tool Bypass/Lazy Agent). LLM nhận thấy việc tự suy nghĩ và tự viết bài đăng nhanh hơn là gọi Tool nên đã đi đường tắt để tối ưu hóa token.

### 4. Giải pháp khắc phục (Solution)
Tôi đã nâng cấp System Prompt lên phiên bản **Prompt v2** (Strict ReAct), chèn thêm phần `QUY TẮC BẮT BUỘC (CRITICAL RULES)` phân định rõ ràng:
- *Nếu có công cụ tương ứng cho bước làm việc, BẮT BUỘC phải gọi công cụ đó.*
- *Nghiêm cấm việc tự viết nội dung hoặc giả lập kết quả.*
- *Bắt buộc làm tuần tự từng bước một.*

*Kết quả:* Ở lượt chạy thử thứ hai với Prompt v2, Agent đã thực thi đầy đủ và tuần tự cả 4 tool, giải quyết triệt để lỗi bỏ qua tool.

---

## III. Personal Insights: Chatbot vs ReAct (10 Points)

1. **Reasoning (Khả năng suy luận):**
   Khối suy nghĩ `Thought` hoạt động như một "trang giấy nháp" giúp phân rã bài toán phức tạp của người dùng thành các phần nhỏ hơn có cấu trúc rõ ràng. So với Chatbot trả lời trực tiếp dễ bị quá tải ngữ cảnh dẫn đến hallucinate, khối `Thought` giúp LLM định hình chính xác mục tiêu tiếp theo trước khi hành động.

2. **Reliability (Độ tin cậy):**
   Agent sẽ hoạt động **tệ hơn** Chatbot trong các câu hỏi đơn giản (Q&A một bước như *"Bạn là ai?"*, *"Thời tiết hôm nay thế nào?"*). Với những tác vụ này, Agent gây lãng phí tài nguyên lớn vì System Prompt quá nặng, phải trải qua tối thiểu 1 vòng lặp ReAct làm tăng độ trễ (latency) và chi phí API không cần thiết, trong khi Chatbot có thể trả lời trực tiếp lập tức.

3. **Observation (Phản hồi môi trường):**
   Các `Observation` đóng vai trò là chiếc mỏ neo kết nối Agent với thế giới thực. Dữ liệu thực tế nhận được từ môi trường ở bước trước (ví dụ: danh sách group IELTS) là cơ sở dữ liệu thực nghiệm để LLM điều chỉnh bài viết marketing tiếp theo cho phù hợp, loại bỏ hoàn toàn tính mơ hồ và võ đoán của mô hình ngôn ngữ lớn.

---

## IV. Future Improvements (5 Points)

Để đưa hệ thống AI Marketing Agent này lên môi trường Production thực tế, tôi đề xuất 3 cải tiến quan trọng:

1. **Scalability (Khả năng mở rộng):** 
   Thay thế các mock tools bằng các API kết nối trực tiếp đến Graph API của Facebook, LinkedIn API. Triển khai hàng đợi tác vụ bất đồng bộ (ví dụ: Celery với Redis) để chạy các tác vụ cào dữ liệu hoặc đăng bài ngầm mà không gây block luồng chính của Agent.

2. **Safety (An toàn bảo mật):**
   Áp dụng các thư viện kiểm tra dữ liệu đầu vào nghiêm ngặt (như Pydantic) cho các tham số hàm bóc tách được từ LLM để tránh các lỗ hổng Injection. Thiết kế một Agent giám sát (LLM Guardrail/Supervisor) để kiểm tra bài viết được sinh ra trước khi thực hiện đặt lịch nhằm lọc bỏ các nội dung vi phạm tiêu chuẩn cộng đồng.

3. **Performance (Hiệu năng):**
   Khi số lượng công cụ tăng lên hàng trăm (tương tác nhiều mạng xã hội khác nhau), việc đưa tất cả vào System Prompt sẽ làm quá tải ngữ cảnh và tăng chi phí. Cần áp dụng cơ chế **Semantic Tool Retrieval** dùng Vector DB (như ChromaDB/FAISS) để tìm kiếm và chỉ chèn vào prompt Top-5 tool hữu ích nhất với yêu cầu hiện tại của người dùng.
