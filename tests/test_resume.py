from agents.resume_agent import parse_resume_to_profile
import json
import os

resume_path = "resumes/resume.pdf" # Update with your actual filename if docx

if os.path.exists(resume_path):
    print("Parsing resume with local Qwen 2.5 1.5B...")
    profile = parse_resume_to_profile(resume_path)
    print("\nSuccessfully Extracted Profile:")
    print(json.dumps(profile.model_dump(), indent=2))
else:
    print(f"Please place your master resume at {resume_path} before running this test.")