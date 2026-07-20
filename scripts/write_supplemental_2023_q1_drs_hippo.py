#!/usr/bin/env python3
"""Write supplemental 2023 Q1 DRS/Hippo minutes and Jan 15, 2023 standalone resolutions.

Outputs live under ``generated_supplemental/2023_q1_drs_hippo/`` and do **not** modify ``generated/``.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

_REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

import corporate_meeting_minutes as cmm  # noqa: E402

_DEFAULT_DATA = os.path.join(_REPO_ROOT, "data", "supplemental", "2023_q1_drs_hippo.json")
_DEFAULT_OUTPUT = os.path.join(_REPO_ROOT, "generated_supplemental", "2023_q1_drs_hippo")

DRS = "DATA RECORD SCIENCE, INC."
HIPPO = "Hippo, Inc"
YEAR = 2023
QUARTER = "Q1"


def _load_data(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _fmt_usd(amount: int) -> str:
    return f"${amount:,}"


def _drs_executive_resolution_blocks(data: dict) -> list[str]:
    appt = data["officers"]["appointed"]
    rem = data["officers"]["removed"]
    eff = cmm._fmt_long_date(data["action_date_iso"])
    return [
        f"""**Appointment of {appt["name"]} as Executive Officer**  
RESOLVED, that **{appt["name"]}** is hereby appointed as an **{appt["role"]}** of the Corporation, with such authority and duties as the Board may designate from time to time, effective **{eff}**.""",
        f"""**Removal of {rem["name"]} as Executive Officer**  
RESOLVED, that **{rem["name"]}** is hereby removed as an **{rem["role"]}** of the Corporation, effective **{eff}**.""",
        """**Minute book and corporate records**  
RESOLVED, that the **Secretary** is authorized and directed to update the Corporation’s officer records, minute book, and related corporate files to reflect the appointments and removals set forth above, and to file copies of these resolutions with the Corporation’s minute book.""",
    ]


def _license_party_name_correction_clause(data: dict) -> str:
    orig = data["parties"]["license_agreement_party_name_original"]
    fixed = data["parties"]["license_agreement_party_name_corrected"]
    return (
        f"correcting the Corporation’s name as stated in that agreement from **{orig}** to **{fixed}**"
    )


def _drs_license_correction_resolution_blocks(data: dict) -> list[str]:
    drs = data["parties"]["drs_legal_name"]
    hippo = data["parties"]["hippo_legal_name"]
    agr = cmm._fmt_long_date(data["license_agreement_date_iso"])
    corr = cmm._fmt_long_date(data["license_correction_date_iso"])
    sec = data["license_section"]
    orig = _fmt_usd(data["license_payment_original_usd"])
    fixed = _fmt_usd(data["license_payment_corrected_usd"])
    name_fix = _license_party_name_correction_clause(data)
    return [
        f"""**Ratification of Software License Agreement with {hippo}**  
RESOLVED, that the **Software License Agreement** between **{drs}** and **{hippo}**, dated **{agr}**, is hereby ratified, confirmed, and approved in all respects (subject to the clerical corrections approved below).""",
        f"""**Correction of clerical errors — Software License Agreement ({corr})**  
RESOLVED, that the Board hereby approves the correction of **clerical errors** in the Software License Agreement between the Corporation and **{hippo}**, dated **{agr}**, including {name_fix}, and correcting the payment amount stated in **Section {sec}** from **{orig}** to **{fixed}**, in each case effective **{corr}**; and **FURTHER RESOLVED**, that the **President** is authorized to execute and deliver any amendment, restatement, or confirmatory instrument necessary to give effect to such corrections.""",
        """**Filing**  
RESOLVED, that the **Secretary** is authorized and directed to file a copy of the corrected agreement (or amendment reflecting the corrections) with the Corporation’s minute book and to maintain an index cross-reference to these resolutions.""",
    ]


def _hippo_license_correction_resolution_blocks(data: dict) -> list[str]:
    drs = data["parties"]["drs_legal_name"]
    hippo = data["parties"]["hippo_legal_name"]
    agr = cmm._fmt_long_date(data["license_agreement_date_iso"])
    corr = cmm._fmt_long_date(data["license_correction_date_iso"])
    sec = data["license_section"]
    orig = _fmt_usd(data["license_payment_original_usd"])
    fixed = _fmt_usd(data["license_payment_corrected_usd"])
    orig_party = data["parties"]["license_agreement_party_name_original"]
    fixed_party = data["parties"]["license_agreement_party_name_corrected"]
    return [
        f"""**Acceptance of corrections to Software License Agreement with {drs}**  
RESOLVED, that the Board hereby accepts and approves the correction of **clerical errors** in the **Software License Agreement** between **{hippo}** and **{drs}**, dated **{agr}**, as corrected on **{corr}**, including changing the licensor name from **{orig_party}** to **{fixed_party}** and changing the payment amount in **Section {sec}** from **{orig}** to **{fixed}**.""",
        """**Authorization**  
RESOLVED, that the **President** is authorized to execute and deliver any amendment, restatement, or confirmatory instrument on behalf of the Corporation necessary to give effect to such correction, and that the **Secretary** shall file copies with the Corporation’s minute book.""",
    ]


def _standalone_resolutions_markdown(
    co_name: str,
    meet_iso: str,
    subject: str,
    blocks: list[str],
    *,
    signer_name: str = "Derek E. Pappas",
    signer_title: str | None = None,
) -> str:
    co = cmm.companies[co_name]
    display = cmm.minutes_display_name(co_name)
    body = "\n\n".join(blocks)
    if signer_title:
        sig = cmm.signature_block(co, signer_name, meet_iso, title=signer_title)
    else:
        sig = cmm.board_meeting_signature_markdown(co, meet_iso, sole_director_name=signer_name)
    return (
        f"**Standalone board resolutions — {display}**\n"
        f"**Meeting date:** {cmm._fmt_long_date(meet_iso)}\n"
        f"**Subject:** {subject}\n\n"
        f"{body}\n\n"
        f"{cmm.SIGNATURE_BLOCK_MARKER}\n\n"
        f"{sig}\n---\n"
    )


def _drs_signer(data: dict) -> tuple[str, str]:
    s = data["drs_resolution_signer"]
    return s["name"], s["title"]


def _drs_q1_supplemental_business_review(data: dict) -> str:
    appt = data["officers"]["appointed"]["name"]
    rem = data["officers"]["removed"]["name"]
    hippo = data["parties"]["hippo_legal_name"]
    orig_party = data["parties"]["license_agreement_party_name_original"]
    fixed_party = data["parties"]["license_agreement_party_name_corrected"]
    action = cmm._fmt_long_date(data["action_date_iso"])
    agr = cmm._fmt_long_date(data["license_agreement_date_iso"])
    corr = cmm._fmt_long_date(data["license_correction_date_iso"])
    sec = data["license_section"]
    orig = _fmt_usd(data["license_payment_original_usd"])
    fixed = _fmt_usd(data["license_payment_corrected_usd"])
    return (
        f"\n\n**Supplemental matters (actions of {action}):**\n"
        f"The Sole Director reported that on **{action}**, the Corporation adopted **written board resolutions** "
        f"(filed with the Secretary as **standalone board resolutions** of even date) to (i) appoint **{appt}** as an "
        f"executive officer of the Corporation and remove **{rem}** as an executive officer, and (ii) ratify the "
        f"**Software License Agreement** between the Corporation and **{hippo}**, dated **{agr}**, and approve "
        f"**clerical corrections** effective **{corr}**, including changing the Corporation’s name as stated in that "
        f"agreement from **{orig_party}** to **{fixed_party}** and changing the payment amount in **Section {sec}** "
        f"from **{orig}** to **{fixed}**. The Sole Director confirmed that copies of such resolutions are on file "
        f"with the Secretary and cross-referenced in these minutes."
    )


def _hippo_q1_supplemental_business_review(data: dict) -> str:
    drs = data["parties"]["drs_legal_name"]
    orig_party = data["parties"]["license_agreement_party_name_original"]
    fixed_party = data["parties"]["license_agreement_party_name_corrected"]
    action = cmm._fmt_long_date(data["action_date_iso"])
    agr = cmm._fmt_long_date(data["license_agreement_date_iso"])
    corr = cmm._fmt_long_date(data["license_correction_date_iso"])
    sec = data["license_section"]
    orig = _fmt_usd(data["license_payment_original_usd"])
    fixed = _fmt_usd(data["license_payment_corrected_usd"])
    return (
        f"\n\n**Supplemental matters (actions of {action}):**\n"
        f"The Sole Director reported that on **{action}**, the Corporation adopted **written board resolutions** "
        f"(filed with the Secretary as **standalone board resolutions** of even date) accepting **clerical corrections** "
        f"to the **Software License Agreement** between the Corporation and **{drs}**, dated **{agr}**, effective **{corr}**, "
        f"including changing the licensor name from **{orig_party}** to **{fixed_party}** and changing the payment amount "
        f"in **Section {sec}** from **{orig}** to **{fixed}**. Copies of such resolutions are on file with the Secretary "
        f"and cross-referenced in these minutes."
    )


def _inject_after_business_review(base: str, supplement: str) -> str:
    """Append supplemental narrative after the III. Business Review paragraph(s)."""
    m = re.search(
        r"(\*\*III\. Business Review:\*\*\n)(.*?)(\n\n\*\*IV\. Resolution)",
        base,
        flags=re.DOTALL,
    )
    if not m:
        raise ValueError("Could not locate Business Review section in quarterly minutes template.")
    return base[: m.end(2)] + supplement + base[m.end(2) :]


def _inject_quarterly_incorporating_resolutions(
    co_name: str,
    base: str,
    year: int,
    quarter: str,
    incorporating_blocks: list[str],
) -> str:
    co = cmm.companies[co_name]
    eco = cmm._effective_co_for_board_meeting(co, co_name, year, quarter)
    date = cmm.quarterly_meeting_date_str(co, year, quarter)
    extra = list(incorporating_blocks) + cmm._stock_ledger_resolution_blocks_for_meeting(co_name, date)
    new_res = cmm._quarterly_resolutions_block(
        co_name, eco, co, year, quarter, extra_blocks=extra
    )
    return re.sub(
        r"\*\*IV\. Resolutions?:\*\*.*?(?=\n\*\*V\. Adjournment:\*\*)",
        new_res.rstrip() + "\n\n",
        base,
        count=1,
        flags=re.DOTALL,
    )


def _supplemental_quarterly_minutes(
    co_name: str,
    year: int,
    quarter: str,
    business_supplement: str,
    incorporating_blocks: list[str],
) -> str:
    base = cmm.generate_quarterly(co_name, year, quarter)
    base = _inject_after_business_review(base, business_supplement)
    return _inject_quarterly_incorporating_resolutions(
        co_name, base, year, quarter, incorporating_blocks
    )


def _write_docx(co_name: str, meet_iso: str, markdown: str, dest: str) -> None:
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    cmm.write_docx_from_minutes(markdown, dest, meet_iso, co_name)
    print(f"Wrote {dest}")


def write_all(output_root: str, data_path: str) -> None:
    data = _load_data(data_path)
    action_iso = data["action_date_iso"]

    drs_co = cmm.companies[DRS]
    hippo_co = cmm.companies[HIPPO]
    drs_q1_iso = cmm.quarterly_meeting_date_str(drs_co, YEAR, QUARTER)
    hippo_q1_iso = cmm.quarterly_meeting_date_str(hippo_co, YEAR, QUARTER)
    drs_safe = cmm.sanitize_company_name(DRS)
    hippo_safe = cmm.sanitize_company_name(HIPPO)

    drs_meetings = os.path.join(output_root, drs_safe, "meetings")
    hippo_meetings = os.path.join(output_root, hippo_safe, "meetings")
    os.makedirs(drs_meetings, exist_ok=True)
    os.makedirs(hippo_meetings, exist_ok=True)

    drs_signer_name, drs_signer_title = _drs_signer(data)

    # Standalone resolutions (January 15, 2023)
    drs_exec = _standalone_resolutions_markdown(
        DRS,
        action_iso,
        "Executive officer appointments and removals",
        _drs_executive_resolution_blocks(data),
        signer_name=drs_signer_name,
        signer_title=drs_signer_title,
    )
    drs_license = _standalone_resolutions_markdown(
        DRS,
        action_iso,
        "Software License Agreement with Hippo, Inc. — ratification and clerical corrections",
        _drs_license_correction_resolution_blocks(data),
        signer_name=drs_signer_name,
        signer_title=drs_signer_title,
    )
    hippo_license = _standalone_resolutions_markdown(
        HIPPO,
        action_iso,
        "Software License Agreement with DATA RECORD SCIENCE, INC. — acceptance of clerical corrections",
        _hippo_license_correction_resolution_blocks(data),
    )

    _write_docx(
        DRS,
        action_iso,
        drs_exec,
        os.path.join(
            drs_meetings,
            f"{drs_safe}_2023_01_15_executive_officer_board_resolutions.docx",
        ),
    )
    _write_docx(
        DRS,
        action_iso,
        drs_license,
        os.path.join(
            drs_meetings,
            f"{drs_safe}_2023_01_15_software_license_agreement_board_resolutions.docx",
        ),
    )
    _write_docx(
        HIPPO,
        action_iso,
        hippo_license,
        os.path.join(
            hippo_meetings,
            f"{hippo_safe}_2023_01_15_software_license_agreement_board_resolutions.docx",
        ),
    )

    drs_incorporating = [
        """**Written board resolutions (executive officers — January 15, 2023)**  
RESOLVED, that the Sole Director hereby approves and adopts the **separate written resolutions dated January 15, 2023** filed with the Secretary as **standalone board resolutions** (executive officer appointments and removals), which set forth those actions in full and are **not reproduced verbatim** in these minutes.""",
        """**Written board resolutions (Software License Agreement — January 15, 2023)**  
RESOLVED, that the Sole Director hereby approves and adopts the **separate written resolutions dated January 15, 2023** filed with the Secretary as **standalone board resolutions** (Software License Agreement with Hippo, Inc. and clerical corrections to party name and Section 2.2(a)), which set forth those actions in full and are **not reproduced verbatim** in these minutes.""",
    ]
    hippo_incorporating = [
        """**Written board resolutions (Software License Agreement correction — January 15, 2023)**  
RESOLVED, that the Sole Director hereby approves and adopts the **separate written resolutions dated January 15, 2023** filed with the Secretary as **standalone board resolutions** (acceptance of clerical corrections to the Software License Agreement with DATA RECORD SCIENCE, INC., including party name and Section 2.2(a)), which set forth those actions in full and are **not reproduced verbatim** in these minutes.""",
    ]

    drs_q1_md = _supplemental_quarterly_minutes(
        DRS, YEAR, QUARTER, _drs_q1_supplemental_business_review(data), drs_incorporating
    )
    hippo_q1_md = _supplemental_quarterly_minutes(
        HIPPO, YEAR, QUARTER, _hippo_q1_supplemental_business_review(data), hippo_incorporating
    )

    _write_docx(
        DRS,
        drs_q1_iso,
        drs_q1_md,
        os.path.join(
            drs_meetings,
            cmm.meeting_filename(DRS, drs_q1_iso, "quarterly_supplement", quarter=QUARTER),
        ),
    )
    _write_docx(
        HIPPO,
        hippo_q1_iso,
        hippo_q1_md,
        os.path.join(
            hippo_meetings,
            cmm.meeting_filename(HIPPO, hippo_q1_iso, "quarterly_supplement", quarter=QUARTER),
        ),
    )

    readme = os.path.join(output_root, "README.txt")
    with open(readme, "w", encoding="utf-8") as f:
        f.write(
            "Supplemental 2023 Q1 DRS / Hippo documents\n"
            "=========================================\n\n"
            "This folder supplements (does not replace) the main generated/ corpus.\n\n"
            f"January 15, 2023 standalone board resolutions and Q1 {YEAR} quarterly supplements:\n"
            f"  - {drs_safe}/meetings/\n"
            f"  - {hippo_safe}/meetings/\n\n"
            f"DRS Q1 governance meeting date (registry schedule): {drs_q1_iso}\n"
            f"Hippo Q1 governance meeting date (registry schedule): {hippo_q1_iso}\n"
        )
    print(f"Wrote {readme}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write supplemental 2023 Q1 DRS/Hippo minutes (separate from generated/)."
    )
    parser.add_argument(
        "--output-root",
        default=_DEFAULT_OUTPUT,
        help=f"Output folder (default: {_DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--data",
        default=_DEFAULT_DATA,
        help=f"JSON facts file (default: {_DEFAULT_DATA})",
    )
    args = parser.parse_args()
    write_all(os.path.abspath(args.output_root), os.path.abspath(args.data))


if __name__ == "__main__":
    main()
