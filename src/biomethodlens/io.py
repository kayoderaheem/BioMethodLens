"""Safe manuscript loading for plain text, Markdown, and optional PDF input."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Manuscript:
    path: Path
    text: str
    sha256: str
    page_count: int


def _digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def load_manuscript(path: Path) -> Manuscript:
    path = path.resolve()
    if not path.is_file():
        raise FileNotFoundError("Manuscript not found: {}".format(path))
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        text = path.read_text(encoding="utf-8")
        pages = max(1, text.count("\f") + 1)
    elif suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("PDF support requires: pip install 'biomethodlens[pdf]'") from exc
        reader = PdfReader(str(path), strict=True)
        page_text = []
        for number, page in enumerate(reader.pages, start=1):
            extracted = page.extract_text() or ""
            page_text.append("\n\n[Page {}]\n{}".format(number, extracted))
        text = "".join(page_text)
        pages = len(reader.pages)
    else:
        raise ValueError("Supported manuscript formats are .txt, .md, and .pdf")
    if len(text.strip()) < 100:
        raise ValueError("The manuscript contains too little extractable text for review")
    return Manuscript(path=path, text=text, sha256=_digest(path), page_count=pages)
