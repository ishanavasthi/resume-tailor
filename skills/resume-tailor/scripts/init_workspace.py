#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Create a private resume workspace from the skill's starter files.

Usage: init_workspace.py DIR --name "First Last" [--from-template] [--json]

Never overwrites: if any file it would write already exists (or a file sits where one of its
folders goes), it writes nothing.
Exit codes: 0 created, 1 a file already exists, 2 bad input or a filesystem error.
With --json, every exit after argument parsing prints JSON: {"ok": true, "dir": ...,
"files": [...]} or {"ok": false, "error": ...}. An argparse usage error prints plain usage text
to stderr and exits 2.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import List, Tuple

ASSETS = Path(__file__).resolve().parent.parent / "assets"
STARTER = ASSETS / "workspace"
RENAMES = {"gitignore": ".gitignore"}  # stored without the dot so it has no effect inside this repo
SKIP = {".DS_Store"}  # Finder litter that may appear in the assets folder; never copied


def pdf_prefix(name: str) -> str:
    return "_".join(re.findall(r"\w+", name))


def plan_files(target: Path, from_template: bool) -> List[Tuple[Path, Path]]:
    pairs = []
    for src in sorted(STARTER.rglob("*")):
        if src.is_file() and src.name not in SKIP:
            rel = src.relative_to(STARTER)
            pairs.append((src, target / rel.with_name(RENAMES.get(rel.name, rel.name))))
    if from_template:
        pairs.append((ASSETS / "template.tex", target / "bases" / "Resume.tex"))
    return pairs


def _clashes(pairs: List[Tuple[Path, Path]]) -> List[Path]:
    """Every destination that exists (a dangling symlink counts), and every non-folder in the
    way of a destination's parent folders."""
    found = []
    for _, dst in pairs:
        if dst.is_symlink() or dst.exists():
            found.append(dst)
        for parent in dst.parents:
            if (parent.is_symlink() or parent.exists()) and not parent.is_dir():
                found.append(parent)
    return list(dict.fromkeys(found))


def init_workspace(target, name: str, from_template: bool = False) -> List[Path]:
    name = " ".join(name.split())
    if not re.search(r"\w", name):
        raise ValueError("--name must contain the user's name")
    target = Path(target).expanduser()
    pairs = plan_files(target, from_template)
    clashes = _clashes(pairs)
    if clashes:
        raise FileExistsError(", ".join(str(c) for c in clashes))
    for src, dst in pairs:
        dst.parent.mkdir(parents=True, exist_ok=True)
        text = src.read_text(encoding="utf-8")
        dst.write_text(text.replace("{{NAME}}", name).replace("{{PDF_PREFIX}}", pdf_prefix(name)),
                       encoding="utf-8")
    return [dst for _, dst in pairs]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Create a private resume workspace.")
    parser.add_argument("dir", type=Path)
    parser.add_argument("--name", required=True, help='the name for PDF file names, e.g. "Jordan Lee"')
    parser.add_argument("--from-template", action="store_true", help="seed bases/Resume.tex with the template")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    def fail(message: str, code: int = 2) -> int:
        print(json.dumps({"ok": False, "error": message}) if args.json else message)
        return code

    try:
        written = init_workspace(args.dir, args.name, args.from_template)
    except ValueError as err:
        return fail(f"error: {err}")
    except FileExistsError as err:
        return fail(f"refusing to overwrite existing files, nothing written: {err}", 1)
    except OSError as err:
        return fail(f"cannot create the workspace at {args.dir}: {err}")
    if args.json:
        name = " ".join(args.name.split())
        print(json.dumps({"ok": True, "dir": str(args.dir.expanduser()), "name": name,
                          "pdf_prefix": pdf_prefix(name), "files": [str(p) for p in written]}, indent=2))
        return 0
    print(f"created workspace at {args.dir} ({len(written)} files)")
    for path in written:
        print(f"  {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
