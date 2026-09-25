import json
from pathlib import Path

import pytest

from helpers import ENGINE, LAB_ANCHOR, TEMPLATE, make_tex, needs_engine, overflow_tex, run_script
import build as builder
import verify


def test_emdash_forms_are_found_but_ranges_and_comments_are_not():
    tex = "\n".join([
        "a \u2014 b",                    # 1 unicode em-dash
        "a---b",                         # 2 LaTeX ligature
        "a \\textemdash{} b",            # 3 macro
        "May 2025 -- Aug. 2025",         # 4 en-dash range: allowed
        "%----------HEADING----------",  # 5 comment: ignored
        "50\\% of it --- here",          # 6 escaped percent is not a comment
    ])
    assert [n for n, _ in verify.find_emdashes(tex)] == [1, 2, 3, 6]


def test_placeholders_found_outside_comments():
    tex = "\\textbf{Avery Sample}\n% TODO in a comment\nTODO: add a bullet"
    assert [n for n, _ in verify.find_placeholders(tex)] == [1, 3]


TEMPLATE_FICTION = ("555-010-0199", "github.com/example", "linkedin.com/in/example",
                    "Example State University", "Example Logistics Co.",
                    "ShelfScan", "ForecastCheck", "StudyBuddy")


def test_every_fictional_detail_in_the_template_is_a_placeholder():
    tex = TEMPLATE.read_text(encoding="utf-8")
    flagged = {n for n, _ in verify.find_placeholders(tex)}
    for detail in TEMPLATE_FICTION:
        lines = {n for n, line in verify._code_lines(tex) if detail in line}
        assert lines and lines <= flagged, detail


def test_link_labels_checked_only_in_projects():
    tex = (
        "\\href{https://x}{\\underline{Portfolio}}\n"
        "\\section{Projects}\n"
        "\\href{https://a}{\\underline{View Project}} \\href{https://b}{\\underline{Slides}}\n"
        "\\section{Technical Skills}\n\\href{https://c}{\\underline{Blog}}\n"
    )
    warnings = verify.link_label_warnings(tex)
    assert len(warnings) == 1 and '"Slides"' in warnings[0]


@needs_engine
def test_template_passes_when_placeholders_allowed(tmp_path):
    proc = run_script("verify.py", make_tex(tmp_path, "resume.tex"), "--engine", ENGINE,
                      "--allow-placeholders", "--json")
    assert proc.returncode == 0, proc.stdout
    payload = json.loads(proc.stdout)
    assert Path(payload["png"]).exists()
    assert payload["skipped"] == ["no template placeholders"]


@needs_engine
def test_skipped_placeholder_check_is_named_in_the_text_report(tmp_path):
    proc = run_script("verify.py", make_tex(tmp_path, "resume.tex"), "--engine", ENGINE,
                      "--allow-placeholders")
    assert proc.returncode == 0, proc.stdout
    assert "SKIP  no template placeholders (--allow-placeholders)" in proc.stdout
    assert "PASS  no template placeholders" not in proc.stdout


@needs_engine
def test_template_fails_on_its_own_placeholders(tmp_path):
    proc = run_script("verify.py", make_tex(tmp_path, "resume.tex"), "--engine", ENGINE)
    assert proc.returncode == 1
    assert "FAIL  no template placeholders" in proc.stdout


@needs_engine
def test_template_with_only_the_name_and_contact_links_replaced_still_fails(tmp_path):
    src = make_tex(tmp_path, "resume.tex",
                   ("\\scshape Avery Sample", "\\scshape Jordan Lee"),
                   ("\\href{mailto:avery@example.com}{\\underline{avery@example.com}} $|$\n", ""),
                   ("\\href{https://example.com}{\\underline{Website}} $|$\n", ""),
                   (" $|$ \\href{https://example.com/shelfscan}{\\underline{Live Demo}}", ""),
                   (" $|$ \\href{https://example.com/studybuddy-video}{\\underline{Demo Video}}", ""))
    code = [line for _, line in verify._code_lines(src.read_text(encoding="utf-8"))]
    assert not any(p in line for line in code for p in ("Avery Sample", "example.com", "TODO"))
    proc = run_script("verify.py", src, "--engine", ENGINE)
    assert proc.returncode == 1, proc.stdout
    assert "FAIL  no template placeholders" in proc.stdout
    assert "555-010-0199" in proc.stdout


@needs_engine
@pytest.mark.parametrize("dash", ["\u2014", "---"])
def test_emdash_fails_in_source_and_pdf(tmp_path, dash):
    src = make_tex(tmp_path, "dash.tex", (LAB_ANCHOR, LAB_ANCHOR + dash + "weekly"))
    proc = run_script("verify.py", src, "--engine", ENGINE, "--allow-placeholders")
    assert proc.returncode == 1
    assert "FAIL  no em-dash in source" in proc.stdout
    assert "FAIL  no em-dash in PDF text" in proc.stdout


@needs_engine
def test_two_pages_fail_the_one_page_check(tmp_path):
    proc = run_script("verify.py", overflow_tex(tmp_path), "--engine", ENGINE, "--allow-placeholders")
    assert proc.returncode == 1
    assert "FAIL  one page" in proc.stdout


@needs_engine
def test_save_copies_only_a_passing_pdf(tmp_path):
    good = make_tex(tmp_path, "good.tex")
    saved = tmp_path / "pdfs" / "Avery_Sample_Resume_Acme_SWE.pdf"
    ok = run_script("verify.py", good, "--engine", ENGINE, "--allow-placeholders", "--save", saved)
    assert ok.returncode == 0 and saved.exists()
    refused = tmp_path / "pdfs" / "refused.pdf"
    bad = run_script("verify.py", good, "--engine", ENGINE, "--save", refused)  # placeholders fail
    assert bad.returncode == 1 and not refused.exists()


@needs_engine
def test_render_falls_back_to_pypdfium2(tmp_path, monkeypatch):
    pytest.importorskip("pypdfium2")
    pdf = builder.build(make_tex(tmp_path, "r.tex"), ENGINE, tmp_path / "out").pdf
    real_which = verify.shutil.which
    monkeypatch.setattr(verify.shutil, "which",
                        lambda name: None if name == "pdftoppm" else real_which(name))
    png = verify.render_png(pdf, tmp_path / "preview.png")
    assert Path(png).stat().st_size > 10_000
