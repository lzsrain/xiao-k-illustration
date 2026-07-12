#!/usr/bin/env python3
"""Validate the public K Skill package without external dependencies."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REQUIRED_ROOT_FILES = {
    "README.md",
    "LICENSE",
    "ASSET-LICENSE.md",
    "NOTICE",
    "TRADEMARK.md",
    "CONTRIBUTING.md",
    "PROVENANCE.md",
    "RELEASE-CHECKLIST.md",
    "SECURITY.md",
    "SIMILARITY-REVIEW.md",
    "VERSION",
}

REQUIRED_SKILL_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "assets/ip/k/character-reference.png",
    "assets/ip/k/expression-sheet.png",
    "references/character-dna.md",
    "references/content-to-scene.md",
    "references/composition-patterns.md",
    "references/platform-formats.md",
    "references/prompt-template.md",
    "references/qa-checklist.md",
}

FORBIDDEN_PUBLIC_TERMS = {
    "Smartisan",
    "锤子科技",
    "sticky-note-like head",
    "K-shaped headset",
    "tiny black bean body",
}


def check_files(root: Path) -> list[str]:
    errors: list[str] = []
    for relative in sorted(REQUIRED_ROOT_FILES):
        if not (root / relative).is_file():
            errors.append(f"missing root file: {relative}")
    skill = root / "xiao-k-illustration"
    for relative in sorted(REQUIRED_SKILL_FILES):
        if not (skill / relative).is_file():
            errors.append(f"missing skill file: xiao-k-illustration/{relative}")
    return errors


def check_skill_frontmatter(root: Path) -> list[str]:
    path = root / "xiao-k-illustration" / "SKILL.md"
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    if not match:
        return ["SKILL.md frontmatter is missing or malformed"]
    frontmatter = match.group(1)
    if "name: xiao-k-illustration" not in frontmatter:
        return ["SKILL.md name must be xiao-k-illustration"]
    if "description:" not in frontmatter:
        return ["SKILL.md description is missing"]
    return []


def check_public_text(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".md", ".yaml", ".py", ".svg"}:
            continue
        if path.name == "validate_package.py":
            continue
        text = path.read_text(encoding="utf-8")
        for term in FORBIDDEN_PUBLIC_TERMS:
            if term in text:
                errors.append(f"forbidden legacy/reference term {term!r} in {path.relative_to(root)}")
    return errors


def check_character_asset(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / "xiao-k-illustration" / "assets" / "ip" / "k" / "character-reference.png"
    if path.is_file():
        data = path.read_bytes()
        if not data.startswith(b"\x89PNG\r\n\x1a\n"):
            errors.append("character-reference.png is not a valid PNG file")
        if len(data) < 100_000:
            errors.append("character-reference.png is unexpectedly small")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    errors = []
    errors.extend(check_files(root))
    errors.extend(check_skill_frontmatter(root))
    errors.extend(check_public_text(root))
    errors.extend(check_character_asset(root))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("K Skill package validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
