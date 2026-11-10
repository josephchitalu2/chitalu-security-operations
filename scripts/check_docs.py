"""Check relative Markdown targets without network calls."""
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

root = Path(__file__).resolve().parents[1]
errors = []
for source in root.rglob("*.md"):
    if any(part in {".git", ".venv", "__pycache__", "node_modules"} for part in source.relative_to(root).parts):
        continue
    for value in re.findall(r"\]\(([^\s\)]+)\)", source.read_text(encoding="utf-8")):
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path:
            continue
        target = root / unquote(url.path.lstrip("/")) if url.path.startswith("/") else source.parent / unquote(url.path)
        if not target.exists():
            errors.append(str(source.relative_to(root)) + ": missing " + value)
if errors:
    raise SystemExit("\n".join(errors))
print("PASS: relative Markdown targets exist (external URLs and anchors are not checked)")
