# 🤖 AI Document Summarizer API

Hệ thống AI tóm tắt văn bản thông minh, hỗ trợ nhiều định dạng file (PDF, DOCX, XLSX, TXT).

## ✨ Tính năng

- ✅ Đọc nhiều loại file: PDF, DOCX, XLSX, TXT
- 🧠 AI thông minh với OpenAI hoặc Claude
- 📊 Tự động phân loại câu hỏi và format output
- 🎯 10+ loại câu hỏi được hỗ trợ
- ⚡ API nhanh với FastAPI
- 📦 Xử lý batch nhiều file

## 🚀 Cài đặt

### 1. Clone hoặc tạo project

```bash
mkdir doc_summarizer
cd doc_summarizer
```

### 2. Tạo cấu trúc thư mục

```
doc_summarizer/
├── main.py
├── parsers.py
├── classifier.py
├── summarizer.py
├── formatters.py
├── config.py
├── requirements.txt
├── .env
└── temp_uploads/
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình API Key

Tạo file `.env`:

```bash
# Dùng OpenAI
AI_PROVIDER=openai
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini

# Hoặc dùng Claude
# AI_PROVIDER=claude
# ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### 5. Chạy server

```bash
python main.py
```

Hoặc:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server chạy tại: http://localhost:8000

## 📖 Sử dụng API

### 1. Kiểm tra API

```bash
curl http://localhost:8000/health
```

### 2. Tóm tắt văn bản

**Python:**

```python
import requests

url = "http://localhost:8000/summarize"

files = {
    'file': open('document.pdf', 'rb')
}

data = {
    'question': 'Tóm tắt tài liệu một cách ngắn gọn',
    'question_type': 'tom_tat'  # Optional
}

response = requests.post(url, files=files, data=data)
result = response.json()

print(result['answer'])
```

**cURL:**

```bash
curl -X POST "http://localhost:8000/summarize" \
  -F "file=@document.pdf" \
  -F "question=Tóm tắt tài liệu" \
  -F "question_type=tom_tat"
```

**JavaScript:**

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('question', 'Tóm tắt tài liệu');

const response = await fetch('http://localhost:8000/summarize', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(result.answer);
```

### 3. Batch processing

```python
import requests
import json

url = "http://localhost:8000/batch-summarize"

files = [
    ('files', open('doc1.pdf', 'rb')),
    ('files', open('doc2.docx', 'rb'))
]

questions = json.dumps([
    {"question": "Tóm tắt tài liệu 1"},
    {"question": "Mục tiêu của tài liệu 2", "question_type": "muc_tieu"}
])

data = {'questions': questions}

response = requests.post(url, files=files, data=data)
results = response.json()
```

## 🎯 Các loại câu hỏi được hỗ trợ

| Loại | Từ khóa | Format Output |
|------|---------|---------------|
| **tom_tat** | tóm tắt, tổng hợp | Sections + Bullets |
| **muc_tieu** | mục tiêu, định hướng | Table + Metrics |
| **cach_thuc_hien** | làm thế nào, cách thực hiện | Steps + Sub-bullets |
| **ke_hoach** | kế hoạch, lộ trình | Table with timeline |
| **kho_khan** | khó khăn, thách thức | Sections + Examples |
| **ket_qua** | kết quả, thành tích | Metrics + Analysis |
| **so_sanh** | so sánh, xếp hạng | Comparison table |
| **goi_y** | gợi ý, đề xuất | Action items |
| **hieu_qua** | hiệu quả, tác động | Analysis + Metrics |
| **phuong_an** | phương án, giải pháp | Options + Comparison |

## 📋 Response Format

```json
{
  "success": true,
  "document_name": "report.pdf",
  "question": "Tóm tắt tài liệu",
  "question_type": "tom_tat",
  "answer": "### TÓM TẮT\n\nI. Phần 1...",
  "format_info": {
    "structure_type": "hierarchical",
    "has_tables": false,
    "sections": "3-6"
  },
  "metadata": {
    "file_size": 1048576,
    "content_length": 5000,
    "answer_length": 1200
  }
}
```

## 🔧 Cấu hình nâng cao

### Thay đổi model

File `.env`:
```bash
OPENAI_MODEL=gpt-4  # Dùng GPT-4 cho chất lượng cao hơn
MAX_TOKENS=8000     # Tăng độ dài output
```

### Custom format

Chỉnh sửa `classifier.py` để thêm loại câu hỏi mới:

```python
self.patterns["custom_type"] = [
    r"pattern1",
    r"pattern2"
]
```

## 🐛 Debug

### Bật logging

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test từng module

```bash
# Test parser
python parsers.py

# Test classifier
python classifier.py

# Test summarizer
python summarizer.py
```

## 📊 Performance

- PDF (10 trang): ~5-10 giây
- DOCX (20 trang): ~8-15 giây
- XLSX (nhiều sheet): ~10-20 giây

Tùy thuộc vào:
- Model AI được dùng
- Độ dài tài liệu
- Độ phức tạp câu hỏi

## 🔒 Bảo mật

- ⚠️ Không lưu file upload vĩnh viễn
- 🔐 API key nên dùng environment variables
- 🚫 Thêm authentication nếu deploy public
- 📝 Rate limiting cho production

## 🚢 Deploy

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```bash
docker build -t doc-summarizer .
docker run -p 8000:8000 --env-file .env doc-summarizer
```

### Cloud (Railway, Render, etc.)

1. Push code lên GitHub
2. Connect repository
3. Add environment variables
4. Deploy!

## 📞 Support

Có vấn đề? Kiểm tra:

1. ✅ API key đúng chưa?
2. ✅ File format có được hỗ trợ?
3. ✅ Dependencies đã cài đủ?
4. ✅ Port 8000 có bị chiếm?

## 📄 License

MIT License - Free to use!