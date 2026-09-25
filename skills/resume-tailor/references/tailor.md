# Tailor for one job description

Goal: `pdfs/<First>_<Last>_Resume_<Company>_<Role>.pdf`, one page, every claim backed, every gap
named.

## 1. Read the job description

Take it as pasted text or a link (fetch the page; if it will not load, ask for the text). Note:

- the company and the exact role title
- the role family, which decides the base
- what it names more than once, and what it marks required versus nice to have
- its words for things the user has done (it may say "evaluation" where the user wrote "tests")

If the user wants, research the company briefly (what the team builds, recent launches) and log
it in `notes/roles.md`. Research shapes framing; it never adds claims.

## 2. Pick the base

Match the role family to a base listed in `notes/variants.md`. If none fits, say so and offer a
new base for that family: copy the closest base to `bases/Resume-<Family>.tex` and adjust it with
the user. Never quietly bend one base into another family.

## 3. Copy it

    cp bases/<base picked in step 2> tailored/Resume-<Company>.tex

If that file exists, ask whether to overwrite it or add the role (`Resume-<Company>-<Role>.tex`).
A copy that was already sent is a record of what went out; do not reuse it for a new
application.

## 4. Map requirements to facts

List each requirement next to the facts entry that backs it, or "none". Show the user the "none"
rows before writing anything, in plain words, for example:

> The posting asks for Kubernetes. Nothing in your facts file uses it, so I will not list it. If
> you have used it somewhere the facts file does not cover yet, tell me and I will add an entry.

Log every unbacked requirement in `notes/gaps.md`.

## 5. Reframe

In the copy only:

- Put the strongest match first.
- Reword bullets into the posting's vocabulary where the facts support it, leading with what it
  cares about most.
- Swap in a different project from `notes/facts.md` when it fits better than one on the base.
- Reorder the skills lines. Drop skills that do not matter for this role before adding new ones.
- Keep every number exactly as the facts file states it.

Test every changed bullet: could the user defend this sentence, word for word, in an interview?

## 6. Build and verify

    python3 <skill>/scripts/verify.py tailored/Resume-<Company>.tex

Fix every failure, then read the PNG. If it overflows, stop and follow `overflow.md`. If more than
about 3 lines are free (`measure.py` reports the slack), tell the user and offer real content to
fill them.

## 7. Save and record

When `verify.py` passes and you have read the page:

    python3 <skill>/scripts/verify.py tailored/Resume-<Company>.tex --save pdfs/<First>_<Last>_Resume_<Company>_<Role>.pdf

Then add a row to the tailored copies table in `notes/variants.md`, update `notes/roles.md` if
you researched, and commit if the workspace is a git repository.

## 8. Report

Tell the user, briefly: the PDF path; what you changed and why (reordered, reworded, swapped);
every gap from step 4; anything you were unsure about. Offer the PNG or the PDF to look at.
