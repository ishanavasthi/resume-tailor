# Hard rules

These hold for every base, every tailored copy, every pass. Breaking one is a defect, not a
style choice. `scripts/verify.py` checks the mechanical ones; the rest are on you.

## 1. Exactly one page

After every edit, run `verify.py`. It fails on anything but one page. If the page overflows,
follow `overflow.md`. Do not cut anything on your own judgement.

## 2. No em-dashes

No U+2014 em-dash character, no `---` (LaTeX prints it as an em-dash), no `\textemdash`. Use a comma, a
colon, parentheses, or two sentences. `--` for date ranges is fine. Em-dashes are widely read
as a sign of machine-written text, and a reader who spots one reads the rest of the page
differently. `verify.py` checks both the source and the text of the PDF.

## 3. Plain, direct language

Mirror a job description by reframing the work in its terms, not by pasting its keywords in a
row. A bullet should read as a sentence a person would say: what was built, how, and what came
of it. A bullet that reads like a keyword list is worse than one that misses a keyword.

## 4. Facts are fixed

Rewording is allowed; changing the work is not. Every claim on the page traces to an entry in
`notes/facts.md` that the user confirmed. Do not inflate scope ("led" for "contributed to"),
invent or round up numbers, rename a technique to a grander one, or present coursework as
production work. When a job description wants something the facts do not support, say so
(rule 9). Details: `facts.md`.

## 5. Never tailor inside a base

A base is the neutral reference the user starts every pass from. To tailor, copy the matching
base to `tailored/Resume-<Company>.tex` and edit the copy. Edit a base only when the user asks
for a change to the reusable version itself.

## 6. Never trim on your own

On overflow: measure, report, offer 3-4 complete trim packages, and wait for the user to pick
one. Protocol: `overflow.md`.

## 7. Look at the page

`verify.py` renders page 1 to a PNG. Read the image before saying the resume is done. The page
count alone misses a heading stranded at the bottom, a link that wrapped, uneven spacing, and
bullets whose last line is a single word.

## 8. Link labels say what is behind the link

| Label | Behind it |
|---|---|
| `View Project` | the source repository |
| `Live Demo` | a deployed app that works today |
| `Demo Video` | a recording, when nothing is deployed |

A second link on one entry may carry a specific label (`Notebook`, `Paper`, `Case Study`) when
none of the three fits. `verify.py` warns on any other label in the Projects section so you look
at it. Never label a recording `Live Demo`. A project with no confirmed URL gets no link at all
(`facts.md`).

## 9. Name the gaps

When a job description asks for something no fact backs, or a skill is listed with no project
behind it, tell the user plainly and log it in `notes/gaps.md`. The user would rather hear the
risk than get a clean-looking page that falls apart in an interview.

## 10. Keep credit that a cut would destroy

If a trim would remove the only line carrying a credential (a hackathon win, an award, a
publication), offer to fold it into a project title instead, for example
`ProjectName: One-line Pitch (Hackathon Name, 1st place)`.

## 11. File naming

- Base: `bases/Resume.tex`, then `bases/Resume-<Family>.tex` for each added role family.
- Tailored copy: `tailored/Resume-<Company>.tex`; add `-<Role>` when one company has two roles.
- PDF: `pdfs/<First>_<Last>_Resume_<Company>_<Role>.pdf`. The name prefix is recorded in the
  workspace `AGENTS.md`.
- Multi-word company and role names: join the words with underscores and drop punctuation, in
  both the `.tex` and the PDF name. "Northwind Logistics", "Backend Engineer, Intern" become
  `tailored/Resume-Northwind_Logistics.tex` and
  `pdfs/Avery_Sample_Resume_Northwind_Logistics_Backend_Engineer_Intern.pdf`.
