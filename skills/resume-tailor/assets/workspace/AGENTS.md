# Resume workspace: {{NAME}}

This folder holds {{NAME}}'s resume sources, tailored copies, compiled PDFs, and the notes an
agent needs to tailor a resume for a new job description. It is private. Never publish it or
push it to a public repository: it contains contact details.

Work here with the `resume-tailor` skill (https://github.com/ishanavasthi/resume-tailor). If the
skill is not loaded, ask the user to install it before editing anything
(`npx skills add ishanavasthi/resume-tailor` works for most agents).

## Layout

| Path | What it is |
|---|---|
| `bases/` | Neutral base resumes, one per role family. Never tailored in place. |
| `tailored/` | `Resume-<Company>.tex`: a copy of a base, edited for one job description. |
| `pdfs/` | Compiled output, named `{{PDF_PREFIX}}_Resume_<Company>_<Role>.pdf`. |
| `notes/facts.md` | What each project and job actually is. Every claim on a page traces here. |
| `notes/variants.md` | What each base contains, and the decisions locked in so far. |
| `notes/roles.md` | Company and role research. |
| `notes/gaps.md` | Job requirements with nothing behind them, and other open risks. |
| `preview.png` | The latest page-1 preview from `verify.py --png preview.png`. Git-ignored. |

## Rules

The hard rules live in the skill (`references/rules.md`) and always apply. The two broken most
often: never edit a base to tailor for a company, and never cut content to fix an overflow until
the user has picked a trim package.

## Standing preferences

Record the user's own standing decisions here as they come up, each with its date, for example:
"2026-01-10: keep the hackathon credit in the project title; never drop it."
