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


def strip_inline_markdown(text: str) -> str:
    """
    Remove inline Markdown emphasis/heading markers, keeping the text.

    The cover letter is shown in an editable plain-text box and exported to
    DOCX as plain paragraphs, so literal `**bold**` markers would otherwise
    appear to the user. (clean_markdown() above is intentionally left alone:
    the resume rewrite still relies on Markdown headings/bullets.)
    """

    if not text:
        return ""

    # **bold** / __bold__ -> bold
    text = re.sub(r"(\*\*|__)(.+?)\1", r"\2", text, flags=re.DOTALL)

    # *italic* / _italic_ -> italic (single markers around a word/phrase)
    text = re.sub(r"(?<![\w*])\*(?!\s)([^*\n]+?)(?<!\s)\*(?![\w*])", r"\1", text)

    # Leading "# " / "## " heading markers
    text = re.sub(r"^\s{0,3}#{1,6}\s+", "", text, flags=re.MULTILINE)

    return text
