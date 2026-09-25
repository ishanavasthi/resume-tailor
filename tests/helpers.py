"""Shared test helpers: paths, engine selection, fixtures built from the shipped template."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "resume-tailor"
SCRIPTS = SKILL / "scripts"
TEMPLATE = SKILL / "assets" / "template.tex"

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

ENGINE = os.environ.get("RESUME_TAILOR_ENGINE", "auto")
_CANDIDATES = ("pdflatex", "tectonic", "xelatex") if ENGINE == "auto" else (ENGINE,)
needs_engine = pytest.mark.skipif(
    not any(shutil.which(e) for e in _CANDIDATES), reason="no TeX engine installed"
)

SKILLS_ANCHOR = r"\section{Technical Skills}"
END_ANCHOR = r"\end{document}"
LAB_ANCHOR = "Ran weekly lab sessions"
SENTINEL = "zebra marmalade sentinel"


def make_tex(tmp_path, name, *replacements):
    """Write the template to tmp_path/name with each (old, new) replacement applied once."""
    text = TEMPLATE.read_text(encoding="utf-8")
    for old, new in replacements:
        assert old in text, f"anchor missing from template: {old!r}"
        text = text.replace(old, new, 1)
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def overflow_tex(tmp_path):
    """The template plus 45 filler bullets and a sentinel, so it runs well onto page 2."""
    items = "\n".join(f"\\item Filler line {n} that pads the page past its end." for n in range(45))
    block = f"\\section{{Overflow}}\n\\begin{{itemize}}\n{items}\n\\item {SENTINEL}\n\\end{{itemize}}\n"
    return make_tex(tmp_path, "two_page.tex", (END_ANCHOR, block + END_ANCHOR))


def overfull_tex(tmp_path):
    """The template plus an unbreakable 160-char token. Returns (path, line of the token)."""
    token = "x" * 160
    block = f"\\section{{Extra}}\n\\begin{{itemize}}\n\\item \\texttt{{{token}}}\n\\end{{itemize}}\n"
    path = make_tex(tmp_path, "overfull.tex", (SKILLS_ANCHOR, block + SKILLS_ANCHOR))
    line = next(n for n, text in enumerate(path.read_text().splitlines(), 1) if token in text)
    return path, line


def run_script(script, *args, env=None):
    return subprocess.run(
        [sys.executable, str(SCRIPTS / script), *map(str, args)],
        capture_output=True, text=True, env=env,
    )
