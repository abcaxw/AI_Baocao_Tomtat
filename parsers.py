"""
Document Parsers - Đọc PDF, DOCX, XLSX
"""

import PyPDF2
from docx import Document
import pandas as pd
from pathlib import Path
from typing import Optional


class DocumentParser:
    """Parse các loại file khác nhau"""

    def parse(self, file_path: str) -> str:
        """
        Parse file và trả về text content
        """
        file_path = Path(file_path)
        ext = file_path.suffix.lower()

        parsers = {
            '.pdf': self._parse_pdf,
            '.docx': self._parse_docx,
            '.xlsx': self._parse_xlsx,
            '.xls': self._parse_xlsx,
            '.txt': self._parse_txt
        }

        parser_func = parsers.get(ext)
        if not parser_func:
            raise ValueError(f"Unsupported file type: {ext}")

        return parser_func(file_path)

    def _parse_pdf(self, file_path: Path) -> str:
        """Parse PDF file"""
        try:
            text = ""
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing PDF: {str(e)}")

    def _parse_docx(self, file_path: Path) -> str:
        """Parse DOCX file"""
        try:
            doc = Document(file_path)
            text = ""

            # Extract paragraphs
            for para in doc.paragraphs:
                text += para.text + "\n"

            # Extract tables
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join([cell.text for cell in row.cells])
                    text += row_text + "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing DOCX: {str(e)}")

    def _parse_xlsx(self, file_path: Path) -> str:
        """Parse XLSX/XLS file"""
        try:
            # Read all sheets
            excel_file = pd.ExcelFile(file_path)
            text = ""

            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)

                text += f"\n=== Sheet: {sheet_name} ===\n"

                # Convert to markdown-style table
                text += df.to_markdown(index=False) if hasattr(df, 'to_markdown') else df.to_string()
                text += "\n"

            return text.strip()
        except Exception as e:
            raise Exception(f"Error parsing Excel: {str(e)}")

    def _parse_txt(self, file_path: Path) -> str:
        """Parse TXT file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read().strip()
        except Exception as e:
            raise Exception(f"Error parsing TXT: {str(e)}")

    def get_metadata(self, file_path: str) -> dict:
        """Lấy metadata của file"""
        file_path = Path(file_path)

        return {
            "filename": file_path.name,
            "extension": file_path.suffix,
            "size_bytes": file_path.stat().st_size,
            "size_mb": round(file_path.stat().st_size / (1024 * 1024), 2)
        }


# Test parser
if __name__ == "__main__":
    parser = DocumentParser()

    # Test với file mẫu
    test_file = "test.pdf"
    if Path(test_file).exists():
        content = parser.parse(test_file)
        print(f"Extracted {len(content)} characters")
        print(f"Preview: {content[:500]}...")