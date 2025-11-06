"""
Hệ thống AI Tóm tắt Văn bản - FastAPI
Hỗ trợ: PDF, DOCX, XLSX, TXT + Token tracking + Cost calculation
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import os
import shutil
from pathlib import Path

# Import các module
from parsers import DocumentParser
from classifier import QuestionClassifier
from summarizer import AISummarizer
from formatters import ResponseFormatter
from config import Config

app = FastAPI(
    title="AI Document Summarizer",
    description="Hệ thống tóm tắt văn bản thông minh với tracking chi phí",
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

# Khởi tạo components
parser = DocumentParser()
classifier = QuestionClassifier()
summarizer = AISummarizer()
formatter = ResponseFormatter()

# Tạo thư mục tạm
UPLOAD_DIR = Path("Downloads")
UPLOAD_DIR.mkdir(exist_ok=True)


class UsageInfo(BaseModel):
    """Token usage information"""
    input_tokens: int
    output_tokens: int
    total_tokens: int


class CostInfo(BaseModel):
    """Cost calculation"""
    input_cost: float
    output_cost: float
    total_cost: float
    currency: str
    pricing_per_1k: Dict[str, float]


class SummaryResponse(BaseModel):
    success: bool
    document_name: str
    question: str
    question_type: str
    answer: str
    format_info: dict
    metadata: dict
    usage: UsageInfo
    cost: CostInfo
    model_info: dict


@app.get("/")
async def root():
    return {
        "message": "AI Document Summarizer API",
        "version": "1.0.0",
        "endpoints": {
            "/summarize": "POST - Tóm tắt văn bản từ file",
            "/health": "GET - Kiểm tra trạng thái",
            "/config": "GET - Xem cấu hình và giá",
            "/batch-summarize": "POST - Xử lý nhiều file"
        }
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Summarizer",
        "provider": Config.AI_PROVIDER,
        "model": Config.OPENAI_MODEL if Config.AI_PROVIDER == "openai" else Config.CLAUDE_MODEL
    }


@app.get("/config")
async def get_config():
    """Xem thông tin cấu hình và giá"""
    return Config.get_info()


@app.post("/summarize", response_model=SummaryResponse)
async def summarize_document(
    file: UploadFile = File(...),
    question: str = Form(...),
    question_type: Optional[str] = Form(None)
):
    """
    API tóm tắt văn bản với tracking chi phí

    Parameters:
    - file: File upload (PDF, DOCX, XLSX, TXT)
    - question: Câu hỏi cần trả lời
    - question_type: (Optional) Loại câu hỏi

    Returns:
    - answer: Câu trả lời
    - usage: Token usage
    - cost: Chi phí API
    - metadata: Thông tin file
    """

    temp_file_path = None

    try:
        # 1. Validate file
        file_ext = Path(file.filename).suffix.lower()
        allowed_exts = ['.pdf', '.docx', '.xlsx', '.xls', '.txt']

        if file_ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"File type not supported. Allowed: {', '.join(allowed_exts)}"
            )

        # 2. Save file
        temp_file_path = UPLOAD_DIR / file.filename
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = os.path.getsize(temp_file_path)
        file_size_mb = round(file_size / (1024 * 1024), 2)

        # 3. Parse document
        print(f"📄 Parsing: {file.filename} ({file_size_mb} MB)")
        document_content = parser.parse(str(temp_file_path))

        if not document_content:
            raise HTTPException(
                status_code=400,
                detail="Cannot extract content from document"
            )

        # 4. Classify question
        if not question_type:
            print(f"🔍 Classifying question...")
            question_type = classifier.classify(question)

        print(f"📝 Type: {question_type}")

        # 5. Generate summary with AI
        print(f"🤖 Generating summary...")
        result = summarizer.summarize(
            document_content=document_content,
            question=question,
            question_type=question_type
        )

        answer = result["answer"]
        usage_info = result["usage"]
        model_used = result["model"]
        provider = result["provider"]

        # 6. Calculate cost
        cost_info = Config.calculate_cost(
            input_tokens=usage_info["input_tokens"],
            output_tokens=usage_info["output_tokens"],
            model=model_used,
            provider=provider
        )

        # Get pricing info
        pricing = Config.get_pricing(model_used, provider)

        # 7. Format response
        formatted_answer = formatter.format(answer, question_type)

        # 8. Build metadata
        metadata = {
            "file_name": file.filename,
            "file_size_bytes": file_size,
            "file_size_mb": file_size_mb,
            "file_type": file_ext,
            "content_length": len(document_content),
            "answer_length": len(formatted_answer)
        }

        # 9. Log info
        print(f"✅ Success!")
        print(f"📊 Tokens: {usage_info['total_tokens']} (in: {usage_info['input_tokens']}, out: {usage_info['output_tokens']})")
        print(f"💰 Cost: ${cost_info['total_cost']:.6f}")

        return SummaryResponse(
            success=True,
            document_name=file.filename,
            question=question,
            question_type=question_type,
            answer=formatted_answer,
            format_info=formatter.get_format_info(question_type),
            metadata=metadata,
            usage=UsageInfo(**usage_info),
            cost=CostInfo(
                **cost_info,
                pricing_per_1k={
                    "input": pricing["input"],
                    "output": pricing["output"]
                }
            ),
            model_info={
                "provider": provider,
                "model": model_used
            }
        )

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # Cleanup
        if temp_file_path and temp_file_path.exists():
            try:
                os.remove(temp_file_path)
            except:
                pass


@app.post("/batch-summarize")
async def batch_summarize(
    files: List[UploadFile] = File(...),
    questions: str = Form(...)
):
    """
    API tóm tắt nhiều văn bản
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
        total_cost = 0.0
        total_tokens = 0

        for file, q in zip(files, questions_list):
            result = await summarize_document(
                file=file,
                question=q.get("question"),
                question_type=q.get("question_type")
            )
            results.append(result)
            total_cost += result.cost.total_cost
            total_tokens += result.usage.total_tokens

        return {
            "success": True,
            "results": results,
            "summary": {
                "total_files": len(files),
                "total_tokens": total_tokens,
                "total_cost": round(total_cost, 6),
                "currency": "USD"
            }
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid questions JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats/pricing")
async def get_pricing_info():
    """Xem bảng giá chi tiết"""
    provider = Config.AI_PROVIDER

    if provider == "openai":
        pricing_table = Config.OPENAI_PRICING
    else:
        pricing_table = Config.CLAUDE_PRICING

    return {
        "provider": provider,
        "current_model": Config.OPENAI_MODEL if provider == "openai" else Config.CLAUDE_MODEL,
        "pricing_table": pricing_table,
        "currency": "USD",
        "unit": "per 1,000 tokens",
        "note": "Prices updated November 2024"
    }


if __name__ == "__main__":
    import uvicorn

    # Validate config
    try:
        Config.validate()
        print("✅ Configuration validated")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        exit(1)

    uvicorn.run(app, host="0.0.0.0", port=5000)