# Financial-Document-Q&A-Assistant-
A powerful RAG (Retrieval-Augmented Generation) system that processes financial documents and provides intelligent Q&A capabilities using local language models.

🎯 Overview
This application transforms static financial documents (PDF, Excel, CSV) into interactive, queryable resources. Upload your financial statements, expense reports, or accounts data and ask questions in natural language to get instant, accurate answers.

✨ Features
📄 Multi-Format Support: PDF, Excel (.xlsx, .xls), and CSV files

🧠 Local AI Processing: Uses Ollama for privacy-focused, offline operation

💡 Smart Extraction: Optimized parsers for financial data structures

🔍 Advanced RAG: Vector-based retrieval with financial context awareness

💬 Interactive Chat: Clean Streamlit interface with persistent conversations

📊 Financial Intelligence: Understands accounting terminology and calculations

🚀 Quick Start
Prerequisites
Python 3.8 or higher

Ollama installed and running

4GB+ RAM recommended

Installation
Clone the repository

bash
git clone https://github.com/your-username/financial-qa-assistant.git
cd financial-qa-assistant
Install dependencies

bash
pip install -r requirements.txt
Install and setup Ollama

bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a model
ollama pull llama2
Run the application

bash
streamlit run main.py
Open your browser to http://localhost:8501

📁 Project Structure
text
financial-qa-assistant/
├── main.py                    # Streamlit web application
├── extractors/
│   ├── pdf_extraction.py     # PDF processing with multiple engines
│   └── excel_extraction.py   # Excel/CSV processing with financial optimization
├── processing/
│   └── qa_pipeline.py        # RAG pipeline with vector database
├── requirements.txt          # Python dependencies
├── chromadb/                 # Vector database (auto-created)
└── README.md
💻 Usage
1. Upload Documents
Drag and drop or select PDF, Excel, or CSV files

Supported formats: .pdf, .xlsx, .xls, .csv

Maximum recommended size: 200MB

2. Process Documents
Click "🚀 Process Document" to extract and index content

View extraction summary with document statistics

Processing time varies by document size and complexity

3. Ask Questions
Start asking questions about your financial data:

Example Questions:

"What is the total revenue for 2022?"

"Which expense category has the highest amount?"

"How many accounts receivable are overdue?"

"What is the net profit margin?"

"Show me the cash flow breakdown"

📋 Requirements
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
🔧 Configuration
Environment Variables
bash
# Optional customization
export CHROMADB_PATH="./custom_chromadb"
export CHUNK_SIZE="1500"
export RETRIEVAL_K="100"
Supported Models
Any Ollama-compatible model:

llama2 (recommended)

mistral

codellama

dolphin-mixtral

📊 Supported Document Types
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
Sample Test Cases
Upload the included sample files and try these questions:

For Expense-Claims.xlsx:

"What is the total amount of expense claims?"

"How many claims were approved vs rejected?"

"Which category has the most expenses?"

For Accounts-Receivable.xlsx:

"What is the total accounts receivable amount?"

"How many customers have outstanding balances?"

"Which currency has the most receivables?"

🛠️ Troubleshooting
Common Issues
Ollama Model Not Found

bash
# Check if Ollama is running
ollama list

# Pull missing model
ollama pull llama2
PDF Processing Errors

bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get install tesseract-ocr poppler-utils

# macOS
brew install tesseract poppler
Large File Processing

Reduce file size or split into smaller documents

Increase system RAM if possible

Use CSV format for large datasets when possible

Vector Database Issues

bash
# Clear and rebuild database
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

Commit your changes (git commit -m 'Add amazing feature')

Push to the branch (git push origin feature/amazing-feature)

Open a Pull Request

📈 Performance
Typical Processing Times
Small PDF (1-10 pages): 10-30 seconds

Excel file (100-1000 rows): 15-45 seconds

Large documents (1000+ records): 1-3 minutes

Query response: 2-10 seconds

System Requirements
Minimum: 4GB RAM, 2GB storage

Recommended: 8GB+ RAM, 5GB+ storage

CPU: Modern multi-core processor recommended

📄 
