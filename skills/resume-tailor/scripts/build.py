#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Compile a resume .tex file to PDF without touching the source.

Usage: build.py FILE.tex [--engine auto|pdflatex|tectonic|xelatex] [--out DIR] [--json]

The source is copied into a build directory and compiled there. For engines other than
pdflatex, the two pdfTeX-only preamble lines are commented out in that copy only; they map
glyphs for text extraction and do not affect layout.
Exit codes: 0 built, 2 missing engine or LaTeX error.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

ENGINES = ("pdflatex", "tectonic", "xelatex")
PDFTEX_ONLY = (
    re.compile(r"^\\input\{glyphtounicode\}", re.M),
    re.compile(r"^\\pdfgentounicode=1", re.M),
)
BOX_RE = re.compile(
    r"^(Overfull|Underfull) \\([hv])box \(([^)]*)\)"
    r"(?: in paragraph at lines (\d+)--\d+| detected at line (\d+))?",
    re.M,
)
ERROR_RE = re.compile(r"^! (.+)$", re.M)
ERROR_LINE_RE = re.compile(r"^l\.(\d+)", re.M)
TIMEOUT_SECONDS = 300
SAME_DIR_MESSAGE = "the build directory must not be the source's directory; the source would be overwritten"
INSTALL_HINTS = """No TeX engine found. Install one:
  macOS:   brew install tectonic   (or MacTeX for pdflatex)
  Linux:   sudo apt-get install texlive-latex-extra texlive-fonts-recommended
  Windows: MiKTeX, https://miktex.org/download"""


class BuildError(Exception):
    """No usable engine, or LaTeX failed."""


@dataclass
class BoxWarning:
    kind: str
    box: str
    detail: str
    line: Optional[int]

    def __str__(self) -> str:
        where = f"line {self.line}" if self.line else "an unknown line"
        return f"{self.kind} \\{self.box} ({self.detail}) at {where}"


@dataclass
class BuildResult:
    source: str
    pdf: str
    engine: str
    warnings: List[BoxWarning] = field(default_factory=list)


def find_engine(preferred: str = "auto") -> str:
    if preferred != "auto":
        if preferred not in ENGINES:
            raise BuildError(f"unknown engine {preferred!r}; use one of {', '.join(ENGINES)}")
        if not shutil.which(preferred):
            raise BuildError(f"{preferred} is not installed.\n{INSTALL_HINTS}")
        return preferred
    for name in ENGINES:
        if shutil.which(name):
            return name
    raise BuildError(INSTALL_HINTS)


def prepare_source(text: str, engine: str) -> str:
    """Comment out pdfTeX-only lines for other engines. Line numbers are preserved."""
    if engine == "pdflatex":
        return text
    for pattern in PDFTEX_ONLY:
        text = pattern.sub(lambda m: "%" + m.group(0), text)
    return text


def parse_log(log_text: str) -> List[BoxWarning]:
    found = []
    for m in BOX_RE.finditer(log_text):
        line = m.group(4) or m.group(5)
        found.append(BoxWarning(m.group(1), m.group(2) + "box", m.group(3), int(line) if line else None))
    return found


def first_error(log_text: str) -> str:
    m = ERROR_RE.search(log_text)
    if not m:
        return ""
    at = ERROR_LINE_RE.search(log_text, m.end())
    return f"{m.group(1)} (line {at.group(1)})" if at else m.group(1)


def _command(engine: str, out_dir: Path, name: str) -> List[str]:
    if engine == "tectonic":
        return ["tectonic", "--keep-logs", "-o", str(out_dir), name]
    return [engine, "-interaction=nonstopmode", "-halt-on-error", f"-output-directory={out_dir}", name]


def build(source, engine: str = "auto", out_dir=None) -> BuildResult:
    source = Path(source).resolve()
    if not source.is_file():
        raise BuildError(f"no such file: {source}")
    out_dir = Path(out_dir).resolve() if out_dir else Path(tempfile.mkdtemp(prefix="resume-build-"))
    # samefile catches a case-flipped or hard-linked path that the string compare misses
    # on case-insensitive filesystems; the string compare covers an out dir not yet created.
    if out_dir == source.parent or (out_dir.exists() and out_dir.samefile(source.parent)):
        raise BuildError(SAME_DIR_MESSAGE)
    engine = find_engine(engine)
    work = out_dir / source.name
    try:
        text = source.read_text(encoding="utf-8")
        out_dir.mkdir(parents=True, exist_ok=True)
        if work.exists() and work.samefile(source):
            raise BuildError(SAME_DIR_MESSAGE)
        work.write_text(prepare_source(text, engine), encoding="utf-8")
        stale_log = out_dir / f"{source.stem}.log"
        if stale_log.exists():
            stale_log.unlink()  # a log left by an earlier build would give a stale first_error
    except (OSError, UnicodeDecodeError) as err:
        raise BuildError(f"cannot prepare the build copy of {source.name}: {err}")
    passes = 1 if engine == "tectonic" else 2  # tectonic reruns by itself; pdflatex needs a second pass for hyperref
    proc = None
    for _ in range(passes):
        try:
            proc = subprocess.run(_command(engine, out_dir, work.name), cwd=out_dir,
                                  capture_output=True, text=True, timeout=TIMEOUT_SECONDS)
        except subprocess.TimeoutExpired:
            raise BuildError(f"{engine} timed out after {TIMEOUT_SECONDS}s")
        if proc.returncode != 0:
            break
    pdf, log = out_dir / f"{source.stem}.pdf", out_dir / f"{source.stem}.log"
    log_text = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    if proc.returncode != 0 or not pdf.exists():
        detail = first_error(log_text) or (proc.stderr or proc.stdout).strip()[-1500:]
        raise BuildError(f"{engine} failed on {source.name}: {detail}")
    return BuildResult(str(source), str(pdf), engine, parse_log(log_text))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Compile a resume .tex file to PDF without touching the source.")
    parser.add_argument("tex", type=Path)
    parser.add_argument("--engine", default="auto", choices=("auto",) + ENGINES)
    parser.add_argument("--out", type=Path, help="build directory (default: a new temp directory)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = build(args.tex, args.engine, args.out)
    except BuildError as err:
        print(json.dumps({"ok": False, "error": str(err)}) if args.json else f"BUILD FAILED: {err}")
        return 2
    if args.json:
        print(json.dumps({"ok": True, **asdict(result)}, indent=2))
    else:
        print(f"built {result.pdf} with {result.engine}")
        for warning in result.warnings:
            print(f"  warning: {warning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
