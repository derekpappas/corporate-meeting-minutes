# Corpus chronology and DGCL audit

**Summary:** 0 error-line(s), 0 warning-line(s).

Automated scan of `audit_text/generated__*__*.docx.txt` plus schedule/stock-ledger checks. Review flagged items with counsel; false positives are possible (e.g. narrative mentions of other dates).

## 1. Filename date vs meeting header date (board minutes only)

*Waivers, notices, and written consents intentionally reference multiple dates; they are skipped here.*

- No mismatches in board-minute-style extracts (AGM / special / org / quarterly).

## 2. Quarterly sequence within each calendar year (filenames)

- No quarter-order anomalies detected from filenames.

## 3. Schedule rules (generator truth, all registry companies)

- Special ≤ annual and organizational ≥ filing (where both dates exist): **OK**.

## 4. Stock ledger `issue_date` vs first board meeting after purchase

- DATA RECORD SCIENCE, INC. **DRS-0001** issue **2008-08-15** → first board slot **2022-04-03** (Q1).
- Hippo, Inc. **HIPPO-0001** issue **2022-06-01** → first board slot **2022-07-01** (Q2).
- Loki Sports Enterprises, Inc. **LOKI-0001** issue **2023-05-07** → first board slot **2023-07-06** (Q2).
- Ritual Growth, Inc. **RG-0001** issue **2023-05-07** → first board slot **2023-07-02** (Q2).
- SurveyTeams, Inc. **ST-0001** issue **2026-05-07** → first board slot **2026-07-05** (Q2).
- SurveyTeams, Inc. **ST-0002** issue **2026-05-07** → first board slot **2026-07-05** (Q2).
- TeamBoost.ai, Inc. **TB-0001** issue **2023-05-07** → first board slot **2023-07-05** (Q2).

## 5. DGCL references in extracted text (non–Delaware-domiciled companies)

- **Loki Sports Enterprises, Inc.** (`loki_sports_enterprises`): no DGCL / “Delaware General Corporation Law” string hits in audit extracts.

## 6. Delaware companies: spot-check for Wyoming statute strings in extracts

- DATA RECORD SCIENCE, INC.: no Wyoming statute phrase hits in per-meeting extracts.
- Hippo, Inc: no Wyoming statute phrase hits in per-meeting extracts.
- Ritual Growth, Inc.: no Wyoming statute phrase hits in per-meeting extracts.
- SurveyTeams, Inc.: no Wyoming statute phrase hits in per-meeting extracts.
- TeamBoost.ai, Inc.: no Wyoming statute phrase hits in per-meeting extracts.

## 7. Cross-company calendar (same date + time)

- `write_company_calendars` conflict slots (same calendar date and **identical** time string across companies): **0**.

## 8. Next steps

- CI: `poetry run python scripts/audit_corpus_chronology_dgcl.py --strict --strict-calendars` or `poetry run python corporate_meeting_minutes.py --write-calendars --strict-calendars`.
- After regenerating `.docx`, run `poetry run python scripts/extract_audit_text.py` so this audit tracks current output.
