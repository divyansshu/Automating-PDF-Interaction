"""
pdf_processor.py
----------------
Handles PDF reading, text extraction, cleaning, and chunking for the
'Automating PDF Interaction using LangChain and Open-Source LLMs' project.
"""

import os
from typing import List, Dict
from pypdf import PdfReader

def extract_text_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Extracts text from each page of the given PDF.

    Args:
        pdf_path (str): Path to the uploaded PDF file.

    Returns:
        List[Dict]: A list of dictionaries, each containing
                    {'page': int, 'text': str}.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    reader = PdfReader(pdf_path)
    pages_data = []
    
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        clean_text = clean_pdf_text(text)
        pages_data.append({
            "page": i+1,
            "text": clean_text
        })
    return pages_data        

def clean_pdf_text(text: str) ->str:
    """
    Cleans extracted PDF text by removing unwanted spaces, line breaks, etc.

    Args:
        text (str): Raw extracted text.

    Returns:
        str: Cleaned text.
    """
    # Normalize whitespaces and remove multiple line breaks
    text = text.replace("\n", " ").replace("\r", " ")
    text = " ".join(text.split())
    return text.strip()

def chunk_text(text: str, max_words: int = 200, overlap: int = 50) -> List[str]:
    """
    Splits text into overlapping chunks for embedding generation.

    Args:
        text (str): The input text string.
        max_words (int): Maximum number of words per chunk.
        overlap (int): Number of overlapping words between chunks.

    Returns:
        List[str]: List of text chunks.
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + max_words
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += max_words - overlap

    return chunks


def prepare_chunks_from_pdf(pdf_path: str) -> List[Dict]:
    """
    Complete preprocessing pipeline:
    1. Extract text from PDF
    2. Clean text
    3. Chunk text
    Combines all pages into a single structured list.

    Args:
        pdf_path (str): Path to the PDF file.

    Returns:
        List[Dict]: List of chunk dictionaries with page and text.
    """
    pages = extract_text_from_pdf(pdf_path)
    all_chunks = []

    for page_data in pages:
        chunks = chunk_text(page_data["text"])
        for idx, chunk in enumerate(chunks):
            all_chunks.append({
                "page": page_data["page"],
                "chunk_id": idx + 1,
                "text": chunk
            })

    return all_chunks

if __name__ == "__main__":
    pdf_path = "sample_pdf.pdf"
    try:
        chunks = prepare_chunks_from_pdf(pdf_path)
        print(f" Successfully extracted {len(chunks)} text chunks.\n")

        # Display the first few chunks for verification
        for i, chunk in enumerate(chunks[:5], start=1):
            print(f"--- Chunk {i} (Page {chunk['page']}, ID {chunk['chunk_id']}) ---")
            print(chunk["text"][:300], "...\n")  # print first 300 chars for readability

    except FileNotFoundError:
        print(f" Error: The file '{pdf_path}' was not found.")
    except Exception as e:
        print(f" Unexpected Error: {e}")