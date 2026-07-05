"""Utilities for loading the local source pack used by the Researcher agent."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re


@dataclass(frozen=True)
class SourceDocument:
    """A small local source document with a stable identifier."""

    source_id: str
    title: str
    path: Path
    text: str


def _extract_title(markdown_text: str, fallback: str) -> str:
    """Extract the first markdown H1 as a title."""

    for line in markdown_text.splitlines():
        if line.startswith("# "):
            return line.replace("# ", "").strip()
    return fallback


def load_source_pack(source_dir: str | Path = "data/source_pack") -> list[SourceDocument]:
    """Load markdown files from the sample source pack.

    Args:
        source_dir: Directory containing .md source files and optional source_index.json.

    Returns:
        List of SourceDocument objects in source-index order when available.
    """

    source_path = Path(source_dir)
    if not source_path.exists():
        raise FileNotFoundError(
            f"Source directory not found: {source_path}. Run this from the project root."
        )

    index_path = source_path / "source_index.json"
    documents: list[SourceDocument] = []

    if index_path.exists():
        index_rows = json.loads(index_path.read_text(encoding="utf-8"))
        for row in index_rows:
            path = source_path / row["file"]
            if not path.exists():
                raise FileNotFoundError(f"Indexed source file missing: {path}")
            text = path.read_text(encoding="utf-8")
            documents.append(
                SourceDocument(
                    source_id=row["source_id"],
                    title=row.get("title") or _extract_title(text, path.stem.replace("_", " ").title()),
                    path=path,
                    text=text,
                )
            )
    else:
        for index, path in enumerate(sorted(source_path.glob("*.md")), start=1):
            text = path.read_text(encoding="utf-8")
            documents.append(
                SourceDocument(
                    source_id=f"SRC-{index:03d}",
                    title=_extract_title(text, path.stem.replace("_", " ").title()),
                    path=path,
                    text=text,
                )
            )

    if not documents:
        raise ValueError(f"No markdown sources found in {source_path}.")
    return documents


def render_sources_for_prompt(documents: list[SourceDocument], max_chars_per_doc: int = 1800) -> str:
    """Render source documents into a compact prompt block.

    Args:
        documents: Loaded source documents.
        max_chars_per_doc: Maximum characters per document to keep prompts affordable.

    Returns:
        A string suitable for an LLM prompt.
    """

    blocks = []
    for doc in documents:
        clipped_text = doc.text[:max_chars_per_doc]
        blocks.append(
            f"Source ID: {doc.source_id}\n"
            f"Title: {doc.title}\n"
            f"Text:\n{clipped_text}\n"
        )
    return "\n---\n".join(blocks)


def keyword_overlap_score(query: str, text: str) -> float:
    """Compute a simple keyword overlap score for deterministic mock mode."""

    query_terms = {term.lower() for term in re.findall(r"[a-zA-Z]{4,}", query)}
    text_terms = {term.lower() for term in re.findall(r"[a-zA-Z]{4,}", text)}
    if not query_terms:
        return 0.1
    return min(1.0, len(query_terms & text_terms) / max(1, len(query_terms)))


def top_sources_by_overlap(
    query: str, documents: list[SourceDocument], limit: int = 3
) -> list[SourceDocument]:
    """Select the most relevant sources using simple keyword overlap."""

    scored = sorted(
        documents,
        key=lambda doc: keyword_overlap_score(query, doc.text),
        reverse=True,
    )
    return scored[:limit]


def first_relevant_snippet(text: str, query: str, max_chars: int = 360) -> str:
    """Return a readable snippet from a source for mock-mode evidence."""

    paragraphs = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 80]
    query_terms = {term.lower() for term in re.findall(r"[a-zA-Z]{4,}", query)}
    if query_terms:
        for paragraph in paragraphs:
            if any(term in paragraph.lower() for term in query_terms):
                return paragraph[:max_chars]
    return (paragraphs[0] if paragraphs else text[:max_chars])[:max_chars]
