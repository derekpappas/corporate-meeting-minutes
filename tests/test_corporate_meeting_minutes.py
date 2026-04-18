"""Tests for `corporate_meeting_minutes` helpers and `generate_all` side effects."""

from __future__ import annotations

import os
import warnings

import pytest

import corporate_meeting_minutes as cmm


def test_jurisdiction_defaults_to_de() -> None:
    assert cmm._jurisdiction({}) == "DE"
    assert cmm._jurisdiction({"jurisdiction": "  wy  "}) == "WY"


def test_corp_law_section_ref_de_vs_wy() -> None:
    de_co: dict = {"jurisdiction": "DE"}
    wy_co: dict = {"jurisdiction": "WY"}
    assert cmm._corp_law_section_ref(de_co, "228") == "DGCL §228"
    assert "Wyoming Business Corporation Act" in cmm._corp_law_section_ref(wy_co, "228")
    assert "DGCL" not in cmm._corp_law_section_ref(wy_co, "228")


def test_corporation_parenthetical_and_statute_name() -> None:
    assert "Delaware" in cmm._corporation_parenthetical({"jurisdiction": "DE"})
    assert "Wyoming" in cmm._corporation_parenthetical({"jurisdiction": "WY"})
    assert cmm._corporation_statute_name({"jurisdiction": "WY"}) == "Wyoming Business Corporation Act"


def test_reliance_standard_de_cites_141e() -> None:
    text = cmm.reliance_standard({"jurisdiction": "DE"})
    assert "141(e)" in text
    assert "Delaware General Corporation Law" in text


def test_reliance_standard_wy_uses_wyoming_act_not_dgcl() -> None:
    text = cmm.reliance_standard({"jurisdiction": "WY"})
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
