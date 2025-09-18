import logging
import os
from typing import List
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.chat_models import ChatOllama
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

# Persistence directory for vector database
PERSIST_DIRECTORY = "./chromadb"
os.makedirs(PERSIST_DIRECTORY, exist_ok=True)

def create_vector_db(documents: List[Document]) -> Chroma:
    """
    Create optimized vector database for financial documents
    
    Key optimizations:
    1. Smaller chunks with more overlap for Excel data
    2. Enhanced metadata for better retrieval
    3. Priority-based document classification
    """
    logger.info(f"Creating vector DB from {len(documents)} documents")
    
    # Optimized splitter for Excel financial data
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,      # Smaller chunks to preserve context
        chunk_overlap=300,    # More overlap to maintain continuity
        separators=[
            "\n\n", "\n", 
            "===", "TOTAL", "SUMMARY", "BREAKDOWN",
            "---", "|", ",", " "
        ],
        keep_separator=True
    )
    
    chunks = splitter.split_documents(documents)
    
    # Enhanced metadata for better retrieval prioritization
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
        chunk.metadata["chunk_size"] = len(chunk.page_content)
        
        content = chunk.page_content.lower()
        
        # Highest priority: Financial summaries and totals
        if any(term in content for term in [
            "total records:", "total amount:", "financial summary", 
            "total:", "sum:", "breakdown"
        ]):
            chunk.metadata["priority"] = "critical"
            chunk.metadata["contains_totals"] = True
            
        # High priority: Calculations and aggregates  
        elif any(term in content for term in [
            "calculation:", "average:", "count:", "distribution"
        ]):
            chunk.metadata["priority"] = "high"
            chunk.metadata["contains_calculations"] = True
            
        # Medium priority: Individual records
        elif any(term in content for term in ["record", "row", "data"]):
            chunk.metadata["priority"] = "medium" 
            chunk.metadata["contains_records"] = True
        else:
            chunk.metadata["priority"] = "low"
    
    # Create vector store
    embedder = OllamaEmbeddings(model="nomic-embed-text")
    vector_db = Chroma.from_documents(
        chunks, 
        embedder, 
        collection_name="financial_rag",
        persist_directory=PERSIST_DIRECTORY
    )
    
    vector_db.persist()
    logger.info(f"Vector DB created with {len(chunks)} chunks")
    return vector_db

def process_question_with_rag(question: str, vector_db: Chroma, model_name: str) -> str:
    """
    Process financial questions with optimized RAG retrieval
    
    Key improvements:
    1. Increased k parameter for better Excel data coverage
    2. Multi-query retrieval for comprehensive results
    3. Strict anti-hallucination prompt
    """
    if vector_db is None:
        return "Please upload and process a financial document first."

    try:
        llm = ChatOllama(model=model_name, temperature=0)

        # Multi-query generation for comprehensive retrieval
        query_prompt = PromptTemplate(
            input_variables=["question"],
            template="""
You are a financial analyst generating search queries for document retrieval.
Create 3 different search queries to find comprehensive information.

Original question: {question}

Generate these specific queries:
1. Query for summary and totals
2. Query for detailed data records  
3. Query for calculations and breakdowns

Query 1:
Query 2:
Query 3:
            """.strip()
        )

        # CRITICAL: Increased k for chunked Excel data coverage
        # Excel data gets split into many chunks, so we need more retrieval
        base_retriever = vector_db.as_retriever(
            search_kwargs={
                "k": 100,  # Significantly increased from 50 to 100
            }
        )
        
        retriever = MultiQueryRetriever.from_llm(
            base_retriever,
            llm,
            prompt=query_prompt,
            include_original=True  # Fixed typo from "Trueacc"
        )

        # Enhanced financial analysis prompt
        financial_prompt = """
You are a professional financial data analyst with access to financial documents.

CONTEXT:
{context}

QUESTION: {question}

CRITICAL ANALYSIS RULES:
1. Use ONLY the data explicitly provided in the context above
2. When you see "TOTAL RECORDS: X" - that's the exact count
3. When you see "TOTAL AMOUNT: $X" - use that exact figure
4. Sum individual amounts from records if no total is provided
5. Count actual data records, NOT document chunks
6. Use exact percentages and breakdowns as shown
7. Never invent or assume data not in the context
8. If information is missing, clearly state what's unavailable
9. Reference specific context sections in your answer
10. Format financial amounts with proper precision ($X,XXX.XX)

FINANCIAL ANALYSIS:
        """.strip()
        
        prompt_chain = ChatPromptTemplate.from_template(financial_prompt)

        # Build the RAG chain
        rag_chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt_chain
            | llm
            | StrOutputParser()
        )

        # Execute the chain
        result = rag_chain.invoke(question)
        
        # Quality checks
        if "insufficient" in result.lower() and "total" in question.lower():
            logger.warning("Total query returned insufficient - may need more retrieval")
        
        logger.info("Successfully processed financial question with enhanced RAG")
        return result

    except Exception as e:
        logger.error(f"RAG processing failed: {e}")
        return f"Error: {str(e)}. Please try rephrasing your question."

def load_existing_vector_db() -> Chroma:
    """Load existing vector database from disk"""
    try:
        embedder = OllamaEmbeddings(model="nomic-embed-text")
        vector_db = Chroma(
            collection_name="financial_rag",
            embedding_function=embedder,
            persist_directory=PERSIST_DIRECTORY
        )
        logger.info("Loaded existing vector database")
        return vector_db
    except Exception as e:
        logger.error(f"Failed to load vector DB: {e}")
        return None

def debug_retrieval(question: str, vector_db: Chroma, k: int = 20) -> List[Document]:
    """Debug function to inspect what documents are being retrieved"""
    try:
        docs = vector_db.similarity_search(question, k=k)
        logger.info(f"Retrieved {len(docs)} documents for: '{question[:50]}...'")
        
        # Show priority distribution
        priorities = {}
        for doc in docs:
            priority = doc.metadata.get("priority", "unknown")
            priorities[priority] = priorities.get(priority, 0) + 1
        
        logger.info(f"Priority distribution: {priorities}")
        return docs
    except Exception as e:
        logger.error(f"Debug retrieval failed: {e}")
        return []

def clear_vector_db():
    """Clear the vector database for fresh start"""
    try:
        if os.path.exists(PERSIST_DIRECTORY):
            import shutil
            shutil.rmtree(PERSIST_DIRECTORY)
            os.makedirs(PERSIST_DIRECTORY, exist_ok=True)
            logger.info("Vector database cleared")
    except Exception as e:
        logger.error(f"Failed to clear vector DB: {e}")
