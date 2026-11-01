import os
import time
import random
from dotenv import load_dotenv
from agents.noukri_search import NaukriJobFinder
from agents.noukari_agent import NaukriAutomationAgent

load_dotenv()

# Configure target search parameters
TARGET_ROLES = ["Machine Learning Engineer", "Data Scientist"]
LOCATION = "India"
EXPERIENCE_YEARS = 2
MAX_JOBS_PER_ROLE = 3  # Start small for testing

def main():
    print("==================================================")
    print("      STARTING AI JOB APPLICATION AGENT           ")
    print("==================================================")

    finder = NaukriJobFinder()
    agent = NaukriAutomationAgent()

    all_jobs_to_apply = []

    # 1. Search and discover jobs for each target role
    for role in TARGET_ROLES:
        print(f"\n--> Searching jobs for role: '{role}'...")
        jobs = finder.search_jobs(
            role_keyword=role,
            location=LOCATION,
            experience=EXPERIENCE_YEARS,
            max_jobs=MAX_JOBS_PER_ROLE
        )
        all_jobs_to_apply.extend(jobs)

    if not all_jobs_to_apply:
        print("\n[INFO] No new matching jobs found to apply right now.")
        return

    print(f"\n==================================================")
    print(f"   STARTING AUTOMATED APPLICATIONS ({len(all_jobs_to_apply)} JOBS)  ")
    print("==================================================")

    # 2. Process each discovered job sequentially
    for idx, job in enumerate(all_jobs_to_apply, 1):
        print(f"\n--- Job {idx}/{len(all_jobs_to_apply)} ---")
        print(f"Company: {job['company']}")
        print(f"Role: {job['title']}")
        print(f"URL: {job['url']}")

        try:
            agent.apply_to_job(
                job_url=job['url'],
                role_name=job['target_role'],
                company_name=job['company']
            )
        except Exception as e:
            print(f"[ERROR] Failed application for {job['company']}: {e}")

        # Inject realistic human delay between jobs
        if idx < len(all_jobs_to_apply):
            delay = random.uniform(10.0, 20.0)
            print(f"[HUMAN EMULATION] Waiting {int(delay)} seconds before next job...")
            time.sleep(delay)

    print("\n==================================================")
    print("   ALL QUEUED APPLICATIONS PROCESSED SUCCESSFULLY! ")
    print("==================================================")

if __name__ == "__main__":
    main()