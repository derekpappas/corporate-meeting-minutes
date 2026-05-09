## Privileged internal memo — DGCL senior-counsel audit (prompt run)

**Posture**: Delaware corporate counsel (25+ year, litigation-heavy) reviewing these documents as if on the eve of a **books-and-records demand, inspection fight, or fiduciary challenge**. **Not legal advice.**

**Method**: `Senior counsel prompt/senior_counsel_audit_prompt.md` (Sections I–VI + Add-ons A–F), **strict** application (“silence is risk”).

**Corpus**: `audit_text/` — **232** plain-text extracts from `generated/` (`corporate_meeting_minutes.py --output-root generated` + `scripts/extract_audit_text.py`, **2026-04-18**). Set includes quarterly, AGM, special, stockholder consent (or DRS / SurveyTeams stockholder meeting stacks), **board notice waivers** (`waiver_of_notice_board_meetings`), compiled **all_meetings_book** extracts, DRS notice/waiver/ratification where applicable, and **Loki** (Wyoming) board minutes.

**COI / bylaws**: Charter OCR text under `ocr_text/` for **Hippo** (`Hippo, Inc. - Certificate of Incorporation (filed).ocr.docx.txt`), **Ritual**, **TeamBoost**, and **DRS**. **Hippo** consents/waivers cite **Amended and Restated Bylaws** (**Article III §13**, **Article IV §21**). **Ritual** and **TeamBoost** cite **By-Laws** (**Article II §9** consent; **Article III §8** and **Article VIII §4** board notice/waiver). **DRS** stockholder-side docs remain generic “bylaws” unless extended. Spot-check live filed charters and bylaws for amendments.

---

### 1. Executive risk assessment

| Level | Rationale |
|------|-----------|
| **GREEN** | No obvious **void**-tier statutory traps in the synthetic set (no §271 asset sale as board-only, etc.). Board acts at meetings; **§141(f)** email-majority fiction not present. **DRS** has **board §213 resolution** in **special** minutes, **stockholder cross-reference**, **majority-holder-only quorum** narrative, **waiver-focused** stockholder minutes, **standalone §222 notice** and **waiver** `.docx` in the corpus, and **§228** consent forms. |
| **YELLOW** | **Book risk** on **material** facts (**§220**), **live COI** vs practice, and **record-date math** (DRS meeting − 10 days) vs bylaws. **Signatures** and **delivery proof** remain out-of-band. **Generator mitigations verified in `audit_text` (2026-04-18)**: annual stockholder §IV uses **to be filed … as Exhibit A following execution** (not “annexed” / “on file” by default); sole-holder **§228** AGM cross-reference uses **will be filed … upon execution** unless `minutes_assert_exhibits_filed: true`; **Notice** `.docx` includes a populated **Date of this notice** line. |
| **RED (integrity)** | **None** on corpus sync (TeamBoost starts **2023**; `audit_text` matches `generated`). |

---

### 2. Material defect / risk register (representative)

| Date / scope | Action / document | Defect type | Legal hook | Risk | Remediation |
|--------------|-------------------|-------------|------------|------|-------------|
| DRS / SurveyTeams annual | Stockholder minutes §IV: waivers **to be filed** as **Exhibit A** **following execution** (default `minutes_assert_exhibits_filed` unset) | **Residual** (execution) | §222 + practice | **Low** | **Sign** waivers; after annexing to the minute book, set **`minutes_assert_exhibits_filed: true`** on the company dict and regenerate if counsel wants **on file** / **annexed** wording. |
| DRS | **Notice** `.docx` — **Date of this notice** | **—** (prior “blank date” memo row **obsolete**) | §222 | **Low** | Extracts show populated date (e.g. **2024-12-01** for 2024). If relying on **notice** path, still retain **delivery** proof outside the corpus. |
| DRS | Majority **§228** ratification consent | **Voidable** (evidence) | §228 | **Medium** | **Execute** signatures; **prompt notice** only if **non-unanimous** among voting holders (often **N/A** if sole voting holder). |
| Hippo / Ritual / TeamBoost | Sole **§228** consent | **Voidable** (evidence) | §228 | **Low–Med** | **Sign** the generated consent; **Hippo** COI in `ocr_text/` (confirm no later amendments); Ritual/TeamBoost charters in `ocr_text/`. |
| Hippo / Ritual / TeamBoost | AGM **§228** cross-reference | **Mitigated** (generator default) | Practice | **Low** | Minutes say **will be filed … upon execution** (and **to be designated Exhibit A upon filing** when label set); not **on file** unless `minutes_assert_exhibits_filed: true`. |
| All | Board minutes “notice given or waived” | **Low** | Bylaws | **Low** | **Board waiver** `.docx` generated per year; sign and file if desired. |
| All | No transactional minutes | **N/A** | §151+, §170, §271… | **N/A** | Use transactional prompt when events exist. |

---

### 3. Remote governance (Section II)

- **Board §141(i)**: Contemporaneous remote participation stated. **Hippo / Ritual / TeamBoost** add **quorum maintained / no vote during comms interruption** language. **Gap** if contested: still no **per-vote** tabulation or disconnect **log** (evidence-grade).
- **Stockholders §211 / §222**: **DRS** notice form includes **date, time, place/remote, record date, purpose**; minutes use **waiver_focus** and match. **Remote verification** line present at meeting. **Gap**: **delivery** and **timeliness** are **not** in the corpus (logs, certificates of mailing).

---

### 4. Stockholder actions (§228; §§211–213, 216–222)

- **Sole-holder §228** (Hippo, Ritual, TeamBoost): Forms + AGM cross-reference: default text is **will be filed … upon execution** (and exhibit **designation upon filing**), not **on file** / **annexed**, unless `minutes_assert_exhibits_filed: true`. **Execute** consents; verify **COI**.
- **DRS annual meeting**: **§213** record date **board-fixed** in special minutes; **§216** quorum = **majority holder present alone** (per your fact pattern). **§218** list/proxy narrative; no tabulation exhibit.
- **DRS §228 majority ratification**: Template **authorizes** prompt notice; **proof** not in extracts.
- **DRS notice/waiver forms**: **Generated** and extracted—**stronger** than minutes-only; still require **signature**, **dating**, and **filing** the path you actually use (**waiver OR notice**, not necessarily both in practice).

---

### 5. Fiduciary record / §220 (Sections IV–V)

- **§141(e)**: Improved boilerplate (materials + officers); **not** deal-specific for **material** transactions.
- **Caremark / Van Gorkom**: Quarterly/AGM **routine** ratification tone; **acceptable** for low-stakes closely held use, **thin** for contested **M&A**-style facts.
- **§220**: Opposing counsel would still seek **underlying** notices, consents, ledger—extracts **point** to them more cleanly for DRS; **execution** remains the user’s burden.

---

### 6. DGCL coverage map (Section VI — pass / gap / N/A)

| Topic | Result | Note |
|-------|--------|------|
| Board existence & powers §141(a)–(b) | **pass** | Sole director; quorum stated. |
| Committees §141(c), §143 | **N/A** | No committee actions. |
| Board vacancies / removal | **N/A** | Not addressed. |
| Board meetings §141(i) | **pass** | Remote boilerplate + optional **quorum/continuity** sentence (H/R/TB). |
| Board written consent §141(f) | **pass** | No improper email-majority board consent. |
| §141(e) | **pass** (routine) / **gap** (material) | Written-consent corps: **materials review** line added; still not deal-specific. |
| Stockholder annual §211 | **pass / gap** | **pass** as narrative; **gap** vs **COI** for consent-only corps—verify. |
| Record date §213 | **pass** (DRS) | Board resolution + cross-ref; **gap** vs **bylaw defaults** if facts differ. |
| Quorum / vote §216 | **pass** (DRS, stated facts) | Majority holder only present—matches provided fact pattern; **gap** if cap table differs. |
| Proxies §218 | **gap** | Narrative only; no exhibit. |
| Notice §222 | **pass** (form) / **gap** (proof) | **Notice** + **waiver** documents generated for DRS; **execution + delivery** proof still **gap**. |
| §228 | **gap** (execution) | Mechanics yes; **signatures** and **prompt notice proof** when required. |
| §204 / §205 | **N/A** | No ratification of defective acts described. |
| §220 | **gap** | Template-leaning without executed exhibits. |
| §145 / §102(b)(7) | **N/A** | Light review; no obvious conflict. |
| Bylaws §109 | **N/A** | No bylaw amendment minutes. |

---

## Section VI — Aggressive grading (summary table)

| Topic | Anchor | Grade | Notes |
|-------|--------|-------|-------|
| Notice | §222 | **YELLOW → mitigated (form)** | Standalone **notice** + **waiver** in corpus; stockholder minutes §IV **softened** (pending filing language). **YELLOW** remains for **delivery / timeliness proof** off-extract. |
| Quorum / vote | §216 | **YELLOW** | **Sole voting presence** narrative for DRS; still no **vote tabulation** figures. |
| §220 | inspection | **YELLOW** | Better **paper trail design** for DRS; execution still **out of band**. |

---

## Add-ons A–F (abbreviated)

- **A**: Reconcile **10-day** record date and **notice dates** to **bylaws** and **facts**.
- **B**: §211 cadence present; TeamBoost from **2023**.
- **C**: §228 **authorization ≠ proof** (signatures, prompt notice when applicable).
- **D**: Run **extract** after every regen.
- **E**: **COI** vs written consent / waiver of separate meeting.
- **F**: §204/§205 if **voidable** defects appear in **live** records.

---

## Deliverables checklist (prompt format)

1. **Executive risk**: **YELLOW** book; **no integrity RED**.  
2. **Defect log**: Table in §2.  
3. **Remote governance**: §3.  
4. **Stockholder actions**: §4.  
5. **Fiduciary / §220**: §5.  
6. **§VI map**: pass/gap table in §6.

---

## Immediate remediation

1. **Execute** stockholder **waivers** and **§228** consents; **file** them with the minute book. After instruments are actually annexed, optionally set **`minutes_assert_exhibits_filed: true`** and regenerate if counsel wants minutes to read **on file** / **annexed**.  
2. If using **notice** path: retain **delivery** and **timeliness** proof (the generated **Notice** includes **Date of this notice** in extracts; that is not the same as proof of delivery).  
3. **Execute** all **§228** consents; keep in minute book.  
4. **Regen → extract → refresh this memo + PDF** when templates change.

---

## Closed / improved in this generator cycle

- **H/R/TB**: **§228** consent **sole-holder explainer** + **execution** block; AGM **filing-upon-execution** default (exhibit label optional); **§141(e) materials** supplement + **remote quorum continuity** on board minutes; bylaw **section cites**; **board waiver** `.docx` per year. **DRS**: **§213** special; **waiver_focus**; notice + waiver + ratification stack.
- **Exhibit / filing claims**: default **`minutes_assert_exhibits_filed`** behavior—stockholder §IV and sole **§228** AGM cross-reference use **pending filing** wording; **operating addendum** “annexed” softened to **designated for attachment upon filing** unless flag is true.
- **Notice** `.docx`: **Date of this notice** populated from the board **record-date** meeting date (verified in `audit_text`).
- **Per-meeting** roll call / quorum / **§141(e)**-style reliance **wording** rotates by meeting (less merge-field identical across dates).

---

## PDF

Render with: `poetry run python scripts/audit_md_to_pdf.py audit_reports/senior_counsel_audit_2022_2026.md --out audit_reports/senior_counsel_audit_2022_2026.pdf`
