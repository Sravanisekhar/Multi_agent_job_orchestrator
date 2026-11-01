import os
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utils.logger import log_application
from utils.question_solver import answer_screening_question

load_dotenv()

class LinkedInAutomationAgent:
    def __init__(self, resume_folder="resumes/", session_state="config/linkedin_state.json"):
        self.resume_folder = Path(resume_folder)
        self.session_state = session_state
        self.username = os.getenv("LINKEDIN_EMAIL")
        self.password = os.getenv("LINKEDIN_PASSWORD")
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
        page.goto("https://www.linkedin.com/login")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        try:
            username_field = page.wait_for_selector("#username", timeout=4000)
        except Exception:
            username_field = None

        if username_field:
            print("[LINKEDIN LOGIN] Autofilling credentials...")
            if self.username and self.password:
                username_field.fill(self.username)
                time.sleep(1)
                page.fill("#password", self.password)
                time.sleep(1)
                page.click("button[type='submit']")
                print("[LINKEDIN LOGIN] Submitted login. Complete any security check if prompted.")
                input("Press Enter here after passing any LinkedIn verification checkpoint...")
            context.storage_state(path=self.session_state)
        else:
            print("[LINKEDIN LOGIN] Active session found.")

    def apply_to_job(self, job_url, role_name, company_name="Unknown Company"):
        selected_resume = self.get_resume_for_role(role_name)
        print(f"\n[LINKEDIN AGENT] Target: '{role_name}' at '{company_name}'")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=100)
            context = browser.new_context(storage_state=self.session_state) if os.path.exists(self.session_state) else browser.new_context()
            page = context.new_page()

            self.ensure_logged_in(page, context)

            print(f"[LINKEDIN AGENT] Opening job URL: {job_url}")
            page.goto(job_url)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(random.uniform(2.0, 3.5))

            # Look for Easy Apply or regular apply button
            apply_btn = page.query_selector("button.jobs-apply-button, button:has-text('Easy Apply')")
            status = "Manual Review / External"

            if apply_btn:
                apply_btn.click()
                print("[LINKEDIN AGENT] Clicked application button.")
                time.sleep(2)

                # Attach resume if input file field exists
                file_input = page.query_selector("input[type='file']")
                if file_input:
                    file_input.set_input_files(selected_resume)
                    print("[LINKEDIN AGENT] Resume attached successfully.")

                status = "Applied / Easy Apply"

            print("\n[SAFE HANDOFF] Review application screen on LinkedIn.")
            input("Press Enter in terminal to save session & complete log...")

            context.storage_state(path=self.session_state)
            log_application(
                platform="LinkedIn",
                company_name=company_name,
                role_name=role_name,
                resume_used=os.path.basename(selected_resume),
                status=status,
                job_url=job_url
            )
            browser.close()