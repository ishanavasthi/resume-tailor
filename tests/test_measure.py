from helpers import ENGINE, SENTINEL, make_tex, needs_engine, overflow_tex, run_script
import build as builder
import measure

FULL = "x" * 100


def test_short_tail_after_full_line_is_flagged():
    lines = ["Heading", FULL, "reconnects", "next bullet"]
    assert [t["line"] for t in measure.find_short_tails(lines, width=110)] == ["reconnects"]


def test_short_line_after_short_line_is_not_a_tail():
    assert measure.find_short_tails(["short", "tiny"], width=110) == []


def test_section_titles_are_never_tails():
    lines = [FULL, "Projects", FULL, "Open Source"]
    exclude = measure.COMMON_SECTIONS | {"open source"}
    assert measure.find_short_tails(lines, 110, exclude) == []


def test_section_titles_are_read_from_tex():
    assert measure.section_titles("\\section{Open Source}\n\\section*{Talks}") == {"open source", "talks"}


@needs_engine
def test_template_fits_with_slack_and_no_tails(tmp_path):
    src = make_tex(tmp_path, "resume.tex")
    m = measure.measure(builder.build(src, ENGINE, tmp_path / "out").pdf, src.read_text())
    assert m.pages == 1 and m.spill_lines == 0
    assert m.slack_lines[0] > 0
    assert m.short_tails == []


@needs_engine
def test_overflow_reports_spill_and_the_text_that_fell(tmp_path):
    proc = run_script("measure.py", overflow_tex(tmp_path), "--engine", ENGINE)
    assert proc.returncode == 1
    assert "OVERFLOW" in proc.stdout
    assert SENTINEL in proc.stdout


@needs_engine
def test_one_page_exits_0_and_reports_slack(tmp_path):
    proc = run_script("measure.py", make_tex(tmp_path, "resume.tex"), "--engine", ENGINE)
    assert proc.returncode == 0
    assert "slack" in proc.stdout
