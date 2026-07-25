import re

patterns = {
    "email": re.compile(r"[\w\.-]+@[\w\.-]+\.\w+"),
    "password": re.compile(r"(password|passwd|api[_-]?key)", re.IGNORECASE),
    "profanity": re.compile(r"\b(badword1|badword2|idiot)\b", re.IGNORECASE),
}

def check_safety(text):
    """
    Check if the given text contains any unsafe patterns.

    Args:
        text (str): The text to be checked.
    """

    for name, pattern in patterns.items():
        if pattern.search(text):
            return False, f"Blocked by {name} filter"

    return True, "Text is safe"


if __name__ == "__main__":
    tests = [
        "This is a safe text.",
        "Contact me at user@example.com",
        "My password is secret123",
        "This is a badword1 text."
    ]

    for text in tests:
        is_safe, message = check_safety(text)
        print(f"Text: {text}\nSafe: {is_safe}, Message: {message}\n")