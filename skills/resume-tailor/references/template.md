# The template

`<skill>/assets/template.tex` is Jake Gutierrez's resume template (MIT), with the side and top
margins narrowed by a quarter inch so each line holds more. It is one column of real text with
no graphics or columns, the shape applicant tracking systems parse most reliably. The lines
`\input{glyphtounicode}` and `\pdfgentounicode=1` make the PDF's text extract cleanly; only
pdflatex understands them, so `build.py` comments them out in its temporary copy when it uses
another engine. Never remove them from the source.

## Capacity

About **105-113 characters** per full-width line and **46-48 lines** per page, counted the way
`measure.py` counts (lines of extracted text). A bullet costs about one line per 105 characters.
The name, the contact line, each section title, and each entry heading cost a line each.

## Commands

- `\resumeSubheading{Title}{Right}{Subtitle}{Right}`: an education or experience entry, two rows,
  left and right aligned.
- `\resumeProjectHeading{Title and links}{Right}`: a one-row project heading. The right side is
  usually empty.
- `\resumeItem{text}`: a bullet.
- `\item[] \small{text}`: an unbulleted summary line under a project heading.
- `\resumeSubHeadingListStart` and `\resumeSubHeadingListEnd`: wrap the entries of a section.
- `\resumeItemListStart` and `\resumeItemListEnd`: wrap the bullets of an entry.

A project heading with two links:

    \resumeProjectHeading
        {\textbf{Name: Short Pitch} $|$ \href{https://github.com/user/repo}{\underline{View Project}} $|$ \href{https://demo.example}{\underline{Live Demo}}}{}

A project written as its heading alone, with no bullet list, costs one line. That is the usual
first step when a project has to shrink.

## Escaping

Write `\&`, `\%`, `\$`, `\#`, `\_`, `\{`, `\}` for those characters. Use `\texttt{...}` for code
and paths, `$|$` as the separator, and `--` for date ranges. Never `---`.

## Things that look fine in the source and break on the page

- A long unbreakable token (a URL, a file path) runs into the margin. `verify.py` catches it as
  an overfull box. Shorten it, or put it behind a link with a short label.
- A section title stranded alone at the bottom of the page. Only the PNG shows this.
- Bold on every other word. Bold the one or two terms a reader should see first, no more.
