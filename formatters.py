"""
Response Formatters - Format output theo từng loại câu hỏi
"""

import re
from typing import Dict


class ResponseFormatter:
    """Format và beautify output"""

    def format(self, answer: str, question_type: str) -> str:
        """
        Format answer theo question type
        """
        # Clean up answer
        answer = self._clean_text(answer)

        # Apply specific formatting
        if question_type in ["muc_tieu", "ket_qua", "so_sanh", "ke_hoach"]:
            answer = self._enhance_tables(answer)

        if question_type in ["tom_tat", "cach_thuc_hien", "kho_khan", "goi_y"]:
            answer = self._enhance_structure(answer)

        return answer

    def _clean_text(self, text: str) -> str:
        """Clean up text"""
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)

        # Remove trailing spaces
        text = re.sub(r' +\n', '\n', text)

        # Ensure proper spacing after headers
        text = re.sub(r'(#+[^\n]+)\n([^\n])', r'\1\n\n\2', text)

        return text.strip()

    def _enhance_tables(self, text: str) -> str:
        """Enhance markdown tables"""
        # Thêm spacing trước/sau bảng
        text = re.sub(r'([^\n])\n(\|)', r'\1\n\n\2', text)
        text = re.sub(r'(\|[^\n]+)\n([^\n|])', r'\1\n\n\2', text)

        return text

    def _enhance_structure(self, text: str) -> str:
        """Enhance hierarchical structure"""
        # Ensure proper spacing for roman numerals
        text = re.sub(r'([IVX]+\.) ', r'\n\n\1 ', text)

        return text

    def get_format_info(self, question_type: str) -> Dict:
        """Return format metadata"""

        format_info = {
            "tom_tat": {
                "structure_type": "hierarchical",
                "has_tables": False,
                "numbering_style": "roman",
                "sections": "3-6",
                "estimated_length": "500-1000 words"
            },
            "muc_tieu": {
                "structure_type": "mixed",
                "has_tables": True,
                "numbering_style": "roman",
                "sections": "2-4",
                "estimated_length": "400-800 words"
            },
            "cach_thuc_hien": {
                "structure_type": "hierarchical",
                "has_tables": False,
                "numbering_style": "roman",
                "sections": "5-8",
                "estimated_length": "800-1500 words"
            },
            "ke_hoach": {
                "structure_type": "table-based",
                "has_tables": True,
                "numbering_style": "phases",
                "sections": "2-4",
                "estimated_length": "600-1000 words"
            },
            "kho_khan": {
                "structure_type": "hierarchical",
                "has_tables": False,
                "numbering_style": "roman",
                "sections": "3-5",
                "estimated_length": "500-900 words"
            },
            "ket_qua": {
                "structure_type": "mixed",
                "has_tables": True,
                "numbering_style": "roman",
                "sections": "2-4",
                "estimated_length": "400-800 words"
            },
            "so_sanh": {
                "structure_type": "table-based",
                "has_tables": True,
                "numbering_style": "ranking",
                "sections": "2-3",
                "estimated_length": "500-900 words"
            },
            "goi_y": {
                "structure_type": "hierarchical",
                "has_tables": False,
                "numbering_style": "roman",
                "sections": "3-5",
                "estimated_length": "600-1000 words"
            },
            "hieu_qua": {
                "structure_type": "mixed",
                "has_tables": True,
                "numbering_style": "roman",
                "sections": "3-5",
                "estimated_length": "600-1000 words"
            },
            "phuong_an": {
                "structure_type": "comparative",
                "has_tables": True,
                "numbering_style": "arabic",
                "sections": "2-4",
                "estimated_length": "700-1200 words"
            }
        }

        return format_info.get(question_type, format_info["tom_tat"])

    def to_html(self, markdown_text: str) -> str:
        """Convert markdown to HTML (optional)"""
        try:
            import markdown
            return markdown.markdown(markdown_text, extensions=['tables', 'nl2br'])
        except ImportError:
            return f"<pre>{markdown_text}</pre>"

    def to_json_structure(self, text: str, question_type: str) -> Dict:
        """Convert text to structured JSON"""

        # Extract sections based on patterns
        sections = []

        # Find roman numeral sections
        section_pattern = r'((?:I{1,3}|IV|V|VI{0,3}|IX|X)\.\s+[^\n]+)'
        matches = re.finditer(section_pattern, text)

        for match in matches:
            section_title = match.group(1)
            # Find content until next section
            start = match.end()
            next_match = re.search(section_pattern, text[start:])
            end = start + next_match.start() if next_match else len(text)

            section_content = text[start:end].strip()

            sections.append({
                "title": section_title,
                "content": section_content
            })

        return {
            "question_type": question_type,
            "format_info": self.get_format_info(question_type),
            "sections": sections,
            "full_text": text
        }


# Test formatter
if __name__ == "__main__":
    formatter = ResponseFormatter()

    test_text = """
    ### TÓM TẮT NGHỊ QUYẾT

    I. Bối cảnh
    - Phát triển KHCN là yếu tố quyết định
    - Việt Nam còn khoảng cách xa với nước phát triển

    II. Mục tiêu
    | Chỉ tiêu | Giá trị |
    |----------|---------|
    | TFP      | >60%    |
    | R&D      | 2% GDP  |
    """

    formatted = formatter.format(test_text, "tom_tat")
    print("=== FORMATTED ===")
    print(formatted)

    print("\n=== FORMAT INFO ===")
    print(formatter.get_format_info("tom_tat"))

    print("\n=== JSON STRUCTURE ===")
    import json

    print(json.dumps(formatter.to_json_structure(test_text, "tom_tat"), indent=2, ensure_ascii=False))