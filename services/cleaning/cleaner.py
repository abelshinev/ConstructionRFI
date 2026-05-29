import re

def clean_steps(text: str) -> str:
    # 1 -> normalize newlines
    text =  text.replace("\r\n", "\n").replace("\r", "\n") 
    # 2 -> remove control chars
    text = "".join(char for char in text
        if char == "\n" or char == "\t" or ord(char) >= 32
    )
    # 3. normalize spaces
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    # 4. fix em dash line breaks
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)
    # 5. normalize para spacing
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def clean_extracted_text(text: str) -> str:
    if not text:
        return ""

    text = clean_steps(text)
    return text.strip()

