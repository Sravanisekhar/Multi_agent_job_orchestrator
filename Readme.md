# Autonomous Multi-Platform Job Application Orchestration System

An intelligent, local-first automation engine designed to concurrently execute job applications across multiple platforms (**Naukri, LinkedIn, Indeed**) using a multi-threaded architecture, automated Gmail OTP verification, and local Generative AI fallback for custom screening questions.

---

## Key Features

* **Multi-Platform Parallel Execution:** Utilizes Python's `ThreadPoolExecutor` to run concurrent browser automation tasks across different job portals simultaneously without session collision.
* **Automated Gmail OTP & Verification:** Intercepts and parses incoming email verification codes via the Gmail API using regex matching, enabling zero-touch login and session recovery.
* **Hybrid Decision Engine:** Combines a fast, zero-latency deterministic rules engine (`candidate_answers.json`) for standard form fields with a local LLM fallback (**Ollama / Qwen 2.5**) to handle open-ended recruiter questionnaires.
* **Session Persistence:** Saves authenticated Playwright browser contexts (`storage_state.json`) to bypass repeated logins and security checkpoints.
* **Production-Grade Audit & Error Logging:** Implements thread-safe platform JSON execution loggers alongside centralized error tracking (`logs/agent_errors.log`) capturing full stack traces.

---

## Tech Stack

* **Language:** Python 3.12
* **Automation:** Playwright (Synchronous API)
* **Concurrency:** `concurrent.futures.ThreadPoolExecutor` with thread-safe file locks
* **AI & Parsing:** Ollama (Qwen 2.5), Pydantic
* **Integrations:** Gmail API, python-dotenv

---
---

## Prerequisites & Local LLM Setup (Ollama)

This project relies on **Ollama** running locally on your machine to handle complex or unmapped recruiter screening questions. Ollama runs as a system-level background service (outside your Python `.venv`).

1. **Install Ollama:** Download and install the desktop engine from [ollama.com](https://ollama.com).
2. **Pull the Required Model:** Open Command Prompt or PowerShell and run:
   ```cmd
   ollama pull qwen2.5

## Project Structure

```text
Ai-Job-Agent/
│
├── agents/                  # Platform-specific automation agents
│   ├── naukri_agent.py
│   ├── linkedin_agent.py
│   └── indeed_agent.py
│
├── utils/                   # Shared utilities & helpers
│   ├── app_logger.py        # Centralized exception logger
│   ├── logger.py            # Platform audit log writer
│   ├── gmail_client.py      # Automated OTP/Email parser
│   └── question_solver.py   # Hybrid rules + LLM decision engine
│
├── config/                  # Ignored configuration & session states
├── data/                    # Platform execution audit logs (.json)
├── logs/                    # System error stack traces (.log)
├── resumes/                 # Role-matched PDF/Docx resumes
├── .env                     # Environment variables (ignored)
├── run_parallel.py          # Multi-threaded parallel runner
└── main.py                  # Single-platform sequential entrypoint


---

## Setup & Running

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/Ai-Job-Agent.git
   cd Ai-Job-Agent
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # On Windows
   # source .venv/bin/activate  # On macOS/Linux
   ```

3. **Install Python dependencies & Playwright drivers:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Configure credentials:**
   Create a `.env` file in the root directory and populate your credentials:
   ```env
   # Naukri Credentials
NAUKRI_EMAIL=
NAUKRI_PASSWORD=
# LinkedIn Credentials
LINKEDIN_EMAIL=
LINKEDIN_PASSWORD=

# Indeed Credentials
INDEED_EMAIL=
INDEED_PASSWORD=


# Candidate Personal Info
CANDIDATE_NAME=
CANDIDATE_EMAIL=
CANDIDATE_PHONE=
   ```

5. **Execute the parallel orchestrator:**
   ```bash
   python run_parallel.py
   ```