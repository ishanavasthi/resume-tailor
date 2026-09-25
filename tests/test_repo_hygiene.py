import re

from helpers import ROOT, SKILL

TEXT_SUFFIXES = {".md", ".py", ".tex", ".json", ".yml", ".yaml", ".txt", ""}
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache"}


def shipped_text_files():
    for path in ROOT.rglob("*"):
        if path.is_file() and not SKIP_DIRS & set(path.parts) and path.suffix in TEXT_SUFFIXES:
            yield path


def test_no_emdash_anywhere_in_the_repo():
    offenders = [str(p.relative_to(ROOT)) for p in shipped_text_files()
                 if "\u2014" in p.read_text(encoding="utf-8")]
    assert offenders == []


def frontmatter():
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\n")
    block = text.split("---\n", 2)[1]
    return dict(line.split(": ", 1) for line in block.strip().splitlines())


def test_skill_frontmatter_follows_the_agent_skills_spec():
    meta = frontmatter()
    assert meta["name"] == SKILL.name
    assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", meta["name"]) and len(meta["name"]) <= 64
    assert 0 < len(meta["description"]) <= 1024
    assert ": " not in meta["description"]  # keeps the YAML a plain scalar


def test_every_reference_is_routed_from_skill_md():
    skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    refs = sorted((SKILL / "references").glob("*.md"))
    assert refs
    for ref in refs:
        assert f"references/{ref.name}" in skill_md, ref.name


def test_every_script_declares_its_dependencies():
    for script in (SKILL / "scripts").glob("*.py"):
        text = script.read_text(encoding="utf-8")
        assert "# /// script" in text and "requires-python" in text, script.name
