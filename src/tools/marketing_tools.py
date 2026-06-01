import json
from typing import Dict, Any, List

def analyze_product(product_info: str) -> str:
    """
    Mock function to analyze a product and return a product profile.
    """
    return json.dumps({
        "product": "Analyzed Product",
        "target_users": ["sinh viên", "người đi làm", "người tự học"],
        "pain_points": ["quên nhanh", "thiếu thời gian", "không có môi trường thực hành"],
        "benefits": ["nhớ lâu", "linh hoạt", "thực tế"],
        "keywords": ["IELTS", "TOEIC", "từ vựng", "giao tiếp"]
    }, ensure_ascii=False)


def discover_groups(keywords: str) -> str:
    """
    Mock function to discover marketing groups based on keywords.
    """
    # Simulate finding groups based on keywords
    return json.dumps([
        {"group": "IELTS Fighter", "size": 100000, "topic": "IELTS"},
        {"group": "Tự học TOEIC 900", "size": 50000, "topic": "TOEIC"},
        {"group": "English Learning Community", "size": 75000, "topic": "English Learning"}
    ], ensure_ascii=False)


def generate_content(product_profile: str, target_group: str, content_type: str) -> str:
    """
    Mock function to generate marketing content.
    """
    # Simulate generating content based on type
    content = ""
    if content_type == "soft":
        content = "Tôi từng quên từ rất nhanh cho đến khi biết cách này..."
    elif content_type == "story":
        content = "Hành trình từ band 5 lên band 7 của mình..."
    elif content_type == "problem":
        content = "Tại sao học 100 từ nhưng nhớ được 10?"
    elif content_type == "tutorial":
        content = "3 cách học từ vựng hiệu quả mỗi ngày"
    elif content_type == "promotion":
        content = "Tặng 7 ngày Premium trải nghiệm học từ vựng không giới hạn!"
    else:
        content = f"Nội dung chung chung về sản phẩm cho nhóm {target_group}."

    return json.dumps({
        "status": "success",
        "content_type": content_type,
        "target_group": target_group,
        "generated_content": content,
        "platform_suggestions": ["Facebook", "LinkedIn"]
    }, ensure_ascii=False)


def schedule_post(content: str, platform: str, time: str) -> str:
    """
    Mock function to schedule a post.
    """
    return json.dumps({
        "status": "scheduled",
        "platform": platform,
        "scheduled_time": time,
        "message": f"Bài viết đã được lên lịch thành công trên {platform} vào lúc {time}."
    }, ensure_ascii=False)


def get_analytics(post_id: str) -> str:
    """
    Mock function to get analytics for a post.
    """
    return json.dumps({
        "post_id": post_id,
        "views": 1250,
        "clicks": 150,
        "comments": 25,
        "conversions": 10,
        "ctr": "12%"
    }, ensure_ascii=False)


# ==========================================
# TOOL DEFINITIONS FOR THE AGENT
# ==========================================
marketing_tools_list = [
    {
        "name": "analyze_product",
        "description": "Phân tích sản phẩm để tạo Product Profile. Nhận vào thông tin cơ bản của sản phẩm (tên, mô tả, USP) và trả về thông tin chi tiết về khách hàng mục tiêu, nỗi đau (pain points), lợi ích, và từ khóa.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_info": {
                    "type": "string",
                    "description": "Thông tin cơ bản về sản phẩm."
                }
            },
            "required": ["product_info"]
        }
    },
    {
        "name": "discover_groups",
        "description": "Tìm kiếm cộng đồng và nhóm phù hợp để đăng bài. Nhận vào các từ khóa liên quan đến sản phẩm (cách nhau bằng dấu phẩy) và trả về danh sách các nhóm/cộng đồng tiềm năng kèm theo quy mô và chủ đề.",
        "parameters": {
            "type": "object",
            "properties": {
                "keywords": {
                    "type": "string",
                    "description": "Danh sách các từ khóa liên quan, ví dụ: 'IELTS, TOEIC, English'."
                }
            },
            "required": ["keywords"]
        }
    },
    {
        "name": "generate_content",
        "description": "Tạo nội dung marketing cho sản phẩm. Cần truyền vào product_profile (thông tin sản phẩm), target_group (tên nhóm mục tiêu), và content_type (loại nội dung: soft, story, problem, tutorial, promotion). Trả về nội dung bài viết đã được sinh ra.",
        "parameters": {
            "type": "object",
            "properties": {
                "product_profile": {
                    "type": "string",
                    "description": "Thông tin chi tiết về sản phẩm (có thể lấy từ analyze_product)."
                },
                "target_group": {
                    "type": "string",
                    "description": "Tên nhóm hoặc cộng đồng mục tiêu."
                },
                "content_type": {
                    "type": "string",
                    "description": "Loại nội dung muốn tạo (soft, story, problem, tutorial, promotion)."
                }
            },
            "required": ["product_profile", "target_group", "content_type"]
        }
    },
    {
        "name": "schedule_post",
        "description": "Lên lịch đăng bài viết. Cần truyền vào nội dung bài viết (content), nền tảng (platform), và thời gian (time). Trả về trạng thái đặt lịch.",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Nội dung bài viết cần lên lịch."
                },
                "platform": {
                    "type": "string",
                    "description": "Nền tảng mạng xã hội muốn đăng (Facebook, LinkedIn, Reddit...)."
                },
                "time": {
                    "type": "string",
                    "description": "Thời gian lên lịch đăng bài (ví dụ: '9h sáng mai', '2023-11-20 19:00')."
                }
            },
            "required": ["content", "platform", "time"]
        }
    },
    {
        "name": "get_analytics",
        "description": "Lấy dữ liệu phân tích hiệu quả của một bài viết hoặc chiến dịch đã đăng. Cần truyền vào post_id. Trả về lượt xem, clicks, conversions và CTR.",
        "parameters": {
            "type": "object",
            "properties": {
                "post_id": {
                    "type": "string",
                    "description": "ID của bài đăng hoặc tên chiến dịch."
                }
            },
            "required": ["post_id"]
        }
    }
]
