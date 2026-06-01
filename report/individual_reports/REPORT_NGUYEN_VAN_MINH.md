# Báo Cáo Cá Nhân: Lab 3 - Chatbot vs ReAct Agent

- **Họ và Tên**: Nguyễn Văn Minh
- **Mã Số Sinh Viên**: 2A202600556
- **Ngày Thực Hiện**: 2026-06-01

---

## I. Phần Việc Tự Làm (Technical Contribution - 15 Điểm)

Trong bài tập nhóm lần này, tôi chịu trách nhiệm chính về phần **Lập trình lõi Agent và kỹ nghệ gợi ý (Prompt Engineering)**:

1. **Viết vòng lặp ReAct (`run` method):**
   - Viết code chính cho vòng lặp ReAct trong file [agent.py](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/src/agent/agent.py) để Agent lặp đi lặp lại các bước: tự suy nghĩ (Thought) -> tự gọi Action -> nhận Observation từ Python.
   - Thiết lập trang nháp (`scratchpad`) ghi nhớ lịch sử chạy để Agent không bị lặp vô hạn và biết mình đang làm đến đâu.
   - Viết các biểu thức Regex thông minh để bóc tách hành động và tham số của Agent, xử lý tốt cả định dạng tham số kiểu JSON và kiểu gán biến thông thường.

2. **Kỹ nghệ gợi ý & Tối ưu hóa System Prompt:**
   - Xây dựng hàm prompt hệ thống `get_system_prompt` định hình vai trò của Marketing Agent.
   - Nâng cấp prompt từ phiên bản v1 lỏng lẻo lên phiên bản **Prompt v2 (Strict ReAct)** thêm bộ luật cưỡng chế bắt buộc Agent phải gọi tool thật và cấm tự bịa kết quả.

---

## II. Phân Tích Lỗi Gặp Phải (Debugging Case Study - 10 Điểm)

### 1. Lỗi gặp phải là gì?
Khi chạy Agent phiên bản v1 với yêu cầu marketing đầy đủ, con AI sau khi tìm kiếm group đã tự ý bỏ qua tool viết bài đăng (`generate_content`) và tool lên lịch (`schedule_post`). Nó tự viết bài quảng cáo và tự thông báo "đã lên lịch đăng lúc 8h tối thành công" trong câu trả lời cuối cùng (`Final Answer`) mà không chạy code Python nghiệp vụ thật.

### 2. Dòng Log lỗi thực tế
Trích từ file log hệ thống [2026-06-01.log](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/logs/2026-06-01.log):
```json
{"timestamp": "2026-06-01T08:29:50.627537", "event": "LLM_CALL_START", "data": {"step": 2}}
{"timestamp": "2026-06-01T08:29:59.814849", "event": "LLM_CALL_END", "data": {"step": 2, ...}}
{"timestamp": "2026-06-01T08:29:59.816469", "event": "AGENT_END", "data": {"steps": 2, "success": true}}
```
*Nhận xét:* Agent kết thúc chương trình sớm ở Step 2, chỉ gọi đúng 2 tool đầu và bỏ qua hoàn toàn bước chạy code viết bài và lên lịch đăng bài.

### 3. Tại sao bị lỗi này?
Do Prompt v1 viết chưa đủ chặt chẽ và nghiêm khắc. Con LLM nhận thấy việc tự nó nghĩ ra bài viết thì nhanh hơn là phải gọi hàm Python chạy tiếp, nên nó đã đi đường tắt (Shortcut) để tối ưu hóa năng lượng.

### 4. Cách sửa lỗi
Tôi đã nâng cấp System Prompt lên bản **Prompt v2**, thêm phần `QUY TẮC BẮT BUỘC` cấm tuyệt đối tự bịa thông tin và bắt buộc phải gọi tool khi có công cụ hỗ trợ. Kết quả là ở lần chạy sau, Agent đã chạy rất kỷ luật và gọi đầy đủ cả 5 công cụ Python một cách tuần tự.

---

## III. Chiêm Nghiệm Cá Nhân: Chatbot vs ReAct (10 Điểm)

1. **Về khả năng suy nghĩ (Reasoning):**
   Vòng lặp ReAct giúp con LLM có cơ hội tự suy nghĩ và tự sửa lỗi. Bước nháp `Thought` giúp nó chia nhỏ công việc phức tạp thành các bước nhỏ dễ làm, giúp kết quả đầu ra vô cùng chính xác thay vì hứa hẹn suông giống như Chatbot thường.

2. **Về độ tin cậy (Reliability):**
   Mặc dù ReAct Agent rất mạnh mẽ nhưng nó phụ thuộc hoàn toàn vào bộ Parser (Regex bóc tách lệnh) và sự chặt chẽ của Prompt. Nếu prompt viết lỏng lẻo, Agent sẽ tự động lách luật để đi đường tắt. Do đó, viết prompt cho Agent cần cực kỳ cẩn thận giống như viết một bản hợp đồng pháp lý vậy.

3. **Về việc nhận phản hồi từ Tool (Observation):**
   Kết quả trả về từ tool (`Observation`) giúp Agent bám sát thực tế. Nó biết được kết quả khách quan ngoài đời thực ra sao để tiếp tục suy luận cho bước sau, không bị lạc lối trong không gian suy nghĩ mơ hồ.

---

## IV. Đề Xuất Cải Tiến Trong Tương Lai (5 Điểm)

1. **Khả năng mở rộng (Scalability):**
   Dùng cấu trúc xuất dữ liệu JSON định hình sẵn của OpenAI (Structured Outputs) thay vì bóc tách text bằng Regex để đảm bảo hệ thống chạy tin cậy 100%, không bao giờ bị lỗi cú pháp khi chạy thực tế.

2. **An toàn bảo mật (Safety):**
   Tích hợp hệ thống lọc sắc thái ngôn ngữ trực tiếp vào System Prompt để ngăn chặn Agent viết ra các nội dung bài đăng tiêu cực, vi phạm pháp luật hoặc tiêu chuẩn quảng cáo.

3. **Hiệu năng hệ thống (Performance):**
   Tối giản hóa mô tả tool trong System Prompt để giảm số lượng Prompt Tokens tiêu thụ trong các vòng lặp ReAct, giúp giảm tối đa chi phí vận hành hệ thống.
