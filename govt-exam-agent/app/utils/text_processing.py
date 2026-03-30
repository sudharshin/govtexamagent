import re

# ✅ Extract PDF links from content
def extract_pdf_links(text: str):
    return re.findall(r'(https?://\S+\.pdf)', text)


# ✅ Clean and extract real questions
def extract_questions(text: str):
    lines = text.split("\n")
    questions = []

    for line in lines:
        line = line.strip()

        # ❌ Remove garbage
        if (
            not line or
            "http" in line or
            "![ " in line or
            line.startswith("###")
        ):
            continue

        # ✅ Keep meaningful questions
        if (
            "?" in line and
            len(line) > 20 and
            line[0].isupper()
        ):
            questions.append(line)

    return questions