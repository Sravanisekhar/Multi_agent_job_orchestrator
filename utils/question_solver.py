import json
import os

ANSWERS_FILE = "config/candidate_answers.json"

def load_candidate_answers():
    if os.path.exists(ANSWERS_FILE):
        with open(ANSWERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def answer_screening_question(question_text, options=None):
    """
    Matches dynamic form labels against candidate_answers.json without any LLM calls.
    """
    answers = load_candidate_answers()
    q_lower = question_text.lower()

    # 1. Match against known key patterns
    for key, val in answers.items():
        key_words = key.replace("_", " ").split()
        if all(word in q_lower for word in key_words):
            # If options are provided (radio/dropdown), pick the matching option
            if options:
                for opt in options:
                    if str(val).lower() in opt.lower():
                        return opt
            return str(val)

    # 2. Smart default fallbacks for common unmapped questions
    if "notice" in q_lower:
        return answers.get("notice_period", "30")
    if "experience" in q_lower or "exp" in q_lower:
        return answers.get("experience", "2")
    if "ctc" in q_lower or "salary" in q_lower:
        return answers.get("expected_ctc", "1000000")
    if "relocat" in q_lower or "travel" in q_lower:
        return "Yes"
    
    if options:
        # Default to "Yes" or first positive answer if option list exists
        for opt in options:
            if opt.lower() in ["yes", "immediate", "hybrid"]:
                return opt
        return options[0]

    return "Yes"