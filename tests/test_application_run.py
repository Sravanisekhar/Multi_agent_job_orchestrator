import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from browser.application_agent import AutoApplicationAgent

def test_run():
    # Define target roles and a sample mock candidate profile
    target_roles = ["Machine Learning Engineer", "Data Scientist"]
    candidate_profile = {
        "full_name": "Test Candidate",
        "email": "nettikantis@gmail.com",
        "phone": "+919876543210"
    }

    print("Initializing Auto Application Agent...")
    agent = AutoApplicationAgent(target_roles=target_roles)

    # Test resume selection logic
    resume_path = agent.get_resume_for_role("Machine Learning Engineer")
    print(f"[SUCCESS] Selected resume for ML role: {resume_path}")

    # Test opening a sample browser page (e.g., a test form or Google)
    test_url = "https://httpbin.org/forms/post"
    print(f"Opening browser automation test on URL: {test_url}")
    
    try:
        agent.apply_to_job(test_url, "Machine Learning Engineer", candidate_profile)
        print("Application test run completed successfully.")
    except Exception as e:
        print(f"Note during browser test execution: {e}")

if __name__ == "__main__":
    test_run()