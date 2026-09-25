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
which organisations, hold the work they want on the resume. If `gh` is logged in as a different
account, say so; public repositories can still be listed by name, and for private ones ask the
user to switch accounts themselves (`gh auth switch`). If a project is only on disk, read it
there and skip the `gh` commands for it.

## 2. Create the workspace

Ask three things first: where it should live (suggest `~/resume`), the name to use in PDF file
names, and which starting point applies (step 3): an existing LaTeX resume, an old PDF or Word
file, or nothing yet. The starting point decides the command.

For an old PDF, a Word file, or from scratch, seed `bases/Resume.tex` with the template:

    python3 <skill>/scripts/init_workspace.py ~/resume --name "First Last" --from-template

For an existing LaTeX resume, leave the flag off; step 3 copies their file into `bases/`:

    python3 <skill>/scripts/init_workspace.py ~/resume --name "First Last"

If it exits 1 with "refusing to overwrite", a workspace (or other files) already exists there and
nothing was written. Stop and ask the user whether to use that workspace or pick another folder.
If they use it and it has no `bases/Resume.tex` yet, seed one by hand when the route needs the
template:

    cp <skill>/assets/template.tex <workspace>/bases/Resume.tex

Then `cd` into the workspace and work from there from here on. Offer, as two separate questions:

1. `git init`, so every change is recorded.
2. Only if they said yes to git: a private GitHub backup,
   `gh repo create <name> --private --source .`. It adds the remote without pushing; the first
   push happens after the base is committed in step 5. The resume holds a phone number and an
   email address. Never create a public repository for it.

## 3. Bring in the starting point

**A LaTeX resume.** Copy it to `bases/Resume.tex` and run
`verify.py bases/Resume.tex --png preview.png` on it. If it is not on this skill's template,
offer to move the content onto the template and say why: one column, real text, no tables used
for layout, no icons, which is the shape applicant tracking systems parse most
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
   ceiling: the strongest true claim, and the grander label it must not be given. Ask for the
   public URL of each repository and of any deployment; if none is confirmed, the entry's Source
   says so and the project goes on the page with no link.
5. Show each entry to the user, ask them to correct it, and record the date they confirmed it.
   Confirmed means the user said yes to the entry as shown, including every detail you read from
   the code. Silence, or "they did not correct it", is not confirmation: an entry with no date
   is a draft, and nothing from a draft goes on a page. See "What counts as confirmed" in
   `facts.md`.

Do the same for experience: draft one entry per role under `## Experience` in `notes/facts.md`,
in the same format plus a **Work** field for what they did in their own words (the example is in
`facts.md`), from what the user told you in step 3 (or from the old resume's text). Show
each to the user, ask them to correct it, and record the date they confirmed it, exactly as for
projects. For private or employer-owned repositories, never link them on the page, and describe
the work in the user's own words.

## 5. Draft the base

1. Ask which role family this base is for (for example "backend engineering") and record it in
   `notes/variants.md`. If the user has no preference, propose the family their confirmed facts
   point to and ask them to confirm it.
2. Pick the projects from `notes/facts.md` that best fit that family, and write the bullets from
   the facts. Follow `template.md` for structure.
3. Run `verify.py bases/Resume.tex --png preview.png`. Fix every failure, then read
   `preview.png`.
4. On overflow, follow `overflow.md`. With slack, tell the user how much and offer real content
   to fill it (another project, a bullet with a number), never padding. If they have nothing to
   add, the base is done with the free lines: note the slack in `notes/variants.md`, say so once,
   and move on.
5. Record the page-1 line count from `measure.py` in `notes/variants.md`.
6. If the workspace is a git repository, commit. If the user created the private backup in
   step 2, push this first commit: `git push -u origin HEAD`.

Setup is done when the base passes `verify.py`, the user has seen the page, and every claim on it
has a confirmed facts entry.
