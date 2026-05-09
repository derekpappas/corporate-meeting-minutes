#!/usr/bin/env python3
"""Scan audit_text extracts for (1) date/chronology issues and (2) DGCL vs jurisdiction mismatches.

Reads: audit_text/generated__<folder>__<stem>.docx.txt
Uses: corporate_meeting_minutes.company_information + schedule helpers + stock ledgers

Usage (repo root):
  poetry run python scripts/audit_corpus_chronology_dgcl.py
  poetry run python scripts/audit_corpus_chronology_dgcl.py --out audit_reports/corpus_chronology_dgcl_audit.md
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

import corporate_meeting_minutes as cmm  # noqa: E402

# audit_text folder name (sanitize_company_name) -> registry key in company_information
_FOLDER_TO_CO: dict[str, str] = {}
for _name, _co in cmm.company_information.items():
    safe = cmm.sanitize_company_name(_name)
    _FOLDER_TO_CO[safe] = _name

_ISO = re.compile(r"\b(\d{4}-\d{2}-\d{2})\b")
_STEM_DATE = re.compile(r"^(\d{4})_(\d{2})_(\d{2})_(.+)$")


def _parse_audit_filename(path: Path) -> tuple[str, str, date | None, str] | None:
    """Return (folder, stem, meeting_date_or_none, kind_suffix) or None if not a dated meeting extract."""
    name = path.name
    if not name.startswith("generated__") or not name.endswith(".docx.txt"):
        return None
    core = name[len("generated__") : -len(".docx.txt")]
    if "__" not in core:
        return None
    folder, stem = core.split("__", 1)
    if folder not in _FOLDER_TO_CO:
        return None
    prefix = folder + "_"
    if not stem.startswith(prefix):
        return None
    tail = stem[len(prefix) :]
    m = _STEM_DATE.match(tail)
    if not m:
        return folder, stem, None, tail
    y, mo, d, rest = m.groups()
    try:
        dt = date(int(y), int(mo), int(d))
    except ValueError:
        return folder, stem, None, rest
    return folder, stem, dt, rest


def _primary_date_from_body(text: str) -> str | None:
    for line in text.splitlines()[:80]:
        s = line.strip()
        if s.startswith("Date:") or s.startswith("Date of Meeting:") or s.startswith("**Date:**"):
            m = _ISO.search(s)
            if m:
                return m.group(1)
        if s.startswith("**Date of Meeting:**"):
            m = _ISO.search(s)
            if m:
                return m.group(1)
    m = _ISO.search("\n".join(text.splitlines()[:25]))
    return m.group(1) if m else None


def _dgcl_hits(text: str) -> list[str]:
    out: list[str] = []
    for i, line in enumerate(text.splitlines(), 1):
        if "DGCL" in line or "Delaware General Corporation Law" in line:
            out.append(f"L{i}: {line.strip()[:200]}")
    return out


def _load_stock_ledgers() -> list[dict]:
    d = _REPO / "data" / "stock_ledgers"
    rows: list[dict] = []
    if not d.is_dir():
        return rows
    for p in sorted(d.glob("*.json")):
        try:
            with open(p, encoding="utf-8") as f:
                rows.append(json.load(f))
        except (OSError, json.JSONDecodeError):
            continue
    return rows


def _norm_ledger_co(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().rstrip(".")).lower()


def _ledger_co_to_registry(legal: str) -> str | None:
    t = _norm_ledger_co(legal)
    for k, co in cmm.company_information.items():
        if _norm_ledger_co(k) == t:
            return k
        md = co.get("minutes_display_name")
        if md and _norm_ledger_co(str(md)) == t:
            return k
    return None


def run_audit() -> tuple[str, list[str], list[str]]:
    """Return (markdown_report, errors, warnings)."""
    audit_dir = _REPO / "audit_text"
    errors: list[str] = []
    warnings: list[str] = []
    lines: list[str] = []

    lines.append("# Corpus chronology and DGCL audit")
    lines.append("")
    lines.append(
        "Automated scan of `audit_text/generated__*__*.docx.txt` plus schedule/stock-ledger checks. "
        "Review flagged items with counsel; false positives are possible (e.g. narrative mentions of other dates)."
    )
    lines.append("")

    # --- Filename vs body date ---
    lines.append("## 1. Filename date vs meeting header date")
    lines.append("")
    mismatches = 0
    if audit_dir.is_dir():
        for path in sorted(audit_dir.glob("generated__*.docx.txt")):
            if "all_meetings_book" in path.name:
                continue
            parsed = _parse_audit_filename(path)
            if not parsed or parsed[2] is None:
                continue
            folder, _stem, file_dt, _rest = parsed
            try:
                body = path.read_text(encoding="utf-8")
            except OSError:
                continue
            body_iso = _primary_date_from_body(body)
            if not body_iso:
                warnings.append(f"No header Date found: {path.name}")
                continue
            if body_iso != file_dt.isoformat():
                mismatches += 1
                errors.append(f"Date mismatch {path.name}: filename {file_dt.isoformat()} vs body {body_iso}")
                lines.append(f"- **MISMATCH** `{path.name}`: file name **{file_dt.isoformat()}**, body **{body_iso}**")
    if mismatches == 0:
        lines.append("- No mismatches found (dated meeting extracts only).")
    lines.append("")

    # --- Quarterly ordering per company-year (from filenames) ---
    lines.append("## 2. Quarterly sequence within each calendar year (filenames)")
    lines.append("")
    by_co_yq: dict[tuple[str, int], list[tuple[str, date]]] = defaultdict(list)
    if audit_dir.is_dir():
        for path in sorted(audit_dir.glob("generated__*.docx.txt")):
            if "all_meetings_book" in path.name:
                continue
            parsed = _parse_audit_filename(path)
            if not parsed or parsed[2] is None:
                continue
            folder, _stem, file_dt, rest = parsed
            co = _FOLDER_TO_CO.get(folder)
            if not co:
                continue
            mq = re.search(r"q_([1-4])", rest.lower())
            if mq:
                q = f"Q{mq.group(1)}"
                by_co_yq[(co, file_dt.year)].append((q, file_dt))

    for (co, year), pairs in sorted(by_co_yq.items()):
        pairs_sorted = sorted(pairs, key=lambda x: x[1])
        order = [p[0] for p in pairs_sorted]
        expected = ["Q1", "Q2", "Q3", "Q4"]
        seen = [x for x in order if x in expected]
        if len(seen) >= 2:
            idxs = [expected.index(x) for x in seen]
            if idxs != sorted(idxs):
                errors.append(f"Quarter order anomaly {co} {year}: {pairs_sorted}")
                lines.append(f"- **ANOMALY** {co} {year}: quarter order {seen} dates {[str(p[1]) for p in pairs_sorted]}")
    if not any("ANOMALY" in x for x in lines[-20:]):
        lines.append("- No quarter-order anomalies detected from filenames.")
    lines.append("")

    # --- Generator: special <= annual, org after filing ---
    lines.append("## 3. Schedule rules (generator truth, all registry companies)")
    lines.append("")
    for co_name, co in sorted(cmm.company_information.items()):
        j = cmm._jurisdiction(co)
        start = int(co.get("minutes_start_year", co.get("inc_year", 2022)))
        last = max(start, cmm._board_series_last_calendar_year(co, start))
        for year in range(start, last + 1):
            ann = cmm.annual_meeting_date_str(co, year)
            spe = cmm.board_special_meeting_date_str(co, year)
            if spe > ann:
                errors.append(f"{co_name} {year}: special {spe} after annual {ann}")
                lines.append(f"- **ERROR** {co_name} {year}: special board **{spe}** > annual board **{ann}**")
            org = cmm.organizational_meeting_date_str(co, year)
            filed = cmm._incorporation_filed_date_iso(co)
            if org and filed:
                if org < filed:
                    errors.append(f"{co_name}: org {org} before filing {filed}")
                    lines.append(f"- **ERROR** {co_name}: organizational **{org}** before incorporation filing **{filed}**")
    if not any("ERROR" in x for x in lines[-30:]):
        lines.append("- Special ≤ annual and organizational ≥ filing (where both dates exist): **OK**.")
    lines.append("")

    # --- Stock ledger issue date vs first board meeting after ---
    lines.append("## 4. Stock ledger `issue_date` vs first board meeting after purchase")
    lines.append("")
    for ledger in _load_stock_ledgers():
        legal = str(ledger.get("company_legal_name") or "").strip()
        co_name = _ledger_co_to_registry(legal)
        if not co_name:
            warnings.append(f"Ledger company not in registry: {legal}")
            continue
        co = cmm.company_information[co_name]
        for ent in ledger.get("ledger_entries") or []:
            if not isinstance(ent, dict):
                continue
            raw = ent.get("issue_date")
            if raw is None or str(raw).strip() == "":
                lines.append(
                    f"- **SKIP** {legal} cert {ent.get('certificate_number')!r}: no `issue_date` (minutes resolution not indexed)."
                )
                continue
            try:
                d_issue = date.fromisoformat(str(raw).strip()[:10])
            except ValueError:
                warnings.append(f"Bad issue_date {raw!r} in {legal}")
                continue
            slot = cmm._first_board_meeting_strictly_after(co_name, co, d_issue)
            if not slot:
                warnings.append(f"No board meeting after {d_issue} for {legal} {ent.get('certificate_number')}")
                lines.append(
                    f"- **WARN** {legal} **{ent.get('certificate_number')}** issue {d_issue}: no scheduled board meeting found after that date."
                )
                continue
            meeting_iso, kind = slot
            lines.append(
                f"- {legal} **{ent.get('certificate_number')}** issue **{d_issue}** → first board slot **{meeting_iso}** ({kind})."
            )
    lines.append("")

    # --- DGCL / jurisdiction ---
    lines.append("## 5. DGCL references in extracted text (non–Delaware-domiciled companies)")
    lines.append("")
    for folder, co_name in sorted(_FOLDER_TO_CO.items()):
        co = cmm.company_information[co_name]
        if cmm._jurisdiction(co) == "DE":
            continue
        hits_total = 0
        if audit_dir.is_dir():
            for path in sorted(audit_dir.glob(f"generated__{folder}__*.docx.txt")):
                try:
                    text = path.read_text(encoding="utf-8")
                except OSError:
                    continue
                h = _dgcl_hits(text)
                if h:
                    hits_total += len(h)
                    lines.append(f"### `{path.name}` ({co_name}, jurisdiction **{cmm._jurisdiction(co)}**)")
                    for ln in h[:12]:
                        lines.append(f"- {ln}")
                    if len(h) > 12:
                        lines.append(f"- … ({len(h) - 12} more lines)")
                    lines.append("")
                    warnings.append(f"DGCL/Delaware law text in non-DE extract: {path.name} ({len(h)} lines)")
        if hits_total == 0:
            lines.append(f"- **{co_name}** (`{folder}`): no DGCL / “Delaware General Corporation Law” string hits in audit extracts.")
            lines.append("")

    lines.append("## 6. Delaware companies: spot-check for Wyoming statute strings in extracts")
    lines.append("")
    wy_pat = re.compile(r"W\.S\.\s*1977|Wyoming Business Corporation Act", re.I)
    for folder, co_name in sorted(_FOLDER_TO_CO.items()):
        co = cmm.company_information[co_name]
        if cmm._jurisdiction(co) != "DE":
            continue
        bad_files = []
        if audit_dir.is_dir():
            for path in sorted(audit_dir.glob(f"generated__{folder}__*.docx.txt")):
                if "all_meetings_book" in path.name:
                    continue
                try:
                    text = path.read_text(encoding="utf-8")
                except OSError:
                    continue
                if wy_pat.search(text):
                    bad_files.append(path.name)
        if bad_files:
            for bf in bad_files[:8]:
                errors.append(f"WY statute string in DE company file: {bf}")
                lines.append(f"- **FLAG** `{bf}` ({co_name}): contains Wyoming statute phrasing — verify intent.")
        else:
            lines.append(f"- {co_name}: no Wyoming statute phrase hits in per-meeting extracts.")
    lines.append("")

    lines.append("## 7. Next steps")
    lines.append("")
    lines.append("- Re-run `poetry run python corporate_meeting_minutes.py --write-calendars --strict-calendars` for cross-company same-slot conflicts.")
    lines.append("- After regenerating `.docx`, run `poetry run python scripts/extract_audit_text.py` so this audit tracks current output.")
    lines.append("")

    summary = f"**Summary:** {len(errors)} error-line(s), {len(warnings)} warning-line(s)."
    lines.insert(2, summary)
    lines.insert(3, "")

    return "\n".join(lines), errors, warnings


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=_REPO / "audit_reports" / "corpus_chronology_dgcl_audit.md",
        help="Output markdown path",
    )
    args = ap.parse_args()
    report, errors, warnings = run_audit()
    out = args.out if args.out.is_absolute() else _REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(report, encoding="utf-8")
    print(f"Wrote {out}")
    print(f"errors={len(errors)} warnings={len(warnings)}")
    if errors:
        for e in errors[:25]:
            print(f"  ERROR: {e}", file=sys.stderr)
        if len(errors) > 25:
            print(f"  … and {len(errors) - 25} more", file=sys.stderr)


if __name__ == "__main__":
    main()
