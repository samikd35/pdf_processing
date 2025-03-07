import os
import pdfplumber
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def process_pdf(file_path):
    """
    Process PDF file: extract text, generate metadata, and split into chunks.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        tuple: (chunks, metadata) where chunks is a list of text chunks and metadata is a dict
    """
    # Extract text from PDF
    raw_text = extract_text_from_pdf(file_path)
    
    # Extract metadata using GPT-4o-mini
    metadata = extract_metadata_with_gpt(raw_text, os.path.basename(file_path))
    
    # Split text into chunks
    chunks = split_into_chunks(raw_text, chunk_size=2000, overlap=200)
    
    return chunks, metadata

def extract_text_from_pdf(file_path):
    """Extract text from PDF file using pdfplumber."""
    full_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                full_text += page_text + "\n\n"
        return full_text
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        raise

def extract_metadata_with_gpt(text, filename):
    """
    Extract metadata from the text using GPT-4o-mini.
    
    Args:
        text (str): Text content of the PDF
        filename (str): Name of the PDF file
        
    Returns:
        dict: Metadata extracted from the PDF
    """
    # Use only the first 6000 characters for metadata extraction
    # This typically includes title, authors, abstract, etc.
    text_sample = text[:6000]
    
    try:
        prompt = f"""
        Extract metadata from this research paper. Based on the text provided, identify:
        1. Title of the paper
        2. Authors (as a list)
        3. Publication year
        4. Journal or conference name (if available)
        5. DOI (if available)
        6. Keywords or topics
        7. Abstract
        
        Format your response as a JSON object with these keys.
        
        Text sample from the paper:
        {text_sample}
        
        Filename: {filename}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a research paper metadata extractor. Extract structured metadata from academic papers."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        metadata = json.loads(response.choices[0].message.content)
        
        # Add source filename to metadata
        metadata["source_filename"] = filename
        
        return metadata
    except Exception as e:
        print(f"Error extracting metadata with GPT: {e}")
        # Return basic metadata if extraction fails
        return {
            "title": "Unknown Title",
            "authors": [],
            "publication_year": None,
            "journal": None,
            "doi": None,
            "keywords": [],
            "abstract": None,
            "source_filename": filename
        }

def split_into_chunks(text, chunk_size=2000, overlap=200):
    """
    Split text into overlapping chunks of approximately chunk_size characters.
    
    Args:
        text (str): Text to split into chunks
        chunk_size (int): Approximate size of each chunk in characters
        overlap (int): Number of characters to overlap between chunks
        
    Returns:
        list: List of text chunks
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Get chunk of text
        end = min(start + chunk_size, text_length)
        
        # If this is not the last chunk, try to end at a paragraph break or sentence end
        if end < text_length:
            # Look for paragraph break within the last 20% of the chunk
            paragraph_break = text.rfind("\n\n", start + int(chunk_size * 0.8), end)
            
            if paragraph_break != -1:
                end = paragraph_break + 2  # Include the paragraph break
            else:
                # Look for sentence end (period followed by space or newline)
                sentence_end = -1
                for pattern in [". ", ".\n", "? ", "?\n", "! ", "!\n"]:
                    pos = text.rfind(pattern, start + int(chunk_size * 0.8), end)
                    if pos > sentence_end:
                        sentence_end = pos + len(pattern)
                
                if sentence_end != -1:
                    end = sentence_end
        
        # Add chunk to list
        chunks.append(text[start:end])
        
        # Move start position for next chunk, considering overlap
        start = end - overlap if end < text_length else text_length
    
    return chunks
