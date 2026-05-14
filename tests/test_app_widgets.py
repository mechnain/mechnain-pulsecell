import ast
from pathlib import Path


def test_streamlit_buttons_have_explicit_keys():
    app_source = Path("app.py").read_text(encoding="utf-8")
    tree = ast.parse(app_source)
    checked_methods = {"button", "download_button"}
    missing_keys = []

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr not in checked_methods:
            continue
        has_key = any(keyword.arg == "key" for keyword in node.keywords)
        if not has_key:
            missing_keys.append((func.attr, node.lineno))

    assert missing_keys == []
