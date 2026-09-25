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
    - **Confirmed by user:** 2026-01-10.

The fields that do the most work:

- **Honest ceiling.** The strongest true description, and the grander label it must never get.
  Write the tempting wrong label down explicitly; naming it is what stops the stretch.
- **Numbers with a source.** A metric with no source (a test, a benchmark, a dashboard, an
  employer report) does not go on a page.
- **Not yet true.** Features that are planned, stubbed, disabled, or broken today. Code that is
  commented out is not a feature.

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
  confirmed, then use it.

## When the user builds something new

Scan the repository as in `setup.md` step 4, draft the entry, and get it confirmed. Then offer
to add it to the bases where it fits; bases change only with the user's go-ahead.
