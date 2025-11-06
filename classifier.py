"""
Question Classifier - Phân loại loại câu hỏi
"""

import re
from typing import Dict, List


class QuestionClassifier:
    """Phân loại câu hỏi theo pattern"""

    def __init__(self):
        # Định nghĩa patterns cho từng loại câu hỏi
        self.patterns = {
            "tom_tat": [
                r"tóm tắt",
                r"tổng hợp",
                r"trình bày",
                r"nêu rõ",
                r"overview",
                r"summarize"
            ],
            "muc_tieu": [
                r"mục tiêu",
                r"mục đích",
                r"định hướng",
                r"target",
                r"objective",
                r"goal"
            ],
            "cach_thuc_hien": [
                r"làm thế nào",
                r"cách thực hiện",
                r"cách làm",
                r"triển khai",
                r"how to",
                r"implementation"
            ],
            "ke_hoach": [
                r"kế hoạch",
                r"lộ trình",
                r"roadmap",
                r"xây dựng.*kế hoạch",
                r"plan"
            ],
            "kho_khan": [
                r"khó khăn",
                r"vướng mắc",
                r"thách thức",
                r"hạn chế",
                r"rào cản",
                r"challenge",
                r"difficulty"
            ],
            "ket_qua": [
                r"kết quả",
                r"thành tích",
                r"đạt được",
                r"hoàn thành",
                r"result",
                r"achievement"
            ],
            "so_sanh": [
                r"so sánh",
                r"đối chiếu",
                r"xếp hạng",
                r"nào.*nhất",
                r"comparison",
                r"ranking"
            ],
            "goi_y": [
                r"gợi ý",
                r"đề xuất",
                r"khuyến nghị",
                r"suggestion",
                r"recommendation"
            ],
            "hieu_qua": [
                r"hiệu quả",
                r"tác động",
                r"ảnh hưởng",
                r"impact",
                r"effect"
            ],
            "phuong_an": [
                r"phương án",
                r"giải pháp",
                r"cách khác",
                r"lựa chọn",
                r"alternative",
                r"solution"
            ]
        }

    def classify(self, question: str) -> str:
        """
        Phân loại câu hỏi dựa trên patterns
        """
        question_lower = question.lower()

        # Check từng pattern
        for qtype, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, question_lower):
                    return qtype

        # Default: tóm tắt
        return "tom_tat"

    def get_format_template(self, question_type: str) -> Dict:
        """
        Trả về template format cho từng loại câu hỏi
        """
        templates = {
            "tom_tat": {
                "structure": ["title", "sections", "bullets", "conclusion"],
                "sections": [3, 6],
                "include_tables": False,
                "numbering": "roman"
            },
            "muc_tieu": {
                "structure": ["overview", "table", "metrics"],
                "include_tables": True,
                "numbering": "roman"
            },
            "cach_thuc_hien": {
                "structure": ["numbered_sections", "sub_bullets", "steps"],
                "sections": [5, 8],
                "numbering": "roman",
                "include_tables": False
            },
            "ke_hoach": {
                "structure": ["table", "timeline", "phases"],
                "include_tables": True,
                "table_columns": ["Nhiệm vụ", "Hoạt động", "Thời gian", "Căn cứ"]
            },
            "kho_khan": {
                "structure": ["sections", "bullets", "examples"],
                "sections": [3, 5],
                "numbering": "roman"
            },
            "ket_qua": {
                "structure": ["overview", "metrics", "bullets"],
                "include_tables": True,
                "numbering": "roman"
            },
            "so_sanh": {
                "structure": ["table", "analysis", "ranking"],
                "include_tables": True,
                "table_columns": ["Đơn vị", "Chỉ tiêu", "Kết quả", "Ghi chú"]
            },
            "goi_y": {
                "structure": ["sections", "action_items", "priority"],
                "sections": [3, 5],
                "numbering": "roman"
            },
            "hieu_qua": {
                "structure": ["overview", "metrics", "analysis"],
                "include_tables": True,
                "numbering": "roman"
            },
            "phuong_an": {
                "structure": ["options", "comparison", "recommendation"],
                "include_tables": True,
                "numbering": "arabic"
            }
        }

        return templates.get(question_type, templates["tom_tat"])

    def get_all_types(self) -> List[str]:
        """Trả về danh sách tất cả các loại câu hỏi"""
        return list(self.patterns.keys())


# Test classifier
if __name__ == "__main__":
    classifier = QuestionClassifier()

    test_questions = [
        "Tóm tắt tài liệu một cách ngắn gọn",
        "Mục tiêu đến năm 2030 là gì?",
        "Làm thế nào để thực hiện nghị quyết này?",
        "Xây dựng kế hoạch triển khai",
        "Khó khăn gì khi thực hiện?",
        "Kết quả thực hiện của xã Vân Hồ",
        "Xã nào đang thực hiện chậm nhất?",
        "Gợi ý các công việc tiếp theo"
    ]

    print("=== Testing Question Classifier ===\n")
    for q in test_questions:
        qtype = classifier.classify(q)
        template = classifier.get_format_template(qtype)
        print(f"Q: {q}")
        print(f"Type: {qtype}")
        print(f"Structure: {template['structure']}\n")