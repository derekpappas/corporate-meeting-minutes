#!/usr/bin/env python3
"""Fill `templates/share_certificate_template.svg` from `data/stock_ledgers/*.json`.

Reads officer / authorized-share hints from `corporate_meeting_minutes.company_information` when present.
Optional per-ledger overrides:

- `total_authorized_shares` (int): formatted with grouping commas for the certificate face.
- `certificate_signatories`: `{"president": "...", "secretary": "...", "treasurer": "..."}`

Usage (repo root):

  python scripts/render_stock_certificates.py
  python scripts/render_stock_certificates.py --ledger data/stock_ledgers/hippo.json
  python scripts/render_stock_certificates.py --pdf   # requires rsvg-convert on PATH

Output filenames: `{Company}_{YYYY-MM-DD}_{Shareholder}_{CertificateNo}.svg`
(underscores replace unsafe characters; `no_issue_date` if `issue_date` is null.)
"""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import date
import subprocess
import sys
import xml.sax.saxutils as saxutils
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from corporate_meeting_minutes import company_information  # noqa: E402

_JURISDICTION_LABEL = {
    "DE": "Delaware",
    "WY": "Wyoming",
    "CA": "California",
    "NY": "New York",
}


def _norm_name(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().rstrip(".")).lower()


def _lookup_company_config(ledger_company_name: str) -> dict | None:
    target = _norm_name(ledger_company_name)
    for key, co in company_information.items():
        if _norm_name(key) == target:
            return co
        disp = co.get("minutes_display_name")
        if disp and _norm_name(str(disp)) == target:
            return co
    return None


def _format_int_grouped(n: int) -> str:
    return f"{n:,}"


def int_to_english_words(n: int) -> str:
    """Cardinal words for non-negative integers (e.g. share counts)."""
    if n < 0:
        raise ValueError("only non-negative integers supported")
    if n == 0:
        return "zero"
    if n >= 10**15:
        return _format_int_grouped(n)

    ones = [
        "",
        "one",
        "two",
        "three",
        "four",
        "five",
        "six",
        "seven",
        "eight",
        "nine",
        "ten",
        "eleven",
        "twelve",
        "thirteen",
        "fourteen",
        "fifteen",
        "sixteen",
        "seventeen",
        "eighteen",
        "nineteen",
    ]
    tens = [
        "",
        "",
        "twenty",
        "thirty",
        "forty",
        "fifty",
        "sixty",
        "seventy",
        "eighty",
        "ninety",
    ]
    scales = [
        (10**12, "trillion"),
        (10**9, "billion"),
        (10**6, "million"),
        (10**3, "thousand"),
    ]

    def under_thousand(x: int) -> str:
        if x == 0:
            return ""
        if x < 20:
            return ones[x]
        if x < 100:
            t, r = divmod(x, 10)
            return tens[t] + (f"-{ones[r]}" if r else "")
        h, r = divmod(x, 100)
        return ones[h] + " hundred" + (" " + under_thousand(r) if r else "")

    parts: list[str] = []
    rem = n
    for scale, name in scales:
        if rem >= scale:
            count, rem = divmod(rem, scale)
            w = under_thousand(count).strip()
            if w:
                parts.append(f"{w} {name}")
    if rem:
        parts.append(under_thousand(rem))
    return " ".join(parts).replace("  ", " ").strip()


def _par_display(ledger: dict) -> str:
    raw = ledger.get("par_value_per_share_usd")
    if raw is None:
        return "$0.0001"
    try:
        v = float(raw)
    except (TypeError, ValueError):
        return str(raw)
    if abs(v - round(v)) < 1e-12:
        s = f"{v:.6f}".rstrip("0").rstrip(".")
        if s == "":
            s = "0"
        return f"${s}"
    return f"${v}"


def _authorized_shares_display(ledger: dict, co: dict | None) -> str:
    ta = ledger.get("total_authorized_shares")
    if isinstance(ta, int):
        return _format_int_grouped(ta)
    if isinstance(ta, str) and ta.strip():
        return ta.strip()
    if co:
        sa = co.get("shares_authorized")
        if isinstance(sa, str) and sa.strip():
            return sa.strip()
    print(
        f"warning: no authorized share count for {ledger.get('company_legal_name')!r}; "
        "using 10,000,000 — set ledger.total_authorized_shares or company_information.shares_authorized",
        file=sys.stderr,
    )
    return "10,000,000"


def _officer_titles_map(co: dict) -> dict[str, str]:
    """Lowercased title -> person name from organizational_officers_elected."""
    out: dict[str, str] = {}
    for row in co.get("organizational_officers_elected") or []:
        name = str(row.get("name") or "").strip()
        if not name:
            continue
        titles = row.get("titles")
        if titles:
            title_list = [str(t) for t in titles]
        else:
            t = row.get("title")
            title_list = [str(t)] if t else []
        for t in title_list:
            out[t.strip().lower()] = name
    return out


def _is_president_title(low: str) -> bool:
    return "president" in low and "vice" not in low


def _signatories(ledger: dict, co: dict | None) -> tuple[str, str, str]:
    ovr = ledger.get("certificate_signatories")
    if isinstance(ovr, dict):
        p = str(ovr.get("president") or "").strip()
        s = str(ovr.get("secretary") or "").strip()
        t = str(ovr.get("treasurer") or "").strip()
        if p and s and t:
            return p, s, t

    if not co:
        print(
            f"warning: no company_information match for {ledger.get('company_legal_name')!r}; "
            "using placeholder signatories",
            file=sys.stderr,
        )
        return "—", "—", "—"

    by_title = _officer_titles_map(co)
    pres = next((by_title[k] for k in by_title if _is_president_title(k)), "")
    sec = next(
        (by_title[k] for k in by_title if "secretary" in k and "assistant" not in k),
        "",
    )
    treas = next((by_title[k] for k in by_title if "treasurer" in k), "")

    officers = co.get("officers") or {}
    if isinstance(officers, dict):
        if not pres:
            pres = str(officers.get("President") or officers.get("CEO") or "").strip()
        if not sec:
            sec = str(officers.get("Secretary") or "").strip()
        if not treas:
            treas = str(officers.get("Treasurer") or "").strip()

    chair = str(co.get("board_meeting_chair_name") or "").strip()
    if not pres:
        pres = chair or "—"
    if not sec:
        sec = chair or pres
    if not treas:
        treas = sec or pres
    return pres, sec, treas


def _state_label(ledger: dict, co: dict | None) -> str:
    j = str(ledger.get("jurisdiction") or "").strip().upper()
    if j in _JURISDICTION_LABEL:
        return _JURISDICTION_LABEL[j]
    if co:
        ij = str(co.get("incorporation_jurisdiction") or co.get("jurisdiction") or "").strip().upper()
        if ij in _JURISDICTION_LABEL:
            return _JURISDICTION_LABEL[ij]
    return j or "—"


def _fill_template(template: str, mapping: dict[str, str]) -> str:
    out = template
    for k, v in mapping.items():
        out = out.replace("{{" + k + "}}", saxutils.escape(v))
    if "{{" in out and "}}" in out:
        left = [m.group(1) for m in re.finditer(r"\{\{([A-Z_]+)\}\}", out)]
        if left:
            print(f"warning: unfilled placeholders: {left}", file=sys.stderr)
    return out


def _slug_from_ledger_path(p: Path) -> str:
    return p.stem


def _safe_filename_component(s: str, max_len: int = 96) -> str:
    """Filesystem-safe fragment; keeps Unicode letters (e.g. names), normalizes punctuation."""
    t = re.sub(r"[^\w.\-]+", "_", s.strip(), flags=re.UNICODE)
    t = re.sub(r"_+", "_", t).strip("_")
    if len(t) > max_len:
        t = t[:max_len].rstrip("_")
    return t or "unknown"


def _issue_date_slug_for_filename(entry: dict) -> str:
    raw = str(entry.get("issue_date") or "").strip()[:10]
    if len(raw) == 10:
        try:
            date.fromisoformat(raw)
            return raw
        except ValueError:
            pass
    return "no_issue_date"


def _certificate_output_stem(company_name: str, entry: dict, cert_no: str, shareholder: str) -> str:
    """{company}_{YYYY-MM-DD}_{owner}_{cert_no} — certificate # suffix keeps multiple lines distinct."""
    parts = [
        _safe_filename_component(company_name),
        _issue_date_slug_for_filename(entry),
        _safe_filename_component(shareholder),
        _safe_filename_component(cert_no),
    ]
    stem = "_".join(parts)
    if len(stem) > 200:
        stem = stem[:200].rstrip("_")
    return stem or "certificate"


def render_ledger(
    ledger_path: Path,
    template: str,
    out_dir: Path,
    write_pdf: bool,
) -> list[Path]:
    with open(ledger_path, encoding="utf-8") as f:
        ledger = json.load(f)

    company_name = str(ledger.get("company_legal_name") or "").strip()
    if not company_name:
        raise ValueError(f"{ledger_path}: missing company_legal_name")

    co = _lookup_company_config(company_name)
    pres, sec, treas = _signatories(ledger, co)

    written: list[Path] = []
    slug = _slug_from_ledger_path(ledger_path)
    company_out = out_dir / slug / "stock_certificates"
    company_out.mkdir(parents=True, exist_ok=True)

    for entry in ledger.get("ledger_entries") or []:
        if not isinstance(entry, dict):
            continue
        cert_no = str(entry.get("certificate_number") or "").strip()
        shareholder = str(entry.get("shareholder") or "").strip()
        shares = entry.get("shares")
        if not cert_no or not shareholder or not isinstance(shares, int):
            print(f"warning: skip incomplete entry in {ledger_path.name}: {entry!r}", file=sys.stderr)
            continue

        mapping = {
            "CERT_NUMBER": cert_no,
            "SHARE_COUNT": _format_int_grouped(shares),
            "SHARE_COUNT_WORDS": int_to_english_words(shares).title(),
            "COMPANY_NAME": company_name,
            "STATE_OF_INC": _state_label(ledger, co),
            "TOTAL_AUTH_SHARES": _authorized_shares_display(ledger, co),
            "PAR_VALUE": _par_display(ledger),
            "HOLDER_NAME": shareholder,
            "PRESIDENT_NAME": pres,
            "SECRETARY_NAME": sec,
            "TREASURER_NAME": treas,
            "SELLER_NAME": shareholder,
        }
        svg_body = _fill_template(template, mapping)
        base = _certificate_output_stem(company_name, entry, cert_no, shareholder)
        svg_path = company_out / f"{base}.svg"
        with open(svg_path, "w", encoding="utf-8") as f:
            f.write(svg_body)
        written.append(svg_path)

        if write_pdf:
            pdf_path = svg_path.with_suffix(".pdf")
            try:
                subprocess.run(
                    ["rsvg-convert", "-f", "pdf", "-o", str(pdf_path), str(svg_path)],
                    check=True,
                    capture_output=True,
                    text=True,
                )
                written.append(pdf_path)
            except FileNotFoundError:
                print("error: rsvg-convert not found; install librsvg or omit --pdf", file=sys.stderr)
                raise
            except subprocess.CalledProcessError as e:
                print(e.stderr or e.stdout or str(e), file=sys.stderr)
                raise

    return written


def main() -> None:
    ap = argparse.ArgumentParser(description="Render stock certificates from SVG template + ledgers.")
    ap.add_argument(
        "--ledger",
        action="append",
        type=Path,
        help="Stock ledger JSON (repeatable). Default: all data/stock_ledgers/*.json",
    )
    ap.add_argument(
        "--out",
        type=Path,
        default=_REPO_ROOT / "generated",
        help="Output root (default: generated/; writes under <safe>/stock_certificates/ per ledger)",
    )
    ap.add_argument("--pdf", action="store_true", help="Also write PDF via rsvg-convert")
    args = ap.parse_args()

    template_path = _REPO_ROOT / "templates" / "share_certificate_template.svg"
    with open(template_path, encoding="utf-8") as f:
        template = f.read()

    if args.ledger:
        paths = [p if p.is_absolute() else _REPO_ROOT / p for p in args.ledger]
    else:
        ledgers_dir = _REPO_ROOT / "data" / "stock_ledgers"
        paths = sorted(ledgers_dir.glob("*.json"))

    if not paths:
        print("no ledger files found", file=sys.stderr)
        sys.exit(1)

    out_dir = args.out if args.out.is_absolute() else _REPO_ROOT / args.out
    all_written: list[Path] = []
    for p in paths:
        if not p.is_file():
            print(f"missing: {p}", file=sys.stderr)
            sys.exit(1)
        all_written.extend(render_ledger(p, template, out_dir, args.pdf))

    print(f"wrote {len(all_written)} file(s) under {out_dir}")


if __name__ == "__main__":
    main()
