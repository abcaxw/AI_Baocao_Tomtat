import os
from typing import Optional, Dict
import anthropic
from openai import OpenAI
import tiktoken


class AISummarizer:
    """
    AI Summarizer với tracking tokens và chi phí
    """

    def __init__(self, provider: str = "openai"):
        """
        Args:
            provider: "openai", "claude", hoặc "local"
        """
        self.provider = provider

        if provider == "openai":
            self.client = OpenAI(api_key="")  # SET KEY TRỰC TIẾP
            self.model = "gpt-4o-mini"
            # Initialize tokenizer for counting
            try:
                self.tokenizer = tiktoken.encoding_for_model(self.model)
            except:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")

        elif provider == "claude":
            self.client = anthropic.Anthropic(api_key="your-claude-key-here")
            self.model = "claude-3-5-sonnet-20241022"
            self.tokenizer = None  # Claude doesn't need local tokenizer

    def count_tokens(self, text: str) -> int:
        """Đếm số token trong text"""
        if self.provider == "openai" and self.tokenizer:
            return len(self.tokenizer.encode(text))
        elif self.provider == "claude":
            # Ước tính cho Claude (1 token ≈ 4 chars)
            return len(text) // 4
        return 0

    def summarize(
            self,
            document_content: str,
            question: str,
            question_type: str,
            max_tokens: int = 4000
    ) -> Dict:
        """
        Tóm tắt văn bản theo câu hỏi

        Returns:
            Dict với keys: answer, usage, cost_info
        """

        # Tạo prompt
        system_prompt = self._build_system_prompt(question_type)
        user_prompt = self._build_user_prompt(document_content, question, question_type)

        # Count input tokens
        input_tokens_estimate = self.count_tokens(system_prompt + user_prompt)

        if self.provider == "openai":
            result = self._summarize_openai(system_prompt, user_prompt, max_tokens)
        elif self.provider == "claude":
            result = self._summarize_claude(system_prompt, user_prompt, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        # Add input token estimate if not provided by API
        if "input_tokens" not in result["usage"]:
            result["usage"]["input_tokens"] = input_tokens_estimate

        return result

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
        max_doc_length = 15000
        if len(document) > max_doc_length:
            document = document[:max_doc_length] + "\n\n[...Tài liệu còn tiếp...]"

        return f"""NỘI DUNG TÀI LIỆU:
{document}

---

CÂU HỎI: {question}

LOẠI CÂU HỎI: {question_type}

Hãy trả lời câu hỏi dựa trên nội dung tài liệu theo đúng format yêu cầu."""

    def _summarize_openai(self, system_prompt: str, user_prompt: str, max_tokens: int) -> Dict:
        """Tóm tắt bằng OpenAI với tracking"""
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

            # Extract usage information
            usage = response.usage

            return {
                "answer": response.choices[0].message.content,
                "usage": {
                    "input_tokens": usage.prompt_tokens,
                    "output_tokens": usage.completion_tokens,
                    "total_tokens": usage.total_tokens
                },
                "model": self.model,
                "provider": "openai"
            }
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")

    def _summarize_claude(self, system_prompt: str, user_prompt: str, max_tokens: int) -> Dict:
        """Tóm tắt bằng Claude với tracking"""
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

            # Extract usage from response
            usage = message.usage

            return {
                "answer": message.content[0].text,
                "usage": {
                    "input_tokens": usage.input_tokens,
                    "output_tokens": usage.output_tokens,
                    "total_tokens": usage.input_tokens + usage.output_tokens
                },
                "model": self.model,
                "provider": "claude"
            }
        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")


# Test summarizer
if __name__ == "__main__":
    summarizer = AISummarizer(provider="openai")

    test_doc = """
    Nghị quyết số 57-NQ/TW về đẩy mạnh phát triển khoa học, công nghệ...
    Mục tiêu đến 2030: TFP đóng góp >60%, R&D đạt 2% GDP...
    """

    test_question = "Tóm tắt mục tiêu chính đến năm 2030"

    result = summarizer.summarize(
        document_content=test_doc,
        question=test_question,
        question_type="muc_tieu"
    )

    print("=== SUMMARY ===")
    print(result["answer"])
    print("\n=== USAGE ===")
    print(f"Input tokens: {result['usage']['input_tokens']}")
    print(f"Output tokens: {result['usage']['output_tokens']}")
    print(f"Total tokens: {result['usage']['total_tokens']}")