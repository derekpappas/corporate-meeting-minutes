## Privileged internal memo — Senior-counsel audit (prompt run)

**Role / method**: `Senior counsel prompt/senior_counsel_audit_prompt.md` (Sections I–VI + Add-ons A–F). **Not legal advice.**

**Inputs reviewed**: Plain-text corpus `audit_text/` (**138** files, synced from `generated/` per `scripts/extract_audit_text.py`). Charter/bylaws were **not** re-OCR’d for this pass; conclusions assume the generator’s stated DGCL hooks are **aspirational** until matched to **COI/bylaw** text (Add-on A).

---

### 1. Executive risk assessment

| Level | Rationale |
|------|-----------|
| **GREEN** | No **void**-tier power violations spotted in the synthetic set (e.g., no §271 asset sale papered as board-only; no unauthorized share issuance narrative). Sole-director board meetings with §141(i)-style remote language are **structurally** coherent for a one-person board. |
| **YELLOW** | **Default posture** for the book: minutes assert **notice**, **record date**, **quorum**, **§228** mechanics, and **§218** list/proxy handling **without** annexed proof (notices, waivers, ledger extracts, vote tabulations). For **closely held, uncontested** use, often acceptable; under **§220** or **contested** scrutiny, **weak**. |
| **RED** | **None** for **corpus integrity** (TeamBoost year alignment and orphan extracts were reconciled). **Substantive RED/YELLOW** remains on **record-date authority** (DRS) and **§220 depth**—these are **evidence and narrative** gaps, not necessarily “void” if underlying facts are clean. |

---

### 2. Material defect log (representative)

| Date (doc) | Action / topic | Defect type | Legal / practice hook | Risk | Remediation |
|------------|----------------|-------------|------------------------|------|-------------|
| Annual stockholder meetings (DRS, each year) | Fix record date; elect director | **Voidable** (if record date not actually fixed per bylaws) | DGCL **§213** + bylaws (board-fixed window vs **default** if board silent) | **High** (contested vote / election) | Add **board consent or meeting minutes** adopting the record date **or** revise template to track **bylaw default** dates with consistent notice math. |
| DRS stockholder minutes | Quorum / roll call | **Voidable** (evidence) | **§216**; **§220** proof | **Medium** | Replace anonymous “majority present” with **named holders** (from `companies` data) or attach **inspector / tabulation** as exhibit. |
| Written consents (Hippo, Ritual, TeamBoost) | §228 annual / ratification path | **Voidable** (if COI requires physical meeting) | **§228** + **COI** | **Medium** (company-specific) | Confirm **COI** permits written consent and **§211** waiver language; if not, switch template branch for that company. |
| Majority consent (DRS ratification) | Prompt notice; signatures | **Voidable** (procedure) | **§228** prompt notice to non-consenting holders | **Medium** | Document **notice given** or confirm **unanimous** facts; keep executed signatures outside generator. |
| All companies | Notice of meetings | **Voidable** (if notice defective) | **§222** | **Medium** | Attach **notice** or **waiver** to minute book; minutes may say “on file” but file must exist. |
| Board quarterly / AGM | Ratification resolutions | **Low / form** | **§141(e)** | **Low–Medium** | Strengthen **specificity** (what reports reviewed) if transaction stakes rise. |
| Hippo written consent heading / body | N/A | **N/A** (style) | Professionalism | **Low** | Entity name reads **“Hippo, Inc,”** (comma splice). Use a **display name** field (e.g. `Hippo, Inc.`) in `corporate_meeting_minutes.py`. |

---

### 3. Remote governance analysis

- **Board (§141(i))**: Minutes state **contemporaneous** audio/visual participation and treat it as **in-person** presence—**adequate** as boilerplate. **Gap**: no **per-vote** confirmation after disconnects (prompt §II); add only if you expect **contested** process challenges.
- **Stockholders (DRS)**: Chair confirms **remote** participants could hear/be heard and **verification** of stockholder/proxyholder status—**good faith** narrative. **Gap**: no **§222** notice **text** or **method/timing** detail in the minute body (only confirmation).

**Language improvements (optional)**  
- One line: “No stockholder requested withdrawal of remote participation; quorum was maintained throughout each vote.”  
- For DRS: cross-reference **date of board action fixing record date** (once that document exists).

---

### 4. Stockholder actions (§228; §§211–213, 216–222 for DRS)

| Path | Findings |
|------|----------|
| **Sole-holder §228** (Hippo, Ritual, TeamBoost) | Mechanics block and **§211** waiver are present; **charter non-prohibition** acknowledged. **Cure gap**: executed consent and **COI** check are **out of band** (expected). |
| **DRS annual meeting** | **§213** record date printed; **§218** list/proxy paragraph; **§222** notice confirmation. **Weak point**: **record date** sourcing (see defect log). **Roll call** does not name holders. |
| **DRS majority ratification consent** | Same **§228** mechanics theme; **prompt notice** not **proved** in text. |

---

### 5. Fiduciary record quality; §220 lens

- **§141(e)**: Present on board minutes but often **generic** (“officers and other persons”) without naming **what** was relied on—**Van Gorkom / §220** exposure if a **material** decision is ever implicated.
- **Caremark**: Quarterly minutes add **questions / risk** language—**helpful** but still **high level**.
- **§220**: A demand for **“purpose reasonably related to interest as stockholder”** would seek **underlying** notices, consents, ledger—minutes **point** to those but do not **substitute** for them.

---

### 6. DGCL coverage map (Section VI checklist)

| Topic | Pass / gap / N/A | Note |
|-------|------------------|------|
| Board existence & powers §141(a)–(b) | **Pass** | Sole director; quorum stated. |
| Committees §141(c), §143 | **N/A** | No committee actions claimed. |
| Vacancies / removal | **N/A** | Not addressed in templates. |
| Board meetings §141(i) | **Pass** | Remote boilerplate present. |
| Board written consent §141(f) | **Pass** | Board acts at meetings; no majority e-mail consent. |
| §141(e) reliance | **Gap** | Thin specificity on **what** was relied upon. |
| Stockholder annual §211 | **Pass / gap** | **Pass** as narrative; **gap** vs **COI** for consent path (verify per company). |
| Record date §213 | **Gap** (DRS) | Date stated; **authority** for date not in same book. |
| Quorum / vote §216 | **Gap** (DRS) | Aggregate description; no names/votes. |
| Proxies §218 | **Pass** (narrative) | No exhibits. |
| Notice §222 | **Gap** | Assertions only. |
| §228 | **Pass / gap** | Mechanics yes; **notice to dissenters** / **execution** not shown. |
| §204 / §205 | **N/A** | No ratification of defective acts described. |
| §220 | **Gap** | Template-leaning book without exhibits. |
| §145 / §102(b)(7) | **N/A** | Not implicated in text. |
| Bylaws §109 | **N/A** | No bylaw amendment minutes. |

---

### Add-ons A–F (short)

- **A**: **Recommended next step** — re-attach or OCR **COI + bylaws** per company and tabulate **quorum, consent, record-date, notice windows** before changing templates further.  
- **B**: **§211** cadence appears **year-by-year** in corpus; TeamBoost starts **2023** (aligned with config).  
- **C**: **§228** — distinguish **sole** vs **majority** paths in checklist when reviewing real signatures.  
- **D**: **Integrity** — run `extract_audit_text.py` after every generation.  
- **E**: **COI** — verify written consent + waiver of separate annual meeting vs charter.  
- **F**: If **voidable** defects found in **live** records, map **§204**/**§205** with counsel.

---

## Proposed plan to fix the documents

### Phase 0 — Process (no template change)

1. After `poetry run python corporate_meeting_minutes.py --output-root generated`, run `poetry run python scripts/extract_audit_text.py`.  
2. Keep **exhibits** (PDFs of notices, signed consents, board consents) in a parallel **appendix folder** and index them in a short **README** or cover memo (outside generator if preferred).

### Phase 1 — Quick wins (`corporate_meeting_minutes.py`)

1. **Hippo entity string**: Add optional `minutes_display_name` (or similar) per company; set to `Hippo, Inc.` for consent title and “sole stockholder of …” line while keeping the internal dict key stable.  
2. **Written consent title**: Use the same display field for any company whose key omits a period.

### Phase 2 — DRS record date (highest legal-process ROI)

**Pick one strategy** (counsel may prefer A or B):

- **A — Board paper trail in-generator**: Emit an extra short document or **section** in the **prior** board AGM (or a standalone unanimous written consent) for DRS: “RESOLVED, that **[date]** is fixed as the record date for the **[date]** annual stockholder meeting.” Ensure the date matches `stockholder_annual_record_date_str()`.  
- **B — Template disclaimer / bylaw-default path**: If the board will **not** fix a date, replace “fixed as the record date **in accordance with the bylaws**” with language tracking **actual bylaw default** (e.g., if default is day before notice, ensure **notice date** exists in the record or in the same minute set).

### Phase 3 — DRS roll call & votes

1. Extend `companies["DATA RECORD SCIENCE, INC."]` with structured **stockholders** (name, shares optional).  
2. Template: “**Stockholders present:** [names]; collectively holding **[X]%** / **[N]** shares…” or attach “**Inspector’s certificate** on file.”

### Phase 4 — Depth for §141(e) and §220 (optional)

1. For quarterly/AGM, one optional sentence: “The Sole Director reviewed **[specific materials]** furnished for the meeting.”  
2. Add **placeholder exhibit references**: “Notice attached as **Exhibit A**” only if you will actually attach—otherwise avoid false precision.

### Phase 5 — Transactional minutes

When equity, dividends, §271, loans, or comp appear in real life, generate separate minutes using `Senior counsel prompt/senior_counsel_transactional_minutes_prompt.md` (not covered by the current generator scope).

---

### Suggested sequencing

| Priority | Item | Effort |
|----------|------|--------|
| P0 | Process + exhibits index | Low |
| P1 | Hippo `minutes_display_name` | Low |
| P2 | DRS record-date board resolution (strategy A or B) | Medium |
| P3 | DRS named roll call from data | Medium |
| P4 | §141(e) specificity + exhibit references | Low–Medium |
| P5 | Transactional prompt / new templates | As needed |

---

**Regenerate after code changes**: `corporate_meeting_minutes.py` → `scripts/extract_audit_text.py` → refresh `audit_reports/senior_counsel_audit_2022_2026.md` (or this memo) → `poetry run python scripts/audit_md_to_pdf.py …` as needed.
