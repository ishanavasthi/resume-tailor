import json

from pypdf import PdfWriter

from helpers import ENGINE, make_tex, needs_engine, run_script
import build as builder


def _blank_pdf(tmp_path):
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    blank = tmp_path / "blank.pdf"
    with open(blank, "wb") as fh:
        writer.write(fh)
    return blank


@needs_engine
def test_prints_the_text_of_a_real_resume(tmp_path):
    pdf = builder.build(make_tex(tmp_path, "r.tex"), ENGINE, tmp_path / "out").pdf
    proc = run_script("extract_pdf.py", pdf)
    assert proc.returncode == 0
    assert "Example State University" in proc.stdout


@needs_engine
def test_json_success_lists_the_text_of_each_page(tmp_path):
    pdf = builder.build(make_tex(tmp_path, "r.tex"), ENGINE, tmp_path / "out").pdf
    proc = run_script("extract_pdf.py", pdf, "--json")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout)
    assert payload["ok"] is True
    assert len(payload["pages"]) == 1
    assert "Example State University" in payload["pages"][0]


def test_blank_pdf_is_reported_as_a_scanned_image(tmp_path):
    proc = run_script("extract_pdf.py", _blank_pdf(tmp_path))
    assert proc.returncode == 1
    assert "scanned image" in proc.stdout


def test_blank_pdf_with_json_prints_a_json_error(tmp_path):
    proc = run_script("extract_pdf.py", _blank_pdf(tmp_path), "--json")
    assert proc.returncode == 1
    payload = json.loads(proc.stdout)
    assert payload["ok"] is False
    assert "scanned image" in payload["error"]


def test_unreadable_file_exits_2(tmp_path):
    junk = tmp_path / "junk.pdf"
    junk.write_text("not a pdf")
    proc = run_script("extract_pdf.py", junk)
    assert proc.returncode == 2
    assert "cannot read" in proc.stdout
    assert "Traceback" not in proc.stderr


def test_missing_file_with_json_prints_a_json_error(tmp_path):
    proc = run_script("extract_pdf.py", tmp_path / "missing.pdf", "--json")
    assert proc.returncode == 2
    assert "Traceback" not in proc.stderr
    payload = json.loads(proc.stdout)
    assert payload["ok"] is False
    assert "missing.pdf" in payload["error"]
