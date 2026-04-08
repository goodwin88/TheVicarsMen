#!/usr/bin/env python3
"""Stage source markdown files into docs/ for MkDocs build.

Requires Python 3.9+.

This script copies individual story files from each category folder into a
docs/ staging directory, skipping the compiled 00-ALL-*.md files.  It also
generates a category index page (index.md) for each section and produces a
.pages file consumed by mkdocs-awesome-pages-plugin to set nice section
titles.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs"

# Directories whose name starts with two digits are category folders.
CATEGORY_PATTERN = re.compile(r"^\d{2}-")

# Strip leading NN- or NN.N- numbering prefix from a filename stem.
PREFIX_RE = re.compile(r"^\d+(\.\d+)?-")

# Articles / prepositions kept lower-case in titles (unless first word).
_SMALL_WORDS = frozenset(
    {"a", "an", "and", "as", "at", "but", "by", "for", "in",
     "nor", "of", "on", "or", "so", "the", "to", "up", "yet"}
)


def title_from_stem(stem: str) -> str:
    """Convert a hyphenated filename stem to a human-readable title."""
    words = stem.replace("-", " ").split()
    result = []
    for i, word in enumerate(words):
        if i == 0 or word.lower() not in _SMALL_WORDS:
            result.append(word.capitalize())
        else:
            result.append(word.lower())
    return " ".join(result)


def category_display_name(dir_name: str) -> str:
    """Return the display name for a category directory (e.g. '01-fairy-tales' → 'Fairy Tales')."""
    stem = PREFIX_RE.sub("", dir_name)
    return title_from_stem(stem)


def strip_prefix(filename_stem: str) -> str:
    """Remove NN- or NN.N- prefix from a file stem."""
    return PREFIX_RE.sub("", filename_stem)


def ensure_heading(title: str, content: str) -> str:
    """Prepend a # heading if the content has none."""
    for line in content.splitlines():
        if line.strip().startswith("#"):
            return content  # already has a heading
    return f"# {title}\n\n{content}"


def main() -> None:
    # Wipe and recreate the staging directory.
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    DOCS_DIR.mkdir()

    # Landing page: copy README.md → docs/index.md
    readme = REPO_ROOT / "README.md"
    if readme.exists():
        shutil.copy(readme, DOCS_DIR / "index.md")
    else:
        (DOCS_DIR / "index.md").write_text(
            "# The Vicar's Men\n\nWelcome to the collection.\n",
            encoding="utf-8",
        )

    # Discover and sort category directories.
    category_dirs = sorted(
        d for d in REPO_ROOT.iterdir()
        if d.is_dir() and CATEGORY_PATTERN.match(d.name)
    )

    for cat_dir in category_dirs:
        display_name = category_display_name(cat_dir.name)
        # Category slug: directory name without leading NN-
        cat_slug = PREFIX_RE.sub("", cat_dir.name)
        out_dir = DOCS_DIR / cat_slug
        out_dir.mkdir()

        # .pages file: tells awesome-pages-plugin the section display title.
        (out_dir / ".pages").write_text(f"title: {display_name}\n", encoding="utf-8")

        # Collect story files, excluding compiled 00-ALL-*.md files.
        story_files = sorted(
            f for f in cat_dir.iterdir()
            if f.is_file()
            and not f.name.startswith("00-ALL-")
            and f.suffix in (".md", ".txt")
        )

        staged: list[tuple[str, str]] = []  # (title, staged_filename)

        for source_file in story_files:
            stem = strip_prefix(source_file.stem)
            staged_filename = stem + ".md"
            staged_path = out_dir / staged_filename

            title = title_from_stem(stem)
            content = source_file.read_text(encoding="utf-8")
            content = ensure_heading(title, content)

            staged_path.write_text(content, encoding="utf-8")
            staged.append((title, staged_filename))

        # Generate category index page.
        lines = [f"# {display_name}\n\n"]
        for story_title, story_file in staged:
            slug = Path(story_file).stem
            lines.append(f"- [{story_title}]({slug}.md)\n")
        (out_dir / "index.md").write_text("".join(lines), encoding="utf-8")

        print(f"  {display_name}: staged {len(staged)} stories → docs/{cat_slug}/")

    print("Done. docs/ is ready for MkDocs.")


if __name__ == "__main__":
    main()
