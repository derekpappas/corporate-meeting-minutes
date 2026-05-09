# DGCL concepts embodied in generated corporate minutes

This note explains **Delaware General Corporation Law (DGCL)** ideas that appear—explicitly or by narrative—in documents produced by `corporate_meeting_minutes.py`. It is **informational only**, not legal advice. Counsel should confirm citations and facts against your certificate of incorporation, bylaws, and resolutions.

---

## How Delaware appears in the generator

- **Delaware corporations** (`incorporation_jurisdiction` / jurisdictional defaults → DE): templates cite **DGCL** sections by label (e.g. **DGCL § 228**, **DGCL § 141(e)**) via `_corp_law_section_ref()` and `_corporation_statute_name()` (“Delaware General Corporation Law”).
- **Wyoming corporations**: the same *logical* placeholders map to **Wyoming Business Corporation Act** citations where implemented (e.g. written consent and record date map to `W.S. 1977 § 17-16-704` and `§ 17-16-707`, respectively per tests)—not DGCL. Treat those entities under Wyoming law, not this DGCL list.

---

## Sections explicitly cited or mechanically labeled

### DGCL § 141(e) — Director reliance on experts and others

**What it does (conceptually):** In broad terms, § 141(e) addresses when directors may rely in good faith on information from officers, experts, committees, and similar sources—often summarized as a **safe-harbor** for reasonable reliance on professionally prepared materials.

**Where it appears:** Board minutes (annual, special, quarterly, organizational) include a **reliance paragraph** after officer/report sections (`board_director_reliance_paragraph`). Registry companies may override with **`board_meeting_reliance_markdown`**, which often uses the shorthand **“DGCL § 141(e)”**.

**What the minutes are trying to record:** That directors acted with appropriate **information flow** from management and advisors—not that every factual assertion in the packet was independently verified.

---

### DGCL § 141(i) — Remote participation at board meetings (concept usually embodied)

**What it does:** Delaware permits participating in board meetings by remote communications when everyone can **hear each other contemporaneously** (subject to charter/bylaw requirements).

**Where it appears:** The generator often **does not print “§ 141(i)”** explicitly. Instead, when **`virtual_ok`** is true, **`board_remote_presence_paragraph`** and quorum blocks describe participation via communications equipment and treat it as **presence in person** or equivalent where permitted—language aligned with typical § 141(i) practice.

**Takeaway:** The *concept* is in the narrative; the *section number* may be omitted unless you add it in a custom override.

---

### DGCL § 211 — Annual meeting of stockholders (concept)

**What it does:** Requires annual meetings of stockholders at stated times or as provided in the charter, subject to exceptions and postponements.

**Where it appears:** Companies configured for a **formal annual meeting of stockholders** generate stockholder meeting minutes, notices, and waivers. The documents describe an **annual meeting** and related logistics; they may not quote “§ 211” by number everywhere.

**Interaction with § 228:** Some companies use **written consent in lieu of** convening a separate annual meeting for stockholder-level housekeeping—see § 228 below and charter authorization.

---

### DGCL § 213 — Record date for stockholders

**What it does:** Governs fixing a **record date** to determine which stockholders are entitled to notice or to vote (within statutory limits).

**Where it appears:** Annual stockholder minutes, notice templates, board special-meeting resolutions fixing a record date, and waiver forms often label the record date with **`_corp_law_section_ref(co, "213")`** → **“DGCL §213”** for Delaware companies.

---

### DGCL § 216 — Quorum and voting for stockholders (concept)

**What it does:** Default quorum and voting rules for stockholders unless the certificate of incorporation provides otherwise (with limits).

**Where it appears:** Minutes may **describe quorum** (e.g. majority holder present alone satisfies quorum for a configured fact pattern). The generator generally **does not** paste “§ 216” into every paragraph; the **story** is “quorum was satisfied under the DGCL and bylaws.”

---

### DGCL § 218 — Voting trusts and agreements; proxies; lists (partial concepts)

**What it does:** Includes rules around **voting trusts** and related matters; annual meeting practice often ties to **lists of stockholders** and **proxies** for meetings.

**Where it appears:** Formal annual stockholder minutes include narrative that a **stock ledger / list** was available and **proxies** were handled in accordance with bylaws—this reflects **meeting mechanics** commonly associated with § 218–style corporate practice (without necessarily citing the section number in every file).

---

### DGCL § 222 — Notice of stockholder meetings

**What it does:** Addresses **notice** of stockholder meetings (timing, content, and related requirements).

**Where it appears:** Generated **notice of annual stockholder meeting** documents and related commentary in code (`§222-style`). Minutes may also confirm **notice given** or **waived** in accordance with the DGCL and bylaws.

---

### DGCL § 228 — Action by written consent of stockholders

**What it does:** Allows stockholder action **without a meeting** if authorized by statute and **the certificate of incorporation**, by written consent meeting ownership signature thresholds.

**Where it appears:**

- **Sole stockholder written consent** packs cite **`_corp_law_section_ref(..., "228")`**.
- Board AGM minutes may **cross-reference** the written consent filed with stockholder records for that year.
- Bylaws acknowledgments in consent packs (per company config) tie mechanics to **Article/section** of your bylaws **and** § 228 / DGCL.
- **Majority stockholder ratification** consent (multi-holder paths) also references the statute name and consent mechanics.

**Critical non-code point:** § 228 **does not apply** if the charter **prohibits** stockholder action by written consent—your **certificate of incorporation** must be checked.

---

## Concepts reflected in board-meeting “housekeeping” language

These are **standard governance narratives** in the generated `.docx` files. They support a coherent minute book; they are **not** a substitute for verifying quorum thresholds and notice rules in your **bylaws** and **charter**.

| Theme | Typical minute-book idea | DGCL anchor (conceptual) |
| --- | --- | --- |
| Board existence and meetings | Board convenes, adopts resolutions | § 141 board management (general) |
| Quorum | Sole director present, or **full board** present—wording matches configured template | § 141 quorum rules as implemented in charter/bylaws |
| Notice | “Notice duly given **or waived**” | Notice/waiver framework implemented in bylaws; DGCL supplies defaults and boundaries |
| Remote participation | Hear/be heard / contemporaneous communications | § 141(i) style |
| Reliance on materials | Financial and officer materials | § 141(e) |
| Resolutions | Adoption of budgets, banking authorization, ratifications | Board authority under § 141 and other provisions as applicable |

---

## What is *not* covered by these templates

The generator focuses on **recurring board and stockholder governance minutes**. It does **not** systematically implement, for example:

- **§ 141(f)** — unanimous written consent **of the board** (distinct from stockholder § 228).
- **§§ 151–165** — stock terms, classes, and related instruments.
- **§ 251 / 263 / 264** — mergers and domestications (except narrative **ratification** language you may add for domestication events).
- **§ 220** — books and records demands (sometimes discussed in audit notes, not generated as standalone minutes).

If a transaction-specific minute is required, use separate counsel-approved templates.

---

## Citation style in the documents

You may see **“DGCL § 141(e)”** in one place and **“Section 141(e) of the Delaware General Corporation Law”** in another (especially in rotating boilerplate variants). That is **editorial variation**, not two different legal standards—unless a typo points to the wrong section (always spot-check final PDFs/DOCX).

---

## Quick map: document type → main DGCL ideas

| Generated artifact (examples) | Primary DGCL themes |
| --- | --- |
| Board AGM / quarterly / special / organizational minutes | § 141 (board meetings, quorum, notice narrative), **§ 141(e)** reliance, **§ 141(i)**-style remote participation |
| Sole stockholder written consent | **§ 228**, charter permissibility, bylaws mechanics |
| Annual meeting of stockholders minutes | **§§ 211, 213, 216, 218, 222** (as narrative: annual meeting, record date, quorum, list/proxies, notice) |
| Notice / waiver of stockholder meeting | **§ 222**-style notice content; waivers as permitted |
| Board waiver of notice (annual compilation) | Notice/waiver story for board meetings (bylaws + statute backdrop; § 141 notice framework) |
| Majority stockholder ratification consent | **§ 228**; prompt notice concepts where applicable |

---

*Last aligned with generator behavior in `corporate_meeting_minutes.py` (section refs and reliance/remote/quorum blocks). Update this document if templates add new statutory hooks.*
