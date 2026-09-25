# Overflow protocol

The resume must fit on one page, and the user decides what goes. Never cut on your own
judgement, not even a word: what looks like filler to you may be the line the user cares about
most.

## 1. Measure

    python3 <skill>/scripts/measure.py tailored/Resume-<Company>.tex

It prints how many lines fell past page 1, the exact text that fell, and the short tails: bullets
whose last line holds only a few words. "It is a bit long" is not a measurement; "it is 6 lines
over" is.

Line counts come from the PDF's extracted text, so they are a close proxy, not exact. Section
spacing and headings shift things slightly. Size each package with a line or two of margin, and
confirm it by rebuilding.

## 2. Report

Tell the user how far over the page runs, in lines, and what spilled.

## 3. Offer 3-4 complete packages

Each package must, on its own, bring the resume back to one page, so the user picks one package
instead of answering a string of yes-or-no questions. For each, show exactly what it cuts or
rewrites and roughly how many lines it saves. Make the packages differ in what they protect.

Build packages from the cheapest cuts first:

1. **Short tails.** Trimming 3-5 words from a bullet whose last line is short wins back a whole
   line and loses almost nothing. `measure.py` lists them.
2. **Wordy phrasing.** Tighten a bullet without losing its point.
3. **Weaker bullets.** Drop the least relevant bullet from an entry that has several.
4. **Whole entries.** Reduce a project to its title and link, or drop it.
5. **Skills and coursework lines.** Merge or shorten.

Protect whatever `notes/variants.md` marks as load-bearing. Never cut the only line carrying a
credential without offering to fold it into a title (rule 10 in `rules.md`).

A package reads like this:

> **Package B, saves about 4 lines: keep every project, tighten instead.** Trim the short tails
> on ShelfScan bullet 1 and StudyBuddy bullet 1 (2 lines), cut ForecastCheck's second bullet
> (1 line), merge Tools into Frameworks (1 line).

## 4. Wait

Apply nothing until the user picks. If they want a mix, build that mix.

## 5. Apply and re-verify

Apply the chosen package, run `verify.py`, and read the PNG. If it still overflows, measure again
and report; do not keep trimming on your own. If the user's choice reflects a standing rule
("always keep the statistics bullets"), record it under locked decisions in `notes/variants.md`.
