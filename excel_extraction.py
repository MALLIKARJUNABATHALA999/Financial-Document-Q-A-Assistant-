import logging
import tempfile
import os
from typing import List
import pandas as pd
from langchain.schema import Document

logger = logging.getLogger(__name__)

def _df_to_text(df: pd.DataFrame, title: str) -> str:
    """Convert DataFrame to comprehensive text representation with ALL data"""
    if df.empty:
        return ""
    
    lines = [
        f"=== {title} ===",
        f"Total Rows: {len(df)}",
        f"Total Columns: {len(df.columns)}",
        "",
        "COLUMN HEADERS: " + " | ".join(str(col) for col in df.columns),
        ""
    ]
    
    # Add complete numerical summary
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) > 0:
        lines.append("=== NUMERICAL SUMMARY ===")
        for col in numeric_cols:
            total = df[col].sum()
            mean = df[col].mean()
            count = df[col].count()
            min_val = df[col].min()
            max_val = df[col].max()
            lines.append(f"{col}: TOTAL={total:.2f}, AVERAGE={mean:.2f}, COUNT={count}, MIN={min_val:.2f}, MAX={max_val:.2f}")
        lines.append("")
    
    # Add categorical summary
    text_cols = df.select_dtypes(include=['object']).columns
    if len(text_cols) > 0:
        lines.append("=== CATEGORICAL SUMMARY ===")
        for col in text_cols:
            unique_count = df[col].nunique()
            top_values = df[col].value_counts().head(10)
            lines.append(f"{col}: {unique_count} unique values")
            for value, count in top_values.items():
                lines.append(f"  {value}: {count} occurrences")
        lines.append("")
    
    # *** CRITICAL: INCLUDE ALL DATA ROWS ***
    lines.append("=== ALL DATA ROWS ===")
    for i, (_, row) in enumerate(df.iterrows()):
        row_data = " | ".join(f"{col}:{str(row[col])}" for col in df.columns)
        lines.append(f"Row {i+1}: {row_data}")
    
    return "\n".join(lines)

def extract_from_excel(uploaded_file) -> List[Document]:
    """Enhanced Excel extraction that processes ALL data completely"""
    docs, tmp = [], None
    try:
        suffix = ".csv" if uploaded_file.name.lower().endswith(".csv") else ".xlsx"
        tmp = tempfile.mktemp(suffix=suffix)
        with open(tmp, "wb") as fh:
            fh.write(uploaded_file.getbuffer())

        if suffix == ".csv":
            # Read entire CSV file without limits
            df = pd.read_csv(tmp, encoding='utf-8', on_bad_lines='skip')
            df = df.fillna("")
            
            logger.info(f"CSV extraction: {len(df)} rows, {len(df.columns)} columns")
            
            # Create main document with ALL data
            content = _df_to_text(df, "Complete CSV Dataset")
            docs.append(Document(
                page_content=content,
                metadata={
                    "source": uploaded_file.name,
                    "type": "csv_complete",
                    "rows": len(df),
                    "columns": len(df.columns),
                    "original_filename": uploaded_file.name
                }
            ))
            
            # Create additional grouped chunks for better retrieval
            if len(df) > 100:  # Lower threshold for grouping
                for col in df.columns:
                    if df[col].dtype == 'object' and df[col].nunique() < 20:
                        for group_name, group_df in df.groupby(col):
                            if len(group_df) > 1:  # Include even small groups
                                group_content = _df_to_text(group_df, f"Category Group - {col}: {group_name}")
                                docs.append(Document(
                                    page_content=group_content,
                                    metadata={
                                        "source": uploaded_file.name,
                                        "type": "csv_group",
                                        "group_column": col,
                                        "group_value": str(group_name),
                                        "rows": len(group_df),
                                        "original_filename": uploaded_file.name
                                    }
                                ))
                        break  # Only group by first suitable column
            
            # Create financial summary chunk for numerical data
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                summary_lines = ["=== FINANCIAL SUMMARY ==="]
                for col in numeric_cols:
                    total = df[col].sum()
                    avg = df[col].mean()
                    count = df[col].count()
                    summary_lines.append(f"{col} TOTAL: {total:.2f}")
                    summary_lines.append(f"{col} AVERAGE: {avg:.2f}")
                    summary_lines.append(f"{col} COUNT: {count}")
                
                summary_content = "\n".join(summary_lines)
                docs.append(Document(
                    page_content=summary_content,
                    metadata={
                        "source": uploaded_file.name,
                        "type": "financial_summary",
                        "focus": "numerical_aggregates",
                        "original_filename": uploaded_file.name
                    }
                ))
            
        else:
            # Read Excel with all sheets and all rows
            try:
                sheets = pd.read_excel(tmp, sheet_name=None, engine='openpyxl')
            except:
                sheets = pd.read_excel(tmp, sheet_name=None, engine='xlrd')
            
            for sheet_name, df in sheets.items():
                df = df.fillna("")
                
                logger.info(f"Excel sheet '{sheet_name}': {len(df)} rows, {len(df.columns)} columns")
                
                # Create comprehensive sheet document
                content = _df_to_text(df, f"Excel Sheet: {sheet_name}")
                docs.append(Document(
                    page_content=content,
                    metadata={
                        "source": uploaded_file.name,
                        "sheet": sheet_name,
                        "type": "excel_sheet_complete",
                        "rows": len(df),
                        "columns": len(df.columns),
                        "original_filename": uploaded_file.name
                    }
                ))
                
                # Create additional chunks for large sheets
                if len(df) > 200:
                    chunk_size = 200
                    for i in range(0, len(df), chunk_size):
                        chunk_df = df.iloc[i:i+chunk_size]
                        chunk_content = _df_to_text(chunk_df, f"Sheet {sheet_name} - Rows {i+1} to {i+len(chunk_df)}")
                        docs.append(Document(
                            page_content=chunk_content,
                            metadata={
                                "source": uploaded_file.name,
                                "sheet": sheet_name,
                                "type": "excel_chunk",
                                "chunk_start": i+1,
                                "chunk_end": i+len(chunk_df),
                                "rows": len(chunk_df),
                                "original_filename": uploaded_file.name
                            }
                        ))
        
        logger.info(f"Excel/CSV extraction completed: {len(docs)} documents created from {uploaded_file.name}")
        return docs
        
    except Exception as e:
        logger.error(f"Excel/CSV extraction failed: {e}")
        return [Document(
            page_content=f"Error extracting Excel/CSV data: {str(e)}",
            metadata={"source": uploaded_file.name, "error": str(e)}
        )]
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
