#!/usr/bin/env python3
"""Stage source markdown files into docs/ for MkDocs build.

Requires Python 3.9+.

This script copies individual story files from each category folder into a
docs/ staging directory, skipping the compiled 00-ALL-*.md files.  It also
generates a category index page (index.md) for each section and produces a
.pages file consumed by mkdocs-awesome-pages-plugin to set nice section
titles and enforce numeric ordering in the left nav.

Numbered subdirectories inside a category (e.g. 03-the-stagecoach-fragments/)
are treated as multipart groups: each part file is staged into a matching
subdirectory under docs/, a group index.md landing page is generated, and
a .pages file controls the nav title and part ordering.
"""

from __future__ import annotations

import re
import shutil
from pathlib import Path

# Image extensions supported for illustration grids (checked case-insensitively).
_IMAGE_EXTENSIONS = frozenset({".jpg", ".jpeg", ".png", ".webp", ".gif"})

# Markers used to wrap the auto-generated illustration block.
_AUTO_START = "<!-- AUTO-ILLUSTRATIONS:START -->"
_AUTO_END = "<!-- AUTO-ILLUSTRATIONS:END -->"

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


def _natural_key(path: Path) -> list[int | str]:
    """Return a sort key that orders numeric stems naturally (1 < 2 < 10)."""
    parts: list[int | str] = []
    for segment in re.split(r"(\d+)", path.stem):
        parts.append(int(segment) if segment.isdigit() else segment)
    return parts


def strip_illustration_block(content: str) -> str:
    """Remove an existing illustration block from staged content.

    Handles two forms:
    1. An AUTO-ILLUSTRATIONS marker block (and the ``---`` rule + ``## Illustrations``
       heading that precede it).
    2. A manually placed trailing ``## Illustrations`` section containing an
       ``illustration-grid`` div (no markers), so the auto-injection can replace it.
    """
    if _AUTO_START in content:
        # Remove the full marked block including the preceding --- / ## Illustrations.
        pattern = re.compile(
            r"\n?---\s*\n\s*## Illustrations\s*\n\s*" + re.escape(_AUTO_START) + r".*?" + re.escape(_AUTO_END) + r"\n?",
            re.DOTALL,
        )
        result = pattern.sub("", content)
        if result == content:
            # Fallback: just strip between markers.
            fallback = re.compile(
                re.escape(_AUTO_START) + r".*?" + re.escape(_AUTO_END) + r"\n?",
                re.DOTALL,
            )
            result = fallback.sub("", content)
        return result.rstrip() + "\n"

    # Strip a trailing manual ## Illustrations section that contains illustration-grid.
    pattern = re.compile(
        r"\n?---\s*\n\s*## Illustrations\s*\n.*?illustration-grid.*",
        re.DOTALL,
    )
    result = pattern.sub("", content)
    return result.rstrip() + "\n"


def build_illustration_block(cat_slug: str, story_slug: str) -> str:
    """Return the Markdown/HTML illustration block for *story_slug*, or '' if no images."""
    image_dir = REPO_ROOT / "assets" / "images" / cat_slug / story_slug
    if not image_dir.is_dir():
        return ""

    images = sorted(
        (f for f in image_dir.iterdir() if f.suffix.lower() in _IMAGE_EXTENSIONS),
        key=_natural_key,
    )
    if not images:
        return ""

    lines: list[str] = [
        "\n---\n",
        "## Illustrations\n",
        f"{_AUTO_START}\n",
        '<div class="illustration-grid">\n',
    ]
    for img in images:
        site_path = f"/TheVicarsMen/assets/images/{cat_slug}/{story_slug}/{img.name}"
        alt = f"Illustration {img.stem}"
        lines.append(
            f'  <a href="{site_path}" target="_blank" rel="noopener">'
            f'<img src="{site_path}" alt="{alt}"></a>\n'
        )
    lines += [
        "</div>\n",
        f"{_AUTO_END}\n",
    ]
    return "".join(lines)


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

        # Collect top-level story files in natural numeric order,
        # excluding compiled 00-ALL-*.md files.
        story_files = sorted(
            (f for f in cat_dir.iterdir()
             if f.is_file()
             and not f.name.startswith("00-ALL-")
             and f.suffix in (".md", ".txt")),
            key=_natural_key,
        )

        # Collect numbered subdirectories (multipart groups) in natural numeric order.
        group_dirs = sorted(
            (d for d in cat_dir.iterdir()
             if d.is_dir() and CATEGORY_PATTERN.match(d.name)),
            key=_natural_key,
        )

        staged: list[tuple[str, str]] = []  # (title, staged_filename)

        for source_file in story_files:
            stem = strip_prefix(source_file.stem)
            staged_filename = stem + ".md"
            staged_path = out_dir / staged_filename

            title = title_from_stem(stem)
            content = source_file.read_text(encoding="utf-8")
            content = ensure_heading(title, content)
            content = strip_illustration_block(content)

            illus_block = build_illustration_block(cat_slug, stem)
            if illus_block:
                content = content.rstrip() + "\n" + illus_block

            staged_path.write_text(content, encoding="utf-8")
            staged.append((title, staged_filename))

        # Stage each numbered subdirectory as a multipart group.
        staged_groups: list[tuple[str, str]] = []  # (group_title, group_slug)

        for group_dir in group_dirs:
            group_slug = strip_prefix(group_dir.name)
            group_display = title_from_stem(group_slug)
            group_out_dir = out_dir / group_slug
            group_out_dir.mkdir()

            # Collect part files in natural numeric order.
            part_files = sorted(
                (f for f in group_dir.iterdir()
                 if f.is_file()
                 and f.suffix in (".md", ".txt")),
                key=_natural_key,
            )

            staged_parts: list[tuple[str, str]] = []  # (title, staged_filename)

            for part_file in part_files:
                part_stem = strip_prefix(part_file.stem)
                part_filename = part_stem + ".md"
                part_path = group_out_dir / part_filename

                part_title = title_from_stem(part_stem)
                content = part_file.read_text(encoding="utf-8")
                content = ensure_heading(part_title, content)
                content = strip_illustration_block(content)

                illus_block = build_illustration_block(cat_slug, part_stem)
                if illus_block:
                    content = content.rstrip() + "\n" + illus_block

                part_path.write_text(content, encoding="utf-8")
                staged_parts.append((part_title, part_filename))

            # Generate group landing page.
            group_index_lines = [f"# {group_display}\n\n"]
            for part_title, part_file in staged_parts:
                part_slug = Path(part_file).stem
                group_index_lines.append(f"- [{part_title}]({part_slug}.md)\n")
            (group_out_dir / "index.md").write_text(
                "".join(group_index_lines), encoding="utf-8"
            )

            # Generate group .pages (controls nav title and part ordering).
            group_nav_items = "".join(
                f"  - {pf}\n" for _, pf in [("", "index.md")] + staged_parts
            )
            (group_out_dir / ".pages").write_text(
                f"title: {group_display}\nnav:\n{group_nav_items}",
                encoding="utf-8",
            )

            staged_groups.append((group_display, group_slug))
            print(
                f"    {group_display}: staged {len(staged_parts)} parts"
                f" → docs/{cat_slug}/{group_slug}/"
            )

        # Generate category index page (includes both stories and groups).
        index_lines = [f"# {display_name}\n\n"]
        for story_title, story_file in staged:
            slug = Path(story_file).stem
            index_lines.append(f"- [{story_title}]({slug}.md)\n")
        for group_title, group_slug in staged_groups:
            index_lines.append(f"- [{group_title}]({group_slug}/index.md)\n")
        (out_dir / "index.md").write_text("".join(index_lines), encoding="utf-8")

        # Generate category .pages with ordered nav list so awesome-pages
        # preserves numeric sequence instead of falling back to alphabetical.
        nav_items = "  - Overview: index.md\n"
        for _, story_file in staged:
            nav_items += f"  - {story_file}\n"
        for _, group_slug in staged_groups:
            nav_items += f"  - {group_slug}\n"
        (out_dir / ".pages").write_text(
            f"title: {display_name}\nnav:\n{nav_items}",
            encoding="utf-8",
        )

        print(
            f"  {display_name}: staged {len(staged)} stories"
            + (f" + {len(staged_groups)} groups" if staged_groups else "")
            + f" → docs/{cat_slug}/"
        )

    # Copy static assets (e.g. CSS, images) from repo-root assets/ into docs/.
    # This is necessary because stage_docs.py wipes docs/ at the start, so any
    # static files must be re-copied here rather than stored directly in docs/.
    assets_src = REPO_ROOT / "assets"
    if assets_src.is_dir():
        shutil.copytree(assets_src, DOCS_DIR / "assets", dirs_exist_ok=True)
        print("  Copied assets/ → docs/assets/")

    print("Done. docs/ is ready for MkDocs.")


if __name__ == "__main__":
    main()
