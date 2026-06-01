# Group Report: Lab 3 - Production-Grade Agentic System

- **Team Name**: Team AI Marketing Agent (Hoàng Anh & Hoàng Long)
- **Team Members**: Phạm Hoàng Anh (2A202600631) & Hoàng Long
- **Deployment Date**: 2026-06-01

---

## 1. Executive Summary

Hệ thống **AI Marketing Agent** được xây dựng nhằm giải quyết bài toán tiếp thị sản phẩm bán tự động một cách thông minh, cá nhân hóa sâu sắc và loại bỏ hành vi spam vô tội vạ trên các mạng xã hội. Bằng cách dịch chuyển từ mô hình Chatbot Baseline truyền thống sang kiến trúc **ReAct Agent** có kiểm soát, hệ thống đã giải quyết thành công các tác vụ lập kế hoạch và thực thi tiếp thị đa bước (multi-step marketing pipelines).

- **Success Rate**: 100% trên các ca thử nghiệm tiếp thị đa bước phức tạp đối với Agent v2 (Strict ReAct), trong khi Chatbot Baseline hoàn toàn thất bại (0% thành công do hallucination/bỏ qua bước thực thi vật lý).
- **Key Outcome**: Agent v2 đã hoàn thành trọn vẹn chuỗi tác vụ: Phân tích sản phẩm -> Tìm kiếm nhóm tiếp thị -> Tạo bài viết cá nhân hóa theo nhóm -> Lên lịch đăng bài tự động bằng việc thực thi chuẩn xác 4 tool nghiệp vụ, tối ưu hóa tài nguyên và ngăn chặn tuyệt đối lỗi bỏ qua tool (Tool Bypass).

---

## 2. System Architecture & Tooling

### 2.1 ReAct Loop Implementation
Kiến trúc Agent tuân thủ nghiêm ngặt mô hình hoạt động **Thought -> Action -> Observation** với trang ghi nhớ tạm thời (`scratchpad history`):

```text
                     ┌──────────────────────────┐
                     │     User Requirement     │
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐
                     │    get_system_prompt()   │
                     └─────────────┬────────────┘
                                   │
                                   ▼
                     ┌──────────────────────────┐  LLM Call
           ┌────────>│   LLM Generates Thought  ├─────────┐
           │         └─────────────┬────────────┘         │
           │                       │                      │
           │                       ▼                      ▼
           │             [Decides to Call Tool]   [Decides to Finish]
           │                       │                      │
           │                       ▼                      ▼
           │             ┌──────────────────┐     ┌───────────────┐
           │             │  Parse Action()  │     │ Final Answer  │
           │             └─────────┬────────┘     └───────────────┘
           │                       │                      │
           │                       ▼                      ▼
  Append Observation     ┌──────────────────┐         [Success]
           │             │  Execute Tool()  │
           └─────────────┤   (Python Run)   │
                         └──────────────────┘
```

### 2.2 Tool Definitions (Inventory)
Chúng tôi thiết kế bộ 5 công cụ nghiệp vụ chi tiết hỗ trợ đắc lực cho quy trình làm việc của Marketing Agent:

| Tool Name | Input Format | Use Case |
| :--- | :--- | :--- |
| `analyze_product` | `{"product_info": "string"}` | Phân tích thông tin sản phẩm để trích xuất Product Profile (nỗi đau, lợi ích, từ khóa). |
| `discover_groups` | `{"keywords": "string"}` | Tìm kiếm và trả về danh sách cộng đồng phù hợp nhất kèm quy mô và chủ đề tương ứng. |
| `generate_content`| `{"product_profile": "string", "target_group": "string", "content_type": "string"}` | Tạo nội dung tiếp thị tùy biến sâu sắc theo nhóm khách hàng mục tiêu và thể loại bài đăng. |
| `schedule_post`   | `{"content": "string", "platform": "string", "time": "string"}` | Thực hiện tác vụ vật lý lên lịch đăng bài trên nền tảng mạng xã hội được chỉ định. |
| `get_analytics`   | `{"post_id": "string"}` | Lấy các chỉ số thống kê hiệu năng (views, clicks, conversions, CTR) của bài đăng. |

### 2.3 LLM Providers Used
- **Primary**: OpenAI GPT-4o (Được sử dụng chính cho việc lập luận phức tạp, phân tích cấu trúc ngữ pháp và gọi tool).
- **Secondary (Backup)**: Google Gemini 1.5 Flash (Dự phòng cho các tác vụ cần độ trễ thấp và xử lý khối lượng dữ liệu lớn nhờ cửa sổ ngữ cảnh cực rộng).

### 2.4 Division of Tasks (Phân chia công việc trong nhóm)
Để đảm bảo tính công bằng và cân bằng khối lượng công việc 50/50 hoàn hảo giữa 2 thành viên:
1. **Phạm Hoàng Anh (2A202600631)**:
   - Thiết kế và lập trình 5 Marketing Tools của MVP trong `src/tools/marketing_tools.py` (JSON Schema, parameters, descriptions).
   - Thiết lập cấu hình tích hợp LLM Provider và quản lý biến môi trường (`.env`).
   - Xây dựng công cụ phân tích logs tự động `parse_logs.py` để trích xuất dữ liệu telemetry cho nhóm.
2. **Hoàng Long**:
   - Thiết kế cấu trúc ReAct Agent và lập trình vòng lặp suy luận chính (`run` method) trong `src/agent/agent.py`.
   - Lập trình bộ Parser bóc tách đối số và hành động thông minh (Regex & JSON Parsing).
   - Kỹ nghệ gợi ý (Prompt Engineering), tối ưu hóa System Prompt từ bản v1 lên Prompt v2 để sửa lỗi bỏ qua tool vật lý.

---

## 3. Telemetry & Performance Dashboard

Dữ liệu thống kê hiệu năng tổng hợp được phân tích tự động thông qua script [parse_logs.py](file:///Users/a/Documents/research/ai/task_ai/Day3-2A202600631/parse_logs.py) trích xuất từ logs hệ thống:

- **Average Latency (P50)**: ~2,500ms cho mỗi bước lặp LLM; Tổng latency cho chuỗi ReAct Agent v2 hoàn chỉnh (4 steps) là ~12,400ms.
- **Average Tokens per Task**: ~1,300 tokens đầu vào và ~200 tokens đầu ra mỗi lượt lặp; Tổng tokens tiêu thụ cho Agent v2 chạy full pipeline là ~6,200 tokens.
- **Total Cost of Test Suite**: ~$0.035 (Ước tính dựa trên đơn giá token gpt-4o).

---

## 4. Root Cause Analysis (RCA) - Failure Traces

### Case Study: Lỗi bỏ qua công cụ (Tool Bypass / Lazy Agent) trên Agent v1
- **Input**: *"Tôi có một ứng dụng học tiếng Anh SpeakFlow sửa phát âm thời gian thực. Hãy phân tích sản phẩm, gợi ý group Facebook, viết bài chia sẻ dạng story post cho sinh viên và đặt lịch đăng lúc 8h tối nay."*
- **Observation**: Agent v1 gọi thành công `analyze_product` ở Step 0 và `discover_groups` ở Step 1. Nhưng tại Step 2, Agent tự động viết bài đăng và tự xác nhận đặt lịch trong câu trả lời cuối cùng (`Final Answer`) mà không hề kích hoạt tool `generate_content` và `schedule_post`.
- **Root Cause (Nguyên nhân gốc rễ)**: System Prompt v1 không có các điều khoản ràng buộc pháp lý chặt chẽ. Khi LLM tự đánh giá rằng khả năng sinh văn bản của nó tự viết bài đăng sẽ nhanh và ít tốn tài nguyên hơn việc gửi yêu cầu qua Tool Python, nó đã tự động đi đường tắt (Shortcut) và bỏ qua tool. điều này phá vỡ tính an toàn của hệ thống vì hành động đặt lịch thực tế không được ghi nhận dưới hệ thống cơ sở dữ liệu vật lý.

---

## 5. Ablation Studies & Experiments

### Experiment 1: Prompt v1 vs Prompt v2 (Strict ReAct Prompt)
Để xử lý lỗi bỏ qua công cụ trên, chúng tôi tiến hành nâng cấp lên **Prompt v2** chèn thêm bộ luật cưỡng chế gọi Tool (`QUY TẮC BẮT BUỘC`):

```diff
- Bạn là một AI Marketing Agent thông minh và có tư duy chiến lược. Nhiệm vụ của bạn là hỗ trợ người dùng lập kế hoạch và triển khai các chiến dịch marketing một cách bán tự động (không spam).
+ Bạn là một AI Marketing Agent thông minh và có tư duy chiến lược cực kỳ chặt chẽ.
+ QUY TẮC BẮT BUỘC (CRITICAL RULES):
+ 1. BẮT BUỘC SỬ DỤNG TOOL: Nếu có công cụ hỗ trợ cho một bước công việc nào đó, bạn BẮT BUỘC phải gọi công cụ đó thông qua Action. Tuyệt đối KHÔNG tự nghĩ ra, KHÔNG tự giả lập, KHÔNG tự bịa ra (hallucinate) dữ liệu hoặc tự làm thay nhiệm vụ của công cụ.
+    - Để tạo nội dung bài viết marketing -> Bắt buộc gọi tool generate_content.
+    - Để lên lịch đăng bài -> Bắt buộc gọi tool schedule_post.
```

- **Kết quả**: Agent v2 chạy chuẩn xác 100% số ca thử nghiệm phức tạp, gọi đầy đủ cả 4 tool tuần tự, loại bỏ hoàn toàn hành vi Tool Bypass.

### Experiment 2: Chatbot Baseline vs ReAct Agent v2
Bảng so sánh đối chứng hiệu năng tổng quát:

| Case / Scenario | Chatbot Result | Agent V2 (Strict ReAct) | Winner |
| :--- | :--- | :--- | :--- |
| **Simple Q (Câu hỏi đơn giản)** | Trả lời nhanh (~1.5s), tốn rất ít token (~200). | Trả lời chậm (~3.5s), tốn nhiều token (~1500) do overhead hệ thống. | **Chatbot Baseline** |
| **Multi-step Pipeline (Yêu cầu phức tạp đa bước)** | Thất bại hoàn toàn. Bịa đặt (Hallucinate) danh sách group và tự nhận đã đăng bài nhưng thực tế không có gì xảy ra. | Thành công rực rỡ. Suy luận chặt chẽ từng bước, gọi tool thực tế và kết xuất dữ liệu chính xác từ môi trường. | **ReAct Agent** |

---

## 6. Production Readiness Review

Để đưa hệ thống AI Marketing Agent này ra thị trường thực tế (Go-to-Market), chúng tôi xây dựng lộ trình chuẩn bị sản xuất gồm 3 khía cạnh:

1. **Security & Guardrails**:
   - Áp dụng các thư viện kiểm duyệt mã độc và cấu trúc tham số (như Pydantic) để lọc sạch các chuỗi đối số bóc tách được từ LLM trước khi gọi hàm Python thực thi nhằm tránh SQL/Command Injection.
   - Giới hạn số bước lặp tối đa của ReAct (`max_steps = 5`) để chặn đứng nguy cơ vòng lặp vô hạn (Infinite Loop) gây tốn kém chi phí API bất thường.

2. **Asynchronous Execution & Scaling**:
   - Sử dụng kiến trúc Task Queue (Celery/Redis) để xử lý các tác vụ gọi tool vật lý chậm (như cào dữ liệu Facebook hay gửi HTTP Request đăng bài lên LinkedIn API) nhằm tránh việc treo luồng suy luận của LLM.

3. **Performance Optimization (Vector Tool Retrieval)**:
   - Khi hệ thống mở rộng lên hàng nghìn tool khác nhau, thay vì nhét tất cả mô tả tool vào prompt gây quá tải ngữ cảnh (Context Overflow), chúng tôi sẽ dùng Vector DB (ChromaDB) để lưu nhúng (Embedding) mô tả tool và chỉ lấy ra Top-5 tool liên quan nhất dựa trên truy vấn hiện tại để chèn vào ngữ cảnh của Agent.
