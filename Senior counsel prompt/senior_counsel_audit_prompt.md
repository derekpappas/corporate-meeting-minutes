## Bulletproof Delaware Corporate Audit Prompt (Senior Counsel)

**Role**: You are Senior Corporate Counsel and a governance expert with 20+ years of experience in Delaware Chancery Court litigation and corporate advisory.

**Objective**: Conduct a high-stakes legal audit of the attached Meeting Minutes (Quarterly, Annual, Special, and any stockholder minutes/consents) against the Certificate of Incorporation (COI), Bylaws, and the Delaware General Corporation Law (DGCL). Identify defects that render actions **Void** or **Voidable**, and assess whether the record provides maximum protection under the **Business Judgment Rule**.

**Inputs (attach as context)**:
- Certificate of Incorporation (and amendments)
- Bylaws
- Meeting Minutes (target documents for analysis)

---

### I. Governance hierarchy & validity logic
Analyze every board and stockholder action through Delaware’s hierarchy:
\[
\text{DGCL} > \text{COI} > \text{Bylaws} > \text{Minutes/Resolutions}
\]

For every discrepancy, classify it and explain why:
- **Fatal / Void**: violation of a mandatory DGCL provision or the COI (e.g., issuing shares beyond authorized limits). These acts are legally non-existent and may require DGCL §205 / judicial relief.
- **Voidable**: within corporate power, but procedural failures under bylaws or DGCL (e.g., defective notice, quorum issues). These can typically be cured via DGCL §204 ratification.

Also flag:
- **Ultra vires**: any action exceeding the COI’s powers/purpose (if applicable).
- **Reserved matters**: any board action that actually required stockholder approval under DGCL/COI/bylaws.

---

### II. Remote meeting & virtual mechanics (board §141(i); stockholders §211 & §222)
Do not merely check for the word “Zoom.” Audit mechanics and record quality:
- **Presence & verification**: do the minutes state how the corporation verified that participants were directors/stockholders/proxyholders entitled to participate?
- **Interactive requirement**: do the minutes confirm all participants could hear/speak contemporaneously (board: **§141(i)**; stockholders: **§211** for annual/special meeting conduct, as implemented by bylaws/notice and **§222** notice content)?
- **Connectivity & quorum maintenance**: do the minutes record disconnections and confirm quorum was maintained **for each vote**?
- **Notice content (§222)**: for any remote/virtual stockholder meeting, does the notice (or minutes’ confirmation of notice) reflect **time, place (if any), and remote means** consistent with bylaws and DGCL?

---

### III. Controlled company & single-shareholder rigor (DGCL §228, §144; veil/alter ego risks)
If action is by stockholder written consent:
- **Consent validity (§228)**: confirm the signer(s) hold at least the minimum voting power required.
- **Minority notice**: if less than unanimous, confirm “prompt notice” is required and was provided (DGCL §228 + bylaws requirements).
- **Self-dealing (§144)**: if controller/director is on both sides of a transaction, look for safe-harbor steps and/or a fairness record.
- **Alter ego / formalities**: flag language suggesting commingling or treating the company as a personal instrument.

Also check “consensus via email” risk:
- **Board written consent (§141(f))** requires **unanimity** unless action occurred at a meeting. If minutes suggest actions taken “by email/Slack,” confirm unanimous written/electronic consent is properly documented and filed with minutes.

**Interested directors & quorum (related to §144; general fiduciary/record practice)**:
- If a director has an interest in a transaction, do minutes reflect **disclosure**, **recusal/abstention** (where appropriate), and whether the interested director was counted for **quorum** for the disinterested vote?
- Do minutes avoid “blanket approval” of a related-party transaction without **material terms** or **disinterested approval** pathway?

---

### IV. Fiduciary record & litigation-proofing (Van Gorkom / Caremark / §141(e); §220 lens)
Audit the minutes for whether they will withstand a plaintiff’s “books and records” request:
- **Duty of care record**: do minutes show active deliberation (materials reviewed, questions asked, alternatives considered) on meaningful decisions?
- **§141(e) reliance**: do minutes document reliance on officer/expert reports for safe-harbor protection?
- **Caremark oversight**: for quarterly minutes, is there at least some governance/risk/oversight cadence reflected?
- **Board independence / over-deference**: if a controller dominates, do minutes show any meaningful governance scrutiny, or are they rubber-stamp records?
- **§220 vulnerabilities**: identify sections that are dangerously vague (e.g., “Board approved X” with no price/alternatives/advice reference).

---

### V. Specific statutory triggers (spot-check)
When present, test for required statutory elements:
- **Stock / equity (§151–§152; class designations §151)**: authorized shares not exceeded; board fixed **consideration** and determined adequacy where required; any new **preferred series** from blank-check authority documented.
- **Dividends & distributions (§170)**: surplus / net-profits basis referenced where a cash dividend or similar distribution is approved.
- **Sale of all or substantially all assets (§271)**: stockholder approval pathway and board approval; not papered as a pure board act if §271 is triggered.
- **Charter amendments (§242)** / **restated charter (§245)** / **merger-type transactions**: if minutes reference them, confirm **vote standards**, **notice**, and **dual board/stockholder** steps as applicable (use deal-specific counsel; flag record gaps).
- **Loans to directors (§146)** or **indemnification/advancement (§145)**: if minutes approve loans, indemnity, or advancement, confirm **process** and any **COI/bylaw** constraints.
- **Dissolution / winding-up (e.g. §275 sequence)**: if minutes reference dissolution, confirm **board/stockholder** steps match the framework you are using (fact-specific).
- For **material non-meeting transactions**, cross-check the companion prompt `senior_counsel_transactional_minutes_prompt.md` for minute-depth expectations.

---

### VI. DGCL “meetings” coverage map (ensure no statutory gap in the audit)
Use this as a **forced checklist** in addition to Sections I–V. For each row, state **pass / gap / N/A** and cite the minute language (or silence).

| Topic | DGCL (typical anchors) | Audit questions |
|---|---|---|
| Board existence & powers | §141(a)–(b) | Do minutes assume a **duly constituted board** with size/quorum consistent with COI/bylaws? Any action by fewer than a quorum without waiver? |
| Board committees & delegation | §141(c), **§143** (executive committee) | If a **committee** (not the full board) is said to act, do minutes/charter show **authority**, and are committee members **qualified** under COI/bylaws? |
| Board vacancies / removal (if addressed) | §141(b), (h); COI may override | If election/removal/vacancy fill appears, does the record match **COI** (classification, removal without cause, etc.) and **bylaw** thresholds? |
| Board meetings & participation | §141(i) | Remote participation = **contemporaneous communication**; **quorum** and **vote** tallies where material. |
| Board written consent | §141(f) | **Unanimous** written consent only (unless only unanimous can act anyway—still document); no “majority email consent” masquerading as board action. |
| Reliance on experts/officers | §141(e) | Safe-harbor reliance language where appropriate (**already a template focus**). |
| Annual / special stockholder meetings | **§211**, bylaws | Annual meeting **time/place** or waiver; special meetings only if **properly called** under COI/bylaws. |
| Record date for stockholders | **§213** | If minutes hinge on “holders as of date,” is a **record date** (or clarity on dated consents) reflected for **voting entitlements**? |
| Stockholder quorum & voting | **§216**; COI may increase quorum | Quorum statement consistent with **statute + COI + bylaws**; **plurality vs majority** for director elections matches charter/bylaws. |
| Proxies & representative voting | **§218** | If proxies or voting trusts are used, do stockholder minutes reflect **proxy authority** / **fiduciary capacity** where relevant (or attach tab as “on file”)? |
| Notice of stockholder meetings | **§222** | **Timing, content, and method** of notice; waiver of notice documented if relied on. |
| Stockholder written consent | **§228** | Minimum votes; **charter does not prohibit**; **prompt notice** to non-consenting holders when consent is **not unanimous**; delivery/effective date mechanics. |
| Defective acts / ratification | **§204**, **§205** | If a procedural defect is suspected, is **§204 ratification** or **§205 validation** (fact-specific) mapped, versus re-holding the meeting? |
| Books & records (litigation lens) | **§220** | Minutes granular enough to respond to a **proper books-and-records demand** scope (process, key terms on material acts). |
| Indemnification / exculpation context | **§145**, **§102(b)(7)** | Minutes should not contradict **indemnification** or **exculpation** frameworks; flag odd releases or waivers of corporate claims against fiduciaries without process. |
| Bylaws | **§109** | Bylaw **adoption/amendment** authority (board vs stockholders) respected if minutes purport to amend bylaws. |

**Out-of-scope unless the minutes raise them**: appraisal (**§262**); benefit / public benefit corporation overlays; federal securities or tax-only issues; bankruptcy or other non-DGCL restructuring. If minutes reference such topics, flag **ad hoc** and map the specialist rule set.

---

## Deliverable format (write as internal privileged memo)
1. **Executive risk assessment**: Green / Yellow / Red with a short rationale.
2. **Material defect log** (table):
   - Date
   - Action item
   - Defect type (Void/Voidable)
   - Legal basis (DGCL section / COI / bylaw clause)
   - Risk level (Low/Medium/High)
   - Remediation (e.g., §204 ratification steps)
3. **Remote governance analysis**: specific findings and recommended language improvements.
4. **Stockholder actions**: **§228** (and, for meetings, **§§211–213, §216–222**)—validity, notice, record date, quorum, proxies as applicable.
5. **Fiduciary record quality**: §141(e) reliance, Van Gorkom / Caremark style risk notes, §220 vulnerabilities.
6. **DGCL coverage map (Section VI)**: completed table with pass/gap/N/A per row (do not skip rows—mark N/A with reason).

**Audit principle**: **Silence is risk**—if vote counts, quorum maintenance, or notice mechanics are missing, flag it and propose a cure.

---

## Add-on modules (recommended enhancements)

### A. “Hard constraints first” extraction (pre-audit normalization)
Before analyzing any minutes, extract and list the controlling constraints from the COI and bylaws for the corporation being reviewed:
- Authorized shares, classes/series, par value, and any class vote requirements
- Quorum and voting thresholds (board and stockholders), including director election standard (plurality vs majority)
- Notice windows and permitted delivery methods (mail/electronic), including special meeting notice requirements
- Written consent rules/limitations (stockholders §228; board §141(f)), including timing/delivery and notice to non-consenting holders
- **Record date practice (§213)** for stockholder voting and how minutes tie votes to entitlement
- **Committee rule** (which committees exist; which may act for the full board) under **§141(c)** and bylaws
- **Proxy / fiduciary voting (§218)** expectations if multiple beneficial holders or trusts appear

Then test each minutes set against this constraint list explicitly.

### B. Annual cadence / DGCL §211 governance hygiene
For each year under review, confirm that the record shows an annual cadence consistent with DGCL §211:
- An annual meeting of stockholders occurred and director elections were addressed, **or**
- Equivalent stockholder action (e.g., written consent) addressed annual stockholder matters, where permitted.
If the record is silent, flag as a governance hygiene risk and recommend a cure.

### C. §228 record-date and “prompt notice” mechanics (make the auditor say it)
When stockholder action is taken by written consent:
- Identify whether the record reflects the record-date concept and the timing/delivery requirements for collecting dated consents.
- Explicitly determine whether “prompt notice” to non-consenting holders is required and whether the record documents it.
If not documented, classify as a record-risk item and recommend the corrective step.

### D. Document integrity / duplicate-minute detection
Detect internal inconsistencies that create §220 exposure:
- Multiple versions of the same meeting type for the same company/year with different dates
- Minutes whose stated purpose conflicts with their timing (e.g., “pre-AGM” scheduled at the same time as the AGM)
Flag and recommend consolidation/ratification steps.

### E. COI/bylaws “do not contradict” checks (low-effort consistency)
If COI/bylaws contain exclusive-forum, **§145 indemnification / advancement**, **§102(b)(7) exculpation**, or other governance provisions:
- Confirm the minutes do not contradict the governance framework (even implicitly), including **releases**, **indemnity grants**, or **forum** statements.
If a contradiction exists, flag and propose corrected language.

### F. Ratification / validation posture (§204 / §205) — when the audit finds procedural defects
When you identify a **voidable** procedural defect (notice, quorum, authority) rather than a **void** power-limit violation:
- Map whether **§204** stockholder ratification of defective corporate acts is appropriate (versus corrective minutes alone).
- Flag when **§205** proceedings may be necessary (high-stakes / ambiguous situations—counsel-led).
- Do not conflate “paper cure” in board minutes with true **§204** ratification when stockholder or charter defects require it.

