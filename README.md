<img width="1906" height="1021" alt="Screenshot 2025-09-18 233818" src="https://github.com/user-attachments/assets/5410d804-51ba-492a-a06f-8e856ad5bba4" />


# Financial Document Q&A Assistant

A powerful RAG (Retrieval-Augmented Generation) system that processes financial documents and provides intelligent Q&A capabilities using local language models.

🎯 Overview
Transform static financial documents (PDF, Excel, CSV) into interactive, queryable resources. Upload your financial statements, expense reports, or accounts data and ask questions in natural language to get instant, accurate answers.

✨ Key Features
📄 Multi-Format Support: PDF, Excel (.xlsx, .xls), and CSV files

🧠 Local AI Processing: Uses Ollama for privacy-focused, offline operation

💡 Smart Extraction: Optimized parsers for financial data structures

🔍 Advanced RAG: Vector-based retrieval with financial context awareness

💬 Interactive Chat: Clean Streamlit interface with persistent conversations

📊 Financial Intelligence: Understands accounting terminology and calculations

🚀 Quick Start
Prerequisites
Python 3.8+

Ollama installed and running

4GB+ RAM recommended

Installation
Clone the repository

bash
git clone repo-url
cd financial-qa-assistant
Install dependencies

bash
pip install -r requirements.txt
Install system dependencies (for PDF OCR)

bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
Setup Ollama

bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
Run the application

bash
streamlit run main.py
Open browser to http://localhost:8501

📁 Project Structure
text
financial-qa-assistant/
├── main.py                    # Streamlit web application
├── extractors/
│   ├── pdf_extraction.py     # PDF processing with multiple engines
│   └── excel_extraction.py   # Excel/CSV processing 
├── processing/
│   └── qa_pipeline.py        # RAG pipeline with vector database
├── requirements.txt          # Python dependencies
└── README.md


💻 Usage
1. Upload Documents
Select PDF, Excel, or CSV files using the file uploader

Supported formats: .pdf, .xlsx, .xls, .csv

Maximum recommended size: 200MB

2. Process Documents
Click "🚀 Process Document" to extract and index content

View extraction summary showing document statistics

Processing time varies by document size

3. Ask Questions
Example Questions:

"What is the total revenue for 2022?"

"Which expense category has the highest amount?"

"How many accounts receivable are overdue?"

"What is the net profit margin?"

"Show me the cash flow breakdown"

📋 Dependencies
text
streamlit==1.28.0
langchain==0.0.350
langchain-community==0.0.10
chromadb==0.4.18
pandas==2.1.0
pdfplumber==0.9.0
PyPDF2==3.0.1
openpyxl==3.1.2
pdf2image==1.16.3
pytesseract==0.3.10
ollama==0.1.7
📊 Supported Documents
PDF Documents
Financial statements (Income, Balance Sheet, Cash Flow)

Annual/quarterly reports

Invoices and receipts

Audit reports

Excel/CSV Files
Financial data spreadsheets

Expense claims and reports

Accounts receivable/payable

Budget and forecast data

🧪 Testing
Sample Questions by Document Type
For Expense Claims:

"What is the total amount of expense claims?"

"How many claims were approved vs rejected?"

"Which category has the most expenses?"

For Accounts Receivable:

"What is the total accounts receivable amount?"

"How many customers have outstanding balances?"

"Which currency has the most receivables?"

🛠️ Troubleshooting
Common Issues
Ollama Model Not Found

bash
ollama list
ollama pull llama2
PDF Processing Errors

Ensure tesseract and poppler are installed

Check file permissions and format

Large File Processing

Reduce file size or use CSV format for large datasets

Increase system RAM if possible

Vector Database Issues

bash
rm -rf chromadb/
# Restart app and reprocess documents
🔒 Privacy & Security
Local Processing: All data stays on your machine

No Cloud Dependency: Uses local Ollama models

Temporary Files: Automatically cleaned after processing

Vector Storage: Local Chroma database

🤝 Contributing
Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit changes (git commit -m 'Add amazing feature')

Push to branch (git push origin feature/amazing-feature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🙏 Acknowledgments
LangChain - LLM application framework

Streamlit - Web app framework

Ollama - Local LLM platform

Chroma - Vector database

📞 Support
🐛 Issues: Create an issue

💬 Discussions: Join discussions

📧 Contact: bathalamallikarjuna666@gmail.com
