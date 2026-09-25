import hashlib
import os

import pytest

from helpers import ENGINE, TEMPLATE, make_tex, needs_engine, overfull_tex, run_script
import build as builder

SAMPLE_LOG = r"""
Overfull \hbox (369.01471pt too wide) in paragraph at lines 152--152
[]\T1/cmtt/m/n/10.95 xxxx|
Underfull \vbox (badness 10000) has occurred while \output is active []
Underfull \hbox (badness 10000) detected at line 88
"""


def test_prepare_source_keeps_pdftex_lines_for_pdflatex():
    text = TEMPLATE.read_text()
    assert builder.prepare_source(text, "pdflatex") == text


def test_prepare_source_comments_out_pdftex_lines_and_keeps_line_count():
    text = TEMPLATE.read_text()
    out = builder.prepare_source(text, "tectonic")
    assert "\n%\\input{glyphtounicode}" in out
    assert "\n%\\pdfgentounicode=1" in out
    assert len(out.splitlines()) == len(text.splitlines())


def test_parse_log_reads_kind_detail_and_line():
    found = builder.parse_log(SAMPLE_LOG)
    assert [(w.kind, w.box, w.line) for w in found] == [
        ("Overfull", "hbox", 152), ("Underfull", "vbox", None), ("Underfull", "hbox", 88)]
    assert found[0].detail == "369.01471pt too wide"


def test_first_error_gives_message_and_line():
    log = "! Undefined control sequence.\nl.42 \\foo\n"
    assert builder.first_error(log) == "Undefined control sequence. (line 42)"


def test_find_engine_without_any_engine_raises(monkeypatch):
    monkeypatch.setattr(builder.shutil, "which", lambda name: None)
    with pytest.raises(builder.BuildError, match="No TeX engine found"):
        builder.find_engine()


def test_cli_without_engine_exits_2(tmp_path):
    proc = run_script("build.py", TEMPLATE, env=dict(os.environ, PATH=str(tmp_path)))
    assert proc.returncode == 2
    assert "No TeX engine found" in proc.stdout


def test_refuses_to_build_into_the_source_directory(tmp_path):
    src = make_tex(tmp_path, "r.tex")
    with pytest.raises(builder.BuildError, match="must not be the source"):
        builder.build(src, ENGINE, out_dir=tmp_path)


@needs_engine
def test_build_template_and_leave_source_untouched(tmp_path):
    src = make_tex(tmp_path, "resume.tex")
    before = hashlib.sha256(src.read_bytes()).hexdigest()
    result = builder.build(src, ENGINE, out_dir=tmp_path / "out")
    assert os.path.exists(result.pdf)
    assert result.warnings == []
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before


@needs_engine
def test_build_reports_overfull_with_source_line(tmp_path):
    src, line = overfull_tex(tmp_path)
    result = builder.build(src, ENGINE, out_dir=tmp_path / "out")
    assert any(w.kind == "Overfull" and w.line == line for w in result.warnings)


def test_refuses_a_case_flipped_source_directory(tmp_path):
    (tmp_path / "Aa").mkdir()
    if not (tmp_path / "aa").exists():
        pytest.skip("filesystem is case-sensitive")
    src_dir = tmp_path / "Src"
    src_dir.mkdir()
    src = make_tex(src_dir, "r.tex")
    before = hashlib.sha256(src.read_bytes()).hexdigest()
    with pytest.raises(builder.BuildError, match="must not be the source"):
        builder.build(src, ENGINE, out_dir=tmp_path / "sRC")
    assert hashlib.sha256(src.read_bytes()).hexdigest() == before
