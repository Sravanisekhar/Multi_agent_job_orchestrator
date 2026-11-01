import json
import os
from datetime import datetime

LOG_FILE = "data/application_log.json"

def log_application(company_name, role_name, resume_used, status="Submitted"):
    """
    Appends a new application entry with daily timestamps to data/application_log.json
    """
    os.makedirs("data", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_str = datetime.now().strftime("%Y-%m-%d")

    entry = {
        "timestamp": timestamp,
        "date": date_str,
        "company": company_name,
        "role": role_name,
        "resume_submitted": resume_used,
        "status": status
    }

    logs = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []

    logs.append(entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)

    print(f"[LOGGER] Logged application for '{company_name}' ({role_name}) on {timestamp}")