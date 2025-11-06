import os
from typing import Optional
import anthropic
from openai import OpenAI


class AISummarizer:
    """
    AI Summarizer với nhiều backend
    """

    def __init__(self, provider: str = "openai"):
        """
        Args:
            provider: "openai", "claude", hoặc "local"
        """
        self.provider = provider

        if provider == "openai":
            # SET KEY TRỰC TIẾP
            self.client = OpenAI(api_key="")
            self.model = "gpt-4o-mini"

        elif provider == "claude":
            # Nếu dùng Claude, set key ở đây
            self.client = anthropic.Anthropic(api_key="your-claude-key-here")
            self.model = "claude-3-5-sonnet-20241022"

    def summarize(
            self,
            document_content: str,
            question: str,
            question_type: str,
            max_tokens: int = 4000
    ) -> str:
        """
        Tóm tắt văn bản theo câu hỏi
        """

        # Tạo prompt dựa trên question_type
        system_prompt = self._build_system_prompt(question_type)
        user_prompt = self._build_user_prompt(document_content, question, question_type)

        if self.provider == "openai":
            return self._summarize_openai(system_prompt, user_prompt, max_tokens)
        elif self.provider == "claude":
            return self._summarize_claude(system_prompt, user_prompt, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def _build_system_prompt(self, question_type: str) -> str:
        """Tạo system prompt theo loại câu hỏi"""

        base_prompt = """Bạn là một chuyên gia phân tích và tóm tắt văn bản tiếng Việt.

NHIỆM VỤ: Trả lời câu hỏi dựa trên nội dung tài liệu được cung cấp.

YÊU CẦU FORMAT:
"""

        format_instructions = {
            "tom_tat": """
- Cấu trúc: Tiêu đề + Các phần (I, II, III...) + Bullets + Kết luận
- Dùng heading rõ ràng (###)
- Mỗi phần có 3-6 bullets
- Độ dài: 500-1000 từ
""",
            "muc_tieu": """
- Cấu trúc: Tổng quan + Bảng chỉ tiêu + Giải thích
- Dùng bảng Markdown cho các chỉ tiêu cụ thể
- Highlight các con số quan trọng
- Độ dài: 400-800 từ
""",
            "cach_thuc_hien": """
- Cấu trúc: Các bước thực hiện (I, II, III...)
- Mỗi bước có sub-items cụ thể
- Dùng số La Mã cho các phần chính
- Độ dài: 800-1500 từ
""",
            "ke_hoach": """
- Cấu trúc: Bảng kế hoạch với cột (Giai đoạn, Nhiệm vụ, Hoạt động, Thời gian)
- Dùng bảng Markdown
- Có phân loại theo thời gian/ưu tiên
- Độ dài: 600-1000 từ
""",
            "kho_khan": """
- Cấu trúc: Các nhóm khó khăn (I, II, III...)
- Mỗi nhóm có bullets cụ thể + ví dụ
- Đánh giá mức độ nghiêm trọng
- Độ dài: 500-900 từ
""",
            "ket_qua": """
- Cấu trúc: Tổng quan + Bảng số liệu + Phân tích
- Dùng bảng cho kết quả định lượng
- Highlight thành tích nổi bật
- Độ dài: 400-800 từ
""",
            "so_sanh": """
- Cấu trúc: Bảng so sánh + Phân tích + Xếp hạng
- Dùng bảng Markdown với nhiều cột
- Có kết luận rõ ràng
- Độ dài: 500-900 từ
""",
            "goi_y": """
- Cấu trúc: Các nhóm gợi ý (I, II, III...)
- Mỗi gợi ý có hành động cụ thể
- Phân loại theo độ ưu tiên
- Độ dài: 600-1000 từ
""",
            "hieu_qua": """
- Cấu trúc: Tổng quan + Các khía cạnh hiệu quả + Số liệu
- Dùng bảng cho số liệu định lượng
- Phân tích cụ thể
- Độ dài: 600-1000 từ
""",
            "phuong_an": """
- Cấu trúc: Liệt kê phương án + So sánh ưu/nhược + Khuyến nghị
- Dùng bảng so sánh nếu cần
- Đánh giá rõ ràng
- Độ dài: 700-1200 từ
"""
        }

        return base_prompt + format_instructions.get(question_type, format_instructions["tom_tat"])

    def _build_user_prompt(self, document: str, question: str, question_type: str) -> str:
        """Tạo user prompt"""

        # Truncate document nếu quá dài (giữ trong context limit)
        max_doc_length = 15000
        if len(document) > max_doc_length:
            document = document[:max_doc_length] + "\n\n[...Tài liệu còn tiếp...]"

        return f"""NỘI DUNG TÀI LIỆU:
{document}

---

CÂU HỎI: {question}

LOẠI CÂU HỎI: {question_type}

Hãy trả lời câu hỏi dựa trên nội dung tài liệu theo đúng format yêu cầu."""

    def _summarize_openai(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """Tóm tắt bằng OpenAI"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _summarize_claude(self, system_prompt: str, user_prompt: str, max_tokens: int) -> str:
        """Tóm tắt bằng Claude"""
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )
            return message.content[0].text
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")


# Test summarizer
if __name__ == "__main__":
    # Cần set OPENAI_API_KEY hoặc ANTHROPIC_API_KEY trong environment
    summarizer = AISummarizer(provider="openai")

    test_doc = """
    Nghị quyết số 57-NQ/TW về đẩy mạnh phát triển khoa học, công nghệ...
    Mục tiêu đến 2030: TFP đóng góp >60%, R&D đạt 2% GDP...
    """

    test_question = "Tóm tắt mục tiêu chính đến năm 2030"

    summary = summarizer.summarize(
        document_content=test_doc,
        question=test_question,
        question_type="muc_tieu"
    )

    print("=== SUMMARY ===")
    print(summary)