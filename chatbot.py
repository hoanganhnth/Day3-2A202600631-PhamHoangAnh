import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from src.core.openai_provider import OpenAIProvider
from src.telemetry.logger import logger

def get_llm_provider():
    provider_name = os.getenv("DEFAULT_PROVIDER", "openai").lower()
    model_name = os.getenv("DEFAULT_MODEL", "gpt-4o")
    
    logger.log_event("CHATBOT_INIT", {"provider": provider_name, "model": model_name})
    
    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key or "your_openai_api_key" in api_key or len(api_key) < 10:
            print("⚠️ Warning: OpenAI API key is missing or invalid in .env")
        return OpenAIProvider(model_name=model_name, api_key=api_key)
    elif provider_name == "google":
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or "your_gemini_api_key" in api_key:
            print("⚠️ Warning: Gemini API key is missing or invalid in .env")
        return GeminiProvider(model_name=model_name, api_key=api_key)
    elif provider_name == "local":
        model_path = os.getenv("LOCAL_MODEL_PATH", "./models/Phi-3-mini-4k-instruct-q4.gguf")
        if not os.path.exists(model_path):
            print(f"❌ Error: Local model not found at {model_path}")
            sys.exit(1)
        return LocalProvider(model_path=model_path)
    else:
        print(f"❌ Error: Unknown provider '{provider_name}' in .env")
        sys.exit(1)

def run_complex_test_case(provider):
    complex_prompt = (
        "Tôi có một ứng dụng học tiếng Anh giao tiếp tích hợp AI, tên là 'SpeakFlow'. "
        "USP: Sửa phát âm thời gian thực bằng AI giọng bản xứ. Đối tượng mục tiêu: sinh viên.\n\n"
        "Hãy thực hiện các bước sau:\n"
        "1. Phân tích sản phẩm để tìm các từ khóa chính.\n"
        "2. Sử dụng các từ khóa đó để gợi ý cho tôi 3 nhóm Facebook/cộng đồng phù hợp nhất để đăng bài marketing.\n"
        "3. Viết 1 bài viết chia sẻ kinh nghiệm tự học tiếng Anh giao tiếp (dạng story post) nhắm đến đối tượng sinh viên để quảng bá khéo léo cho SpeakFlow.\n"
        "4. Lên lịch đăng bài viết đó vào lúc 8h tối nay trên nhóm 'IELTS Fighter'.\n"
        "5. Trả về kết quả phân tích, bài viết và xác nhận lịch đăng bài."
    )
    
    print("\n" + "="*50)
    print("🚀 RUNNING COMPLEX MULTI-STEP TEST CASE")
    print("Prompt:")
    print(complex_prompt)
    print("="*50 + "\n")
    
    logger.log_event("CHATBOT_START", {"prompt": complex_prompt, "type": "complex_test"})
    
    print("Thinking...", end="", flush=True)
    try:
        # Generate completion
        result = provider.generate(complex_prompt)
        
        print("\r" + " "*20 + "\r", end="")
        print("🤖 CHATBOT RESPONSE:")
        print(result["content"])
        print("\n" + "-"*50)
        print(f"📊 Telemetry: Provider={result['provider']}, Latency={result['latency_ms']}ms, "
              f"Tokens: Prompt={result['usage'].get('prompt_tokens')}, Completion={result['usage'].get('completion_tokens')}")
        print("-"*50)
        
        logger.log_event("CHATBOT_END", {
            "success": True,
            "latency_ms": result["latency_ms"],
            "usage": result["usage"],
            "provider": result["provider"]
        })
        
        print("\n📝 PHÂN TÍCH THẤT BẠI (Failure Analysis) - Tại sao Chatbot thất bại?")
        print("1. [Hallucination]: Chatbot tự bịa ra danh sách các group và xác nhận đã đặt lịch đăng bài, nhưng thực tế KHÔNG có hoạt động đặt lịch thực sự nào diễn ra.")
        print("2. [No Action]: Chatbot chỉ biết 'nói' chứ không biết 'làm' (thiếu cơ chế gọi tool/action của ReAct Agent).")
        print("3. [Linearity]: Chatbot không thể lấy kết quả từ bước 1 để làm đầu vào cho bước 2 một cách động dựa trên thế giới thực.")
        
    except Exception as e:
        print(f"\n❌ Error running LLM: {e}")
        logger.log_event("CHATBOT_ERROR", {"error": str(e)})

def run_interactive_mode(provider):
    print("\n" + "="*50)
    print("💬 INTERACTIVE CHATBOT BASELINE (Press Ctrl+C or type 'exit' to quit)")
    print("="*50 + "\n")
    
    system_prompt = "You are a helpful AI Assistant."
    
    while True:
        try:
            user_input = input("👤 User: ")
            if user_input.strip().lower() in ["exit", "quit"]:
                break
                
            if not user_input.strip():
                continue
                
            logger.log_event("CHATBOT_START", {"prompt": user_input, "type": "interactive"})
            
            print("🤖 Assistant: ", end="", flush=True)
            full_response = ""
            for chunk in provider.stream(user_input, system_prompt=system_prompt):
                print(chunk, end="", flush=True)
                full_response += chunk
            print("\n")
            
            logger.log_event("CHATBOT_END", {"success": True, "type": "interactive"})
            
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logger.log_event("CHATBOT_ERROR", {"error": str(e)})

def main():
    provider = get_llm_provider()
    
    while True:
        print("\n" + "="*40)
        print("      LAB 3: CHATBOT BASELINE MENU")
        print("="*40)
        print("1. Chạy ca kiểm thử phức tạp (Complex Test Case)")
        print("2. Trò chuyện tương tác (Interactive Mode)")
        print("3. Thoát (Exit)")
        print("="*40)
        
        choice = input("Nhập lựa chọn của bạn (1-3): ").strip()
        
        if choice == "1":
            run_complex_test_case(provider)
        elif choice == "2":
            run_interactive_mode(provider)
        elif choice == "3":
            print("Thoát chương trình. Hẹn gặp lại!")
            break
        else:
            print("Lựa chọn không hợp lệ, vui lòng chọn lại.")

if __name__ == "__main__":
    main()
