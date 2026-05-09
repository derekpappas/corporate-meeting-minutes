# corporate-meeting-minutes

Synthetic Delaware-style (and related) corporate meeting minutes and minute-book outputs from `corporate_meeting_minutes.py`.

## Quick generate

```bash
poetry run python corporate_meeting_minutes.py
```

Writes under `generated/` (gitignored). `.docx` / `.pdf` at repo root are also ignored by `.gitignore`; source inputs live in `data/` and the script.

## Full local regeneration

After pulling, or when changing registry data or templates, rebuild the corpus and plain-text audit mirrors:

```bash
poetry run python corporate_meeting_minutes.py --output-root generated --extract-audit-text --write-samples --write-master-book
```

Then, if you need meeting calendars and the bundled review tree:

```bash
poetry run python corporate_meeting_minutes.py --write-calendars
poetry run python scripts/build_review_pack.py
```

Rebuild `generated/review_pack/` after calendar runs so `all/calendars/` inside the pack matches `calendars/`. For a stricter check in one step, use `--write-calendars --strict-calendars` instead of plain `--write-calendars`, then run `build_review_pack.py` again.

Outputs: `generated/` (including optional `generated/<safe>/samples/` from `--write-samples`), `audit_text/`, `calendars/`, and `generated/review_pack/` are gitignored; regenerate on each machine as needed.

## Optional hygiene (schedules / registry edits)

Fail the process if the unified calendar audit finds same date+time used by more than one company:

```bash
poetry run python corporate_meeting_minutes.py --write-calendars --strict-calendars
```

Chronology / DGCL spot-check over extracted text (expects fresh `audit_text/`):

```bash
poetry run python scripts/audit_corpus_chronology_dgcl.py
```

Tests:

```bash
poetry run pytest tests/test_corporate_meeting_minutes.py
```
