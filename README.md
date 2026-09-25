# resume-tailor

An agent skill that tailors a one-page LaTeX resume to a job description, using only facts you
have confirmed from your own GitHub repositories.

Set it up once: it builds a private workspace with your base resume and a facts file drawn from
your repositories. Then, for each job, paste the description and get back a PDF named for the
company and role, still on one page, with every claim traceable and every gap said out loud.

![A resume built from the template, with fictional content](docs/example.png)

## What it enforces

- **One page.** Checked after every edit, by compiling and counting.
- **No invented facts.** Each project gets a facts entry, confirmed by you, recording what it is
  and the strongest claim it can honestly carry. Tailoring rewords; it never inflates.
- **You decide every cut.** When a page overflows, the agent measures the overflow in lines and
  offers 3-4 complete trim packages. Nothing is cut until you pick one.
- **Bases stay clean.** Each application gets its own copy, so your base resume stays neutral.
- **No em-dashes, plain sentences, honest link labels** (`View Project`, `Live Demo`, `Demo Video`).
- **Gaps said out loud.** A requirement with nothing behind it is reported, not papered over.
- **Look before done.** Every verify run renders page 1 to an image, and the agent reads it.

## Install

**Any agent, one command** (Claude Code, Codex, Cursor, Gemini CLI, OpenCode, Windsurf, GitHub
Copilot, Cline, and the rest of the [skills CLI](https://skills.sh) list):

    npx skills add ishanavasthi/resume-tailor

It asks which agents to install to. To skip the prompts, name the agents, or use `*` for all:

    npx skills add ishanavasthi/resume-tailor -a claude-code -a codex -y
    npx skills add ishanavasthi/resume-tailor -a '*' -y

Add `-g` to install for every project on the machine instead of the current one. The command
installs the whole `skills/resume-tailor/` folder (instructions, scripts, template), so the
scripts run from wherever it lands.

**Claude Code, as a plugin** (an alternative to the command above):

    /plugin marketplace add ishanavasthi/resume-tailor
    /plugin install resume-tailor@resume-tailor

**By hand:** copy `skills/resume-tailor/` into your agent's skills folder. It follows the
[Agent Skills](https://agentskills.io) format, so any agent that reads `SKILL.md` can use it.

[![skills.sh](https://skills.sh/b/ishanavasthi/resume-tailor)](https://skills.sh/ishanavasthi/resume-tailor)

## Requirements

- Python 3.9+ with `pypdf`, `pypdfium2`, and `pillow`, or [`uv`](https://docs.astral.sh/uv/),
  which installs what each script needs
- A TeX engine: `pdflatex` (TeX Live, MacTeX, MiKTeX) or [`tectonic`](https://tectonic-typesetting.github.io)
- The [GitHub CLI](https://cli.github.com), logged in (`gh auth login`), so the agent can read
  your repositories
- Optional: poppler's `pdftoppm` for page previews (`pypdfium2` is the fallback)

## First prompt

After installing, open your agent in the folder where you want the workspace (or anywhere; it
will ask) and paste this:

    Use the resume-tailor skill to set up my resume workspace from the beginning.
    Check the tools it needs (Python, a TeX engine, pypdf, a page renderer, the GitHub CLI) and
    give me the install commands for anything missing before going on. Check that gh is logged
    in; if not, tell me and wait. Then ask me, a few questions at a time, where the workspace
    should live, my name, and whether I am starting from an existing LaTeX resume, an old PDF,
    or nothing. Build the facts file from my GitHub repositories and confirm each entry with me
    before you use it. Finish with a verified one-page base resume and tell me what you built,
    what is on the page, and what is still missing.

In Claude Code, `Set up my resume workspace.` is enough on its own: the skill's description
matches it and the setup steps do the rest. The longer prompt is for agents that pick skills
less eagerly, and it makes the agent say what it is about to do before it does it.

If you already have a workspace, open the agent inside that folder; its `AGENTS.md` points the
agent at the skill and your notes.

## Then

Each of these is a complete request. Paste a job description or a link where shown.

    Tailor my resume for this job: <paste the description or a link>
    Tailor my resume for the Backend Engineer role at Northwind Logistics: <link>

    My resume spills onto a second page. Measure it and give me trim options.

    Add a bullet to my internship about the dashboard work I did.
    Remove the StudyBuddy project from the Northwind copy and use the space for testing work.

    I shipped a new project: <repo link>. Add it to my facts file and tell me where it fits.
    Correct a fact: the FleetPing load test was 1,500 pings per second, not 2,000.

    Which of my confirmed projects best covers this requirement: <paste one line of the JD>
    What should I build next to get more backend roles? Use my gaps file.

    Start a second base for data science roles from my current one.
    I have an old PDF of my resume at ~/Downloads/resume.pdf; use it as the starting point.

What you will always get back: the PDF path, what changed, and the requirements the page does
not back. What you will never get: a cut you did not choose, a claim you did not confirm.

## Layout

    skills/resume-tailor/
      SKILL.md        routing and the hard rules
      references/     rules, setup, tailoring, overflow, facts, template, project ideas
      scripts/        build, verify, measure, extract_pdf, init_workspace
      assets/         the LaTeX template and the workspace starter files

Your data never goes in this repository. The workspace the skill creates is yours, and private.

### Your workspace

Setup creates a folder of your own, outside this repository:

    AGENTS.md         instructions any agent reads on entering the folder
    CLAUDE.md         points Claude Code at AGENTS.md
    bases/            your base resumes, one per role family, never tailored in place
    tailored/         one copy per application: Resume-<Company>.tex
    pdfs/             finished PDFs: <First>_<Last>_Resume_<Company>_<Role>.pdf
    notes/
      facts.md        what each project and job actually is; every claim traces here
      variants.md     what each base contains, and the decisions locked in so far
      roles.md        company and role research
      gaps.md         job requirements with nothing behind them, and other open risks

To create one by hand, without an agent:

    uv run skills/resume-tailor/scripts/init_workspace.py ~/resume --name "First Last" --from-template

`--from-template` is optional: it seeds `bases/Resume.tex` from the template. The script never
overwrites an existing file.

## The scripts on their own

They work without an agent:

    uv run skills/resume-tailor/scripts/verify.py my-resume.tex
    uv run skills/resume-tailor/scripts/measure.py my-resume.tex

`verify.py` checks one page, em-dashes, overfull boxes, and leftover placeholders, and renders
page 1. `measure.py` reports how far a page overflows, the text that spilled, and the cheapest
lines to win back.

## Development

    uv run --no-project --with-requirements requirements-dev.txt pytest -q

CI runs the suite with both pdflatex and tectonic.

## Credits

Built by [Ishan Avasthi](https://github.com/ishanavasthi), from a workflow used for real job
applications.

The LaTeX template is [Jake Gutierrez's resume](https://github.com/jakegut/resume) (MIT), itself
based on [sb2nov/resume](https://github.com/sb2nov/resume) (MIT), with wider usable width and
fictional example content.

## License

MIT. See [LICENSE](LICENSE), which also carries the template's upstream notices.
