"""Tests for `corporate_meeting_minutes` helpers and `generate_all` side effects."""

from __future__ import annotations

import os
import warnings
from datetime import date

import pytest

import corporate_meeting_minutes as cmm


def test_jurisdiction_defaults_to_de() -> None:
    assert cmm._jurisdiction({}) == "DE"
    assert cmm._jurisdiction({"jurisdiction": "  wy  "}) == "WY"


def test_corp_law_section_ref_de_vs_wy() -> None:
    de_co: dict = {"jurisdiction": "DE"}
    wy_co: dict = {"jurisdiction": "WY"}
    assert cmm._corp_law_section_ref(de_co, "228") == "DGCL §228"
    assert cmm._corp_law_section_ref(de_co, "141(e)") == "DGCL §141(e)"
    assert cmm._corp_law_section_ref(de_co, "141(i)") == "DGCL §141(i)"
    assert cmm._corp_law_section_ref(wy_co, "228") == "W.S. 1977 § 17-16-704"
    assert cmm._corp_law_section_ref(wy_co, "213") == "W.S. 1977 § 17-16-707"
    assert "DGCL" not in cmm._corp_law_section_ref(wy_co, "228")


def test_corporation_parenthetical_and_statute_name() -> None:
    assert "Delaware" in cmm._corporation_parenthetical({"jurisdiction": "DE"})
    assert "Wyoming" in cmm._corporation_parenthetical({"jurisdiction": "WY"})
    assert cmm._corporation_statute_name({"jurisdiction": "WY"}) == "Wyoming Business Corporation Act"


def test_reliance_standard_de_cites_141e() -> None:
    text = cmm.reliance_standard({"jurisdiction": "DE"})
    assert "141(e)" in text
    assert "DGCL" in text
    assert "Delaware General Corporation Law" not in text


def test_reliance_standard_wy_uses_wyoming_act_not_dgcl() -> None:
    text = cmm.reliance_standard({"jurisdiction": "WY"})
    assert "17-16-830" in text
    assert "Wyoming Business Corporation Act" in text
    assert "141(e)" not in text
    assert "DGCL" not in text


def test_warn_if_non_de_company_has_delaware_snippets_emits_warning() -> None:
    co = {
        "jurisdiction": "WY",
        "stockholder_consent_bylaws_acknowledgment": "Section 228 of the DGCL.",
    }
    with pytest.warns(UserWarning, match=r"Delaware/DGCL.*stockholder_consent_bylaws_acknowledgment"):
        cmm._warn_if_non_de_company_has_delaware_snippets("FixtureCo", co)


def test_warn_if_non_de_company_has_delaware_general_corporation_law() -> None:
    co = {
        "jurisdiction": "WY",
        "board_notice_waiver_bylaws_ref": "the Delaware General Corporation Law and bylaws",
    }
    with pytest.warns(UserWarning, match="board_notice_waiver_bylaws_ref"):
        cmm._warn_if_non_de_company_has_delaware_snippets("FixtureCo", co)


def test_warn_if_non_de_clean_no_warning() -> None:
    co = {"jurisdiction": "WY", "inc_year": 2023}
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        cmm._warn_if_non_de_company_has_delaware_snippets("CleanWY", co)


def test_warn_if_de_ignores_dgcl_in_strings() -> None:
    co = {
        "jurisdiction": "DE",
        "stockholder_consent_bylaws_acknowledgment": "DGCL §228",
    }
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        cmm._warn_if_non_de_company_has_delaware_snippets("DelawareCo", co)


def test_generate_all_restores_cwd_after_run(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    """`generate_all` must return the process cwd to its starting directory (see try/finally)."""
    fake_registry = {
        "SkipGen Co": {
            "minutes_start_year": 2100,
            "inc_year": 2100,
        }
    }
    monkeypatch.setattr(cmm, "companies", fake_registry, raising=False)
    monkeypatch.setattr(cmm, "company_information", fake_registry, raising=False)

    def _noop(*_args, **_kwargs) -> None:
        return None

    monkeypatch.setattr(cmm, "generate_annual", _noop)
    monkeypatch.setattr(cmm, "generate_special_meeting", _noop)
    monkeypatch.setattr(cmm, "generate_stockholder_side", _noop)
    monkeypatch.setattr(cmm, "generate_board_waiver_of_notice", _noop)
    monkeypatch.setattr(cmm, "generate_quarterly_summary", _noop)
    monkeypatch.setattr(cmm, "generate_company_all_meetings_book", _noop)

    out_root = tmp_path / "gen_out"
    monkeypatch.chdir(tmp_path)
    before = os.getcwd()
    cmm.generate_all(str(out_root.relative_to(tmp_path)), years=(2023,))
    assert os.getcwd() == before == str(tmp_path)


def test_development_centers_and_banking_differ_across_registry() -> None:
    """Regression: per-company lines avoid identical cross-corp boilerplate."""
    h = cmm.companies["Hippo, Inc"]
    d = cmm.companies["DATA RECORD SCIENCE, INC."]
    assert cmm.development_centers_line_for_company(h) != cmm.development_centers_line_for_company(d)
    assert h["primary_banking_institution"] != d["primary_banking_institution"]


def test_board_meeting_materials_acknowledgment_block() -> None:
    assert cmm.board_meeting_materials_acknowledgment_block({}) == ""
    assert cmm.board_meeting_materials_acknowledgment_block({"board_meeting_materials_acknowledgment_markdown": ""}) == ""
    assert cmm.board_meeting_materials_acknowledgment_block({"board_meeting_materials_acknowledgment_markdown": "   "}) == ""
    out = cmm.board_meeting_materials_acknowledgment_block(
        {"board_meeting_materials_acknowledgment_markdown": "The Sole Director reviewed **Exhibit C**."}
    )
    assert "Exhibit C" in out
    assert out.endswith("\n\n")


def test_board_remote_presence_and_reliance_helpers() -> None:
    assert "communications equipment" in cmm.board_remote_presence_paragraph({"virtual_ok": True})
    assert cmm.board_remote_presence_paragraph({"virtual_ok": True, "board_meeting_remote_presence_markdown": ""}) == ""
    custom = "The Sole Director joined by secure video in accordance with the bylaws."
    assert custom in cmm.board_remote_presence_paragraph(
        {"virtual_ok": True, "board_meeting_remote_presence_markdown": custom}
    )
    assert "141(e)" in cmm.board_director_reliance_paragraph({"jurisdiction": "DE"})
    assert cmm.board_director_reliance_paragraph({"jurisdiction": "DE", "board_meeting_reliance_markdown": ""}) == ""


def test_principal_address_note_for_wy_filing_address_de_corp() -> None:
    md = cmm.generate_agm("DATA RECORD SCIENCE, INC.", 2024)
    assert "**Address note:**" in md
    assert "designated notice and filing address" in md.lower()
    assert "delaware general corporation law" in md.lower() or "dgcl" in md.lower()


def test_principal_address_note_suppressed_when_empty_override(monkeypatch: pytest.MonkeyPatch) -> None:
    drs = dict(cmm.companies["DATA RECORD SCIENCE, INC."])
    drs["minutes_principal_address_note"] = ""
    reg = {"DATA RECORD SCIENCE, INC.": drs}
    monkeypatch.setattr(cmm, "companies", reg, raising=False)
    monkeypatch.setattr(cmm, "company_information", reg, raising=False)
    md = cmm.generate_agm("DATA RECORD SCIENCE, INC.", 2024)
    assert "**Address note:**" not in md


def test_agm_prior_minutes_first_series_year_after_incorporation_not_denying_history() -> None:
    """DATA RECORD SCIENCE: inc 2006 but minute series starts 2022—IV must not claim no board meetings ever occurred."""
    co = cmm.companies["DATA RECORD SCIENCE, INC."]
    assert co["inc_year"] < co.get("minutes_start_year", co["inc_year"])
    md = cmm.generate_agm("DATA RECORD SCIENCE, INC.", 2022)
    assert "no prior annual meeting of the Board was held" not in md
    low = md.lower()
    assert "compiled minute book series" in low
    assert "within this compilation series" in low
    assert "2006" in md
    assert "2022" in md


def test_agm_prior_minutes_true_first_year_after_incorporation_uses_original_language() -> None:
    """New corp whose series starts in the incorporation year still uses the true-first-annual wording."""
    md = cmm.generate_agm("SurveyTeams, Inc.", 2026)
    assert "no prior annual meeting of the Board was held" in md
    assert "following incorporation" in md


def test_surveyteams_board_minutes_two_directors_full_board_attendance() -> None:
    """SurveyTeams: two directors, 50/50 stock; board minutes require both directors at each meeting."""
    md = cmm.generate_agm("SurveyTeams, Inc.", 2026)
    assert "Mohamed Mohamed" in md
    assert "Derek E. Pappas" in md
    assert "**Directors Present:**" in md
    assert "Sole Director" not in md
    assert "Upon consideration, the Board adopted" in md
    assert "**Mohamed Mohamed** is authorized" in md
    q = cmm.generate_quarterly("SurveyTeams, Inc.", 2026, "Q1")
    assert "The directors reviewed quarterly" in q
    assert "acting as Chair of the Board" in q


def test_agm_prior_minutes_non_drs_first_year_matches_incorporation_start() -> None:
    """Registry companies (except DRS) have minutes_start_year == inc_year; first AGM uses incorporation-first wording."""
    h = cmm.companies["Hippo, Inc"]
    assert h.get("minutes_start_year", h["inc_year"]) == h["inc_year"]
    md = cmm.generate_agm("Hippo, Inc", 2022)
    assert "following incorporation" in md
    assert "compiled minute book series" not in md.lower()


def test_board_special_meeting_on_record_date_for_annual_stockholder_corps() -> None:
    co = cmm.companies["DATA RECORD SCIENCE, INC."]
    y = 2022
    assert cmm.board_special_meeting_date_str(co, y) == cmm.stockholder_annual_record_date_str(co, y)
    assert cmm.board_special_meeting_date_str(co, y) != cmm.annual_meeting_date_str(co, y)


def test_sole_written_consent_wy_uses_unanimous_shareholder_formulation() -> None:
    md = cmm.sole_stockholder_written_consent_markdown("Loki Sports Enterprises, Inc.", 2023)
    assert "W.S. 1977 § 17-16-704" in md
    assert "minimum number of votes" not in md.lower()


def test_schedule_seed_from_environment_parses_int_and_hex(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("CORPORATE_MINUTES_SCHEDULE_SEED", "42")
    assert cmm.schedule_seed_from_environment() == 42
    monkeypatch.setenv("CORPORATE_MINUTES_SCHEDULE_SEED", "0x10")
    assert cmm.schedule_seed_from_environment() == 16


def test_scheduled_stockholder_time_without_env_seed_is_nominal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("CORPORATE_MINUTES_SCHEDULE_SEED", raising=False)
    co = {"jurisdiction": "DE", "inc_year": 2020, "minutes_start_year": 2020, "schedule_time_jitter_minutes": 120}
    reg = {"OnlyCo": co}
    monkeypatch.setattr(cmm, "companies", reg, raising=False)
    monkeypatch.setattr(cmm, "company_information", reg, raising=False)
    assert cmm.scheduled_stockholder_meeting_time(co, 2025) == cmm.STOCKHOLDER_MEETING_TIME


def test_q4_quarterly_never_collides_with_december_annual_or_special_board() -> None:
    """Regression: Q4 anchor can land on the annual weekday; quarterly date must shift within December."""
    co = cmm.companies["Hippo, Inc"]
    for year in (2022, 2023, 2024, 2025, 2026):
        if year < co.get("minutes_start_year", co.get("inc_year", year)):
            continue
        annual = cmm.annual_meeting_date_str(co, year)
        special = cmm.board_special_meeting_date_str(co, year)
        q4 = cmm.quarterly_meeting_date_str(co, year, "Q4")
        assert q4 != annual
        assert q4 != special


def test_same_day_meeting_times_ordered_special_then_board_written_consent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Heavy jitter must not put annual board AGM before the same-day special board block."""
    co = {
        "jurisdiction": "DE",
        "inc_year": 2020,
        "minutes_start_year": 2020,
        "stockholder_meeting": "written_consent",
        "annual_day_offset": 0,
        "meeting_stagger_day": 0,
        "schedule_time_jitter_minutes": 180,
        "schedule_time_round_minutes": 5,
    }
    reg = {"WrittenCo": co}
    monkeypatch.setattr(cmm, "companies", reg, raising=False)
    monkeypatch.setattr(cmm, "company_information", reg, raising=False)
    monkeypatch.setenv("CORPORATE_MINUTES_SCHEDULE_SEED", "99")
    sp = cmm.scheduled_special_meeting_time(co, 2025)
    bd = cmm.scheduled_board_agm_time(co, 2025)
    assert cmm._clock_to_minutes_since_midnight(sp) <= cmm._clock_to_minutes_since_midnight(bd)


def test_scheduled_times_deterministic_and_differ_by_company_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    co_a = {
        "jurisdiction": "DE",
        "inc_year": 2020,
        "minutes_start_year": 2020,
        "schedule_time_jitter_minutes": 120,
    }
    co_b = {
        "jurisdiction": "DE",
        "inc_year": 2020,
        "minutes_start_year": 2020,
        "schedule_time_jitter_minutes": 120,
    }
    reg = {"AlphaScheduleCo": co_a, "BetaScheduleCo": co_b}
    monkeypatch.setattr(cmm, "companies", reg, raising=False)
    monkeypatch.setattr(cmm, "company_information", reg, raising=False)
    monkeypatch.setenv("CORPORATE_MINUTES_SCHEDULE_SEED", "7")
    ta = cmm.scheduled_stockholder_meeting_time(co_a, 2025)
    assert ta == cmm.scheduled_stockholder_meeting_time(co_a, 2025)
    tb = cmm.scheduled_stockholder_meeting_time(co_b, 2025)
    assert ta != tb


def test_stockholder_minutes_default_does_not_claim_waivers_on_file() -> None:
    """Default: annual stockholder minutes use to-be-filed exhibit wording (DRS waiver_focus)."""
    md = cmm.generate_annual_meeting_stockholders("DATA RECORD SCIENCE, INC.", 2024)
    assert "on file" not in md.lower()
    assert "to be filed" in md.lower() or "are to be filed" in md.lower()


def test_annual_stockholder_director_vote_tabulation_when_configured() -> None:
    """Phase 3 remediation: per-holder FOR lines after §VI when `annual_stockholder_director_election_votes` is set."""
    st = cmm.generate_annual_meeting_stockholders("SurveyTeams, Inc.", 2026)
    assert "VI-A. Vote Tabulation" in st
    assert "Mohamed Mohamed" in st
    assert "4,000,000" in st
    drs = cmm.generate_annual_meeting_stockholders("DATA RECORD SCIENCE, INC.", 2024)
    assert "VI-A. Vote Tabulation" in drs
    assert "5,346,132" in drs


def test_board_remote_presence_cites_dgcl_141i_delaware() -> None:
    md = cmm.generate_quarterly("Hippo, Inc", 2023, "Q1")
    assert "DGCL §141(i)" in md


def test_stockholder_minutes_may_claim_on_file_when_assert_exhibits_flag(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    co = dict(cmm.companies["DATA RECORD SCIENCE, INC."])
    co["minutes_assert_exhibits_filed"] = True
    reg = {"DATA RECORD SCIENCE, INC.": co}
    monkeypatch.setattr(cmm, "companies", reg, raising=False)
    monkeypatch.setattr(cmm, "company_information", reg, raising=False)
    md = cmm.generate_annual_meeting_stockholders("DATA RECORD SCIENCE, INC.", 2024)
    assert "on file" in md.lower()


def test_agm_written_consent_cross_ref_default_pending_filing() -> None:
    md = cmm.generate_agm("Hippo, Inc", 2023)
    assert "will be filed" in md.lower()
    assert "upon execution" in md.lower()
    assert "The Sole Director noted" in md
    assert "The Board noted" not in md


def test_loki_registry_has_wy_jurisdiction_no_dgcl_in_scanned_fields() -> None:
    """Regression: real WY company must not keep DGCL in guardrail-scanned `company_information` strings."""
    loki = cmm.company_information["Loki Sports Enterprises, Inc."]
    assert cmm._jurisdiction(loki) == "WY"
    scanned = (
        "stockholder_consent_bylaws_acknowledgment",
        "stockholder_consent_bylaws_mechanics_suffix",
        "stockholders_quorum_collective_sentence",
        "board_notice_waiver_bylaws_ref",
    )
    for key in scanned:
        val = loki.get(key)
        if isinstance(val, str):
            low = val.lower()
            assert "dgcl" not in low, key
            assert "delaware general corporation law" not in low, key


def test_hippo_ritual_teamboost_board_minutes_exclude_removed_director_name() -> None:
    """Hippo / Ritual / TeamBoost: sole-director board minutes must not name a former second director."""
    for text in (
        cmm.generate_quarterly("Hippo, Inc", 2022, "Q2"),
        cmm.generate_organizational("Hippo, Inc", 2022),
        cmm.generate_organizational("TeamBoost.ai, Inc.", 2023),
        cmm.generate_quarterly("TeamBoost.ai, Inc.", 2023, "Q1"),
        cmm.generate_agm("Ritual Growth, Inc.", 2022),
    ):
        low = text.lower()
        assert "marija" not in low
        assert "cejovic" not in low


def test_quarterly_schedule_blocks_json_loads_and_blocks_august_2023() -> None:
    ranges = cmm._load_quarterly_schedule_block_ranges()
    assert any(lo <= date(2023, 8, 20) <= hi for lo, hi in ranges)
    assert "2023-08-20" in cmm._schedule_blocked_iso_dates_in_month(2023, 8)


def test_board_chronological_index_orders_quarterly_before_december_annual() -> None:
    co = cmm.companies["Hippo, Inc"]
    assert cmm._board_meeting_chronological_index("Hippo, Inc", co, 2022, "Q1") == 0
    assert cmm._board_meeting_chronological_index("Hippo, Inc", co, 2022, "special") > 0


def test_cap_table_and_stock_ledger_document_markdown() -> None:
    hippo = cmm.cap_table_document_markdown("Hippo, Inc", cmm.companies["Hippo, Inc"])
    assert "Cap table summary" in hippo
    assert "Derek E. Pappas" in hippo
    assert "8,000,000" in hippo
    h_ledger = cmm.stock_ledger_document_markdown("Hippo, Inc", cmm.companies["Hippo, Inc"])
    assert "Stock ledger" in h_ledger
    assert "HIPPO-0001" in h_ledger
    drs = cmm.stock_ledger_document_markdown(
        "DATA RECORD SCIENCE, INC.", cmm.companies["DATA RECORD SCIENCE, INC."]
    )
    assert "DATA RECORD SCIENCE" in drs
    assert "DRS-0001" in drs
    assert "5,346,132" in drs or "5346132" in drs


def test_cap_table_carta_pulley_csv_rows() -> None:
    rows = cmm.cap_table_carta_pulley_rows("Hippo, Inc", cmm.companies["Hippo, Inc"])
    assert rows
    assert rows[0]["company_legal_name"]
    assert rows[0]["certificate_id"] == "HIPPO-0001"
    assert rows[0]["shares"] == "8000000"
    assert rows[0]["security_type"] == "Common Stock"
    drs_rows = cmm.cap_table_carta_pulley_rows(
        "DATA RECORD SCIENCE, INC.", cmm.companies["DATA RECORD SCIENCE, INC."]
    )
    assert any(r.get("certificate_id") == "DRS-0001" for r in drs_rows)


def test_stock_ledger_acknowledgment_first_meeting_after_purchase_date() -> None:
    """Ledger `issue_date` 2022-06-01 → first board meeting strictly after is 2022 Q2 (see data/stock_ledgers/hippo.json)."""
    cmm._reset_stock_ledger_meeting_index_for_tests()
    co_name = "Hippo, Inc"
    co = cmm.companies[co_name]
    md = cmm.generate_quarterly(co_name, 2022, "Q2")
    assert "Written board resolutions (equity)" in md
    assert "HIPPO-0001" in md
    assert "standalone board resolutions" in md
    assert "Issuance of Common Stock — HIPPO-0001" not in md
    q2_iso = cmm.quarterly_meeting_date_str(co, 2022, "Q2")
    pairs = cmm._ensure_stock_ledger_meeting_index().get((co_name, q2_iso), [])
    assert pairs
    entry, ledger = pairs[0]
    standalone = "\n\n".join(cmm._stock_ledger_resolution_blocks_for_entry(entry, ledger))
    assert "Issuance of Common Stock — HIPPO-0001" in standalone
    assert "Acknowledgment of Consideration — HIPPO-0001" in standalone
    assert "Stock Ledger and Books and Records — HIPPO-0001" in standalone
    assert "June 01, 2022" in standalone
    assert "8,000,000" in standalone
