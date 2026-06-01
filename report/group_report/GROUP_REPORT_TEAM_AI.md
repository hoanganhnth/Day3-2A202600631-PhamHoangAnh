# Báo Cáo Nhóm: Lab 3 - Phát Triển Hệ Thống Agentic AI Thực Tế

- **Tên Nhóm**: Team AI Marketing Agent (Hoàng Anh & Nguyễn Văn Minh)
- **Thành Viên**: Phạm Hoàng Anh (2A202600631) & Nguyễn Văn Minh (2A202600556)
- **Ngày Nộp**: 2026-06-01

---

## 1. Tóm Tắt Dự Án (Executive Summary)

Dự án này xây dựng một **AI Marketing Agent** giúp tự động làm marketing cho sản
phẩm mà không đi spam hàng loạt.

- Thay vì dùng Chatbot thường (chỉ biết nói suông và tự bịa thông tin), chúng
  tôi chuyển sang dùng **ReAct Agent** (biết suy nghĩ rồi tự gọi code Python
  chạy thật).
- **Tỷ lệ thành công**: Đạt **100%** trên các yêu cầu phức tạp sau khi nâng cấp
  lên phiên bản Agent v2. Trong khi đó, Chatbot thường thất bại hoàn toàn (0%)
  vì chỉ biết hứa hẹn mà không làm được gì thực tế.
- **Kết quả chính**: Agent v2 đã tự động chạy trơn tru chuỗi công việc: Phân
  tích sản phẩm -> Tìm nhóm Facebook phù hợp -> Tự viết bài theo nhóm -> Tự lên
  lịch đăng bài thật bằng cách gọi 4 công cụ Python chuẩn xác.

---

## 2. Kiến Trúc Hệ Thống & Các Công Cụ

### 2.1 Vòng Lặp ReAct Hoạt Động Như Thế Nào

Agent hoạt động theo quy trình khép kín: **Nghĩ (Thought) -> Gọi Tool (Action)
-> Nhận kết quả thật (Observation)**. Nó dùng một trang nháp (`scratchpad`) để
ghi nhớ lại các bước đã làm:

```text
                  ┌──────────────────────────┐
                  │     Yêu cầu người dùng   │
                  └─────────────┬────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐
                  │  Hệ thống gợi ý Prompt   │
                  └─────────────┬────────────┘
                                │
                                ▼
                  ┌──────────────────────────┐  LLM suy nghĩ
        ┌────────>│   LLM tự suy nghĩ bước   ├─────────┐
        │         └─────────────┬────────────┘         │
        │                       │                      │
        │                       ▼                      ▼
        │             [Quyết định gọi Tool]     [Đã làm xong hết]
        │                       │                      │
        │                       ▼                      ▼
        │             ┌──────────────────┐     ┌───────────────┐
        │             │ Bóc tách Action  │     │ Câu trả lời   │
        │             └─────────┬────────┘     │   cuối cùng   │
        │                       │              └───────────────┘
        │                       ▼                      │
Lưu kết quả vào nháp  ┌──────────────────┐             ▼
        │             │ Chạy Tool Python │         [Hoàn thành]
        └─────────────┤   lấy kết quả    │
                      └──────────────────┘
```

### 2.2 Danh Sách 5 Công Cụ Đã Tạo

Chúng tôi viết 5 hàm Python để Agent tự gọi khi cần:

| Tên Tool           | Tham Số Đầu Vào                               | Nhiệm Vụ Thực Tế                                                              |
| :----------------- | :-------------------------------------------- | :---------------------------------------------------------------------------- |
| `analyze_product`  | Mô tả sản phẩm (string)                       | Phân tích sản phẩm để tìm ra từ khóa, nỗi đau và khách hàng mục tiêu.         |
| `discover_groups`  | Các từ khóa (string)                          | Tìm kiếm các nhóm Facebook phù hợp nhất để đăng bài.                          |
| `generate_content` | Profile sản phẩm, tên nhóm, loại bài (string) | Tự viết bài quảng cáo phù hợp riêng cho nhóm đó (dạng kể chuyện, chia sẻ...). |
| `schedule_post`    | Nội dung bài, mạng xã hội, giờ đăng (string)  | Lên lịch đăng bài viết lên mạng xã hội.                                       |
| `get_analytics`    | ID bài viết (string)                          | Lấy các chỉ số tương tác thực tế (lượt xem, clicks, bình luận, CTR).          |

### 2.3 Mô Hình Ngôn Ngữ Sử Dụng (LLMs)

- **Dòng chính**: OpenAI GPT-4o (Dùng để Agent suy luận logic phức tạp và gọi
  tool chính xác).
- **Dự phòng**: Google Gemini 1.5 Flash (Dùng khi cần xử lý nhanh hoặc nhiều dữ
  liệu đầu vào).

### 2.4 Phân Chia Công Việc Trong Nhóm (50/50)

1. **Phạm Hoàng Anh (2A202600631)**:
   - Nghĩ ra và viết code 5 công cụ Python trong `src/tools/marketing_tools.py`.
   - Kết nối các mô hình OpenAI, Gemini và quản lý biến môi trường `.env`.
   - Viết script `parse_logs.py` để tự động đọc file logs JSON và đo đạc hiệu
     năng cho nhóm.
2. **Nguyễn Văn Minh (2A202600556)**:
   - Thiết kế cấu trúc Agent và viết vòng lặp suy luận chính (`run`) trong
     `src/agent/agent.py`.
   - Viết bộ lọc bóc tách lệnh Regex/JSON để Agent hiểu đúng tham số.
   - Làm Prompt Engineering (thiết kế Prompt v1 và sửa lên Prompt v2 để Agent
     không bị lười gọi tool).

---

## 3. Đo Đạc Hiệu Năng & Chi Phí (Telemetry)

Chúng tôi dùng file log JSON thực tế thu được từ script `parse_logs.py` để đo
đạc:

- **Độ trễ trung bình**: ~2.5 giây cho mỗi lượt LLM suy nghĩ; Tổng thời gian
  chạy hết cả 5 bước của Agent v2 là khoảng 12.4 giây.
- **Lượng Token tiêu thụ**: ~1,300 tokens đầu vào và ~200 tokens đầu ra cho mỗi
  bước; Tổng cả bài chạy tốn khoảng 6,200 tokens.
- **Ước tính chi phí**: Khoảng $0.035 cho một lần chạy trọn vẹn (rất rẻ).

---

## 4. Phân Tích Lỗi Thực Tế Qua Logs (Root Cause Analysis)

### Ca kiểm thử: Lỗi Agent tự ý bỏ qua tool (Bypass Tool) trên bản Agent v1

- **Yêu cầu của user**: Nhập sản phẩm SpeakFlow, tìm group, viết bài kể chuyện
  và đặt lịch đăng lúc 8h tối.
- **Hiện tượng**: Agent v1 chạy thành công tool tìm sản phẩm và tìm group. Nhưng
  đến bước viết bài và đặt lịch, Agent **tự ý không thèm gọi tool**
  `generate_content` và `schedule_post`. Nó tự viết luôn bài đăng và tự thông
  báo "đã đặt lịch thành công" trong câu trả lời cuối cùng.
- **Tại sao lỗi**: Vì Prompt v1 viết lỏng lẻo. Con LLM nhận ra tự nó viết bài và
  tự nó báo xong việc thì nhanh hơn là phải gọi hàm Python chạy tiếp, nên nó đã
  đi đường tắt. Điều này rất nguy hiểm vì trên thực tế, không có code Python nào
  được chạy để đăng bài thật cả.

---

## 5. Các Thử Nghiệm & So Sánh (Ablation Studies)

### Thử nghiệm 1: Prompt v1 (Lỏng lẻo) vs Prompt v2 (Nghiêm khắc)

Để sửa lỗi tự ý bỏ qua tool ở trên, chúng tôi nâng cấp lên **Prompt v2**, viết
thêm phần `QUY TẮC BẮT BUỘC` cực kỳ nghiêm khắc:

```diff
- Bạn là một AI Marketing Agent thông minh. Nhiệm vụ của bạn là lập kế hoạch marketing...
+ Bạn là một AI Marketing Agent có tư duy cực kỳ chặt chẽ.
+ QUY TẮC BẮT BUỘC:
+ Nếu có công cụ hỗ trợ cho bước nào, bạn BẮT BUỘC phải gọi công cụ đó qua Action.
+ Tuyệt đối KHÔNG được tự bịa ra kết quả, KHÔNG được tự làm thay nhiệm vụ của công cụ.
```

- **Kết quả**: Agent v2 đã chạy cực kỳ nghiêm chỉnh, gọi đầy đủ cả 5 công cụ
  Python tuần tự, lỗi bỏ qua tool hoàn toàn biến mất.

### Thử nghiệm 2: So sánh Chatbot thường vs ReAct Agent v2

Bảng so sánh thực tế:

| Tác Vụ                         | Chatbot Thường                                                      | ReAct Agent v2 (Chúng tôi viết)                                                             | Người Thắng        |
| :----------------------------- | :------------------------------------------------------------------ | :------------------------------------------------------------------------------------------ | :----------------- |
| **Hỏi đáp đơn giản**           | Trả lời siêu nhanh (~1s), tốn rất ít token.                         | Chạy chậm hơn (~3s), tốn token do prompt hệ thống dài.                                      | **Chatbot Thường** |
| **Công việc đa bước phức tạp** | Thất bại. Tự bịa thông tin group và nói dối đã đăng bài thành công. | Thành công tốt đẹp. Suy nghĩ từng bước, gọi tool thật để lấy dữ liệu thật và đăng bài thật. | **ReAct Agent**    |

---

## 6. Đánh Giá Để Đưa Vào Thực Tế (Production Readiness)

Để mang hệ thống này ra chạy thực tế kiếm tiền, chúng tôi cần chuẩn bị 3 thứ:

1. **Bảo mật & Rào cản an toàn (Guardrails)**:
   - Dùng thư viện Pydantic để kiểm tra kỹ các tham số mà LLM parse ra trước khi
     truyền vào hàm Python chạy, tránh bị kẻ xấu hack hệ thống qua câu lệnh
     (Prompt Injection).
   - Đặt giới hạn `max_steps = 5` hoặc `10` để tránh Agent bị kẹt vào vòng lặp
     vô hạn gây tốn tiền API.

2. **Chạy ngầm bất đồng bộ**:
   - Dùng Celery và Redis để các tác vụ nặng (như cào dữ liệu Facebook thật hoặc
     gọi API đăng bài thật) được chạy ngầm dưới nền, tránh làm treo Agent.

3. **Tìm kiếm công cụ thông minh (Vector Tool Retrieval)**:
   - Khi dự án phình to lên có hàng trăm tool, chúng tôi sẽ dùng Vector DB (như
     ChromaDB) để lọc lấy ra 5 tool phù hợp nhất chèn vào prompt, giúp tiết kiệm
     tiền token hệ thống.
