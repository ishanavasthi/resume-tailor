#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pypdf>=4", "pypdfium2>=4", "pillow>=10"]
# ///
"""Build a resume, run every mechanical hard-rule check, and render page 1 to PNG.

Usage: verify.py FILE.tex [--engine ...] [--save PDF] [--png PNG] [--allow-placeholders] [--json]

Checks: exactly one page; no em-dash in the source (U+2014, ---, \\textemdash) or in the PDF
text; no overfull or underfull boxes; no leftover template placeholders (the template's fictional
name, contact details, school, employer and project names, plus TODO). A link label in the
Projects section other than View Project, Live Demo, or Demo Video is a warning.
--save copies the built PDF to the given path, and only when every check passes.
Exit codes: 0 all checks pass, 1 a check failed, 2 build or render error.
With --json, every exit after argument parsing prints JSON: {"ok": true|false, ...checks} or
{"ok": false, "error": ...}. An argparse usage error prints plain usage text to stderr and exits 2.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

import build as builder
import measure

EMDASH = "\u2014"
LIGATURE_RE = re.compile(r"(?<!-)---(?!-)")
MACRO_RE = re.compile(r"\\textemdash(?![A-Za-z])")
COMMENT_RE = re.compile(r"(?<!\\)%.*")
# The shipped template's fictional name, contact details, school, employer and project names, plus
# TODO. Any of them on a code line means template text is still on the page. Case-sensitive.
PLACEHOLDERS = (
    "Avery Sample", "example.com", "555-010-0199", "github.com/example", "linkedin.com/in/example",
    "Example State University", "Example Logistics Co.", "ShelfScan", "ForecastCheck", "StudyBuddy",
    "TODO",
)
ALLOWED_LABELS = ("View Project", "Live Demo", "Demo Video")
LABEL_RE = re.compile(r"\\href\{[^}]*\}\{\\underline\{([^}]*)\}\}")
SECTION_SPLIT_RE = re.compile(r"\\section\*?\{([^}]*)\}")
RENDER_DPI = 110
RENDER_TIMEOUT_SECONDS = 120


@dataclass
class Check:
    name: str
    ok: bool
    detail: str = ""


@dataclass
class Report:
    source: str
    pdf: str
    engine: str
    png: Optional[str]
    checks: List[Check]
    warnings: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return all(c.ok for c in self.checks)


def _code_lines(tex_text: str):
    for n, raw in enumerate(tex_text.splitlines(), 1):
        yield n, COMMENT_RE.sub("", raw)


def find_emdashes(tex_text: str) -> List[Tuple[int, str]]:
    return [(n, line.strip()) for n, line in _code_lines(tex_text)
            if EMDASH in line or LIGATURE_RE.search(line) or MACRO_RE.search(line)]


def find_placeholders(tex_text: str) -> List[Tuple[int, str]]:
    return [(n, line.strip()) for n, line in _code_lines(tex_text)
            if any(p in line for p in PLACEHOLDERS)]


def link_label_warnings(tex_text: str) -> List[str]:
    parts = SECTION_SPLIT_RE.split(tex_text)  # [preamble, title1, body1, title2, body2, ...]
    warnings = []
    for title, body in zip(parts[1::2], parts[2::2]):
        if title.strip().lower() != "projects":
            continue
        for label in LABEL_RE.findall(COMMENT_RE.sub("", body)):
            if label.strip() not in ALLOWED_LABELS:
                warnings.append(
                    f'link label "{label.strip()}" in Projects is not one of {", ".join(ALLOWED_LABELS)}; '
                    "fine only for a second link none of them describes")
    return warnings


def render_png(pdf, png, dpi: int = RENDER_DPI) -> str:
    """Render page 1 of pdf to png, with pdftoppm if present, else pypdfium2. Returns the PNG path."""
    pdf, png = Path(pdf), Path(png)
    if png.suffix.lower() != ".png":
        png = png.with_suffix(".png")  # never write the image under another extension, .tex included
    png = png.resolve()
    png.parent.mkdir(parents=True, exist_ok=True)
    if shutil.which("pdftoppm"):
        prefix = png.with_suffix("")  # pdftoppm appends .png itself
        proc = subprocess.run(["pdftoppm", "-png", "-r", str(dpi), "-f", "1", "-l", "1", "-singlefile",
                               str(pdf), str(prefix)], capture_output=True, text=True,
                              timeout=RENDER_TIMEOUT_SECONDS)
        if proc.returncode != 0:
            raise RuntimeError(f"pdftoppm failed on {pdf.name}: {(proc.stderr or proc.stdout).strip()}")
        written = prefix.with_name(prefix.name + ".png")
        if written != png:  # a .PNG request on a case-sensitive filesystem
            written.replace(png)
        return str(png)
    try:
        import pypdfium2 as pdfium
    except ImportError:
        raise RuntimeError("cannot render a preview: install poppler (pdftoppm) or `pip install pypdfium2 pillow`")
    doc = pdfium.PdfDocument(str(pdf))
    try:
        doc[0].render(scale=dpi / 72).to_pil().save(str(png), format="PNG")
    finally:
        doc.close()
    return str(png)


def _lines(hits: List[Tuple[int, str]]) -> str:
    return "; ".join(f"line {n}: {text[:80]}" for n, text in hits)


def verify(tex, engine: str = "auto", allow_placeholders: bool = False, png=None) -> Report:
    tex = Path(tex)
    tex_text = tex.read_text(encoding="utf-8")
    result = builder.build(tex, engine)
    pages = measure.page_lines(result.pdf)
    pdf_text = "\n".join(ln for page in pages for ln in page)
    dashes = find_emdashes(tex_text)
    checks = [
        Check("one page", len(pages) == 1,
              "" if len(pages) == 1 else f"{len(pages)} pages; run measure.py to size the overflow"),
        Check("no em-dash in source", not dashes, _lines(dashes)),
        Check("no em-dash in PDF text", EMDASH not in pdf_text,
              "" if EMDASH not in pdf_text else "an em-dash reaches the page"),
        Check("no overfull or underfull boxes", not result.warnings,
              "; ".join(str(w) for w in result.warnings)),
    ]
    skipped = []
    if allow_placeholders:
        skipped.append("no template placeholders")
    else:
        holders = find_placeholders(tex_text)
        checks.append(Check("no template placeholders", not holders, _lines(holders)))
    png_path = render_png(result.pdf, png or Path(result.pdf).with_name(f"{tex.stem}-page1.png"))
    return Report(str(tex), result.pdf, result.engine, png_path, checks, link_label_warnings(tex_text),
                  skipped)


def format_report(report: Report) -> str:
    out = [f"{'PASS' if c.ok else 'FAIL'}  {c.name}" + (f": {c.detail}" if not c.ok and c.detail else "")
           for c in report.checks]
    out.extend(f"SKIP  {name} (--allow-placeholders)" for name in report.skipped)
    out.extend(f"warning: {w}" for w in report.warnings)
    out.append(f"pdf: {report.pdf} (engine: {report.engine})")
    out.append(f"page 1 rendered: {report.png}")
    out.append("Read this image before reporting done. These checks cannot see layout problems.")
    failed = sum(not c.ok for c in report.checks)
    out.append("RESULT: PASS" if report.ok else f"RESULT: FAIL ({failed} of {len(report.checks)} checks failed)")
    return "\n".join(out)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Build a resume and run every hard-rule check.")
    parser.add_argument("tex", type=Path)
    parser.add_argument("--engine", default="auto", choices=("auto",) + builder.ENGINES)
    parser.add_argument("--save", type=Path, help="copy the PDF here (a .pdf path), only if every check passes")
    parser.add_argument("--png", type=Path, help="where to write the page-1 preview")
    parser.add_argument("--allow-placeholders", action="store_true",
                        help="skip the placeholder check (for the shipped template itself)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    def fail(message: str) -> int:
        print(json.dumps({"ok": False, "error": message}) if args.json else message)
        return 2

    if args.tex.suffix.lower() != ".tex":
        return fail(f"expected a .tex source, got {args.tex}")
    if args.save and args.save.suffix.lower() != ".pdf":
        return fail(f"--save must name a .pdf file, got {args.save}")
    try:
        report = verify(args.tex, args.engine, args.allow_placeholders, args.png)
    except ImportError as err:
        return fail(f"missing dependency {err.name}: pip install {err.name}, or run this script with uv run")
    except builder.BuildError as err:
        return fail(f"BUILD FAILED: {err}")
    except (RuntimeError, subprocess.SubprocessError) as err:
        return fail(f"RENDER FAILED: {err}")
    except (OSError, UnicodeDecodeError) as err:
        return fail(f"cannot read {args.tex}: {err}")
    saved = None
    if args.save and report.ok:
        try:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(report.pdf, args.save)
        except OSError as err:
            return fail(f"all checks passed but the PDF could not be saved to {args.save}: {err}")
        saved = str(args.save)
    if args.json:
        print(json.dumps({"ok": report.ok, **asdict(report), "saved": saved}, indent=2))
    else:
        print(format_report(report))
        if args.save:
            print(f"saved: {saved}" if saved else "not saved: fix the failures first")
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
