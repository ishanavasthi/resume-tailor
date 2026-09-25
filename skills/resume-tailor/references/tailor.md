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
A copy that was already sent (the `Sent` column in `notes/variants.md`) is a record of what went
out; do not reuse it for a new application. Company and role names follow rule 11 in
`rules.md`: words joined with underscores, punctuation dropped (`Northwind_Logistics`).

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
- Keep every number exactly as the facts file states it, attached to the same noun ("60
  students" never becomes "60 projects"). A number with no source in the facts file stays off
  the page, even when the work it describes goes on (`facts.md`, "Numbers with a source").

Test every changed bullet: could the user defend this sentence, word for word, in an interview?

## 6. Build and verify

    python3 <skill>/scripts/verify.py tailored/Resume-<Company>.tex --png preview.png

Fix every failure, then read `preview.png`. A FAIL on "no template placeholders" means template
text (`Avery Sample`, `example.com`, `TODO`) is still on the page; replace it, and do not reach
for `--allow-placeholders`, which is only for the shipped template or a deliberately fictional
page. If it overflows, stop and follow `overflow.md`. If
more than about 3 lines are free (`measure.py` reports the slack), tell the user how many and
offer real content to fill them: another project or a bullet from `notes/facts.md`. If they have
nothing to add, the page is done with the free lines: say so once in the report, do not pad,
and do not keep asking.

## 7. Save and record

When `verify.py` passes and you have read the page:

    python3 <skill>/scripts/verify.py tailored/Resume-<Company>.tex --png preview.png --save pdfs/<First>_<Last>_Resume_<Company>_<Role>.pdf

Then add a row to the tailored copies table in `notes/variants.md` with `Sent` set to "not
sent", update `notes/roles.md` if you researched, and commit if the workspace is a git
repository. When the user says they sent it, record the date in `Sent`. If the table has no
`Sent` column (a workspace made by an older version of this skill), add it.

## 8. Report

Tell the user, briefly: the PDF path; what you changed and why (reordered, reworded, swapped);
every gap from step 4; any project shown without a link because no URL is confirmed; anything
you were unsure about. Offer the PNG or the PDF to look at.

## Changing a resume after it is saved

When the user asks to add, change, or remove something on a resume that already exists ("add a
bullet about X to the internship"):

1. **Back it first.** Every new claim needs a confirmed facts entry (`facts.md`). If the facts
   file does not cover it, ask for what a bullet needs: what they did, when, and any number with
   its source. Record what they said under that entry's **Pending** field, and put on the page
   only what they have confirmed: a bullet whose work is confirmed but whose number is not goes
   on without the number, and the number stays under Pending. For a new project, follow "When
   the user builds something new" in `facts.md`. If the only fact behind the request is already
   on the page, say so instead of restating it in a second bullet.
2. **Pick the file.** Edit a base only when the user asks for the base itself. Otherwise read the
   copy's `Sent` column in `notes/variants.md`:
   - **Not sent:** edit the tailored copy in place and re-save over the same PDF.
   - **Sent, and this is for a new application:** start again from step 1 of this file, with a
     role suffix on the copy (`Resume-<Company>-<Role>.tex`) and a PDF name that does not
     overwrite the sent one. The sent copy stays as the record.
   - **Sent, and the user wants it corrected and resent:** edit it in place and re-save over the
     same PDF, and say in the report that the old PDF was replaced.
   If `Sent` is empty, missing, or "unknown", ask the user which case applies. If an older
   workspace's tailored copies table has no `Sent` column, add it.
   Before overwriting a PDF that was sent, copy it to `pdfs/sent/<same name>-<sent date>.pdf`
   (for example `pdfs/sent/Avery_Sample_Resume_Northwind_Logistics_Backend_Engineer_Intern-2026-01-15.pdf`)
   and say so in the report.
3. **Rebuild and verify**, as in step 6. If it overflows, stop and follow `overflow.md`: new
   content never pushes other content off the page without the user's pick.
4. **Re-save** with `--save`, to the path step 2 picked. Update the row in `notes/variants.md`
   (set `Sent` back to "not sent" if the corrected copy has not gone out yet) and commit if the
   workspace is a git repository.
5. **Report** what changed, whether a PDF was replaced (and where the sent one was archived), and
   anything you held back as pending and why.
