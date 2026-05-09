# Privileged internal memo — Senior DGCL audit (generator + registry posture)

**Date:** May 9, 2026  
**Audience:** Records / management and counsel of record  
**Posture:** Experienced Delaware corporate counsel reviewing **synthetic minute packs** produced by `corporate_meeting_minutes.py` as if under **§220** scrutiny or **buy-side diligence**. **Not legal advice** and **not** a substitute for review of filed **certificates of incorporation**, **bylaws**, ledgers, executed consents, and banking resolutions.

**Method:** Aligned with `doc/senior_counsel_prompt/senior_counsel_audit_prompt.md` (Sections I–VI): hierarchy (DGCL > COI > bylaws > minutes), “silence is risk,” and the Section VI coverage map.

**Corpus layout (current generator):** Per-company **meeting-minute** **`.docx`** files (organizational through quarterlies, stockholder-side instruments where applicable, and **standalone board resolutions** for equity / domestication) live in a **single** folder **`generated/<safe>/meetings/`** (no per-year subfolders; filenames remain date-sortable). The per-company **compiled** volume is **`generated/<safe>/<safe>_all_meetings_book.{docx,pdf}`** at the company folder **root**. **Cap table** (`.docx` + Carta/Pulley CSV) and **stock ledger** excerpt **`.docx`** sit in **`generated/<safe>/cap_tables/`** and **`generated/<safe>/stock_ledgers/`**. Optional **PDF/CSV samples** of representative generated docs from **`--write-samples`** land in a **single** folder **`generated/samples/`** (all companies; filenames carry each **`generated/<safe>/`** prefix). The **multi-company** compiled book remains **`generated/books/all_companies_all_meetings_book.{docx,pdf}`**.

**Corpus reviewed for this run:** Current **`corporate_meeting_minutes.py`** behavior and registry strings for **Hippo, Inc.**, **Ritual Growth, Inc.**, **TeamBoost.ai, Inc.**, **DATA RECORD SCIENCE, INC.**, **SurveyTeams, Inc.**, and **Loki Sports Enterprises, Inc.** Plain-text mirrors live under **`audit_text/`** (run `scripts/extract_audit_text.py` after each full regeneration; naming uses the company folder segment so paths like `generated/<safe>/meetings/…`, `…/cap_tables/…`, and `…/stock_ledgers/…` still map to `generated__<safe>__…` extracts).

**Automated chronology / hygiene:** Latest `scripts/audit_corpus_chronology_dgcl.py` pass on refreshed extracts: **0 errors, 0 warnings, 0 calendar conflict slots** (see **`audit_reports/corpus_chronology_dgcl_audit.md`**). That script does **not** replace substantive counsel review of facts and filed instruments.

**Hard-audit corpus:** See **`audit_reports/hard_audit_corpus_run.md`** for the one-liner, naming convention, and search tips.

---

## 1. Executive risk assessment

| Level | Rationale |
|-------|-----------|
| **Green** | No obvious **void**-tier traps in the **templates** (e.g. no §271 asset sale papered as routine board consent; no board “majority email” action posing as **§141(f)**). Stockholder **§228** packs tie to bylaws acknowledgments per company config; default minutes **avoid** claiming exhibits are already **on file** unless `minutes_assert_exhibits_filed: true`. Board remote participation uses **§141(i)**-style contemporaneous communications narrative. |
| **Yellow** | **Evidence and facts**: execution, dating, delivery of notices/waivers/consents; **live COI** (including **§228** permissibility); cap table vs quorum stories; **record-date** math vs bylaws for meeting-path corps. **Record depth**: routine ratification tone—**thin** for contested M&A or self-dealing. **Multi-pattern boards**: Hippo/RG use **sole-director-first quarterly** then full board; TeamBoost uses **full-board organizational** then quarterlies—**internally coherent** if facts match; diligence will ask for **why** ordering differs by company. |
| **Red (integrity)** | **None** identified solely from template logic for the registry companies named above; **RED** would require **fact** mismatches (e.g. Marija not a director until after org but minutes show her at org—user has elected **full-board org** for TB/RG/Hippo org; confirm against **actual** seating dates). |

---

## 2. Material defect / risk register (template + practice)

| Scope | Document / action | Type | Legal hook | Risk | Remediation |
|-------|-------------------|------|------------|------|-------------|
| All written-consent corps | Sole stockholder **§228** consent `.docx` | Voidable until **executed** | DGCL **§228**; COI must **not prohibit** consent | **Med** | Obtain **signed** consent; file with stockholder minutes; confirm **COI** still authorizes consent. |
| All written-consent corps | AGM cross-reference to consent | Practice / evidence | §228 + minute book | **Low** | Default: **“will be filed … upon execution”**; after filing, consider `minutes_assert_exhibits_filed: true` if counsel wants **on file / annexed** wording. |
| Hippo / Ritual / TB | **Board noted** vs **Sole Director** on §228 cross-ref at AGM | Consistency | Practice | **Low** (mitigated) | Generator uses **Board** when AGM is multi-director; avoid manual edits that reintroduce “Sole Director” in multi-director AGMs. |
| Hippo / Ritual / TB | **Organizational** meeting | Facts vs narrative | §141; org practice | **Low–Med** | **`organizational_meeting_full_board: True`**: org minuted with **both** directors present; **no** “Appointment of Additional Director” at org. **Confirm** both were actually directors **as of** org date. |
| Hippo / Ritual (not TB) | **Q1** (or first chronological meeting) | Sole director + appointment | §141 | **Med** if facts differ | First meeting is **sole director** with resolution appointing second director **effective after meeting**. If Marija was already a director at that date, this block is **wrong**—requires config/fact change. |
| TeamBoost | **Q1** after full-board org | No director appointment in Q1 | §141 | **Low** if facts match | Consistent when **both** directors already seated at org; **verify** no gap vs stock ledger. |
| Banking | AGM banking resolution | Ultra vires / authority (**low** if aligned) | §141 + agency | **Low** | Minutes authorize **Derek E. Pappas** as **sole authorized signatory** (per registry config). Match **bank** signature cards and resolutions. |
| DRS / SurveyTeams | Annual stockholder stack | Notice §222; quorum §216 | **§§211–222** | **Med** | **Notice/waiver** forms exist; **delivery** and **timeliness** proof out-of-band; reconcile **record date** to bylaws. |
| Loki (WY) | Same logical checklist | **WYBCA**, not DGCL | Mapping | **Med** | Generator maps some placeholders to **W.S. 1977** sections; treat as **Wyoming** law review. |
| Equity / domestication | **Standalone board resolutions** (`.docx` in `…/meetings/`) | Evidence / ratification | Practice + ledger | **Med** | Full decision text is in **separate** packets; minutes use **short incorporating** resolutions—confirm **execution** of standalone packets and consistency with **stock ledgers** / charter. |

---

## 3. Remote governance (prompt Section II)

- **Board §141(i):** Minutes state **remote/contemporaneous** participation and treat it as **presence** where permitted. **Gap (strict):** no **disconnection** narrative, no **per-vote** quorum maintenance after interruptions, no **identity verification** beyond roll call.
- **Stockholders §211 / §222:** Where generated (e.g. DRS, SurveyTeams), notice content and minutes reference **record date**, **remote** participation, and **list/proxy** themes. **Gap:** **Proof** of notice delivery and **verification** of remote stockholders beyond boilerplate.

---

## 4. Stockholder actions (§228; §§211–213, 216–222)

| Path | Assessment |
|------|------------|
| **§228 sole holder** (Hippo, Ritual, TeamBoost, Loki pattern) | Mechanics and bylaws **ack** blocks are **present** in consent templates; **prompt notice** language included where configured for less-than-unanimous paths. **Must confirm** COI and **signatures**. |
| **Annual meeting** (DRS, SurveyTeams) | **§213** record date appears in minutes/special resolutions where applicable; **§216**-style quorum narrative is **configured to facts**—**dangerous** if cap table changes without updating `company_information`. |
| **Majority §228 ratification** (SurveyTeams) | **Vote threshold** wording; **execute**; **notice** if non-unanimous among voting holders. |

---

## 5. Fiduciary record / §220 (prompt Sections IV–V)

- **§141(e):** Reliance paragraphs **are** included for Delaware (and WY analog for Loki). **Acceptable** for routine governance; **insufficient alone** for **material** transactions (price, process, conflicts, advice).
- **Caremark / Van Gorkom:** Quarterlies and AGMs are **ratification-forward**; fine for **low-stakes** operations; **not** a substitute for **M&A-grade** process minutes.
- **§220:** Opponents will demand **underlying** notices, consents, ledgers, and email—minutes **point** to exhibits but **execution** is external.

---

## 6. DGCL coverage map (Section VI — pass / gap / N/A)

| Topic | DGCL anchor | Result | Note |
|-------|-------------|--------|------|
| Board existence & powers | §141(a)–(b) | **pass** (template) | Quorum/roll call narrative; **verify** board size vs COI/bylaws. |
| Board committees | §141(c), §143 | **N/A** | No committee actions in templates. |
| Vacancies / removal | §141(b), (h) | **N/A** | Not addressed except **appointment** resolution on **first** sole-director meeting where configured. |
| Board meetings & participation | §141(i) | **pass** / **gap** | Contemporaneous remote **pass**; **gap** on disconnects / per-vote quorum. |
| Board written consent | §141(f) | **pass** | No non-unanimous “email board consent” pattern. |
| Reliance on experts/officers | §141(e) | **pass** / **gap** | Boilerplate **pass**; **gap** for material decisions. |
| Annual / special stockholders | §211 | **pass** / **gap** | Meeting path **pass** where generated; **gap** if COI mandates in-person only—check COI. |
| Record date | §213 | **pass** (DRS-style) / **varies** | Written consent path may rely on **dated consent** rather than meeting record date—**confirm** practice. |
| Stockholder quorum & voting | §216 | **pass** (configured facts) / **gap** | **High** sensitivity: must match **live** shares. |
| Proxies / lists | §218 | **gap** | Narrative; **no** vote tabulation exhibit in generator. |
| Notice of stockholder meetings | §222 | **pass** (forms) / **gap** (proof) | Generated notices/waivers; **delivery** off-corpus. |
| Stockholder written consent | §228 | **gap** (execution) | Template **pass**; **voidable** until signed and COI confirmed. |
| Defective acts | §204, §205 | **N/A** | Not generated. |
| Books & records | §220 | **gap** | Exhibit references **soft** until bound with execution copies. |
| Indemnification / exculpation | §145, §102(b)(7) | **N/A** | No minute block asserting advancement/indemnity. |
| Bylaws adoption | §109 | **pass** (org) | Organizational adoption of bylaws **references exhibit labels**; still **confirm** PDF matches. |

---

## 7. Operational follow-ups (non-DGCL but diligence-adjacent)

1. **Re-run** `scripts/extract_audit_text.py` after each full regeneration so **`audit_text/`** matches **`generated/**/*.docx`**.  
2. **Calendar** `--strict-calendars`—keep running **after schedule changes** (cross-company conflicts).  
3. **Officer roster** in org minutes: **CEO/COO** titles now in config—confirm **bylaws** and **state reports** match.  
4. **Review pack / samples:** After regeneration, run **`scripts/build_review_pack.py`** if you rely on **`generated/review_pack/`** snapshots; use **`--write-samples`** for **`generated/samples/`** PDF/CSV samples (including master-book copies in the same folder).

---

## 8. Changelog vs prior audit snapshot (`audit_reports/senior_counsel_audit_2022_2026.md`)

- **Organizational meetings** for Hippo/Ritual/TeamBoost: **`organizational_meeting_full_board`** → **two-director** org; **TeamBoost** no longer **sole-director** at org.  
- **§228 AGM cross-ref:** **Board** intro when AGM is multi-director.  
- **Banking:** **Single** authorized signatory (**Derek E. Pappas**) for Hippo/Ritual/TeamBoost per registry config.  
- **Fiscal language:** **Calendar year** default harmonization in resolutions/president report (unless `fiscal_year_is_calendar_year: false`).  
- Coverage map row **§141(a)–(b)** is **no longer** “sole director only” for **all** corps—**SurveyTeams** and **post-appointment** meetings are **multi-director**.
- **Output paths:** Per-company meeting minutes under **`generated/<safe>/meetings/`** (flat); compiled book at **`generated/<safe>/<safe>_all_meetings_book.*`**; cap table / ledger under **`cap_tables/`** and **`stock_ledgers/`**; **standalone** equity/domestication resolutions under **`meetings/`**; optional PDF/CSV samples under **`generated/samples/`**; master book under **`generated/books/`**.  
- **Quarterly / IP narrative:** Contractor vs owned-equipment clarifications; company-specific **President’s Report** product lines (including **year-keyed** `agm_president_report_product_line` dict for **TeamBoost**).  
- **Execution blocks:** Optional **wet-ink** **Name / Title / Date** lines when **`signature_block_print_signing_lines: true`** (registry-wide).
- **Output tree (flat meetings + flat samples):** Loose minutes under **`generated/<safe>/meetings/`**; compiled **`<safe>_all_meetings_book`** at **`generated/<safe>/`** root; cap table / stock ledger under **`cap_tables/`** and **`stock_ledgers/`**; **`--write-samples`** PDF/CSV under **`generated/samples/`**; master book unchanged under **`generated/books/`**.

---

*End of memo.*
