# Facts

`notes/facts.md` in the workspace is the only source of claims. This file explains how to write
entries and how to use them.

## Why it exists

Tailoring for a job description puts steady pressure on the wording to stretch: a data-cleaning
notebook becomes an "ML pipeline", a class project becomes a "production service". Each stretch
is small and reads well; together they produce a resume the user cannot defend in an interview.
The facts file settles, once and with the user, what each piece of work is and is not.

## Entry format

    ### ShelfScan

    - **What it is:** a mobile-first web app that lets a small shop track stock by scanning
      barcodes with a phone camera.
    - **Source:** https://github.com/<user>/shelfscan. Deployed: yes (`Live Demo`, https://...).
    - **Stack:** React, TypeScript, FastAPI, PostgreSQL with Alembic migrations, Docker,
      GitHub Actions.
    - **Numbers:** offline queue tested with 500 queued scans (`tests/test_sync.py`).
    - **Honest ceiling:** a working inventory tool used by one shop. Never "inventory platform"
      or "used by retailers": there is one user.
    - **Not yet true:** multi-shop accounts are designed but not built; CSV export is disabled.
    - **Pending:** none.
    - **Confirmed by user:** 2026-01-10.

A role goes under `## Experience` with the same fields plus **Work**, what the user did, in their
own words:

    ### Data Intern, Example Freight Co.

    - **What it is:** a summer internship, Jun 2025 to Aug 2025, remote.
    - **Source:** the user's own account. Employer-owned code: never linked on the page.
    - **Stack:** Python, SQL, Airflow.
    - **Work:** rewrote the nightly shipment report as an Airflow job with row-count checks.
    - **Numbers:** report runtime from 40 to 6 minutes (the team's job dashboard).
    - **Honest ceiling:** an intern who rebuilt one report pipeline. Never "led the data
      platform" or "owned the warehouse".
    - **Not yet true:** none.
    - **Pending:** 2026-01-12, the user mentioned joining the on-call rotation; asked for dates
      and what they handled, no answer yet.
    - **Confirmed by user:** 2026-01-10.

When a project has no public URL the user has confirmed, the Source field says so ("no public
URL confirmed"), and the project goes on the page with no link at all. Tell the user in the
report, and log it in `notes/gaps.md` if a link would help for the role.

The fields that do the most work:

- **Honest ceiling.** The strongest true description, and the grander label it must never get.
  Write the tempting wrong label down explicitly; naming it is what stops the stretch.
- **Numbers with a source.** Every number on the page needs a source: results and metrics, and
  also scope and configuration figures (months, intervals, counts). A test, a benchmark, a
  dashboard, or an employer report is a source, and so are the user's own words in this
  session, recorded as such ("the user's own account, 2026-01-10"). A bullet whose work is
  confirmed but whose number is not goes on the page without the number; the number stays
  under **Pending** until it has a source.
- **Not yet true.** Features that are planned, stubbed, disabled, or broken today. Code that is
  commented out is not a feature.
- **Pending.** Things the user has mentioned that are not yet confirmed, or that lack what a
  bullet needs (what they did, when, a number's source). Date each one. Nothing under Pending
  goes on a page; ask for the missing detail, and move it into the entry once the user confirms.

## What counts as confirmed

An entry that only restates what the user told you in this session, in their own words, is
confirmed by those words: record the date in **Confirmed by user**. An entry with anything
drafted from code, from an old PDF, or from your own reading is confirmed only when the user has
read it and said yes, after any corrections. Silence is not confirmation, and neither is "they
did not correct it". Show such an entry in full and ask plainly: "Is every line of this
right?" If they confirm only part, keep the rest under **Pending**. An entry with no
confirmation date is a draft: nothing from it goes on a page. A later change to an entry is
confirmed the same way, with a new date.

## Reading a repository honestly

- The README says what the author hoped. The code, tests, and CI say what exists.
- Check deployment: is there a URL that works today? If not, the label is `View Project` or
  `Demo Video`, never `Live Demo`.
- On shared repositories, check commit authors. Claim the user's share only, and ask when unsure.
- Coursework, tutorials, and hackathon prototypes are fine to list. Call them what they are.

## Using it while tailoring

- Every bullet on the page maps to one entry. If you cannot point to the entry, the bullet does
  not go on the page.
- Rewording toward the job description is expected. Going past the honest ceiling is not.
- When the user tells you something new about their work, update the entry first, get it
  confirmed, then use it. Until then it sits under **Pending**, never on the page.
- When the user asks for a bullet whose only backing fact is already on the page, say so rather
  than restating the same fact in a second bullet.

## When the user builds something new

Scan the repository as in `setup.md` step 4, draft the entry, and get it confirmed. Then offer
to add it to the bases where it fits; bases change only with the user's go-ahead.
