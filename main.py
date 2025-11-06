"""
Hệ thống AI Tóm tắt Văn bản - FastAPI
Hỗ trợ: PDF, DOCX, XLSX, TXT
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import os
import shutil
from pathlib import Path

# Import các module khác
from parsers import DocumentParser
from classifier import QuestionClassifier
from summarizer import AISummarizer
from formatters import ResponseFormatter

app = FastAPI(
    title="AI Document Summarizer",
    description="Hệ thống tóm tắt văn bản thông minh",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Khởi tạo các components
parser = DocumentParser()
classifier = QuestionClassifier()
summarizer = AISummarizer()
formatter = ResponseFormatter()

# Tạo thư mục tạm
UPLOAD_DIR = Path("Downloads")
UPLOAD_DIR.mkdir(exist_ok=True)


class SummaryRequest(BaseModel):
    document_name: str
    question: str
    question_type: Optional[str] = None


class SummaryResponse(BaseModel):
    success: bool
    document_name: str
    question: str
    question_type: str
    answer: str
    format_info: dict
    metadata: dict


@app.get("/")
async def root():
    return {
        "message": "AI Document Summarizer API",
        "version": "1.0.0",
        "endpoints": {
            "/summarize": "POST - Tóm tắt văn bản từ file",
            "/health": "GET - Kiểm tra trạng thái"
        }
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "AI Summarizer"}


@app.post("/summarize", response_model=SummaryResponse)
async def summarize_document(
    file: UploadFile = File(...),
    question: str = Form(...),
    question_type: Optional[str] = Form(None)
):
    """
    API tóm tắt văn bản

    Parameters:
    - file: File upload (PDF, DOCX, XLSX, TXT)
    - question: Câu hỏi cần trả lời
    - question_type: (Optional) Loại câu hỏi
    """

    temp_file_path = None

    try:
        # 1. Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        allowed_exts = ['.pdf', '.docx', '.xlsx', '.xls', '.txt']

        if file_ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(allowed_exts)}"
            )

        # 2. Save uploaded file
        temp_file_path = UPLOAD_DIR / file.filename
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 3. Parse document
        print(f"📄 Parsing document: {file.filename}")
        document_content = parser.parse(str(temp_file_path))

        if not document_content:
            raise HTTPException(
                status_code=400,
                detail="Cannot extract content from document"
            )

        # 4. Classify question type
        if not question_type:
            print(f"🔍 Classifying question type...")
            question_type = classifier.classify(question)

        print(f"📝 Question type: {question_type}")

        # 5. Generate summary using AI
        print(f"🤖 Generating AI summary...")
        answer = summarizer.summarize(
            document_content=document_content,
            question=question,
            question_type=question_type
        )

        # 6. Format response
        formatted_answer = formatter.format(answer, question_type)

        # 7. Metadata
        metadata = {
            "file_name": file.filename,
            "file_size": os.path.getsize(temp_file_path),
            "file_type": file_ext,
            "content_length": len(document_content),
            "answer_length": len(formatted_answer)
        }

        return SummaryResponse(
            success=True,
            document_name=file.filename,
            question=question,
            question_type=question_type,
            answer=formatted_answer,
            format_info=formatter.get_format_info(question_type),
            metadata=metadata
        )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup temp file
        if temp_file_path and temp_file_path.exists():
            try:
                os.remove(temp_file_path)
            except:
                pass


@app.post("/batch-summarize")
async def batch_summarize(
    files: List[UploadFile] = File(...),
    questions: str = Form(...)  # JSON string of questions
):
    """
    API tóm tắt nhiều văn bản cùng lúc
    """
    import json

    try:
        questions_list = json.loads(questions)

        if len(files) != len(questions_list):
            raise HTTPException(
                status_code=400,
                detail="Number of files must match number of questions"
            )

        results = []

        for file, q in zip(files, questions_list):
            result = await summarize_document(
                file=file,
                question=q.get("question"),
                question_type=q.get("question_type")
            )
            results.append(result)

        return {"success": True, "results": results}

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid questions JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)