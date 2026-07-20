"""Stock certificate rendering and cap-table / ledger alignment."""

from __future__ import annotations

import json
from pathlib import Path

import corporate_meeting_minutes as cmm


def test_certificate_output_slug_matches_minutes_folder() -> None:
    co_name = "TeamBoost.ai, Inc."
    ledger = {"company_legal_name": "TeamBoost.ai, Inc."}
    from scripts.render_stock_certificates import _company_output_slug

    slug = _company_output_slug(Path("data/stock_ledgers/teamboost.json"), ledger, co_name)
    assert slug == cmm.sanitize_company_name(co_name)


def test_cap_table_markdown_shows_authorized_and_issued_from_ledger() -> None:
    md = cmm.cap_table_document_markdown("Loki Sports Enterprises, Inc.", cmm.company_information["Loki Sports Enterprises, Inc."])
    assert "10,000,000" in md
    assert "Total authorized shares" in md
    assert "4,000,000" in md
    assert "Total issued shares (ledger entries)" in md
    assert "Derek E. Pappas" in md


def test_carta_pulley_rows_match_loki_ledger_entry() -> None:
    co_name = "Loki Sports Enterprises, Inc."
    co = cmm.company_information[co_name]
    rows = cmm.cap_table_carta_pulley_rows(co_name, co)
    derek = [r for r in rows if r["stakeholder_name"] == "Derek E. Pappas"]
    assert len(derek) == 1
    assert derek[0]["certificate_id"] == "LOKI-0001"
    assert derek[0]["shares"] == "4000000"
    assert derek[0]["issue_date"] == "2023-05-07"


def test_all_ledgers_have_derek_or_second_holder_entries() -> None:
    root = Path(__file__).resolve().parents[1] / "data" / "stock_ledgers"
    for path in sorted(root.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        entries = data.get("ledger_entries") or []
        assert entries, f"{path.name} has no ledger_entries"
        names = {str(e.get("shareholder") or "").strip() for e in entries if isinstance(e, dict)}
        assert "Derek E. Pappas" in names or "Mohamed Mohamed" in names, path.name
