import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field
import ollama
from utils.pdf_parser import extract_text_from_pdf
from utils.docs_parser import extract_text_from_docx

class Experience(BaseModel):
    company: str
    role: str
    duration: str
    highlights: List[str]

class Education(BaseModel):
    degree: str
    institution: str
    year: str

class CandidateProfile(BaseModel):
    full_name: str
    email: str
    phone: str
    location: str
    summary: str
    technical_skills: List[str]
    experience: List[Experience]
    education: List[Education]
    certifications: List[str] = []

def parse_resume_to_profile(file_path: str, model_name: "str" = "qwen2.5:1.5b-instruct") -> CandidateProfile:
    if file_path.endswith(".pdf"):
        raw_text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        raw_text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file format. Use PDF or DOCX.")

    prompt = f"""You are an expert resume parser. Extract structured candidate information from the resume text below.
Return ONLY valid JSON matching this schema keys:
full_name, email, phone, location, summary, technical_skills (list of strings), experience (list of objects with company, role, duration, highlights list), education (list of objects with degree, institution, year), certifications (list of strings).
Do NOT invent or fabricate any information. Extract strictly what is present.

Resume Text:{raw_text}
"""

    response = ollama.chat(model=model_name, messages=[{'role': 'user', 'content': prompt}])
    content = response['message']['content']
    
    # Clean potential markdown wrapping from LLM response
    cleaned = content.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    data = json.loads(cleaned)
    return CandidateProfile(**data)