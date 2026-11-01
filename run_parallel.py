import concurrent.futures
from agents.naukri_agent import NaukriAutomationAgent
from agents.linkedin_agent import LinkedInAutomationAgent
from agents.indeed_agent import IndeedAutomationAgent
from utils.logger import log_application
from utils.app_logger import log_error

def run_agent(platform_name, agent_instance, role, url):
    print(f"[PARALLEL] Launching {platform_name} Agent...")
    try:
        agent_instance.apply_to_job(
            job_url=url,
            role_name=role,
            company_name=f"Sample {platform_name} Corp"
        )
    except Exception as e:
        # 1. Write full error stack trace to logs/agent_errors.log
        log_error(
            platform=platform_name,
            context_msg=f"Execution failed while processing job at {url}",
            exception=e
        )

        # 2. Update platform-specific log JSON file with failure record
        log_application(
            platform=platform_name,
            company_name=f"Sample {platform_name} Corp",
            role_name=role,
            resume_used="N/A",
            status=f"Failed: {str(e)}",
            job_url=url
        )

def main():
    print("==================================================")
    print("      STARTING TRIPLE-AGENT PARALLEL RUN          ")
    print("==================================================")

    naukri = NaukriAutomationAgent()
    linkedin = LinkedInAutomationAgent()
    indeed = IndeedAutomationAgent()

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(run_agent, "Naukri", naukri, "Machine Learning Engineer", "https://www.naukri.com"),
            executor.submit(run_agent, "LinkedIn", linkedin, "Machine Learning Engineer", "https://www.linkedin.com/jobs"),
            executor.submit(run_agent, "Indeed", indeed, "Machine Learning Engineer", "https://in.indeed.com")
        ]
        concurrent.futures.wait(futures)

    print("\n==================================================")
    print("      ALL PARALLEL PLATFORM RUNS COMPLETED!       ")
    print("==================================================")

if __name__ == "__main__":
    main()