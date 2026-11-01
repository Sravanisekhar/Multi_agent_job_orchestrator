import os
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utils.logger import log_application
from utils.question_solver import answer_screening_question

load_dotenv()

# Candidate profile used for LLM decision making
CANDIDATE_PROFILE = {
    "full_name": os.getenv("CANDIDATE_NAME", None),
    "email": os.getenv("CANDIDATE_EMAIL", None),
    "total_experience_years": 2,
    "notice_period_days": 30,
    "location": "India"
}

class NaukriAutomationAgent:
    def __init__(self, resume_folder="resumes/", session_state="config/naukri_state.json"):
        self.resume_folder = Path(resume_folder)
        self.session_state = session_state
        self.username = os.getenv("NAUKRI_EMAIL")
        self.password = os.getenv("NAUKRI_PASSWORD")
        os.makedirs("config", exist_ok=True)

    def get_resume_for_role(self, role_name):
        resumes = list(self.resume_folder.glob("*.pdf")) + list(self.resume_folder.glob("*.docx"))
        if not resumes:
            raise FileNotFoundError("No resume files found in resumes/ folder!")
        for resume in resumes:
            if any(word.lower() in resume.name.lower() for word in role_name.split()):
                return str(resume.resolve())
        return str(resumes[0].resolve())

    def ensure_logged_in(self, page, context):
        page.goto("https://www.naukri.com/nlogin/login")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        try:
            username_field = page.wait_for_selector("#usernameField, input[placeholder*='Email']", timeout=4000)
        except Exception:
            username_field = None

        if username_field:
            print("[NAUKRI LOGIN] Autofilling login credentials...")
            if self.username and self.password:
                username_field.fill(self.username)
                time.sleep(1)
                
                password_field = page.query_selector("#passwordField, input[type='password']")
                if password_field:
                    password_field.fill(self.password)
                    time.sleep(1)
                
                login_btn = page.query_selector("button[type='submit']")
                if login_btn:
                    login_btn.click()
                    print("[NAUKRI LOGIN] Login submitted. Waiting for dashboard...")
                    time.sleep(4)

            context.storage_state(path=self.session_state)
        else:
            print("[NAUKRI LOGIN] Active session found.")

    def fill_screening_questions(self, page):
        """Scans for modal screening inputs (radio, text, selects) and answers using LLM."""
        print("[SCREENING ENGINE] Checking for questionnaire modal...")
        time.sleep(2)

        # 1. Text Inputs & Numbers (e.g. Notice period, Experience)
        inputs = page.query_selector_all("div.qna-container input[type='text'], div.qna-container input[type='number'], form input.input")
        for inp in inputs:
            try:
                label_elem = page.evaluate("(element) => element.closest('div').innerText", inp)
                if label_elem:
                    answer = answer_screening_question(label_elem, CANDIDATE_PROFILE)
                    print(f"[LLM ANSWER] Question: '{label_elem.strip()[:40]}...' -> Answer: '{answer}'")
                    inp.fill(str(answer))
                    time.sleep(0.5)
            except Exception as e:
                continue

        # 2. Radio Options (e.g. Yes/No, relocation)
        radio_groups = page.query_selector_all("div.radio-group, div.question-wrapper")
        for group in radio_groups:
            try:
                q_text = group.inner_text().strip()
                options = [opt.inner_text().strip() for opt in group.query_selector_all("label, span.radio-label")]
                if options:
                    best_option = answer_screening_question(q_text, CANDIDATE_PROFILE, options)
                    print(f"[LLM ANSWER] Choice Question: '{q_text[:40]}...' -> Selected: '{best_option}'")
                    
                    # Click matching option label
                    for label in group.query_selector_all("label"):
                        if best_option.lower() in label.inner_text().lower():
                            label.click()
                            time.sleep(0.5)
                            break
            except Exception:
                continue

    def apply_to_job(self, job_url, role_name, company_name="Unknown Company"):
        selected_resume = self.get_resume_for_role(role_name)
        print(f"\n[NAUKRI AGENT] Target: '{role_name}' at '{company_name}'")
        print(f"[NAUKRI AGENT] Resume: {os.path.basename(selected_resume)}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=100)
            
            if os.path.exists(self.session_state):
                context = browser.new_context(storage_state=self.session_state)
            else:
                context = browser.new_context()

            page = context.new_page()

            self.ensure_logged_in(page, context)

            print(f"[NAUKRI AGENT] Navigating to job posting...")
            page.goto(job_url)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(random.uniform(2.0, 3.5))

            apply_button = page.query_selector("button.apply-button, button:has-text('Apply')")
            status = "Pre-filled / Manual Review"

            if apply_button:
                apply_button.click()
                print("[NAUKRI AGENT] Clicked Apply button.")
                time.sleep(2.5)

                # Dynamically fill screening questions if they pop up
                self.fill_screening_questions(page)

                # Attach matching resume if upload field exists
                file_input = page.query_selector("input[type='file']")
                if file_input:
                    file_input.set_input_files(selected_resume)
                    print("[NAUKRI AGENT] Resume attached successfully.")

                # Click secondary submit inside modal if present
                modal_submit = page.query_selector("button:has-text('Submit'), button:has-text('Apply Now'), button.submit-btn")
                if modal_submit and modal_submit.is_visible():
                    modal_submit.click()
                    print("[NAUKRI AGENT] Submitted screening form.")
                    time.sleep(2)

                status = "Applied"

            print("\n[SAFE HANDOFF] Application details filled. Review the screen!")
            input("Press Enter in terminal to save session & complete log...")

            context.storage_state(path=self.session_state)
            log_application(
                company_name=company_name,
                role_name=role_name,
                resume_used=os.path.basename(selected_resume),
                status=status
            )
            browser.close()

if __name__ == "__main__":
    agent = NaukriAutomationAgent()
    print("Naukri Agent ready with Qwen Screening Question Solver!")