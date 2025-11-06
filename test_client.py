"""
Test Client - Script để test API
"""

import requests
import json
from pathlib import Path
import sys


class APITester:
    """Client để test Document Summarizer API"""

    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url

    def health_check(self):
        """Kiểm tra server"""
        print("🔍 Checking server health...")
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Server is healthy!")
                print(f"   Response: {response.json()}")
                return True
            else:
                print(f"❌ Server returned status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Is it running?")
            return False

    def summarize(self, file_path: str, question: str, question_type: str = None):
        """Test summarize endpoint"""

        file_path = Path(file_path)

        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return None

        print(f"\n📄 Summarizing: {file_path.name}")
        print(f"❓ Question: {question}")

        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_path.name, f, 'application/octet-stream')}

                data = {'question': question}
                if question_type:
                    data['question_type'] = question_type

                print(f"⏳ Processing...")
                response = requests.post(
                    f"{self.base_url}/summarize",
                    files=files,
                    data=data,
                    timeout=120  # 2 minutes timeout
                )

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success!")
                print(f"📊 Question Type: {result['question_type']}")
                print(f"📏 Answer Length: {result['metadata']['answer_length']} chars")
                print("\n" + "=" * 60)
                print("ANSWER:")
                print("=" * 60)
                print(result['answer'])
                print("=" * 60)

                return result
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return None

        except requests.exceptions.Timeout:
            print("❌ Request timeout (>2 minutes)")
            return None
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None

    def batch_summarize(self, files_questions: list):
        """Test batch summarize"""

        print(f"\n📦 Batch processing {len(files_questions)} files...")

        try:
            files = []
            questions = []

            for item in files_questions:
                file_path = Path(item['file'])
                if not file_path.exists():
                    print(f"⚠️  Skipping {file_path.name} - file not found")
                    continue

                files.append(('files', open(file_path, 'rb')))
                questions.append({
                    'question': item['question'],
                    'question_type': item.get('question_type')
                })

            if not files:
                print("❌ No valid files to process")
                return None

            data = {'questions': json.dumps(questions)}

            print(f"⏳ Processing {len(files)} files...")
            response = requests.post(
                f"{self.base_url}/batch-summarize",
                files=files,
                data=data,
                timeout=300  # 5 minutes
            )

            # Close files
            for _, f in files:
                f.close()

            if response.status_code == 200:
                result = response.json()
                print(f"✅ Batch completed!")
                print(f"📊 Processed {len(result['results'])} files")
                return result
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"   {response.text}")
                return None

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return None


def main():
    """Main test function"""

    print("=" * 60)
    print("🤖 AI DOCUMENT SUMMARIZER - TEST CLIENT")
    print("=" * 60)

    tester = APITester()

    # 1. Health check
    if not tester.health_check():
        print("\n⚠️  Server is not running. Start it with:")
        print("   python main.py")
        sys.exit(1)

    # 2. Test single file
    print("\n" + "=" * 60)
    print("TEST 1: Single File Summarization")
    print("=" * 60)

    # Thay đổi đường dẫn file này
    test_file = "test_document.pdf"

    if Path(test_file).exists():
        result = tester.summarize(
            file_path=test_file,
            question="Tóm tắt tài liệu một cách ngắn gọn",
            question_type="tom_tat"
        )
    else:
        print(f"⚠️  Test file not found: {test_file}")
        print("   Please create a test file or update the path in test_client.py")

    # 3. Test batch (nếu có nhiều file)
    batch_files = [
        {
            'file': 'doc1.pdf',
            'question': 'Tóm tắt tài liệu',
            'question_type': 'tom_tat'
        },
        {
            'file': 'doc2.docx',
            'question': 'Mục tiêu chính là gì?',
            'question_type': 'muc_tieu'
        }
    ]

    # Check if files exist
    valid_batch = [item for item in batch_files if Path(item['file']).exists()]

    if len(valid_batch) >= 2:
        print("\n" + "=" * 60)
        print("TEST 2: Batch Processing")
        print("=" * 60)

        result = tester.batch_summarize(valid_batch)

    print("\n✅ Testing completed!")


if __name__ == "__main__":
    # Example usage:
    # python test_client.py

    # Hoặc dùng interactive:
    if len(sys.argv) > 1:
        tester = APITester()

        if sys.argv[1] == "health":
            tester.health_check()

        elif sys.argv[1] == "summarize":
            if len(sys.argv) < 4:
                print("Usage: python test_client.py summarize <file> <question>")
                sys.exit(1)

            tester.summarize(
                file_path=sys.argv[2],
                question=sys.argv[3],
                question_type=sys.argv[4] if len(sys.argv) > 4 else None
            )

        else:
            print("Unknown command. Available: health, summarize")

    else:
        # Run full test suite
        main()