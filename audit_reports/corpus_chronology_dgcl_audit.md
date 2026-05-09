# Corpus chronology and DGCL audit

**Summary:** 10 error-line(s), 39 warning-line(s).

Automated scan of `audit_text/generated__*__*.docx.txt` plus schedule/stock-ledger checks. Review flagged items with counsel; false positives are possible (e.g. narrative mentions of other dates).

## 1. Filename date vs meeting header date

- **MISMATCH** `generated__ritual_growth__ritual_growth_2022_12_13_waiver_of_notice_board_meetings.docx.txt`: file name **2022-12-13**, body **2022-06-17**
- **MISMATCH** `generated__ritual_growth__ritual_growth_2023_12_12_waiver_of_notice_board_meetings.docx.txt`: file name **2023-12-12**, body **2023-04-02**
- **MISMATCH** `generated__ritual_growth__ritual_growth_2024_12_10_waiver_of_notice_board_meetings.docx.txt`: file name **2024-12-10**, body **2024-04-02**
- **MISMATCH** `generated__ritual_growth__ritual_growth_2025_12_09_waiver_of_notice_board_meetings.docx.txt`: file name **2025-12-09**, body **2025-04-02**
- **MISMATCH** `generated__ritual_growth__ritual_growth_2026_12_15_waiver_of_notice_board_meetings.docx.txt`: file name **2026-12-15**, body **2026-04-02**
- **MISMATCH** `generated__surveyteams__surveyteams_2026_12_18_waiver_of_notice_board_meetings.docx.txt`: file name **2026-12-18**, body **2026-04-05**
- **MISMATCH** `generated__teamboost_ai__teamboost_ai_2023_12_14_waiver_of_notice_board_meetings.docx.txt`: file name **2023-12-14**, body **2023-01-20**
- **MISMATCH** `generated__teamboost_ai__teamboost_ai_2024_12_12_waiver_of_notice_board_meetings.docx.txt`: file name **2024-12-12**, body **2024-04-05**
- **MISMATCH** `generated__teamboost_ai__teamboost_ai_2025_12_11_waiver_of_notice_board_meetings.docx.txt`: file name **2025-12-11**, body **2025-04-05**
- **MISMATCH** `generated__teamboost_ai__teamboost_ai_2026_12_17_waiver_of_notice_board_meetings.docx.txt`: file name **2026-12-17**, body **2026-04-05**

## 2. Quarterly sequence within each calendar year (filenames)

- No quarter-order anomalies detected from filenames.

## 3. Schedule rules (generator truth, all registry companies)

- Special ≤ annual and organizational ≥ filing (where both dates exist): **OK**.

## 4. Stock ledger `issue_date` vs first board meeting after purchase

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

## 7. Next steps

- Re-run `poetry run python corporate_meeting_minutes.py --write-calendars --strict-calendars` for cross-company same-slot conflicts.
- After regenerating `.docx`, run `poetry run python scripts/extract_audit_text.py` so this audit tracks current output.
