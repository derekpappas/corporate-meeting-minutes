#!/usr/bin/env python3
"""Assemble `generated/review_pack/` in two trees:

- **sample/** — one Delaware company (**Hippo, Inc.**), one file per meeting / instrument type.
- **all/** — cross-company snapshot: one example per doc type (any company), all compiled book PDFs, audits, calendars, etc.

Copies only (does not move). Run after generating minutes (and after calendars if you copy them into the pack):

  poetry run python corporate_meeting_minutes.py --output-root generated --extract-audit-text --write-examples --write-master-book
  poetry run python corporate_meeting_minutes.py --write-calendars
  poetry run python scripts/build_review_pack.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
_GEN = _REPO / "generated"
_SHARED_GEN_BOOKS = _GEN / "books"
_OUT = _GEN / "review_pack"


def _is_shared_generated_books(p: Path) -> bool:
    """True for ``generated/books/*`` (master book only); per-company books live under ``generated/<co>/``."""
    try:
        return p.parent.resolve() == _SHARED_GEN_BOOKS.resolve()
    except OSError:
        return False

# Single-company sample: Delaware, full written-consent / board cycle (no multi-stockholder pack).
# Registry key in `company_information` (display name in minutes is "Hippo, Inc.").
_SAMPLE_CO_NAME = "Hippo, Inc"
_SAMPLE_DISPLAY = "Hippo, Inc."
_SAMPLE_JURISDICTION = "Delaware (DE)"


def _pick_first(pattern: str, root: Path) -> Path | None:
    found = sorted(root.rglob(pattern))
    return found[0] if found else None


def _copy(src: Path | None, dst: Path) -> bool:
    if src is None or not src.is_file():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _root_readme() -> str:
    return f"""Review pack

sample/  — One U.S. state and one company only: **{_SAMPLE_DISPLAY}** ({_SAMPLE_JURISDICTION}).
           One example per meeting or instrument type (organizational through compiled book).

all/     — Broader review set: examples drawn from any registry company where needed (e.g. SurveyTeams
           stockholder-only types), all compiled minute-book PDFs, audit mirrors, calendars, data snippets.

Rebuild:
  poetry run python scripts/build_review_pack.py

.gitignore may ignore *.docx / *.pdf; files remain on disk under generated/review_pack/.
"""


def _sample_readme() -> str:
    return f"""Single-company sample

Company: **{_SAMPLE_DISPLAY}**
Domicile (for this pack): **{_SAMPLE_JURISDICTION}**

docx/ — numbered roughly in calendar order for one recent cycle year (organizational uses incorporation year).
pdf/  — Hippo compiled minute book only (if generated).

Other folders are optional context (audit extract, stock certificate for this company, template).
"""


def build_sample_pack(out: Path) -> tuple[int, int]:
    """Return (docx_count, other_counts_approx)."""
    if str(_REPO) not in sys.path:
        sys.path.insert(0, str(_REPO))
    import corporate_meeting_minutes as cmm  # noqa: E402

    name = _SAMPLE_CO_NAME
    co = cmm.companies[name]
    safe = cmm.sanitize_company_name(name)
    co_dir = _GEN / safe
    docx_out = out / "docx"
    pdf_out = out / "pdf"
    tx_out = out / "audit_text"
    cert_out = out / "stock_certificates"
    tpl_out = out / "templates"

    n_docx = 0
    if not co_dir.is_dir():
        (out / "MISSING_GENERATED_DIR.txt").write_text(
            f"Expected generated/{safe}/ — run corporate_meeting_minutes.py first.\n", encoding="utf-8"
        )
        return 0, 0

    years = (2022, 2023, 2024, 2025, 2026)
    start = co.get("minutes_start_year", co["inc_year"])
    applicable = [y for y in years if y >= start]
    y_last = applicable[-1]

    specs: list[tuple[str, str]] = []

    org_iso = cmm.organizational_meeting_date_str(co, co["inc_year"])
    if org_iso:
        specs.append(
            ("01_organizational.docx", cmm.meeting_filename(name, org_iso, "organizational", ext="docx"))
        )

    q1_iso = cmm.quarterly_meeting_date_str(co, y_last, "Q1")
    specs.append(
        (
            "02_quarterly_Q1.docx",
            cmm.meeting_filename(name, q1_iso, "quarterly", quarter="Q1", ext="docx"),
        )
    )

    sp_iso = cmm.board_special_meeting_date_str(co, y_last)
    specs.append(
        (
            "03_yearly_special_meeting.docx",
            cmm.meeting_filename(name, sp_iso, "yearly_special_meeting", ext="docx"),
        )
    )

    ann_iso = cmm.annual_meeting_date_str(co, y_last)
    specs.append(("04_agm.docx", cmm.meeting_filename(name, ann_iso, "agm", ext="docx")))

    specs.append(
        (
            "06_written_consent_in_lieu_of_annual_meeting.docx",
            cmm.meeting_filename(name, ann_iso, "written_consent_in_lieu_of_annual_meeting", ext="docx"),
        )
    )
    specs.append(
        (
            "07_waiver_of_notice_board_meetings.docx",
            cmm.meeting_filename(name, ann_iso, "waiver_of_notice_board_meetings", ext="docx"),
        )
    )

    meetings_dir = co_dir / "meetings"

    for dst_name, stem in specs:
        if dst_name.startswith("01_") and not org_iso:
            continue
        src = meetings_dir / stem
        if _copy(src, docx_out / dst_name):
            n_docx += 1

    for y in reversed(applicable):
        ann_y = cmm.annual_meeting_date_str(co, y)
        add_stem = cmm.meeting_filename(name, ann_y, "agm_operating_addendum", ext="docx")
        add_src = meetings_dir / add_stem
        if add_src.is_file():
            if _copy(add_src, docx_out / "05_agm_operating_addendum.docx"):
                n_docx += 1
            break

    book_docx = co_dir / f"{safe}_all_meetings_book.docx"
    if _copy(book_docx, docx_out / "08_all_meetings_book.docx"):
        n_docx += 1
    _copy(co_dir / f"{safe}_all_meetings_book.pdf", pdf_out / f"{safe}_all_meetings_book.pdf")

    # Audit text: one Hippo AGM extract (latest year in filename)
    at_root = _REPO / "audit_text"
    if at_root.is_dir():
        hippo_agm = sorted(at_root.glob(f"generated__{safe}__{safe}_*_agm.docx.txt"))
        hippo_agm = [p for p in hippo_agm if "operating_addendum" not in p.name]
        if _copy(hippo_agm[-1] if hippo_agm else None, tx_out / "hippo_agm.docx.txt"):
            pass

    svg_dir = _GEN / "stock_certificates" / safe
    if svg_dir.is_dir():
        svgs = sorted(svg_dir.glob("*.svg"))
        if svgs:
            _copy(svgs[0], cert_out / svgs[0].name)
    _copy(_REPO / "templates" / "share_certificate_template.svg", tpl_out / "share_certificate_template.svg")

    (out / "README.txt").write_text(_sample_readme(), encoding="utf-8")
    return n_docx, 0


def build_all_pack(out: Path) -> tuple[int, int, int, int]:
    """Returns copied counts: docx, pdf, txt, cert."""
    docx_dir = out / "docx"
    pdf_dir = out / "pdf"
    tx_dir = out / "audit_text"
    cert_dir = out / "stock_certificates"
    tpl_dir = out / "templates"
    ar_dir = out / "audit_reports"
    data_dir = out / "data"

    docx_specs = [
        ("sample_organizational.docx", "*_organizational.docx"),
        ("sample_agm.docx", "*_agm.docx"),
        ("sample_agm_operating_addendum.docx", "*_agm_operating_addendum.docx"),
        ("sample_yearly_special_meeting.docx", "*_yearly_special_meeting.docx"),
        ("sample_written_consent_in_lieu_of_annual_meeting.docx", "*_written_consent_in_lieu_of_annual_meeting.docx"),
        ("sample_waiver_of_notice_board_meetings.docx", "*_waiver_of_notice_board_meetings.docx"),
        ("sample_quarterly_q1.docx", "*_q_1_quarterly.docx"),
        ("sample_annual_meeting_of_stockholders.docx", "*_annual_meeting_of_stockholders.docx"),
        ("sample_waiver_of_notice_annual_stockholder_meeting.docx", "*_waiver_of_notice_annual_stockholder_meeting.docx"),
        ("sample_notice_of_annual_stockholder_meeting.docx", "*_notice_of_annual_stockholder_meeting.docx"),
        (
            "sample_majority_stockholders_written_consent_ratification.docx",
            "*_majority_stockholders_written_consent_ratification_of_annual_board_actions.docx",
        ),
        ("sample_cap_table.docx", "*_cap_table.docx"),
        ("sample_stock_ledger.docx", "*_stock_ledger.docx"),
        ("sample_cap_table_carta_pulley.csv", "*_cap_table_carta_pulley.csv"),
    ]
    copied_docx = 0
    for dst_name, globpat in docx_specs:
        candidates = [
            p
            for p in _GEN.rglob(globpat)
            if not _is_shared_generated_books(p)
            and p.parent.name not in ("review_pack", "examples")
            and "review_pack" not in p.parts
        ]
        candidates.sort()
        if _copy(candidates[-1] if candidates else None, docx_dir / dst_name):
            copied_docx += 1

    books_d = _SHARED_GEN_BOOKS
    per_co_book_docx = sorted(
        p
        for p in _GEN.glob("*/*_all_meetings_book.docx")
        if p.parent.name != "books"
        and p.name != "all_companies_all_meetings_book.docx"
        and "review_pack" not in p.parts
        and "examples" not in p.parts
    )
    if _copy(per_co_book_docx[0] if per_co_book_docx else None, docx_dir / "sample_company_all_meetings_book.docx"):
        copied_docx += 1
    ac = books_d / "all_companies_all_meetings_book.docx"
    if books_d.is_dir() and _copy(ac if ac.is_file() else None, docx_dir / "sample_all_companies_all_meetings_book.docx"):
        copied_docx += 1

    copied_pdf = 0
    if books_d.is_dir():
        for p in sorted(books_d.glob("*.pdf")):
            if _copy(p, pdf_dir / p.name):
                copied_pdf += 1
    for p in sorted(
        q
        for q in _GEN.glob("*/*_all_meetings_book.pdf")
        if q.parent.name != "books"
        and q.name != "all_companies_all_meetings_book.pdf"
        and "review_pack" not in q.parts
        and "examples" not in q.parts
    ):
        if _copy(p, pdf_dir / p.name):
            copied_pdf += 1
    ex_pdf = _pick_first("*.pdf", _GEN / "examples")
    if ex_pdf and re.search(r"agm", ex_pdf.name, re.I):
        if _copy(ex_pdf, pdf_dir / f"example_{ex_pdf.name}"):
            copied_pdf += 1

    copied_txt = 0
    at_root = _REPO / "audit_text"
    if at_root.is_dir():
        agm_txts = sorted(at_root.glob("*_agm.docx.txt"))
        agm_txts = [p for p in agm_txts if "operating_addendum" not in p.name]
        if _copy(agm_txts[-1] if agm_txts else None, tx_dir / "sample_agm.docx.txt"):
            copied_txt += 1
        book_txts = sorted(at_root.glob("*_all_meetings_book.docx.txt"))
        if _copy(book_txts[-1] if book_txts else None, tx_dir / "sample_all_meetings_book.docx.txt"):
            copied_txt += 1

    copied_cert = 0
    svg = _pick_first("*.svg", _GEN / "stock_certificates")
    if svg and _copy(svg, cert_dir / svg.name):
        copied_cert += 1
    _copy(_REPO / "templates" / "share_certificate_template.svg", tpl_dir / "share_certificate_template.svg")

    for name in ("stock_ledgers/hippo.json", "share_subscription_transaction_templates.json"):
        p = _REPO / "data" / name
        if p.is_file():
            _copy(p, data_dir / name.replace("/", "_"))

    _copy(_REPO / "audit_reports" / "corpus_chronology_dgcl_audit.md", ar_dir / "corpus_chronology_dgcl_audit.md")
    _copy(
        _REPO / "doc" / "audit_reports" / "senior_counsel_audit_2022_2026.md",
        ar_dir / "senior_counsel_audit_2022_2026.md",
    )
    _copy(
        _REPO / "doc" / "audit_reports" / "senior_counsel_audit_2022_2026.pdf",
        pdf_dir / "senior_counsel_audit_2022_2026.pdf",
    )

    cal_root = _REPO / "calendars"
    if cal_root.is_dir():
        cal_out = out / "calendars"
        for name in ("unified_calendar.txt", "conflicts.txt"):
            p = cal_root / name
            if p.is_file():
                _copy(p, cal_out / name)

    (out / "README.txt").write_text(
        "all/ — cross-company review set (see parent README.txt).\n", encoding="utf-8"
    )
    return copied_docx, copied_pdf, copied_txt, copied_cert


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=_OUT,
        help="Output directory (default: generated/review_pack)",
    )
    args = ap.parse_args()
    out: Path = args.out if args.out.is_absolute() else _REPO / args.out

    if not _GEN.is_dir():
        print("error: generated/ missing — run corporate_meeting_minutes.py first", file=sys.stderr)
        sys.exit(1)

    if out.is_dir():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "README.txt").write_text(_root_readme(), encoding="utf-8")

    s_docx, _ = build_sample_pack(out / "sample")
    a_docx, a_pdf, a_txt, a_cert = build_all_pack(out / "all")

    print(f"Wrote {out}")
    print(f"  sample/ docx: {s_docx} ({_SAMPLE_DISPLAY} only)")
    print(f"  all/ docx: {a_docx}, pdf: {a_pdf}, audit_text: {a_txt}, stock svg: {a_cert}")


if __name__ == "__main__":
    main()
