# Setup (first run)

Goal: a private workspace holding one verified base resume and a facts file the user has
confirmed. Do the steps in order. Ask one small batch of questions at a time.

## 1. Check the tools

Run the checks and report anything missing with the install line for the user's system.

| Need | Check | Install |
|---|---|---|
| Python 3.9+ | `python3 --version` | python.org, or `brew install python` |
| A TeX engine | `pdflatex --version` or `tectonic --version` | macOS `brew install tectonic`; Linux `sudo apt-get install texlive-latex-extra texlive-fonts-recommended`; Windows MiKTeX |
| pypdf | `python3 -c "import pypdf"` | `pip install pypdf`, or use `uv run`, which installs it per script |
| A page renderer, for `verify.py`'s preview | `pdftoppm -v` | macOS `brew install poppler`; Linux `sudo apt-get install poppler-utils`; or `pip install pypdfium2 pillow`, which `uv run` installs per script |
| GitHub CLI | `gh --version` | https://cli.github.com |

Tectonic downloads LaTeX packages on first use, so the first build needs a network connection
and can take a minute.

Then run `gh auth status`. If the user is not logged in, ask them to run `gh auth login`
themselves. Never ask for, type, or handle a token or password. Ask which GitHub account, and
which organisations, hold the work they want on the resume.

## 2. Create the workspace

Ask where it should live (suggest `~/resume`) and the name to use in PDF file names. Then:

    python3 <skill>/scripts/init_workspace.py ~/resume --name "First Last"

Add `--from-template` when starting from scratch or from an old PDF; it seeds `bases/Resume.tex`
with the template. Then offer, as two separate questions:

1. `git init` in the workspace, so every change is recorded.
2. A private GitHub backup: `gh repo create <name> --private --source . --push`. The resume holds
   a phone number and an email address. Never create a public repository for it.

Work from the workspace directory from here on.

## 3. Pick the starting point

Ask which applies.

**A LaTeX resume.** Copy it to `bases/Resume.tex` and run `verify.py` on it. If it is not on this
skill's template, offer to move the content onto the template and say why: one column, real text,
no tables used for layout, no icons, which is the shape applicant tracking systems parse most
reliably. If the user declines, keep their file and treat `template.md` as a guide only.

**An old PDF, or a Word file.** For Word, ask them to export a PDF first. Then:

    python3 <skill>/scripts/extract_pdf.py old-resume.pdf

Map the text into the template's sections in `bases/Resume.tex`. Every bullet you carry over is a
claim, so it gets a facts entry in step 4 like everything else. If no text comes back, the PDF is
a scanned image; ask the user to paste the text.

**From scratch.** Interview in batches, confirming each before moving on:

1. Header: name as it should appear, phone, email, website, GitHub, LinkedIn.
2. Education: institution, degree, dates, and a grade only if they want it shown.
3. Experience: for each role, the title, organisation, dates, location, and what they did in their
   own words. Ask for numbers, and where each number comes from.
4. Skills they would be comfortable being questioned on in an interview.

Projects come from step 4.

## 4. Build the facts file

This step is what keeps every later tailoring honest. Take the time.

1. List candidate repositories, forks excluded:
   `gh repo list <account> --limit 200 --no-archived --source --json name,description,pushedAt,isPrivate,primaryLanguage`
   Repeat for each organisation the user named.
2. Show the list, most recently pushed first, and ask which count as resume projects.
3. For each chosen repository, read enough to know what it really is: the README, the top-level
   layout, the main entry points, the tests, the CI configuration, and recent commits
   (`gh api "repos/<owner>/<repo>/commits?per_page=30"`) for how current it is and, on shared
   repositories, how much of it is the user's.
4. Draft an entry in `notes/facts.md` in the format from `facts.md`, including the honest
   ceiling: the strongest true claim, and the grander label it must not be given.
5. Show each entry to the user, ask them to correct it, and record the date they confirmed it.

For experience, use what the user told you. For private or employer-owned repositories, never
link them on the page, and describe the work in the user's own words.

## 5. Draft the base

1. Ask which role family this base is for (for example "backend engineering") and record it in
   `notes/variants.md`.
2. Pick the projects from `notes/facts.md` that best fit that family, and write the bullets from
   the facts. Follow `template.md` for structure.
3. Run `verify.py bases/Resume.tex`. Fix every failure, then read the PNG.
4. On overflow, follow `overflow.md`. With slack, tell the user how much and offer real content
   to fill it (another project, a bullet with a number), never padding.
5. Record the page-1 line count from `measure.py` in `notes/variants.md`.
6. If the workspace is a git repository, commit.

Setup is done when the base passes `verify.py`, the user has seen the page, and every claim on it
has a confirmed facts entry.
