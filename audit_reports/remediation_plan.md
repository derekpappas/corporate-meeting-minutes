# Remediation plan — generated minutes (post-template updates)

**Context**: `corporate_meeting_minutes.py` already covers **DRS §213** (board resolution in the pre-AGM **special** meeting + stockholder cross-reference), **partial DRS roll call**, **Hippo** display name, and richer **§141(e)** boilerplate. This plan addresses what the audit still treats as **open**: **exhibits**, **§222 / §228 proof**, **DRS vote detail**, **bylaw/fact alignment**, and **transactional** minutes.

**Not legal advice** — sequence and depth should be confirmed with Delaware counsel for each company.

---

## Phase 0 — Inventory and sources of truth (1–2 hours per company)

1. **Gather** current **COI** (and amendments), **bylaws**, and any **stock ledger** / cap table summary.
2. **Extract** (or OCR to text you keep in-repo, e.g. under `bylaws_text/` / `charter_text/`) the clauses that control:
   - **§213**-style record dates (board-fixed window vs **default** if the board does not fix).
   - **§222** notice (timing, content, electronic delivery if used).
   - **§228** (written consent permitted or not; notice to non-consenting holders).
   - Stockholder **quorum** and **director election** standard.
3. **Decide** what will live **only outside** the generator (PDFs in an **appendix folder**) vs what you will **encode** in `companies` / templates.

**Exit criterion**: A short checklist per company (can be a table in a private memo) mapping “minute assertion → supporting document or template parameter.”

---

## Phase 1 — Exhibits and minute-book hygiene (process + files)

**Goal**: Minutes that say “on file,” “attached,” or “waiver executed” have a **real** counterpart in a defined place.

1. Create something like `minute_book_appendix/` (or your DMS path) with a **numbered index** (Exhibit A, B, …).
2. For **each annual cycle** (and DRS stockholder meeting), plan to file at least:
   - **Notice** of stockholder meeting (or **written waiver of notice**).
   - **Executed** written consents (sole or majority), if used.
   - Optional but valuable: **ledger excerpt** or **inspector’s list** cover page as of **record date**.
3. Optionally add to generated minutes a **single sentence** placeholder only where you will **actually** attach, e.g. “Notice of meeting is attached as **Exhibit A** to these minutes.” Avoid false “attached” language if nothing is filed.

**Exit criterion**: Index exists; every “on file” line in the current corpus maps to a document or is reworded to “to be filed” / removed.

---

## Phase 2 — §222 (notice) and §228 (consent) *proof* (non-generator work)

**Goal**: Reduce **§220** exposure on “bare assertions.”

1. **§222**: For each meeting that relies on **notice**, retain **email PDF + send log**, **certified mail**, or **waiver** with **dates** that satisfy **bylaws + DGCL** relative to the **record date** and meeting date.
2. **§228**:
   - **Sole stockholder** path: **signed** consent in the appendix; confirm **COI** does not bar consent.
   - **DRS majority consent**: **signed** counterparts; if not **unanimous**, document **prompt notice** to non-consenting holders (email log, template notice, or counsel file note).

**Exit criterion**: For a sample year per company, you can hand an associate **notice + consent** without editing the `.docx` body.

---

## Phase 3 — DRS vote detail (template + data)

**Goal**: Move from “chair + aggregate majority language” to **defensible** roll call when multiple holders matter.

1. Extend `companies["DATA RECORD SCIENCE, INC."]` with structured data: each **record holder** (name, optional share count or “as on ledger”), **presence**, **vote** on director election if you want tabulation in minutes.
2. Update `generate_annual_meeting_stockholders` to render a **table or enumerated list** of holders and votes when data is present; keep current aggregate fallback when data is empty (closely held shortcut).
3. Optional: add a line that **inspector of election** appointment/results are **Exhibit B** (and then file one for real contests).

**Exit criterion**: At least one year of DRS minutes shows **names + votes** (or explicit reference to a **signed inspector** report in the appendix).

---

## Phase 4 — Bylaw/fact alignment (generator parameters)

**Goal**: Template dates and narrative **match** governing documents and what the board **actually** did.

1. **Record date**: If bylaws use a **default** when the board does not fix a date, either:
   - Keep board-fixed path and ensure **real** board minutes match `stockholder_annual_record_date_str()` (adjust **offset** or replace with **explicit dates** in `companies` per year), **or**
   - Add a template branch for **bylaw-default** record date with **notice date** inputs (requires **notice date** in data).
2. **Annual / quarterly dates**: Confirm **December anchor** and **quarterly** stagger still match how you want the book to read (purely fictional vs tied to real meetings).
3. **§211 / written consent**: Per company, confirm **COI** allows **§228** and waiver of a **separate** annual meeting; if not, add a **company flag** to force **meeting-style** stockholder minutes for that entity.

**Exit criterion**: A one-page “diff” for each company: **bylaw quote → generator field / template behavior.**

---

## Phase 5 — Transactional minutes (new documents)

**Goal**: Cover **§151–152, §170, §271, §144**, etc., when real events exist.

1. Use `Senior counsel prompt/senior_counsel_transactional_minutes_prompt.md` (or counsel forms) for **issuances**, **dividends**, **asset sales**, **loans**, **comp**, **indemnification** actions.
2. Decide whether to **extend** `corporate_meeting_minutes.py` with optional `transaction_templates` / YAML-driven events, or keep transactional sets as **hand-drafted** Word/PDF in the appendix.
3. Cross-reference in annual/board minutes only when accurate (“Board approved X as described in the minutes of [date]” + exhibit).

**Exit criterion**: For each material transaction type you’ve actually done, at least one **board** (and if required **stockholder**) record exists outside the routine annual/quarterly set.

---

## Phase 6 — Audit loop

1. After any template or `companies` change:  
   `poetry run python corporate_meeting_minutes.py --output-root generated`  
   then `poetry run python scripts/extract_audit_text.py`.
2. Update `audit_reports/senior_counsel_audit_2022_2026.md` (and PDF) only when the **open defect list** meaningfully changes.
3. Optionally re-run the full `senior_counsel_audit_prompt.md` pass against **audit_text + bylaws/COI text** when you refresh charters.

---

## Suggested priority order

| Order | Track | Rationale |
|------|--------|-----------|
| 1 | Phase 0 + Phase 4 | Wrong **law/facts** is worse than missing **polish**. |
| 2 | Phase 1 + Phase 2 | **Exhibits** and **notice/consent proof** address the largest **§220** gaps. |
| 3 | Phase 3 | **DRS** vote detail when more than one holder or any **contest** risk. |
| 4 | Phase 5 | Only when transactions exist; scope explodes if done prematurely. |
| 5 | Phase 6 | Continuous hygiene. |

---

## What you do *not* need to “fix” in templates anymore

- **Missing board resolution for DRS record date** (addressed in **special** meeting + stockholder cross-reference).
- **Hippo “Inc,”** entity string (addressed via **`minutes_display_name`**).

Those items should stay **closed** unless you revert generator logic.
