import logging
import tempfile
import os
from typing import List
import pdfplumber
from PyPDF2 import PdfReader
from pdf2image import convert_from_path
import pytesseract
from langchain.schema import Document

logger = logging.getLogger(__name__)

def _text_pdfplumber(path: str) -> List[Document]:
    docs = []
    try:
        with pdfplumber.open(path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                txt = page.extract_text() or ""
                if txt.strip():
                    docs.append(Document(
                        page_content=txt,
                        metadata={
                            "source": path,
                            "page": i,
                            "method": "pdfplumber",
                            "char_count": len(txt)
                        }
                    ))
        logger.info(f"pdfplumber extracted {len(docs)} pages")
    except Exception as e:
        logger.warning(f"pdfplumber failed: {e}")
    return docs

def _text_pypdf(path: str) -> List[Document]:
    docs = []
    try:
        reader = PdfReader(path)
        for i, page in enumerate(reader.pages, 1):
            txt = page.extract_text() or ""
            if txt.strip():
                docs.append(Document(
                    page_content=txt,
                    metadata={
                        "source": path,
                        "page": i,
                        "method": "pypdf",
                        "char_count": len(txt)
                    }
                ))
        logger.info(f"PyPDF2 extracted {len(docs)} pages")
    except Exception as e:
        logger.warning(f"PyPDF2 failed: {e}")
    return docs

def _text_ocr(path: str, dpi=150) -> List[Document]:
    docs = []
    try:
        for i, img in enumerate(convert_from_path(path, dpi=dpi), 1):
            txt = pytesseract.image_to_string(img)
            if txt.strip():
                docs.append(Document(
                    page_content=txt,
                    metadata={
                        "source": path,
                        "page": i,
                        "method": "ocr",
                        "char_count": len(txt)
                    }
                ))
        logger.info(f"OCR extracted {len(docs)} pages")
    except Exception as e:
        logger.error(f"OCR failed: {e}")
    return docs

def _tables(path: str) -> List[Document]:
    docs = []
    try:
        with pdfplumber.open(path) as pdf:
            for p, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables() or []
                for t_idx, tbl in enumerate(tables, 1):
                    if not tbl:
                        continue
                        
                    # Better table processing
                    rows = []
                    headers = None
                    
                    for row_idx, row in enumerate(tbl):
                        if not any(cell for cell in row if cell):  # Skip empty rows
                            continue
                            
                        clean_row = [str(cell or "").strip() for cell in row]
                        
                        if row_idx == 0 and not headers:
                            headers = clean_row
                            rows.append("HEADERS: " + " | ".join(headers))
                        else:
                            if headers:
                                row_data = []
                                for i, cell in enumerate(clean_row):
                                    col_name = headers[i] if i < len(headers) else f"Col{i+1}"
                                    row_data.append(f"{col_name}: {cell}")
                                rows.append(" | ".join(row_data))
                            else:
                                rows.append(" | ".join(clean_row))
                    
                    if rows:
                        table_content = f"TABLE {t_idx} (Page {p}):\n" + "\n".join(rows)
                        docs.append(Document(
                            page_content=table_content,
                            metadata={
                                "source": path,
                                "page": p,
                                "type": "table",
                                "table_id": t_idx,
                                "rows": len(rows),
                                "method": "table_extraction"
                            }
                        ))
        logger.info(f"Extracted {len(docs)} tables")
    except Exception as e:
        logger.warning(f"Table extraction failed: {e}")
    return docs

def extract_from_pdf(uploaded_file, enable_ocr=True) -> List[Document]:
    tmp = tempfile.mktemp(suffix=".pdf")
    try:
        with open(tmp, "wb") as fh:
            fh.write(uploaded_file.getbuffer())
        
        # Try multiple extraction methods
        docs = (_text_pdfplumber(tmp) or 
                _text_pypdf(tmp) or 
                (_text_ocr(tmp) if enable_ocr else []))
        
        # Always try to extract tables
        table_docs = _tables(tmp)
        docs.extend(table_docs)
        
        # Update metadata with original filename
        for d in docs:
            d.metadata["original_filename"] = uploaded_file.name
            
        logger.info(f"PDF extraction completed: {len(docs)} documents ({len([d for d in docs if d.metadata.get('type') != 'table'])} text pages, {len(table_docs)} tables)")
        
        return docs or [Document(
            page_content="No text extracted from PDF",
            metadata={"source": uploaded_file.name, "error": "no_content"}
        )]
        
    except Exception as e:
        logger.error(f"PDF extraction fatal: {e}")
        return [Document(
            page_content=f"Error extracting PDF: {e}",
            metadata={"source": uploaded_file.name, "error": str(e)}
        )]
    finally:
        try:
            os.remove(tmp)
        except Exception:
            pass
