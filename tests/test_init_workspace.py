import json

from helpers import SKILL, run_script
import init_workspace as iw

EXPECTED = ("AGENTS.md", "CLAUDE.md", ".gitignore", "notes/facts.md", "notes/variants.md",
            "notes/roles.md", "notes/gaps.md", "bases/.gitkeep", "tailored/.gitkeep", "pdfs/.gitkeep")


def test_creates_the_workspace_and_fills_every_token(tmp_path):
    ws = tmp_path / "resume"
    proc = run_script("init_workspace.py", ws, "--name", "Jordan Lee")
    assert proc.returncode == 0, proc.stdout
    for rel in EXPECTED:
        assert (ws / rel).exists(), rel
    agents = (ws / "AGENTS.md").read_text()
    assert "Jordan Lee" in agents and "Jordan_Lee_Resume_" in agents
    for path in ws.rglob("*"):
        if path.is_file():
            assert "{{" not in path.read_text(), path
    assert not (ws / "bases" / "Resume.tex").exists()


def test_from_template_seeds_the_base(tmp_path):
    ws = tmp_path / "resume"
    assert run_script("init_workspace.py", ws, "--name", "Jordan Lee", "--from-template").returncode == 0
    assert "\\resumeSubheading" in (ws / "bases" / "Resume.tex").read_text()


def test_refuses_to_overwrite_and_writes_nothing(tmp_path):
    ws = tmp_path / "resume"
    run_script("init_workspace.py", ws, "--name", "Jordan Lee")
    (ws / "notes" / "facts.md").write_text("mine")
    proc = run_script("init_workspace.py", ws, "--name", "Someone Else", "--from-template")
    assert proc.returncode == 1
    assert (ws / "notes" / "facts.md").read_text() == "mine"
    assert not (ws / "bases" / "Resume.tex").exists()


def test_empty_name_exits_2(tmp_path):
    assert run_script("init_workspace.py", tmp_path / "ws", "--name", "  ").returncode == 2


def test_pdf_prefix_keeps_unicode_letters():
    assert iw.pdf_prefix("José Núñez-Díaz") == "José_Núñez_Díaz"
    assert iw.pdf_prefix("  Jordan   Lee ") == "Jordan_Lee"


def test_json_output_on_every_exit(tmp_path):
    ws = tmp_path / "resume"
    ok = run_script("init_workspace.py", ws, "--name", "Jordan Lee", "--json")
    assert ok.returncode == 0
    report = json.loads(ok.stdout)
    assert report["ok"] is True and report["name"] == "Jordan Lee"
    assert report["pdf_prefix"] == "Jordan_Lee"
    assert str(ws / "AGENTS.md") in report["files"]

    clash = run_script("init_workspace.py", ws, "--name", "Jordan Lee", "--json")
    assert clash.returncode == 1
    report = json.loads(clash.stdout)
    assert report["ok"] is False and "AGENTS.md" in report["error"]

    empty = run_script("init_workspace.py", tmp_path / "other", "--name", "", "--json")
    assert empty.returncode == 2
    assert json.loads(empty.stdout)["ok"] is False
    assert not (tmp_path / "other").exists()


def test_a_file_where_a_folder_goes_is_a_clash(tmp_path):
    ws = tmp_path / "resume"
    ws.mkdir()
    (ws / "notes").write_text("not a folder")
    proc = run_script("init_workspace.py", ws, "--name", "Jordan Lee")
    assert proc.returncode == 1
    assert "Traceback" not in proc.stderr
    assert sorted(p.name for p in ws.iterdir()) == ["notes"]


def test_a_dangling_symlink_is_a_clash(tmp_path):
    ws = tmp_path / "resume"
    ws.mkdir()
    outside = tmp_path / "outside.md"
    (ws / "AGENTS.md").symlink_to(outside)
    proc = run_script("init_workspace.py", ws, "--name", "Jordan Lee")
    assert proc.returncode == 1
    assert not outside.exists()
    assert sorted(p.name for p in ws.iterdir()) == ["AGENTS.md"]


def test_target_that_is_a_file_is_a_clash(tmp_path):
    target = tmp_path / "resume"
    target.write_text("a file")
    proc = run_script("init_workspace.py", target, "--name", "Jordan Lee")
    assert proc.returncode == 1
    assert "Traceback" not in proc.stderr
    assert target.read_text() == "a file"


def test_finder_litter_is_not_copied(tmp_path, monkeypatch):
    starter = tmp_path / "starter"
    (starter / "notes").mkdir(parents=True)
    (starter / "notes" / "facts.md").write_text("# Facts\n")
    (starter / ".DS_Store").write_bytes(b"\x00\x01\xff")
    monkeypatch.setattr(iw, "STARTER", starter)
    ws = tmp_path / "resume"
    assert iw.init_workspace(ws, "Jordan Lee") == [ws / "notes" / "facts.md"]
    assert not (ws / ".DS_Store").exists()


def test_workspace_gitignore_ignores_the_preview_the_skill_writes(tmp_path):
    ws = tmp_path / "resume"
    assert run_script("init_workspace.py", ws, "--name", "Jordan Lee").returncode == 0
    ignored = (ws / ".gitignore").read_text().splitlines()
    assert "preview.png" in ignored
    assert "--png preview.png" in (SKILL / "SKILL.md").read_text(encoding="utf-8")


def test_tailored_copies_table_records_whether_each_copy_was_sent(tmp_path):
    ws = tmp_path / "resume"
    assert run_script("init_workspace.py", ws, "--name", "Jordan Lee").returncode == 0
    header = next(ln for ln in (ws / "notes" / "variants.md").read_text().splitlines()
                  if ln.startswith("| File | Company"))
    assert header.rstrip().endswith("| Sent |")
