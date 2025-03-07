import pdfplumber
import os
from openai import OpenAI
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_pdf_text(file_path):
    """
    Extract text and structure from a PDF file.
    
    Args:
        file_path (str): Path to the PDF file
        
    Returns:
        dict: Structured content of the PDF with sections
    """
    # Extract raw text from PDF
    raw_text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                raw_text += f"\n\n--- PAGE {page_num + 1} ---\n\n{text}"
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return {"status": "error", "message": str(e)}
    
    # Use GPT-4o-mini to identify and structure the content
    structured_content = extract_structure_with_gpt(raw_text, os.path.basename(file_path))
    
    return structured_content

def extract_structure_with_gpt(text, filename):
    """
    Use GPT-4o-mini to identify sections and structure the content.
    
    Args:
        text (str): Raw text extracted from the PDF
        filename (str): Name of the PDF file
        
    Returns:
        dict: Structured content of the PDF
    """
    try:
        # Limit input to avoid token limits (using first 15000 chars)
        text_sample = text[:15000]
        
        prompt = f"""
        Analyze the following research paper text and structure it into sections.
        Identify the following components:
        1. Title
        2. Authors
        3. Abstract
        4. Introduction
        5. Methods
        6. Results
        7. Discussion/Conclusion
        8. References
        
        For each section, extract the key information and organize it accordingly.
        If a section is not clearly present, indicate that it's missing or couldn't be identified.
        
        Format your response as a JSON object with these sections as keys.
        
        Text from the paper:
        {text_sample}
        
        Filename: {filename}
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a research paper analyzer. Extract and structure the content of academic papers."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        
        structured_content = json.loads(response.choices[0].message.content)
        
        # Add source information
        structured_content["source"] = {
            "filename": filename,
            "extraction_method": "gpt-4o-mini",
            "full_text_length": len(text)
        }
        
        return structured_content
    except Exception as e:
        print(f"Error structuring content with GPT: {e}")
        return {
            "status": "error",
            "message": f"Failed to structure content: {e}",
            "filename": filename,
            "raw_text_sample": text[:500] + "..." if len(text) > 500 else text
        }
