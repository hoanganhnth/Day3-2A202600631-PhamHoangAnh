# Báo Cáo Cá Nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và Tên**: Phạm Hoàng Anh
- **Mã Số Sinh Viên**: 2A202600631
- **Ngày Thực Hiện**: 2026-06-01

---

## I. Phần Việc Tự Làm (Technical Contribution - 15 Điểm)

Trong bài tập nhóm lần này, tôi chịu trách nhiệm chính về phần **Tạo công cụ (Tool Design), Kết nối mô hình và Viết code đo đạc hiệu năng (Telemetry)**:

1. **Thiết kế và viết code 5 công cụ Python (Phase 1):**
   - Viết code cho file [marketing_tools.py](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/src/tools/marketing_tools.py) định nghĩa 5 công cụ của dự án: `analyze_product` (phân tích sản phẩm), `discover_groups` (tìm group Facebook), `generate_content` (tự viết bài đăng), `schedule_post` (lên lịch đăng) và `get_analytics` (đo lường hiệu quả).
   - Mô tả cực kỳ chi tiết các tham số đầu vào và chức năng bằng tiếng Việt dễ hiểu để mô hình AI đọc và hiểu chính xác cách gọi hàm Python.

2. **Viết script tự động phân tích logs (Phase 5):**
   - Lập trình file [parse_logs.py](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/parse_logs.py) ở thư mục gốc để tự động đọc toàn bộ lịch sử chạy trong thư mục `logs/`. 
   - Script tự động tính toán ra thời gian chạy trung bình (Latency), số lượng Token tiêu thụ và vẽ ra bảng so sánh kết quả giữa Chatbot thường với Agent để nhóm đưa vào báo cáo.

---

## II. Phân Tích Lỗi Gặp Phải (Debugging Case Study - 10 Điểm)

### 1. Lỗi gặp phải là gì?
Ở phiên bản chạy thử đầu tiên của Agent v1, khi tôi nhập yêu cầu marketing phức tạp, Agent chỉ chạy đúng 2 bước đầu là phân tích sản phẩm và tìm group. Đến bước viết bài và lên lịch đăng, nó **tự ý bỏ qua không chạy tool** `generate_content` và `schedule_post`. Nó tự viết bài văn và tự thông báo "đặt lịch thành công" luôn trong phần kết luận.

### 2. Dòng Log lỗi thực tế
Tôi mở file log [2026-06-01.log](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/logs/2026-06-01.log) và thấy:
```json
{"timestamp": "2026-06-01T08:29:49.550749", "event": "LLM_CALL_START", "data": {"step": 1}}
{"timestamp": "2026-06-01T08:29:50.627126", "event": "TOOL_CALL", "data": {"tool": "discover_groups", "args": {"keywords": "IELTS, TOEIC"}}}
{"timestamp": "2026-06-01T08:29:50.627346", "event": "TOOL_OBSERVATION", "data": {"tool": "discover_groups", "observation": "[...]"}}
{"timestamp": "2026-06-01T08:29:50.627537", "event": "LLM_CALL_START", "data": {"step": 2}}
{"timestamp": "2026-06-01T08:29:59.814849", "event": "LLM_CALL_END", "data": {"step": 2, ...}}
{"timestamp": "2026-06-01T08:29:59.816469", "event": "AGENT_END", "data": {"steps": 2, "success": true}}
```
*Giải thích:* Lịch sử cho thấy Agent chỉ chạy đúng 2 tool rồi dừng chương trình ở Step 2 luôn, bỏ qua hoàn toàn bước chạy code Python viết bài và lên lịch.

### 3. Tại sao bị lỗi này?
Do cấu trúc Prompt v1 hệ thống viết còn lỏng lẻo, chưa ép buộc con AI phải tuân thủ kỷ luật. Con LLM nhận ra việc tự nó nghĩ ra bài viết thì nhanh hơn là phải gọi hàm Python chạy, nên nó đã đi đường tắt cho rảnh việc.

### 4. Cách sửa lỗi
Chúng tôi đã cùng nhau nâng cấp System Prompt lên bản **Prompt v2**. Tôi đã thêm vào mục `QUY TẮC BẮT BUỘC` cấm tuyệt đối việc tự bịa thông tin và bắt buộc phải gọi tool khi có công cụ tương ứng. Nhờ vậy ở lần chạy sau, Agent đã chạy đầy đủ và nghiêm túc cả 5 công cụ.

---

## III. Chiêm Nghiệm Cá Nhân: Chatbot vs ReAct (10 Điểm)

1. **Về khả năng suy nghĩ (Reasoning):**
   Khối suy nghĩ `Thought` hoạt động giống như một trang nháp giúp con AI bình tĩnh chia nhỏ bài toán khó thành các bước dễ. Việc này giúp nó không bị rối và không bị nói bừa giống như khi dùng Chatbot thường.

2. **Về độ tin cậy (Reliability):**
   Agent sẽ chạy **tệ hơn** Chatbot thường khi gặp các câu hỏi siêu đơn giản (như *"Bạn tên là gì?"*). Với các câu này, dùng Agent rất tốn thời gian và tốn tiền API vì prompt hệ thống quá dài và phải chạy qua vòng lặp phức tạp không cần thiết, trong khi Chatbot chỉ cần 1 giây để trả lời trực tiếp.

3. **Về việc nhận phản hồi từ Tool (Observation):**
   Kết quả trả về từ tool (`Observation`) giúp Agent bám sát thực tế. Nó biết được môi trường ngoài đời thực ra sao (ví dụ: tìm được group nào) để lấy thông tin đó làm bàn đạp suy nghĩ cho bước tiếp theo, giúp kết quả vô cùng chính xác.

---

## IV. Đề Xuất Cải Tiến Trong Tương Lai (5 Điểm)

Để mang hệ thống Marketing này ra thực tế chạy thương mại, tôi đề xuất 3 ý tưởng:

1. **Khả năng mở rộng (Scalability):**
   Thay thế các công cụ giả lập bằng API thật của Facebook, LinkedIn. Dùng hàng đợi Celery chạy ngầm dưới nền để Agent không bị treo khi chờ cào dữ liệu hoặc chờ đăng bài lên mạng xã hội.

2. **An toàn bảo mật (Safety):**
   Dùng Pydantic để kiểm tra và lọc sạch dữ liệu đầu vào mà Agent parse ra trước khi nạp vào Python chạy, tránh bị hack hoặc crash hệ thống.

3. **Tối ưu chi phí (Performance):**
   Khi có hàng trăm công cụ khác nhau, chúng tôi sẽ dùng Vector DB (như ChromaDB) để tìm kiếm và chỉ chèn 5 công cụ liên quan nhất vào prompt, tránh làm quá tải bộ nhớ Agent và tiết kiệm tiền API.
