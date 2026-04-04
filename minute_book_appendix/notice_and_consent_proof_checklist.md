# Notice & consent proof — checklist (not legal advice)

**Purpose**: Track **delivery evidence** for stockholder **meeting notice (DGCL §222 / bylaws)** and **§228 prompt notice** (when consent is not unanimous). These are **not** generated as `.docx` by `corporate_meeting_minutes.py`; you attach **vendor exports**, **mail receipts**, or an **affidavit** (where bylaws allow) from real operations.

**Sources in repo**: `bylaws_text/Bylaws of TeamBoost.ai, Inc.pdf.txt`, `Bylaws of Ritual Growth, Inc.pdf.txt`, `Hippo, Inc. - Bylaws.docx.pdf.txt`, `Data_Reord_Science_bylaws.pdf.txt`.

---

## 1. Who must receive notices (stockholders) — by company

All four companies’ bylaws follow the same **core rule** for **calling a stockholder meeting**: notice goes to **each stockholder entitled to vote** at that meeting, determined as of the **record date** (board-fixed or default under DGCL), using the **name and address (and/or electronic contact) on the corporation’s stock ledger / records**.

| Company | Bylaws file | Meeting notice recipients | Manner (summary) | §228 “prompt notice” recipients (if applicable) |
|--------|-------------|---------------------------|------------------|--------------------------------------------------|
| **Hippo, Inc.** | `Hippo, Inc. - Bylaws.docx.pdf.txt` (§7) | Each **stockholder entitled to vote** at the meeting | Writing or **electronic transmission**; if **mailed**, when deposited in **U.S. mail**, postage prepaid, to address **on the corporation’s records** | **Stockholders who did not consent** (in writing or electronic transmission) and who would have been **entitled to notice of a meeting** if the **§228(c) record date** were the meeting record date (§13(c)) |
| **Ritual Growth, Inc.** | `Bylaws of Ritual Growth, Inc.pdf.txt` (Art. II §3) | Each **stockholder entitled to vote** | **Personal delivery** or **mail** to address **on the corporation’s records**; **10–60 days** before meeting; **electronic transmission** if effective under applicable law | **Stockholders who have not consented in writing** (less than unanimous consent) (§9) |
| **TeamBoost.ai, Inc.** | `Bylaws of TeamBoost.ai, Inc.pdf.txt` (same pattern as Ritual) | Each **stockholder entitled to vote** | Same pattern as Ritual (personal delivery, mail, electronic per law) | Same as Ritual (**non-consenting** stockholders) |
| **DATA RECORD SCIENCE, INC.** | `Data_Reord_Science_bylaws.pdf.txt` (§§2.4–2.5) | Each **stockholder entitled to vote** | **10–60 days** before meeting; **mail** = when deposited U.S. mail to address **on the records**; may also use **email/other electronic transmission** per **DGCL §232**; **affidavit of secretary / assistant secretary / transfer agent** can be **prima facie** evidence notice was given | **Stockholders who have not consented in writing** (including electronic as permitted) (§2.11) |

**Practical recipient list**: For a given meeting, it is **the record holders entitled to vote** (and, if you use proxies, your process still starts from **who must receive notice**—often record holders; confirm with counsel). **Beneficial owners** do not replace ledger addresses unless your **§232** consent and process say otherwise.

**Board meetings**: Separate rule — notice to **directors** (not stockholders). See each bylaws’ board-notice article if you paper director meetings.

**Not covered here**: Hippo **Rule 14a-8**-style **stockholder proposal** notices to the Secretary (public-company path); that is a different notice regime from standard annual-meeting notice.

---

## 2. What extra data the program would need to **generate** more (optional)

The generator does **not** produce send logs or proof packs. To **auto-fill** recipient lines, mail-merge notices per holder, or emit a **stub** CSV from Python, you would need structured inputs (none of this is required for current `.docx` output):

| Data | Why |
|------|-----|
| **Per-meeting record date** (ISO) + confirmation it matches board resolution | Determines **who** is entitled to notice/vote |
| **Ledger extract** or table: legal name, **shares**, **mailing address**, optional **email** for §232-style electronic notice | Recipient list; method per holder |
| **Chosen delivery method** per recipient (mail / email / both) + proof you have **§232** consents if using electronic notice | Legally effective delivery, not just template text |
| **Meeting type** (annual vs special) + **purposes** for special meetings | Content requirements |
| For **§228**: which holders **signed** vs **did not sign**; date **sufficient consents** delivered | **Prompt notice** only to **non-consenting** eligible holders |
| **Adjournment** facts: >30 days or **new record date**? | May require **fresh notice** to all entitled stockholders (see each bylaws adjournment section) |
| **DRS only**: if using **affidavit of notice** path, identity of signatory (**Secretary / Assistant Secretary / transfer agent**) | Matches §2.5 affidavit option |

Until those exist, **manual** completion of `send_log_column_headers.csv` (and your vendor’s native export) is the right approach.

---

## 3. Checklist — meeting notice (§222 / bylaws)

- [ ] Record date fixed (board resolution on file if not default)
- [ ] List of **each** record holder **entitled to vote** as of that date
- [ ] Notice content: time, place (if any), remote means (if any), purpose (if special), matches bylaws/DGCL
- [ ] Notice sent **within** bylaws window (e.g. **10–60 days** before meeting for these companies)
- [ ] **Proof retained**: e.g. email vendor export, certified-mail receipts, courier POD, or **affidavit** (DRS §2.5) — see `send_log_column_headers.csv`
- [ ] If **waiver** used instead of notice: executed **waiver** dated appropriately; minutes language matches reality

---

## 4. Checklist — §228 prompt notice (less than unanimous consent)

- [ ] Identify **non-consenting** stockholders who are **entitled to notice** under the bylaws/DGCL test for your company (Hippo §13(c) is more explicit than the shorter Ritual/TeamBoost/DRS formulations)
- [ ] Prepare short notice of the **action taken** (form/content per counsel)
- [ ] Send within **prompt** timeframe; retain **delivery proof** same as §222 practice
- [ ] If **unanimous** written consent among **all voting holders**, prompt notice is typically **N/A** (confirm facts and COI)

---

## 5. CSV template

Use `send_log_column_headers.csv` as the header row only; **export real rows** from your email vendor, USPS, etc.
