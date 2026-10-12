"""Delimiter check extracted from pinned ML check_html.py; excludes code at callers."""
import re

def math_delimiter_errors(text: str) -> list[str]:
    errors: list[str] = []
    t = text.replace("\\$", "")
    if t.count("$$") % 2:
        errors.append("unbalanced $$ (display math)")
    t = re.sub(r"\$\$.*?\$\$", "", t, flags=re.S)
    if t.count("$") % 2:
        errors.append("unbalanced $ (inline math)")
    return errors


def prose_text(node):
    if isinstance(node, str): return node
    if node.tag in ('pre', 'code', 'script', 'style'): return ''
    return ''.join(prose_text(c) for c in node.children)
