import json

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


def test_missing_file_with_json_prints_a_json_error(tmp_path):
    proc = run_script("measure.py", tmp_path / "missing.pdf", "--json")
    assert proc.returncode == 2
    payload = json.loads(proc.stdout)
    assert payload["ok"] is False and "missing.pdf" in payload["error"]


def test_pdf_with_no_text_is_an_error_not_a_fit(tmp_path):
    from pypdf import PdfWriter
    blank = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(612, 792)
    with open(blank, "wb") as handle:
        writer.write(handle)
    text = run_script("measure.py", blank)
    assert text.returncode == 2 and "no text could be extracted" in text.stdout
    proc = run_script("measure.py", blank, "--json")
    assert proc.returncode == 2
    assert json.loads(proc.stdout)["ok"] is False


@needs_engine
def test_json_success_is_ok_and_uppercase_tex_is_built(tmp_path):
    proc = run_script("measure.py", make_tex(tmp_path, "resume.TEX"), "--engine", ENGINE, "--json")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True and payload["pages"] == 1


@needs_engine
def test_text_report_names_the_pdf(tmp_path):
    proc = run_script("measure.py", make_tex(tmp_path, "resume.tex"), "--engine", ENGINE)
    first = proc.stdout.splitlines()[0]
    assert first.startswith("pdf: ") and first.endswith("resume.pdf")


def one_page(widest=121, tails=()):
    return measure.Measurement(pdf="resume.pdf", pages=1, lines_per_page=[20], words_per_page=[200],
                               widest_line=widest, spill_lines=0, spill_text=[], slack_lines=(26, 28),
                               short_tails=list(tails))


def test_clean_page_report_reads_as_information_not_a_warning():
    report = measure.format_report(one_page(), (46, 48), 110)
    line = next(ln for ln in report.splitlines() if "121" in ln)
    assert line.startswith("longest text line: 121 chars")
    assert "for reference" in line and "widest" not in line


def test_short_tails_on_a_fitting_page_say_they_only_matter_when_trimming():
    tail = {"page": 1, "index": 3, "line": "dashboard)", "after": FULL}
    report = measure.format_report(one_page(tails=[tail]), (46, 48), 110)
    assert "only matter if you need to trim" in report


@needs_engine
def test_page_above_the_line_estimate_is_called_full_not_zero_slack(tmp_path):
    proc = run_script("measure.py", make_tex(tmp_path, "resume.tex"), "--engine", ENGINE,
                      "--capacity-lines", "10-12")
    assert proc.returncode == 0, proc.stdout
    assert "above the usual estimate: treat the page as full" in proc.stdout
    assert "0-0 lines of slack" not in proc.stdout


def test_default_line_estimate_is_46_to_54():
    assert measure.DEFAULT_CAPACITY_LINES == (46, 54)
    assert "--capacity-lines 46-54" in measure.__doc__
