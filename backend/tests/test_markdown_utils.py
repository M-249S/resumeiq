from app.utils.markdown_utils import strip_inline_markdown


def test_strips_bold_markers_but_keeps_text():
    assert strip_inline_markdown("**Ahmed Ali**") == "Ahmed Ali"


def test_strips_multiple_bold_spans_on_separate_lines():
    text = "**Hiring Manager**\n[Company Name]\n**Re: Junior IT Engineer**"
    assert strip_inline_markdown(text) == (
        "Hiring Manager\n[Company Name]\nRe: Junior IT Engineer"
    )


def test_strips_italic_and_heading_markers():
    assert strip_inline_markdown("*hello* world") == "hello world"
    assert strip_inline_markdown("## Summary\nText") == "Summary\nText"


def test_leaves_plain_text_and_math_like_asterisks_alone():
    plain = "Dear Hiring Manager,\n\nI use Python, Java and SQL."
    assert strip_inline_markdown(plain) == plain
    assert strip_inline_markdown("5 * 3 = 15") == "5 * 3 = 15"


def test_handles_empty_input():
    assert strip_inline_markdown("") == ""
