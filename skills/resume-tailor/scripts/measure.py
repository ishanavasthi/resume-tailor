#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pypdf>=4"]
# ///
"""Measure a resume PDF to size a trim.

Usage: measure.py FILE.tex|FILE.pdf [--engine ...] [--capacity-lines 46-54] [--capacity-chars 110] [--json]

Reports lines per page, the text that spilled past page 1, slack on a one-page result, and
short tails: a bullet whose last line holds only a few words, the cheapest line to win back.
Line counts come from extracted text, a close proxy but not exact. Confirm trims by rebuilding.
The 46-54 line capacity is an estimate that shifts with the number of headings on the page; pass
--capacity-lines with the count at which this base last filled its page when you know it.
Exit codes: 0 fits on one page, 1 overflows, 2 build or read error, or no extractable text.
With --json, every exit after argument parsing prints JSON: {"ok": true, ...} or
{"ok": false, "error": ...}. An argparse usage error prints plain usage text to stderr and exits 2.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, FrozenSet, List, Optional, Tuple

import build as builder

COMMON_SECTIONS = frozenset({
    "education", "experience", "work experience", "projects", "technical skills", "skills",
    "achievements", "awards", "certifications", "publications", "leadership", "activities",
    "summary", "coursework", "research", "volunteering",
})
SECTION_RE = re.compile(r"\\section\*?\{([^}]*)\}")
DEFAULT_CAPACITY_LINES = (46, 54)  # an estimate; the build is the truth
TAIL_MAX = 0.3  # a tail is shorter than 30% of a full line...
FULL_MIN = 0.8  # ...and completes a line at least 80% full


@dataclass
class Measurement:
    pdf: str
    pages: int
    lines_per_page: List[int]
    words_per_page: List[int]
    widest_line: int
    spill_lines: int
    spill_text: List[str]
    slack_lines: Optional[Tuple[int, int]]
    short_tails: List[Dict]


def page_lines(pdf) -> List[List[str]]:
    from pypdf import PdfReader
    reader = PdfReader(str(pdf))
    return [[ln.strip() for ln in (page.extract_text() or "").split("\n") if ln.strip()]
            for page in reader.pages]


def section_titles(tex_text: str) -> FrozenSet[str]:
    return frozenset(title.strip().lower() for title in SECTION_RE.findall(tex_text))


def find_short_tails(lines, width, exclude=COMMON_SECTIONS) -> List[Dict]:
    tails = []
    for i in range(1, len(lines)):
        line, prev = lines[i], lines[i - 1]
        if line.lower() in exclude:
            continue
        if len(line) < TAIL_MAX * width and len(prev) >= FULL_MIN * width:
            tails.append({"index": i, "line": line, "after": prev})
    return tails


def measure(pdf, tex_text: str = "", capacity_lines=DEFAULT_CAPACITY_LINES, capacity_chars=110) -> Measurement:
    pages = page_lines(pdf)
    exclude = COMMON_SECTIONS | section_titles(tex_text)
    first = pages[0] if pages else []
    spill = [ln for page in pages[1:] for ln in page]
    slack = None
    if len(pages) == 1:
        slack = (max(0, capacity_lines[0] - len(first)), max(0, capacity_lines[1] - len(first)))
    tails = [dict(t, page=n + 1) for n, page in enumerate(pages)
             for t in find_short_tails(page, capacity_chars, exclude)]
    return Measurement(
        pdf=str(pdf),
        pages=len(pages),
        lines_per_page=[len(p) for p in pages],
        words_per_page=[sum(len(ln.split()) for ln in p) for p in pages],
        widest_line=max((len(ln) for p in pages for ln in p), default=0),
        spill_lines=len(spill),
        spill_text=spill,
        slack_lines=slack,
        short_tails=tails,
    )


def format_report(m: Measurement, capacity_lines, capacity_chars) -> str:
    out = [f"pdf: {m.pdf}", f"pages: {m.pages}"]
    for n, (lines, words) in enumerate(zip(m.lines_per_page, m.words_per_page), 1):
        out.append(f"page {n}: {lines} lines, {words} words")
    out.append(f"longest text line: {m.widest_line} chars, for reference (wrapped bullet text runs about "
               f"{capacity_chars} per line; a heading with its date on the right can run longer)")
    if m.pages > 1:
        out.append(f"OVERFLOW: {m.spill_lines} lines past page 1. This text fell off page 1:")
        out.extend(f"  | {ln}" for ln in m.spill_text)
    elif m.lines_per_page and m.lines_per_page[0] > capacity_lines[1]:
        out.append(f"fits on one page with {m.lines_per_page[0]} lines, above the usual estimate: "
                   f"treat the page as full (estimate {capacity_lines[0]}-{capacity_lines[1]} lines)")
    elif m.slack_lines is not None:
        lo, hi = m.slack_lines
        out.append(f"fits on one page with about {lo}-{hi} lines of slack "
                   f"(estimated capacity {capacity_lines[0]}-{capacity_lines[1]} lines)")
    if m.short_tails:
        if m.pages > 1:
            out.append("short tails (trim a few words from that bullet to win back a whole line):")
        else:
            out.append("short tails (these only matter if you need to trim; each costs a whole line):")
        out.extend(f'  page {t["page"]}: "{t["line"]}" ends the line "...{t["after"][-50:]}"'
                   for t in m.short_tails)
    out.append("note: line counts come from extracted text; confirm any trim by rebuilding.")
    return "\n".join(out)


def parse_range(text: str) -> Tuple[int, int]:
    lo, _, hi = text.partition("-")
    return int(lo), int(hi or lo)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Measure a resume PDF to size a trim.")
    parser.add_argument("file", type=Path, help="a .tex (built first) or a .pdf")
    parser.add_argument("--engine", default="auto", choices=("auto",) + builder.ENGINES)
    parser.add_argument("--capacity-lines", default=DEFAULT_CAPACITY_LINES, type=parse_range)
    parser.add_argument("--capacity-chars", default=110, type=int)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    tex_text = ""

    def fail(message: str) -> int:
        print(json.dumps({"ok": False, "error": message}) if args.json else message)
        return 2

    try:
        if args.file.suffix.lower() == ".tex":
            tex_text = args.file.read_text(encoding="utf-8")
            pdf = builder.build(args.file, args.engine).pdf
        else:
            pdf = args.file
        m = measure(pdf, tex_text, args.capacity_lines, args.capacity_chars)
    except ImportError as err:
        return fail(f"missing dependency {err.name}: pip install {err.name}, or run this script with uv run")
    except builder.BuildError as err:
        return fail(f"BUILD FAILED: {err}")
    except Exception as err:  # unreadable or missing PDF
        return fail(f"cannot read {args.file}: {err}")
    if not any(m.lines_per_page):  # no pages, or pages with no text layer: nothing was measured
        return fail(f"no text could be extracted from {m.pdf}; it cannot be measured")
    print(json.dumps({"ok": True, **asdict(m)}, indent=2) if args.json
          else format_report(m, args.capacity_lines, args.capacity_chars))
    return 0 if m.pages <= 1 else 1


if __name__ == "__main__":
    sys.exit(main())
