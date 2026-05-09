Review pack

sample/  — One U.S. state and one company only: **Hippo, Inc.** (Delaware (DE)).
           One example per meeting or instrument type (organizational through compiled book).

all/     — Broader review set: examples drawn from any registry company where needed (e.g. SurveyTeams
           stockholder-only types), all compiled minute-book PDFs, audit mirrors, calendars, data snippets.

Rebuild:
  poetry run python scripts/build_review_pack.py

.gitignore may ignore *.docx / *.pdf; files remain on disk under generated/review_pack/.
