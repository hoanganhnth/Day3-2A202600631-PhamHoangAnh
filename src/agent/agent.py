import os
import re
import json
from typing import List, Dict, Any, Optional
from src.core.llm_provider import LLMProvider
from src.telemetry.logger import logger

class ReActAgent:
    """
    A ReAct-style Agent that follows the Thought-Action-Observation loop.
    Implements core loop logic, argument parsing, and tool execution.
    """
    
    def __init__(self, llm: LLMProvider, tools: List[Dict[str, Any]], max_steps: int = 5):
        self.llm = llm
        self.tools = tools
        self.max_steps = max_steps
        self.history = []

    def get_system_prompt(self) -> str:
        """
        [PROMPT V2] - Strict ReAct instructions to prevent Tool Bypass (Lazy Agent).
        Forces the agent to use tools for analysis, generation, and scheduling rather than doing it in-head.
        """
        tool_descriptions = "\n".join([
            f"- {t['name']}: {t['description']}\n  Parameters: {json.dumps(t.get('parameters', {}), ensure_ascii=False)}"
            for t in self.tools
        ])
        
        return f"""Bạn là một AI Marketing Agent thông minh và có tư duy chiến lược cực kỳ chặt chẽ. Nhiệm vụ của bạn là hỗ trợ người dùng lập kế hoạch và triển khai các chiến dịch marketing một cách bán tự động thông qua việc sử dụng các công cụ.

Bạn có quyền truy cập vào các công cụ (Tools) sau để hỗ trợ thực hiện nhiệm vụ:
{tool_descriptions}

QUY TẮC BẮT BUỘC (CRITICAL RULES):
1. **BẮT BUỘC SỬ DỤNG TOOL**: Nếu có công cụ hỗ trợ cho một bước công việc nào đó, bạn BẮT BUỘC phải gọi công cụ đó thông qua Action. Tuyệt đối KHÔNG tự nghĩ ra, KHÔNG tự giả lập, KHÔNG tự bịa ra (hallucinate) dữ liệu hoặc tự làm thay nhiệm vụ của công cụ.
   - Để phân tích sản phẩm -> Bắt buộc gọi tool `analyze_product`.
   - Để tìm cộng đồng/nhóm phù hợp -> Bắt buộc gọi tool `discover_groups`.
   - Để tạo nội dung bài viết marketing -> Bắt buộc gọi tool `generate_content`.
   - Để lên lịch đăng bài -> Bắt buộc gọi tool `schedule_post`.
   - Để lấy dữ liệu phân tích -> Bắt buộc gọi tool `get_analytics`.
2. **Quy trình hoạt động nghiêm ngặt (Thought -> Action -> Observation)**:
   - **Thought**: Suy nghĩ và phân tích xem bước hiện tại cần làm gì, công cụ nào cần gọi.
   - **Action**: Chỉ gọi duy nhất 1 công cụ tại mỗi bước Action theo định dạng chuẩn:
     Action: tool_name(arg_name="arg_val", ...)
   - **Observation**: Xem kết quả trả về từ công cụ để suy nghĩ cho bước tiếp theo.
3. **Thứ tự thực hiện tuần tự**: Hãy thực hiện từng bước một. Không gộp nhiều bước lại và không đưa ra 'Final Answer:' khi chưa gọi đầy đủ các công cụ tương ứng để xử lý các bước của yêu cầu.

Định dạng trả về bắt buộc:
Thought: <suy nghĩ của bạn>
Action: <tên_công_cụ>(<đối_số>)
Observation: <kết quả của công cụ - KHÔNG tự sinh dòng này, hệ thống sẽ tự trả về>

... (Lặp lại chu trình Thought -> Action -> Observation)

Khi đã gọi đầy đủ các công cụ cần thiết và có kết quả cuối cùng từ tất cả các bước, bạn mới được phép kết luận:
Final Answer: <nội dung phản hồi hoàn chỉnh cho người dùng dựa trên kết quả thực tế từ các Observation>
"""

    def run(self, user_input: str) -> str:
        """
        Executes the ReAct loop logic.
        1. Generate Thought + Action.
        2. Parse Action and execute Tool.
        3. Append Observation and repeat.
        4. Break on Final Answer or max_steps.
        """
        logger.log_event("AGENT_START", {"input": user_input, "model": self.llm.model_name})
        
        scratchpad = ""
        steps = 0
        final_answer = None

        print(f"\n🚀 [AGENT START] Processing user query...")

        while steps < self.max_steps:
            # We append the scratchpad (history of thoughts and observations) to the prompt
            prompt = f"User Request: {user_input}\n\nScratchpad history:\n{scratchpad}"
            
            logger.log_event("LLM_CALL_START", {"step": steps})
            
            # Generate LLM response
            result = self.llm.generate(prompt, system_prompt=self.get_system_prompt())
            content = result["content"]
            
            logger.log_event("LLM_CALL_END", {
                "step": steps,
                "latency_ms": result["latency_ms"],
                "usage": result["usage"]
            })
            
            print(f"\n🤖 [Step {steps + 1} Thinking...]")
            print(content)
            
            # Append LLM's response to scratchpad
            scratchpad += f"\n{content}"
            
            # 1. Check if the LLM reached a Final Answer
            if "Final Answer:" in content:
                final_answer_match = re.search(r"Final Answer:\s*(.*)", content, re.DOTALL)
                if final_answer_match:
                    final_answer = final_answer_match.group(1).strip()
                    break
            
            # 2. Check if the LLM chose to take an Action
            action_match = re.search(r"Action:\s*(\w+)\((.*)\)", content)
            if action_match:
                tool_name = action_match.group(1).strip()
                args_str = action_match.group(2).strip()
                
                # Parse tool arguments robustly
                args = {}
                try:
                    # Handle JSON object arguments if the LLM outputs standard JSON
                    if args_str.startswith("{") and args_str.endswith("}"):
                        args = json.loads(args_str)
                    else:
                        # Extract keyword arguments like key="value" or key='value' or key=val
                        matches = re.findall(r'(\w+)\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s,]+))', args_str)
                        for key, val1, val2, val3 in matches:
                            val = val1 or val2 or val3
                            # Strip outer quotes just in case
                            args[key] = val
                except Exception as e:
                    logger.log_event("PARSER_ERROR", {"error": str(e), "raw": args_str})
                    print(f"⚠️ Failed to parse tool arguments: {e}")
                
                logger.log_event("TOOL_CALL", {"tool": tool_name, "args": args})
                print(f"🔌 [Executing Tool] Calling {tool_name} with arguments: {args}")
                
                # Execute the tool
                observation = self._execute_tool(tool_name, args)
                
                logger.log_event("TOOL_OBSERVATION", {"tool": tool_name, "observation": observation})
                print(f"📥 [Observation] {observation}")
                
                # Feed the Observation back into the scratchpad
                scratchpad += f"\nObservation: {observation}"
            else:
                # If no Action and no Final Answer, prompt LLM to proceed
                scratchpad += "\nObservation: Please take an Action using the format 'Action: tool_name(args)' or provide your 'Final Answer:'."
                logger.log_event("NO_ACTION_FOUND", {"content": content[:100]})
                print("⚠️ Warning: No valid Action or Final Answer detected.")
            
            steps += 1
            
        logger.log_event("AGENT_END", {"steps": steps, "success": final_answer is not None})
        
        if final_answer:
            return final_answer
        else:
            return "Rất tiếc, Agent không thể hoàn thành nhiệm vụ trong số bước tối đa cho phép."

    def _execute_tool(self, tool_name: str, args: Dict[str, Any]) -> str:
        """
        Dynamically executes tool functions by matching names inside src.tools.marketing_tools.
        """
        try:
            import src.tools.marketing_tools as mt
            func = getattr(mt, tool_name, None)
            if func:
                # Filter keyword arguments using inspect to match function signature
                import inspect
                sig = inspect.signature(func)
                valid_args = {}
                for param_name, param in sig.parameters.items():
                    if param_name in args:
                        valid_args[param_name] = args[param_name]
                    elif param.default == inspect.Parameter.empty:
                        # If a required parameter is missing, try to find a fallback or just use first available args string
                        if len(args) == 1:
                            valid_args[param_name] = list(args.values())[0]
                
                # Execute the python function
                return func(**valid_args)
            else:
                return f"Error: Tool '{tool_name}' not defined in marketing_tools."
        except Exception as e:
            return f"Error executing tool {tool_name}: {str(e)}"

