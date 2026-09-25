---
name: resume-tailor
description: Tailor a one-page LaTeX resume to a specific job description without inventing facts. Use when the user wants to set up a resume workspace, build a resume from scratch or from an old PDF, tailor a resume for a company or job posting, fix a resume that spills onto a second page, or decide what project to build next for a role. Enforces one page and no em-dashes, traces every claim to the user's own confirmed facts, and asks before cutting anything.
license: MIT
compatibility: Needs Python 3.9+, a TeX engine (pdflatex or tectonic), and the GitHub CLI (gh) to read the user's repositories.
---

# resume-tailor

Produce a one-page, ATS-friendly LaTeX resume tailored to one job description, using only facts
the user has confirmed.

`<skill>` below means the absolute path of the directory this file is in. Scripts live in
`<skill>/scripts/`; run them with `python3 <skill>/scripts/NAME.py` (needs `pip install pypdf`,
and for `verify.py`'s page preview either poppler's `pdftoppm` or `pip install pypdfium2 pillow`)
or `uv run <skill>/scripts/NAME.py` (installs what it needs). Run them from the user's workspace.

## Hard rules

Full text and reasons: `references/rules.md`. These are not style preferences.

1. Exactly one page, verified after every edit.
2. No em-dashes: not the U+2014 character, not `---`, not `\textemdash`. Use a comma, a colon, or a new sentence.
3. Plain language. Mirror the job description's priorities in sentences, not a row of its keywords.
4. Facts are fixed. Every claim traces to a confirmed entry in the workspace's `notes/facts.md`.
5. Never tailor inside a base. Copy it to `tailored/Resume-<Company>.tex` first.
6. Never trim on your own. Measure, offer 3-4 complete trim packages, wait for the user's pick.
7. Look at the rendered page before saying it is done.
8. Link labels: `View Project` (repo), `Live Demo` (deployed), `Demo Video` (recording only).
9. Say plainly when a requirement is not met or a claim is not backed.

## Find the workspace

The user's data lives in a private workspace, never in this skill's directory. A workspace is a
folder containing `AGENTS.md`, `bases/`, and `notes/facts.md`. Check the current directory; if it
is not one, ask the user where theirs is. If they have none, run setup.

## Route

| The user... | Read and follow |
|---|---|
| has no workspace yet, or asks to set one up | `references/setup.md` |
| gives a job description, a job link, or names a company and role | `references/tailor.md` |
| has a resume that runs past one page | `references/overflow.md` |
| built or shipped something new, or corrects a fact | `references/facts.md` |
| asks to add, change, or remove content (a bullet, a skill, a project) on a resume already made | Back any new claim with a confirmed facts entry first. Edit the tailored copy for that company; edit a base only when the user asks for the base. Then `verify.py`, read the PNG, and re-save with `--save`. Steps: `references/tailor.md`, "Changing a resume after it is saved" |
| asks what to build next, or how to close a gap | `references/project-ideas.md` |
| asks to change a base itself | Only on that explicit request: edit the base, verify, update `notes/variants.md` |

Read `references/template.md` before the first `.tex` edit in a session.

## Scripts

| Command | What it does |
|---|---|
| `init_workspace.py DIR --name "First Last" [--from-template]` | Creates the workspace. Never overwrites. |
| `build.py FILE.tex` | Compiles a temporary copy. Never touches the source. |
| `verify.py FILE.tex --png preview.png [--save PDF]` | Every mechanical rule check (one page, no em-dash, no overfull or underfull boxes, no template placeholders), plus a PNG of page 1. `--save` copies the PDF only if all checks pass. |
| `measure.py FILE.tex` | Lines per page, the text that spilled, slack, and short tails, for sizing trims. |
| `extract_pdf.py FILE.pdf` | Text from an old resume PDF, for setup. |

Exit codes: `0` pass; `1` a check failed or the script refused (overflow, no text in the PDF,
workspace clash); `2` a missing tool, bad input, or a LaTeX error. Add `--json` for
machine-readable output.

Always pass `--png preview.png` to `verify.py`, so the preview lands in the workspace root, where
the workspace `.gitignore` ignores it. Without `--png` the image stays in a temporary directory
outside the workspace. `build.py`, `verify.py`, and `measure.py` all compile into a temporary
directory, by design; only `--save` and `--png` write into the workspace.

`verify.py`'s "no template placeholders" check fails on any non-comment line containing
`Avery Sample` (the template's fictional name), `example.com`, or `TODO`. A FAIL there means
template text is still on the page: replace it with the user's real details.
`--allow-placeholders` skips the check; use it only to verify the shipped template or a
deliberately fictional page, never a real resume.

## Done means

`verify.py` exits 0, you have read the PNG it printed, the PDF is saved in `pdfs/` under the
naming rule, and the workspace notes are updated. Then report: the PDF path, what changed and
why, and every gap you found. Free lines are not a defect: if the user has nothing more to add,
say once how many lines are free and stop. Never pad to fill the page.
