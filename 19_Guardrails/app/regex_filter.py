import re

patterns = {
    "email": re.compile(r"[\w.-]+@[\w.-]+\.\w+"),
    "password": re.compile(r"(password|passwd|api[_-]?key)", re.IGNORECASE),
    "profanity": re.compile(r"\b(badword1|badword2|idiot)\b", re.IGNORECASE),
}

def check_safety(text):
    for name, pattern in patterns.items():
        if pattern.search(text):
            return False, f"Blocked by {name} filter"
    return True, "Safe"

if __name__ == "__main__":
    tests = ["Email me at test@mail.com", "My password is admin123", "I like sunshine"]
    for t in tests:
        safe, msg = check_safety(t)
        print(f"[{t}] → {msg}")
