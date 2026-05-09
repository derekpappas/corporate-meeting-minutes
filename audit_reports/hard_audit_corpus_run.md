# Hard audit corpus — plain-text extract run

**Run:** Regenerate all outputs under `generated/`, then mirror every non-lockfile `.docx` into `audit_text/` as UTF-8 `.txt`.

**Command (authoritative one-liner):**

```bash
poetry run python corporate_meeting_minutes.py --output-root generated --extract-audit-text
```

Equivalent two-step form:

```bash
poetry run python corporate_meeting_minutes.py --output-root generated
poetry run python scripts/extract_audit_text.py
```

**Last execution note:** After a full run, every **`generated/**/*.docx`** should have a matching **`audit_text/*.txt`**. **`--write-samples`** writes **PDF/CSV** under **`generated/<safe>/samples/`** (not `.docx`), so it normally does **not** change extract counts. The extractor **deletes** stale `.txt` files that no longer have a matching `.docx`.

**Naming:** `audit_text/generated__<folder>__<filename_without_docx>.docx.txt`  
Example: `generated/teamboost_ai/meetings/teamboost_ai_2023_01_20_organizational.docx` → `audit_text/generated__teamboost_ai__teamboost_ai_2023_01_20_organizational.docx.txt`

**Included:** Per-company flat **`meetings/`** (quarterly, AGM, special, consent, waivers, organizational, standalone equity/domestication packets), **`cap_tables/`** and **`stock_ledgers/`** companion `.docx`, per-company **`<safe>_all_meetings_book.docx`** at **`generated/<safe>/`**, and **`generated/books/`** multi-company compiled `.docx` minute books.

**Not extracted:** `.pdf` files (use separate PDF text tools if needed).

**Strict calendar check (operational, post-regen):**

```bash
poetry run python corporate_meeting_minutes.py --write-calendars --calendar-output-dir calendars --strict-calendars
```

**Counsel / diligence workflow:**

1. Line-search the corpus: e.g. `rg -n 'DGCL|§|Written Consent|quorum|Record date' audit_text/`
2. Cross-read with `ocr_text/` certificate and bylaws extracts.
3. Compare executed PDFs in the physical minute book to “to be filed / upon execution” language in extracts unless `minutes_assert_exhibits_filed` is enabled in `company_information`.

**Privileged memo:** Substantive DGCL posture remains in `audit_reports/senior_dgcl_audit_2026-05-08.md`.
