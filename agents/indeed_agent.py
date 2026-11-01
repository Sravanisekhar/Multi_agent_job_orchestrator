import os
import time
import random
from pathlib import Path
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from utils.logger import log_application

load_dotenv()

class IndeedAutomationAgent:
    def __init__(self, resume_folder="resumes/", session_state="config/indeed_state.json"):
        self.resume_folder = Path(resume_folder)
        self.session_state = session_state
        self.username = os.getenv("INDEED_EMAIL")
        self.password = os.getenv("INDEED_PASSWORD")
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
        page.goto("https://secure.indeed.com/account/login")
        page.wait_for_load_state("domcontentloaded")
        time.sleep(2)

        try:
            email_field = page.wait_for_selector("#ifl-input-1, input[type='email']", timeout=4000)
        except Exception:
            email_field = None

        if email_field:
            print("[INDEED LOGIN] Autofilling credentials...")
            if self.username and self.password:
                email_field.fill(self.username)
                time.sleep(1)
                page.click("button[type='submit']")
                time.sleep(2)
                
                pass_field = page.query_selector("#i1-password, input[type='password']")
                if pass_field:
                    pass_field.fill(self.password)
                    time.sleep(1)
                    page.click("button[type='submit']")
                    print("[INDEED LOGIN] Login submitted.")
            context.storage_state(path=self.session_state)
        else:
            print("[INDEED LOGIN] Active session found.")

    def apply_to_job(self, job_url, role_name, company_name="Unknown Company"):
        selected_resume = self.get_resume_for_role(role_name)
        print(f"\n[INDEED AGENT] Target: '{role_name}' at '{company_name}'")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=100)
            context = browser.new_context(storage_state=self.session_state) if os.path.exists(self.session_state) else browser.new_context()
            page = context.new_page()

            self.ensure_logged_in(page, context)

            print(f"[INDEED AGENT] Opening job URL: {job_url}")
            page.goto(job_url)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(random.uniform(2.0, 3.5))

            apply_btn = page.query_selector("button.indeed-apply-button, button:has-text('Apply now')")
            status = "Manual Review / External"

            if apply_btn:
                apply_btn.click()
                print("[INDEED AGENT] Clicked Indeed Apply button.")
                time.sleep(2)

                file_input = page.query_selector("input[type='file']")
                if file_input:
                    file_input.set_input_files(selected_resume)
                    print("[INDEED AGENT] Resume attached successfully.")

                status = "Applied / Indeed Apply"

            print("\n[SAFE HANDOFF] Review application screen on Indeed.")
            input("Press Enter in terminal to save session & complete log...")

            context.storage_state(path=self.session_state)
            log_application(
                platform="Indeed",
                company_name=company_name,
                role_name=role_name,
                resume_used=os.path.basename(selected_resume),
                status=status,
                job_url=job_url
            )
            browser.close()