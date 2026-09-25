#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pypdf>=4"]
# ///
"""Print the text of an existing resume PDF, page by page, to seed a new base.

Usage: extract_pdf.py FILE.pdf [--json]
Exit codes: 0 text found, 1 no extractable text (a scanned image), 2 unreadable file.
With --json, every exit after argument parsing prints JSON: {"ok": true, "pages": [...]} or
{"ok": false, "error": ...}. An argparse usage error prints plain usage text to stderr and exits 2.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

NO_TEXT = "No text found. The PDF is probably a scanned image. Ask the user to paste the text instead."


def extract(pdf) -> List[str]:
    from pypdf import PdfReader
    return [(page.extract_text() or "").strip() for page in PdfReader(str(pdf)).pages]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Print the text of a resume PDF, page by page.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    def fail(message: str, code: int = 2) -> int:
        print(json.dumps({"ok": False, "error": message}) if args.json else message)
        return code

    try:
        pages = extract(args.pdf)
    except ImportError as err:
        return fail(f"missing dependency {err.name}: pip install {err.name}, or run this script with uv run")
    except Exception as err:  # missing file or not a PDF
        return fail(f"cannot read {args.pdf}: {err}")
    if not any(pages):
        return fail(NO_TEXT, 1)
    if args.json:
        print(json.dumps({"ok": True, "pages": pages}, indent=2))
    else:
        for n, text in enumerate(pages, 1):
            print(f"===== page {n} =====\n{text}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
