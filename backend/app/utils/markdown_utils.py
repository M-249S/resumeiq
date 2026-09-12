import re


def clean_markdown(text: str) -> str:
    """
    Clean Gemini Markdown output before rendering or exporting to PDF.
    """

    if not text:
        return ""

    # Remove code fences
    text = re.sub(r"```(?:markdown|md)?", "", text, flags=re.IGNORECASE)
    text = text.replace("```", "")

    # Remove horizontal rules
    text = re.sub(r"^\s*---+\s*$", "", text, flags=re.MULTILINE)

    # Remove HTML comments
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)

    # Remove excessive blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove trailing spaces
    text = "\n".join(line.rstrip() for line in text.splitlines())

    return text.strip()
