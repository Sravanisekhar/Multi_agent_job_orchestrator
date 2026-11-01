import os
import json
import time
import random
from pathlib import Path
from urllib.parse import quote
from playwright.sync_api import sync_playwright

LOG_FILE = "data/application_log.json"

class NaukriJobFinder:
    def __init__(self, session_state="config/naukri_state.json"):
        self.session_state = session_state

    def _get_applied_urls(self):
        """Loads already applied job records to prevent duplicate applications."""
        if os.path.exists(LOG_FILE):
            try:
                with open(LOG_FILE, "r", encoding="utf-8") as f:
                    logs = json.load(f)
                    return set(entry.get("job_url", "") for entry in logs)
            except Exception:
                return set()
        return set()

    def search_jobs(self, role_keyword, location="Bangalore", experience=2, max_jobs=5):
        """
        Searches Naukri for a target role and extracts job posting URLs.
        """
        applied_urls = self._get_applied_urls()
        encoded_keyword = quote(role_keyword.lower().replace(" ", "-"))
        encoded_location = quote(location.lower().replace(" ", "-"))
        
        # Build standard Naukri search URL format
        search_url = f"https://www.naukri.com/{encoded_keyword}-jobs-in-{encoded_location}?experience={experience}"
        print(f"\n[SEARCH] Accessing Naukri: {search_url}")

        job_results = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, slow_mo=100)
            
            if os.path.exists(self.session_state):
                context = browser.new_context(storage_state=self.session_state)
            else:
                context = browser.new_context()

            page = context.new_page()
            page.goto(search_url)
            page.wait_for_load_state("domcontentloaded")
            time.sleep(random.uniform(3.0, 5.0))

            # Locate job cards on search page
            job_cards = page.query_selector_all(".srp-jobtuple-wrapper, article.jobTuple")
            print(f"[SEARCH] Found {len(job_cards)} job listings on page 1.")

            for card in job_cards:
                if len(job_results) >= max_jobs:
                    break

                try:
                    title_elem = card.query_selector("a.title")
                    company_elem = card.query_selector("a.comp-name, .subTitle")
                    
                    if title_elem:
                        url = title_elem.get_attribute("href")
                        title = title_elem.inner_text().strip()
                        company = company_elem.inner_text().strip() if company_elem else "Unknown Company"

                        # Skip duplicates
                        if url in applied_urls:
                            print(f"[SKIP] Already applied to: {title} at {company}")
                            continue

                        job_results.append({
                            "title": title,
                            "company": company,
                            "url": url,
                            "target_role": role_keyword
                        })
                except Exception as e:
                    continue

            browser.close()

        print(f"[SEARCH] Successfully queued {len(job_results)} new jobs to apply.")
        return job_results

if __name__ == "__main__":
    finder = NaukriJobFinder()
    jobs = finder.search_jobs("Machine Learning Engineer", location="India", max_jobs=3)
    print("Found Jobs:", json.dumps(jobs, indent=2))