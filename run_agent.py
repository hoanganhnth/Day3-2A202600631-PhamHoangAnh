import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from src.core.openai_provider import OpenAIProvider
from src.agent.agent import ReActAgent
from src.tools.marketing_tools import marketing_tools_list
from src.telemetry.logger import logger

def get_llm_provider():
    provider_name = os.getenv("DEFAULT_PROVIDER", "openai").lower()
    model_name = os.getenv("DEFAULT_MODEL", "gpt-4o")
    
    if provider_name == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        return OpenAIProvider(model_name=model_name, api_key=api_key)
    else:
        print(f"❌ Error: run_agent.py currently only optimized for OpenAI (DEFAULT_PROVIDER=openai in .env)")
        sys.exit(1)

def run_agent_test():
    provider = get_llm_provider()
    
    # Initialize ReActAgent with the provider and our custom tools
    agent = ReActAgent(llm=provider, tools=marketing_tools_list, max_steps=10)
    
    # Define the complex multi-step prompt
    complex_prompt = (
        "Tôi có một ứng dụng học tiếng Anh giao tiếp tích hợp AI, tên là 'SpeakFlow'. "
        "USP: Sửa phát âm thời gian thực bằng AI giọng bản xứ. Đối tượng mục tiêu: sinh viên.\n\n"
        "Hãy thực hiện các bước sau:\n"
        "1. Phân tích sản phẩm để tìm các từ khóa chính.\n"
        "2. Sử dụng các từ khóa đó để gợi ý cho tôi các nhóm Facebook/cộng đồng phù hợp nhất để đăng bài marketing.\n"
        "3. Viết 1 bài viết chia sẻ kinh nghiệm tự học tiếng Anh giao tiếp (dạng story post) nhắm đến đối tượng sinh viên để quảng bá khéo léo cho SpeakFlow.\n"
        "4. Lên lịch đăng bài viết đó vào lúc 8h tối nay trên nhóm phù hợp nhất tìm được ở bước 2.\n"
        "5. Trả về kết quả phân tích, bài viết và xác nhận lịch đăng bài."
    )
    
    print("\n" + "="*50)
    print("🚀 RUNNING REACT AGENT (Phase 3)")
    print("Prompt:")
    print(complex_prompt)
    print("="*50)
    
    # Execute the agentic reasoning loop
    final_answer = agent.run(complex_prompt)
    
    print("\n" + "="*50)
    print("🏆 FINAL ANSWER FROM AGENT:")
    print(final_answer)
    print("="*50 + "\n")

if __name__ == "__main__":
    run_agent_test()
