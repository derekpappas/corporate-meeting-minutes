import json
import os
import random
import re
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from docx import Document

# 1. DATA STRUCTURES
locations_timeline = [
    ("2018-07-01", "2021-08-15", "Palo Alto, California"),
    ("2021-08-15", "2021-10-15", "Amstelveen, Holland"),
    ("2021-10-15", "2021-11-15", "Barcelona, Spain"),
    ("2022-03-15", "2022-05-15", "Sunny Isles, Florida"),
    ("2022-05-15", "2022-07-05", "Wayne, Pennsylvania"),
    ("2022-07-05", "2022-07-15", "Portland, Oregon"),
    ("2022-07-15", "2023-09-27", "Wayne, Pennsylvania"),
    ("2023-09-27", "2023-10-09", "Knoxville, TN"),
    ("2023-10-09", "2023-10-19", "Austin, TX"),
    ("2023-10-19", "2023-10-25", "Palo Alto, California"),
    ("2023-10-25", "2023-10-29", "Surrey, Canada"),
    ("2023-10-29", "2023-11-07", "Knoxville, TN"),
    ("2023-11-08", "2023-11-27", "Belgrade, Serbia"),
    ("2023-11-27", "2024-01-13", "Thessaloniki, Greece"),
    ("2024-01-13", "2024-01-27", "Valencia, Spain"),
    ("2024-01-28", "2024-02-14", "Knoxville, TN"),
    ("2024-02-14", "2024-04-21", "Belgrade, Serbia"),
    ("2024-04-21", "2024-05-17", "Thessaloniki, Greece"),
    ("2024-05-17", "2024-07-06", "Belgrade, Serbia"),
    ("2024-07-06", "2024-07-12", "Athens, Greece"),
    ("2024-07-12", "2024-07-19", "Istanbul, Turkey"),
    ("2024-07-19", "2024-08-19", "Birmingham, England"),
    ("2024-08-19", "2024-10-31", "Hoegaarden, Belgium"),
    ("2024-10-31", "2024-11-18", "Birmingham, England"),
    ("2024-11-18", "2025-02-15", "Denver, NC"),
    ("2025-02-15", "2025-03-31", "Lantana, FL"),
    ("2025-04-01", "2026-04-30", "Wayne, Pennsylvania"),
    ("2026-05-01", "2026-12-31", "Wayne, Pennsylvania")
]

# Stockholder-side instruments:
# - "written_consent": sole stockholder action by written consent under DGCL § 228 (charter must authorize written consent).
# - "annual_meeting_stockholders": formal minutes of an annual meeting of stockholders (e.g. multiple stockholders).
#
# Location in minutes:
# - use_timeline_place: include principal-operational place from locations_timeline for the meeting date (all corps here).
# - virtual_ok: Delaware permits remote meetings when notice/boilerplate matches your bylaws; minutes use "via digital
#   communication" alongside the timeline place for consistency. Set False only if you intentionally omit remote language.
#
# Annual scheduling constraints (sole director across multiple corporations):
# - annual_day_offset staggers annual meetings on consecutive weekdays in December
#   (computed as Monday-based business days starting from the first Monday on or after December 8).
# - All annual meetings for a single corporation occur on the same day, commencing at 1:00 PM (sequence is documented in minutes).
# Optional per company: voting_shares_description — phrase after "holding" in §228 written consent if not all voting power is one class.
# minutes_display_name — legal name as it should appear in minutes (e.g. "Hippo, Inc.") when the dict key omits a period.
# stockholders_roll_call — for annual_meeting_stockholders only: list of {"name": str, "presence": str} for roll call.
# stockholders_quorum_collective_sentence — follows roll call; explains majority quorum.
# stockholders_absent_line — text under Stockholders Absent (default "None.").
# annual_board_resolution_blocks — optional list of markdown strings (each: optional **title** line + RESOLVED, …). If key
#   omitted, AGM uses the default three resolutions. If [] (empty list), minutes use “no resolutions” language.
# quarterly_resolution_blocks — same for quarterly board minutes; default one ratification. [] for no resolutions.
# agm_president_report_product_line — optional AGM sentence(s) after the standard ops/dev locations paragraph: factual product
#   scope (e.g. API / web / mobile). If omitted, a short generic “continued development…” sentence is used.
# agm_president_report_infrastructure_line — optional sentence on hosting / infrastructure (e.g. named providers).
# agm_president_report_operating_exhibit_label — if set (e.g. "Exhibit B"), minutes may reference a written addendum with deeper
#   specs, roadmaps, KPIs, and diagrams. When `audit_reports/all_corp_accomplishments_2021-2025.json` lists detailed
#   `annual_report` bullets for the year, an operating addendum .docx is generated and the minutes reference **detailed accomplishments**.
#   If detailed bullets exist but this key is omitted, **Exhibit B** is used by default for that addendum.
STOCKHOLDER_MEETING_TIME = "1:00 PM"
BOARD_AGM_TIME = "1:00 PM"
QUARTERLY_MEETING_TIME = "1:00 PM"
SPECIAL_MEETING_TIME = "12:00 PM"

# Timeline place label (from get_location) → IANA timezone for file mtimes (meeting “local” business hours).
_TIMELINE_LOCATION_TZ: dict[str, str] = {
    "Palo Alto, California": "America/Los_Angeles",
    "Amstelveen, Holland": "Europe/Amsterdam",
    "Barcelona, Spain": "Europe/Madrid",
    "Sunny Isles, Florida": "America/New_York",
    "Wayne, Pennsylvania": "America/New_York",
    "Portland, Oregon": "America/Los_Angeles",
    "Knoxville, TN": "America/New_York",
    "Austin, TX": "America/Chicago",
    "Surrey, Canada": "America/Vancouver",
    "Belgrade, Serbia": "Europe/Belgrade",
    "Thessaloniki, Greece": "Europe/Athens",
    "Valencia, Spain": "Europe/Madrid",
    "Athens, Greece": "Europe/Athens",
    "Istanbul, Turkey": "Europe/Istanbul",
    "Birmingham, England": "Europe/London",
    "Hoegaarden, Belgium": "Europe/Brussels",
    "Denver, NC": "America/New_York",
    "Lantana, FL": "America/New_York",
}

def _jurisdiction(co: dict) -> str:
    """Two-letter jurisdiction code (default: DE)."""
    return str(co.get("jurisdiction") or "DE").strip().upper()


def _corporation_parenthetical(co: dict) -> str:
    """Parenthetical used on covers (e.g., *(Delaware corporation)*)."""
    j = _jurisdiction(co)
    if j == "WY":
        return "*(Wyoming corporation)*"
    return "*(Delaware corporation)*"


def _corporation_statute_name(co: dict) -> str:
    """Full statute name for narrative references."""
    j = _jurisdiction(co)
    if j == "WY":
        return "Wyoming Business Corporation Act"
    return "Delaware General Corporation Law"


def _corp_law_section_ref(co: dict, section: str) -> str:
    """Short section citation; DE uses DGCL §X, other jurisdictions omit section numbers to avoid mis-citation."""
    j = _jurisdiction(co)
    if j == "DE":
        return f"DGCL §{section}"
    return f"the applicable provisions of the {_corporation_statute_name(co)}"


def reliance_standard(co: dict) -> str:
    j = _jurisdiction(co)
    if j == "DE":
        return (
            "In taking the actions reflected in these minutes, the Sole Director relied in good faith on information, opinions, reports, and "
            "statements—including financial and operational materials prepared for this meeting and presentations from officers of the "
            "Corporation—as to matters the Sole Director reasonably believed were within such persons’ professional or expert competence, "
            "as contemplated by Section 141(e) of the Delaware General Corporation Law.\n"
        )
    return (
        "In taking the actions reflected in these minutes, the Sole Director relied in good faith on information, opinions, reports, and "
        "statements—including financial and operational materials prepared for this meeting and presentations from officers of the "
        "Corporation—as to matters the Sole Director reasonably believed were within such persons’ professional or expert competence, "
        f"as contemplated by the {_corporation_statute_name(co)}.\n"
    )

# Company information (canonical registry for minute generation)
company_information = {
    "Hippo, Inc": {
        "minutes_display_name": "Hippo, Inc.",
        "address": "30 N Gould St Ste 21106, Sheridan, WY 82801",
        "par": "$.0001",
        "inc_year": 2022,
        "minutes_start_year": 2022,
        "director_election_standard": "plurality",
        "shares_issued": {2022: "8,000,000", 2023: "8,160,000", 2024: "8,160,000", 2025: "8,160,000", 2026: "8,160,000"},
        "annual_day_offset": 0,
        "meeting_stagger_day": 0,
        "stockholder_meeting": "written_consent",
        # Annex executed consent PDF to board book; minutes cross-reference (AGM). Set to None until filed.
        "sole_stockholder_consent_exhibit_label": "Exhibit A",
        "use_timeline_place": True,
        "virtual_ok": True,
        # Cite filed Amended and Restated Bylaws (`bylaws_text/Hippo, Inc. - Bylaws.docx.pdf.txt`).
        "stockholder_consent_bylaws_acknowledgment": (
            "The undersigned acknowledges that this consent is intended to comply with **Article III, Section 13** "
            "of the Corporation’s **Amended and Restated Bylaws** (Action Without Meeting), as well as **Section 228** of the DGCL."
        ),
        "stockholder_consent_bylaws_mechanics_suffix": (
            "Under **Article III, Section 13(b)** of those Bylaws, written consents must be delivered to the Corporation "
            "within **sixty (60) days** of the earliest dated consent; delivery to the registered office, if used, must be "
            "by hand or by certified or registered mail, return receipt requested, as set forth in the Bylaws."
        ),
        "board_notice_waiver_bylaws_ref": (
            "the Corporation’s **Amended and Restated Bylaws**, including **Article IV, Section 21** "
            "(meetings of the Board of Directors; notice; and waiver of notice)"
        ),
    },
    "Ritual Growth, Inc.": {
        "address": "30 N Gould St Ste 27616, Sheridan, WY 82801",
        "par": "$.0001",
        "inc_year": 2022,
        "minutes_start_year": 2022,
        "shares_issued": {2022: "4,000,000", 2023: "4,000,000", 2024: "4,000,000", 2025: "4,000,000", 2026: "4,000,000"},
        "annual_day_offset": 1,
        "meeting_stagger_day": 1,
        "stockholder_meeting": "written_consent",
        "sole_stockholder_consent_exhibit_label": "Exhibit A",
        "use_timeline_place": True,
        "virtual_ok": True,
        # `bylaws_text/Bylaws of Ritual Growth, Inc.pdf.txt` — Roman articles II / III / VIII.
        "stockholder_consent_bylaws_acknowledgment": (
            "The undersigned acknowledges that this consent is intended to comply with **Article II, Section 9** "
            "of the **By-Laws of Ritual Growth, Inc.** (Action Without Meeting), as well as **Section 228** of the DGCL."
        ),
        "stockholder_consent_bylaws_mechanics_suffix": (
            "Under **Article II, Section 9** of those By-Laws, delivery to the Corporation’s registered office shall be "
            "by hand or by certified or registered mail, return receipt requested, where that delivery method is used; "
            "**prompt notice** of action taken without a meeting is required when consent is less than unanimous among "
            "applicable stockholders, as described in the By-Laws."
        ),
        "board_notice_waiver_bylaws_ref": (
            "the **By-Laws of Ritual Growth, Inc.**, including **Article III, Section 8** (notice and place of meetings of "
            "the Board of Directors) and **Article VIII, Section 4** (waiver of notice)"
        ),
        "agm_president_report_product_line": (
            "The Sole Director summarized continued product development during the year, including API servers and services "
            "and web applications; the Corporation did not ship a separate consumer mobile application during the period summarized."
        ),
        "agm_president_report_infrastructure_line": (
            "The Corporation continued to operate hardware and cloud infrastructure using hosting providers including **DigitalOcean** and **Hetzner**."
        ),
        "agm_president_report_operating_exhibit_label": "Exhibit B",
    },
    "DATA RECORD SCIENCE, INC.": {
        "address": "30 N Gould St Ste 24165, Sheridan, WY 82801",
        "par": "$0.001",
        # Originally incorporated in Delaware in 2006 (as Yoterra, Inc.), later renamed to Data Record Science, Inc.
        "inc_year": 2006,
        "minutes_start_year": 2022,
        "director_election_standard": "plurality",
        "shares_issued": {2022: "5,346,132", 2023: "5,346,132", 2024: "5,346,132", 2025: "5,346,132", 2026: "5,346,132"},
        "annual_day_offset": 2,
        "meeting_stagger_day": 2,
        "stockholder_meeting": "annual_meeting_stockholders",
        # Annual stockholder meeting §222: for a single voting stockholder, waiver-only path is usually simplest; use
        # "notice_focus" if counsel prefers formal notice. Set annual_stockholder_notice_exhibit_label when you annex PDFs.
        "annual_stockholder_notice_record": "waiver_focus",
        "annual_stockholder_notice_exhibit_label": "Exhibit A",
        "use_timeline_place": True,
        "virtual_ok": True,
        "stockholders_roll_call": [
            {"name": "Derek E. Pappas", "presence": "present in person"},
        ],
        # Majority voting stockholder only: quorum satisfied by his presence alone (no other voters present).
        "stockholders_quorum_collective_sentence": (
            "**Derek E. Pappas** holds a **majority** of the outstanding shares of the Corporation entitled to vote at the meeting; "
            "he was the **only stockholder present** (in person or by proxy) entitled to vote at the meeting, and his presence "
            "**alone satisfied** the quorum requirement under the DGCL and the Corporation’s bylaws."
        ),
    },
    "TeamBoost.ai, Inc.": {
        "address": "30 N Gould St Ste 23049, Sheridan, WY 82801",
        "par": "$.0001",
        # Filed January 30, 2023 (Delaware).
        "inc_year": 2023,
        "minutes_start_year": 2023,
        "shares_issued": {2023: "10,000,000", 2024: "10,000,000", 2025: "10,000,000", 2026: "10,000,000"},
        "annual_day_offset": 3,
        "meeting_stagger_day": 3,
        "stockholder_meeting": "written_consent",
        "sole_stockholder_consent_exhibit_label": "Exhibit A",
        "use_timeline_place": True,
        "virtual_ok": True,
        # Same article/section map as Ritual (`bylaws_text/Bylaws of TeamBoost.ai, Inc.pdf.txt`).
        "stockholder_consent_bylaws_acknowledgment": (
            "The undersigned acknowledges that this consent is intended to comply with **Article II, Section 9** "
            "of the **By-Laws of TeamBoost.ai, Inc.** (Action Without Meeting), as well as **Section 228** of the DGCL."
        ),
        "stockholder_consent_bylaws_mechanics_suffix": (
            "Under **Article II, Section 9** of those By-Laws, delivery to the Corporation’s registered office shall be "
            "by hand or by certified or registered mail, return receipt requested, where that delivery method is used; "
            "**prompt notice** of action taken without a meeting is required when consent is less than unanimous among "
            "applicable stockholders, as described in the By-Laws."
        ),
        "board_notice_waiver_bylaws_ref": (
            "the **By-Laws of TeamBoost.ai, Inc.**, including **Article III, Section 8** (notice and place of meetings of "
            "the Board of Directors) and **Article VIII, Section 4** (waiver of notice)"
        ),
        "agm_president_report_product_line": (
            "The Sole Director summarized continued product development during the year, including API servers and services, "
            "web applications, and mobile applications."
        ),
        "agm_president_report_infrastructure_line": (
            "The Corporation continued to operate hardware and cloud infrastructure using hosting providers including **DigitalOcean** and **Hetzner**."
        ),
        "agm_president_report_operating_exhibit_label": "Exhibit B",
    },
    "SurveyTeams, Inc.": {
        "minutes_display_name": "SurveyTeams, Inc.",
        # Lease address (also used as principal address in minutes unless you provide a separate mailing/principal line).
        "address": "30 N Gould St #58611, Sheridan, WY 82801, USA",
        "par": "$.0001",
        # Inc/year not provided; defaulting minutes generation to start in 2026.
        "inc_year": 2026,
        "minutes_start_year": 2026,
        "director_election_standard": "plurality",
        # Share data per intake:
        # - 10,000,000 authorized
        # - 8,000,000 issued/outstanding (4,000,000 Derek; 4,000,000 Mohamed)
        "shares_authorized": "10,000,000",
        "shares_issued": {2026: "8,000,000"},
        "stockholder_shares": {
            "Derek E. Pappas": "4,000,000",
            "Mohamed Mohamed": "4,000,000",
        },
        "annual_day_offset": 4,
        "meeting_stagger_day": 4,
        # Two named stockholders: generate formal annual stockholder meeting minutes + notice/waiver instruments.
        "stockholder_meeting": "annual_meeting_stockholders",
        "annual_stockholder_notice_record": "waiver_focus",
        "annual_stockholder_notice_exhibit_label": "Exhibit A",
        "use_timeline_place": True,
        "virtual_ok": True,
        "stockholders_roll_call": [
            {"name": "Mohamed Mohamed", "presence": "present in person"},
            {"name": "Derek E. Pappas", "presence": "present in person"},
        ],
        "stockholders_quorum_collective_sentence": (
            "Collectively, the stockholders present at the meeting held a **majority** of the outstanding shares of the Corporation "
            "entitled to vote at the meeting, and their presence satisfied the quorum requirement under the DGCL and the Corporation’s bylaws."
        ),
        # Optional metadata captured from intake (not currently used by templates).
        "irs_ein": "41-3602747",
        "irs_legal_name": "SURVEYTEAMS INC",
        "officers": {"CEO": "Mohamed Mohamed", "CTO": "Derek E. Pappas"},
    },
    "Loki Sports Enterprises, Inc.": {
        "minutes_display_name": "Loki Sports Enterprises, Inc.",
        "address": "30 N Gould St Ste 24709, Sheridan, WY 82801",
        "jurisdiction": "WY",
        "par": "$.0001",
        # WY domestic profit corporation filing (2023).
        "inc_year": 2023,
        "minutes_start_year": 2023,
        "shares_issued": {
            2023: "10,000,000",
            2024: "10,000,000",
            2025: "10,000,000",
            2026: "10,000,000",
        },
        "annual_day_offset": 5,
        "meeting_stagger_day": 5,
        # Sole stockholder: use written consent pack (DGCL-style templates; adjust if you later add WY-specific variants).
        "stockholder_meeting": "written_consent",
        "sole_stockholder_consent_exhibit_label": "Exhibit A",
        "use_timeline_place": True,
        "virtual_ok": True,
        # Optional metadata captured from intake (not currently used by templates).
        "irs_ein": "93-2976555",
        "irs_legal_name": "LOKI SPORTS ENTERPRISES INC",
        "wy_sos_filing_id": "2023-001316332",
        "dba": "DEREK EDWIN PAPPAS",
        "mailing_address": "1317 Edgewater Dr Num 1961, Orlando, FL 32804",
    },
}

# Backwards-compatible alias (existing generator code expects `companies`).
companies = company_information

# Accomplishments (President’s report summary + operating addendum detail) — `audit_reports/all_corp_accomplishments_2021-2025.json`.
# Top-level keys in JSON: "Hippo", "TB", "RG", … mapped from `companies` dict keys below.
_ACCOMPLISHMENTS_JSON_KEY: dict[str, str] = {
    "Hippo, Inc": "Hippo",
    "TeamBoost.ai, Inc.": "TB",
    "Ritual Growth, Inc.": "RG",
}
_ACCOMPLISHMENTS_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "audit_reports",
    "all_corp_accomplishments_2021-2025.json",
)
_accomplishments_cache: dict | None = None


def _accomplishments_root() -> dict:
    global _accomplishments_cache
    if _accomplishments_cache is None:
        if os.path.isfile(_ACCOMPLISHMENTS_PATH):
            with open(_ACCOMPLISHMENTS_PATH, encoding="utf-8") as f:
                _accomplishments_cache = json.load(f)
        else:
            _accomplishments_cache = {}
    return _accomplishments_cache


def accomplishments_for_year(co_name: str, year: int) -> tuple[str | None, list[str]]:
    """Return (summary text or None, cleaned detail bullets) from accomplishments JSON for this company and calendar year."""
    jkey = _ACCOMPLISHMENTS_JSON_KEY.get(co_name)
    if not jkey:
        return None, []
    block = _accomplishments_root().get(jkey)
    if not isinstance(block, dict):
        return None, []
    yblock = block.get(str(year))
    if not isinstance(yblock, dict):
        return None, []
    summary_raw = yblock.get("summary")
    summary = summary_raw.strip() if isinstance(summary_raw, str) and summary_raw.strip() else None
    raw_list = yblock.get("annual_report", [])
    details: list[str] = []
    if isinstance(raw_list, list):
        for x in raw_list:
            if isinstance(x, str) and x.strip():
                details.append(x.strip())
    return summary, details


def agm_operating_addendum_markdown(
    co_name: str, year: int, exhibit_label: str, detail_lines: list[str]
) -> str:
    """Markdown body for the AGM operating addendum (same text as standalone .docx)."""
    if not detail_lines:
        return ""
    co = companies[co_name]
    display = minutes_display_name(co_name)
    bullets = "\n".join(f"- {line}" for line in detail_lines)
    return f"""
**Operating addendum ({exhibit_label})**
**{display}**
{_corporation_parenthetical(co)}

**Purpose**
This addendum supplements the **Minutes of the Annual Meeting of the Board of Directors** of the Corporation for **{year}** and is annexed to those minutes as **{exhibit_label}**.

**Detailed accomplishments ({year})**

{bullets}

**Other materials**
To the extent referenced in the minutes, this addendum may also include or incorporate by reference supplemental technical materials furnished for the meeting (including technical specifications, roadmaps, KPIs, and architecture diagrams).

---
""".strip() + "\n"


def _generate_agm_operating_addendum_docx(
    company_name_year: str,
    co_name: str,
    year: int,
    exhibit_label: str,
    detail_lines: list[str],
) -> None:
    """Write `{company_name_year}_agm_operating_addendum.docx` (Exhibit referenced in AGM minutes)."""
    if not detail_lines:
        return
    co = companies[co_name]
    mdate = annual_meeting_date_str(co, year)
    content = agm_operating_addendum_markdown(co_name, year, exhibit_label, detail_lines)
    path = f"{company_name_year}_agm_operating_addendum.docx"
    print(f"Writing AGM operating addendum to {path}")
    write_docx_from_minutes(content, path, mdate, co_name)


def office_locations_for_year(ranges, year):
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    locations = []

    for start, end, location in ranges:
        start_d = date.fromisoformat(start)
        end_d = date.fromisoformat(end)

        # overlap test
        if start_d <= year_end and end_d >= year_start:
            if location not in locations:
                locations.append(location)

    return locations


def normalize_locations(locations):
    normalized = []
    for loc in locations:
        if loc == "Denver, NC":
            normalized.append("Denver, North Carolina, USA")
        elif loc == "Lantana, FL":
            normalized.append("Lantana, Florida, USA")
        elif loc == "Wayne, Pennsylvania":
            normalized.append("Wayne, Pennsylvania, USA")
        else:
            normalized.append(loc)
    return "; ".join(normalized)

def development_locations():
    normalized = []
    normalized.append("Bosnia and Herzegovina")
    normalized.append("Serbia")
    normalized.append("Tunisia")
    return "; ".join(normalized)

# 2. HELPER LOGIC
def get_location(date_str):
    target = datetime.strptime(date_str, "%Y-%m-%d")
    for start, end, loc in locations_timeline:
        s_dt = datetime.strptime(start, "%Y-%m-%d")
        e_dt = datetime.strptime(end, "%Y-%m-%d")
        if s_dt <= target <= e_dt:
            return loc
    raise Exception("Location not found for date: " + date_str)


def _zoneinfo_for_meeting(co: dict, meeting_date_iso: str) -> ZoneInfo:
    """Timezone for the operational meeting place (timeline row or registered-office fallback)."""
    if co.get("use_timeline_place", True):
        loc = get_location(meeting_date_iso)
        iana = _TIMELINE_LOCATION_TZ.get(loc)
        if not iana:
            raise ValueError(f"No IANA timezone mapped for timeline location: {loc!r}")
        return ZoneInfo(iana)
    # Principal address (Wyoming) — Mountain Time
    return ZoneInfo("America/Denver")


def _random_utime_after_meeting(filepath: str, meeting_date_iso: str, co: dict) -> None:
    """Set atime/mtime to a random weekday time 1–3 calendar days after the meeting, in the meeting timezone (9:00–16:59 local)."""
    meeting_d = datetime.strptime(meeting_date_iso, "%Y-%m-%d").date()
    tz = _zoneinfo_for_meeting(co, meeting_date_iso)
    weekday_candidates = []
    for delta in (1, 2, 3):
        d = meeting_d + timedelta(days=delta)
        if d.weekday() < 5:
            weekday_candidates.append(d)
    if not weekday_candidates:
        d = meeting_d + timedelta(days=4)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        weekday_candidates = [d]
    chosen = random.choice(weekday_candidates)
    minute_of_day = random.randint(9 * 60, 17 * 60 - 1)
    h, m = divmod(minute_of_day, 60)
    s = random.randint(0, 59)
    local_dt = datetime(
        chosen.year, chosen.month, chosen.day, h, m, s, tzinfo=tz
    )
    ts = local_dt.timestamp()
    os.utime(filepath, (ts, ts))


def _annual_series_date(year: int, offset_days: int) -> date:
    """Pick a December weekday for the annual meeting series: first Monday on/after Dec 8, then consecutive weekdays."""
    ref = date(year, 12, 8)
    days_to_monday = (0 - ref.weekday()) % 7
    anchor_monday = ref + timedelta(days=days_to_monday)
    return anchor_monday + timedelta(days=offset_days)


def annual_meeting_date_str(co, year):
    """ISO date (YYYY-MM-DD) for this corporation’s annual meetings (stockholders / board / special) for the year."""
    offset_days = co.get("annual_day_offset", 0)
    d = _annual_series_date(year, offset_days)
    return d.strftime("%Y-%m-%d")


def stockholder_annual_record_date_str(co, year: int) -> str:
    """ISO date for stockholders entitled to vote at the annual meeting (record date), prior to meeting date.

    Fixed offset (calendar days) for template continuity; adjust per bylaws if a business-day or different window applies.
    """
    meeting = datetime.strptime(annual_meeting_date_str(co, year), "%Y-%m-%d").date()
    return (meeting - timedelta(days=10)).strftime("%Y-%m-%d")


def quarterly_meeting_date_str(co, year, quarter):
    """Governance check date per quarter; bumped by meeting_stagger_day so the same director isn’t quadruple-booked on one calendar day across corporations."""
    stagger = co.get("meeting_stagger_day", 0)
    if quarter == "Q1":
        y, month, base_day = year, 4, 1
    elif quarter == "Q2":
        y, month, base_day = year, 7, 1
    elif quarter == "Q3":
        y, month, base_day = year, 10, 1
    elif quarter == "Q4":
        y, month, base_day = year, 12, 1
    else:
        raise ValueError(f"Unknown quarter: {quarter}")
    day = base_day + stagger
    return f"{y}-{month:02d}-{day:02d}"


def meeting_place_line(co, date_str):
    """Where line for minutes: timeline place + remote participation, or principal address only."""
    if co.get("use_timeline_place", True):
        loc = get_location(date_str)
        if co.get("virtual_ok", True):
            return f"{loc}, via digital communication"
        return loc
    if co.get("virtual_ok", True):
        return f"{co['address']}, via digital communication"
    return co["address"]


def minutes_display_name(co_name: str) -> str:
    co = companies[co_name]
    return co.get("minutes_display_name", co_name)


def _annual_stockholder_notice_section_iv(co: dict) -> str:
    """Section IV for annual stockholder meeting minutes: waiver-first, notice-first, or combined (counsel to choose)."""
    mode = co.get("annual_stockholder_notice_record", "combined")
    ex = co.get("annual_stockholder_notice_exhibit_label")
    annex = f" A copy is **annexed to these minutes as {ex}**." if ex else ""

    if mode == "waiver_focus":
        return f"""**IV. Notice; Waiver**
The Chairperson confirmed that **written waivers of notice** of this annual meeting, executed by stockholders entitled to cast the votes required by applicable law and the Corporation’s bylaws, are **on file** with the records of the Corporation, and that the meeting was held in reliance on such waivers in accordance with the {_corporation_statute_name(co)} and the bylaws.{annex}"""

    if mode == "notice_focus":
        return f"""**IV. Notice**
The Chairperson confirmed that **notice** of this annual meeting was given to each stockholder entitled to vote, **not less than** the minimum time period required by the {_corporation_statute_name(co)} and the Corporation’s bylaws, and that such notice stated the date, time, and principal place (if any) of the meeting and the **means of remote communication**, if any, for participating in the meeting.{annex}"""

    annex_w = f" Waivers, if any, may be **annexed to these minutes as {ex}**." if ex else ""
    return f"""**IV. Notice**
The Chairperson confirmed that **notice** of this annual meeting was given to each stockholder entitled to vote, **not less than** the minimum time period required by the {_corporation_statute_name(co)} and the Corporation’s bylaws, and that such notice stated the date, time, and principal place (if any) of the meeting and the **means of remote communication**, if any, for participating in the meeting. The Chairperson further confirmed that, to the extent notice was waived, **written waivers of notice** executed by stockholders entitled to cast sufficient votes to satisfy the requirements of applicable law and the bylaws are **on file** with the records of the Corporation.{annex_w}"""


def format_stockholders_roll_call_block(co: dict) -> str:
    roll = co.get("stockholders_roll_call")
    absent = co.get("stockholders_absent_line", "None.")
    if not roll:
        return f"""**Stockholders Present:**  
The stockholders of the Corporation holding a majority of the outstanding shares of the Corporation entitled to vote at the meeting.

**Stockholders Absent:**  
{absent}"""
    lines = "\n".join(f"- **{r['name']}**, {r['presence']}" for r in roll)
    collective = co.get(
        "stockholders_quorum_collective_sentence",
        "Together with other record holders voting in person or by valid proxy as tallied for this meeting, these stockholders "
        "constituted holders of a majority of the outstanding shares entitled to vote at the meeting.",
    )
    return f"""**Stockholders Present:**  
{lines}

{collective}

**Stockholders Absent:**  
{absent}"""


def _stockholder_waiver_signature_blocks(co: dict) -> str:
    roll = co.get("stockholders_roll_call")
    if not roll:
        return """**Stockholder (print name):** _________________________________

**Signature:** _________________________________

**Date:** _________________________________"""
    parts = []
    for r in roll:
        parts.append(
            f"""**Stockholder:** {r["name"]}

**Signature:** _________________________________

**Date:** _________________________________"""
        )
    return "\n\n".join(parts)


def stockholder_waiver_of_notice_annual_meeting_markdown(
    company_name_year: str, year: int, co_name: str
) -> str:
    """Markdown for standalone waiver of notice (annual stockholders)."""
    co = companies[co_name]
    date_iso = annual_meeting_date_str(co, year)
    record_date = stockholder_annual_record_date_str(co, year)
    place = meeting_place_line(co, date_iso)
    as_meeting = datetime.strptime(date_iso, "%Y-%m-%d").strftime("%B %d, %Y")
    sig_blocks = _stockholder_waiver_signature_blocks(co)
    return f"""
**Waiver of Notice of Annual Meeting of Stockholders**
**{co_name}**
{_corporation_parenthetical(co)}

The undersigned record stockholder(s) of **{co_name}** (the “Corporation”) entitled to vote at the annual meeting described below, intending to be legally bound, **waive notice** of that meeting and of any postponement or adjournment thereof to the extent permitted by the {_corporation_statute_name(co)}, the Corporation’s **certificate of incorporation**, and **bylaws**.

**Meeting**  
**Date:** {date_iso} ({as_meeting})  
**Time:** {STOCKHOLDER_MEETING_TIME}  
**Place / remote means:** {place}

**Record date ({_corp_law_section_ref(co, "213")}):** {record_date}  
(Stockholders of record as of this date are entitled to notice of, and to vote at, the meeting, subject to the certificate of incorporation and bylaws.)

**Business**  
The meeting may include election of directors and any other annual business proper under the charter and bylaws.

{sig_blocks}
---
"""


def generate_stockholder_waiver_of_notice_annual_meeting(
    company_name_year: str, year: int, co_name: str
) -> None:
    """Standalone waiver of notice for the annual stockholder meeting (file alongside minutes; sign and annex as Exhibit A if used)."""
    co = companies[co_name]
    date_iso = annual_meeting_date_str(co, year)
    content = stockholder_waiver_of_notice_annual_meeting_markdown(company_name_year, year, co_name)
    path = f"{company_name_year}_waiver_of_notice_annual_stockholder_meeting.docx"
    print(f"Writing Waiver of Notice (annual stockholders) to {path}")
    write_docx_from_minutes(content, path, date_iso, co_name)


def notice_of_annual_stockholder_meeting_markdown(
    company_name_year: str, year: int, co_name: str
) -> str:
    """Markdown for §222-style notice of annual stockholder meeting."""
    co = companies[co_name]
    date_iso = annual_meeting_date_str(co, year)
    record_date = stockholder_annual_record_date_str(co, year)
    place = meeting_place_line(co, date_iso)
    as_meeting = datetime.strptime(date_iso, "%Y-%m-%d").strftime("%B %d, %Y")
    principal = co["address"]
    officer = co.get("notice_signatory_line", "Derek E. Pappas, President")
    return f"""
**Notice of Annual Meeting of Stockholders**
**{co_name}**
{_corporation_parenthetical(co)}

To the stockholders of the Corporation:

Notice is hereby given that an **annual meeting of stockholders** of **{co_name}** (the “Corporation”) will be held:

**Date:** {as_meeting} ({date_iso})  
**Time:** {STOCKHOLDER_MEETING_TIME}  
**Place / means of participation:** {place}

**Record date:** The **record date** for determining stockholders entitled to notice of and to vote at the meeting (or any adjournment or postponement) is **{record_date}**, as fixed by the Board of Directors in accordance with the bylaws and the {_corporation_statute_name(co)}.

**Purpose**  
To elect directors and to transact such other business as may properly come before the meeting and any adjournment or postponement, in accordance with the certificate of incorporation and bylaws.

Stockholders may attend and vote in person or, where permitted by the bylaws and applicable law, by remote communication in the manner described in this notice or in supplemental instructions provided by the Corporation.

This notice is given pursuant to the {_corporation_statute_name(co)} and the Corporation’s bylaws. Notice may be delivered by hand, United States mail, or electronic transmission in the manner and within the time frames permitted by applicable law and the bylaws.

**Principal executive office:** {principal}

By order of the Board of Directors,

{officer}

**Date of this notice:** _________________________________
---
"""


def generate_notice_of_annual_stockholder_meeting(
    company_name_year: str, year: int, co_name: str
) -> None:
    """Standalone §222-style notice of annual stockholder meeting (deliver or file as required; may annex to minute book)."""
    co = companies[co_name]
    date_iso = annual_meeting_date_str(co, year)
    content = notice_of_annual_stockholder_meeting_markdown(company_name_year, year, co_name)
    path = f"{company_name_year}_notice_of_annual_stockholder_meeting.docx"
    print(f"Writing Notice of Annual Stockholder Meeting to {path}")
    write_docx_from_minutes(content, path, date_iso, co_name)


def _board_meeting_rows_for_year(co: dict, year: int) -> list[tuple[str, str, str, str]]:
    """(date_iso, meeting_title, time_str, place_line) sorted chronologically; matches minuted board meetings for the year."""
    annual = annual_meeting_date_str(co, year)
    rows: list[tuple[str, int, str, str, str]] = []
    # Same calendar day as annual series: special (noon) then annual board (afternoon), per generate_special / generate_agm.
    rows.append(
        (
            annual,
            12 * 60,
            "Special Meeting of the Board of Directors",
            SPECIAL_MEETING_TIME,
            meeting_place_line(co, annual),
        )
    )
    rows.append(
        (
            annual,
            13 * 60,
            "Annual Meeting of the Board of Directors",
            BOARD_AGM_TIME,
            meeting_place_line(co, annual),
        )
    )
    for quarter in ("Q1", "Q2", "Q3", "Q4"):
        qd = quarterly_meeting_date_str(co, year, quarter)
        rows.append(
            (
                qd,
                13 * 60,
                f"Quarterly Governance Meeting – {year} {quarter}",
                QUARTERLY_MEETING_TIME,
                meeting_place_line(co, qd),
            )
        )
    rows.sort(key=lambda r: (r[0], r[1]))
    return [(r[0], r[2], r[3], r[4]) for r in rows]


def board_waiver_of_notice_markdown(company_name_year: str, year: int, co_name: str) -> str:
    """Markdown for sole director waiver of notice (board meetings listed for the year)."""
    co = companies[co_name]
    director_name = "Derek E. Pappas"
    doc_date_iso = annual_meeting_date_str(co, year)
    rows = _board_meeting_rows_for_year(co, year)
    bullet_lines = "\n".join(
        f"- **{title}** — **Date:** {d_iso}; **Time:** {t_str}; **Place / remote means:** {place}"
        for d_iso, title, t_str, place in rows
    )
    bylaws_ref = co.get("board_notice_waiver_bylaws_ref") or "**the Corporation\u2019s bylaws**"
    return f"""
**Waiver of Notice of Meetings of the Board of Directors**
**{co_name}**
{_corporation_parenthetical(co)}

**Calendar year {year}**

The undersigned, **{director_name}**, Sole Director of **{co_name}** (the “Corporation”), intending to be legally bound, **waives all notice** of the time, place, and purposes of each meeting of the Board of Directors of the Corporation listed below, and of any postponement or adjournment of any such meeting, to the extent permitted by the **{_corporation_statute_name(co)}**, the Corporation’s **certificate of incorporation**, and {bylaws_ref}. This waiver is given to supplement the minutes of the Corporation, which state that notice of each such meeting was duly given **or waived**.

**Meetings covered**

{bullet_lines}

{signature_block(director_name, doc_date_iso)}
---
"""


def generate_board_waiver_of_notice(
    company_name_year: str, year: int, co_name: str
) -> None:
    """Optional standalone waiver: sole director waives notice of board meetings minuted for this year (file with minute book).

    Supports the board minutes line that notice of each meeting was duly given **or waived** (Delaware DGCL + typical bylaws).
    """
    co = companies[co_name]
    doc_date_iso = annual_meeting_date_str(co, year)
    content = board_waiver_of_notice_markdown(company_name_year, year, co_name)
    path = f"{company_name_year}_waiver_of_notice_board_meetings.docx"
    print(f"Writing Waiver of Notice (board meetings) to {path}")
    write_docx_from_minutes(content, path, doc_date_iso, co_name)


def signature_block(name, date):
    return f"""**Signature:**

**Director Name:** {name}

**Signature:**
_____________________ 

**Date:** {date}
**Name:** {name}"""


def _sole_director_adopted_resolutions_section(section_heading: str, resolution_parts: list[str]) -> str:
    """Sole-director minutes: resolution list, or explicit none if every part is blank."""
    cleaned = [p.strip() for p in resolution_parts if p and p.strip()]
    if not cleaned:
        return f"{section_heading}\nNone. No resolutions were presented for adoption.\n\n"
    if len(cleaned) == 1:
        intro = "Upon consideration, the Sole Director adopted the following resolution:\n\n"
    else:
        intro = "Upon consideration, the Sole Director adopted the following resolutions:\n\n"
    body = "\n\n".join(cleaned) + "\n\n"
    return f"{section_heading}\n{intro}{body}"


def _agm_president_report_body(co: dict, office_locations: str, dev_locations: str, co_name: str, year: int) -> str:
    """President’s Report narrative: operational baseline, optional product/hosting lines, accomplishments summary, addendum."""
    base = (
        "The Sole Director reported on the Corporation’s operational and engineering activities for the fiscal year, "
        "including centralized management of globally distributed development and the use of operational office location(s) "
        f"during the fiscal year, with operations conducted from {office_locations} and development from {dev_locations}, "
        "while confirming that management, oversight, and decision-making remained centralized and continuously recorded "
        "through the Corporation’s official records. "
    )
    product = co.get(
        "agm_president_report_product_line",
        "The Sole Director summarized continued development of the Corporation’s software and service offerings. ",
    )
    if not product.endswith(" "):
        product = product.rstrip() + " "
    infra_raw = co.get("agm_president_report_infrastructure_line") or ""
    infra = (" " + infra_raw.strip()) if infra_raw.strip() else ""

    summary, detail_items = accomplishments_for_year(co_name, year)
    summary_sentence = ""
    if summary:
        summary_sentence = (
            f" The President’s report included the following **accomplishments summary** for the calendar year {year}: "
            f"{summary}"
        )

    lab = co.get("agm_president_report_operating_exhibit_label")
    if detail_items and not lab:
        lab = "Exhibit B"

    exhibit = ""
    if detail_items and lab:
        exhibit = (
            f" A written addendum annexed as **{lab}** to these minutes sets forth **detailed accomplishments** "
            "for the period covered by the President’s report, together with supplemental technical materials furnished "
            "for the meeting (including technical specifications, roadmaps, KPIs, and architecture diagrams) where applicable."
        )
    elif lab:
        exhibit = (
            f" A written addendum annexed as **{lab}** to these minutes sets forth additional detail furnished for the meeting, "
            "including technical specifications, roadmaps, KPIs, and architecture diagrams."
        )

    ip_close = (
        " All software, algorithms, and intellectual property developed during the year, regardless of development location, "
        "were reaffirmed as the exclusive property of the Corporation."
    )
    return base + product + infra + summary_sentence + exhibit + ip_close


def _agm_resolutions_block(co: dict, director_name: str, year: int) -> str:
    if "annual_board_resolution_blocks" in co:
        parts = list(co["annual_board_resolution_blocks"])
    else:
        parts = [
            f"""**Approval of Financial Reports**  
RESOLVED, that the financial statements for the fiscal year {year} are hereby approved.""",
            f"""**Approval of {year + 1} Budget**  
RESOLVED, that the operating, engineering, and marketing budget for the fiscal year {year + 1} is hereby approved.""",
            f"""**Banking Authorization**  
RESOLVED, that {director_name} is authorized to open, maintain, and manage one or more corporate bank accounts in the name of the Corporation at JPMorgan Chase Bank, N.A., and any successor institution, and to act as the sole authorized signatory with full authority to execute all related documents.""",
        ]
    return _sole_director_adopted_resolutions_section("**VII. Resolutions**", parts)


def _special_resolutions_block(year: int, record_date_resolution: str) -> str:
    parts = [
        f"""**Ratification of International Operations**  
RESOLVED, that all operational and management decisions made during the Corporation’s international operations cycle for the year {year} are hereby ratified, confirmed, and approved in all respects."""
    ]
    extra = record_date_resolution.strip()
    if extra:
        parts.append(extra)
    return _sole_director_adopted_resolutions_section("**III. Resolutions:**", parts)


def _quarterly_resolutions_block(co: dict) -> str:
    if "quarterly_resolution_blocks" in co:
        parts = list(co["quarterly_resolution_blocks"])
    else:
        parts = [
            "RESOLVED, that all operational, infrastructure, and intellectual property assets created during the quarter are hereby ratified, confirmed, and approved as assets of the Corporation."
        ]
    n = len([p for p in parts if p and str(p).strip()])
    if n == 0:
        heading = "**IV. Resolutions**"
    elif n == 1:
        heading = "**IV. Resolution:**"
    else:
        heading = "**IV. Resolutions**"
    return _sole_director_adopted_resolutions_section(heading, parts)


# 3. OUTPUT HELPERS

def write_docx_from_minutes(
    content: str,
    filepath: str,
    meeting_date_iso: str | None = None,
    co_name: str | None = None,
):
    doc = Document()
    for raw_line in content.splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            doc.add_paragraph()
            continue
        # Render inline markdown-style bold using **...** into bold runs
        p = doc.add_paragraph()
        i = 0
        while i < len(line):
            if line[i:i+2] == "**":
                j = line.find("**", i + 2)
                if j != -1:
                    bold_text = line[i+2:j]
                    run = p.add_run(bold_text)
                    run.bold = True
                    i = j + 2
                else:
                    # No closing ** found; write the remaining text as-is
                    p.add_run(line[i:])
                    break
            else:
                next_bold = line.find("**", i)
                if next_bold == -1:
                    p.add_run(line[i:])
                    break
                else:
                    p.add_run(line[i:next_bold])
                    i = next_bold
    doc.save(filepath)
    if meeting_date_iso and co_name:
        _random_utime_after_meeting(filepath, meeting_date_iso, companies[co_name])

# 3. GENERATORS
def generate_agm(co_name, year):
    co = companies[co_name]
    date = annual_meeting_date_str(co, year)
    place = meeting_place_line(co, date)
    issued = co["shares_issued"].get(year, "4,000,000")

    # select locations for the given year
    locations = office_locations_for_year(locations_timeline, year)

    # normalize and format for template insertion
    office_locations = normalize_locations(locations)

    dev_locations = development_locations()

    director_name = "Derek E. Pappas"
    inc_year = co["inc_year"]
    minutes_start_year = co.get("minutes_start_year", inc_year)
    if year > inc_year and (year - 1) >= minutes_start_year:
        prior_date = annual_meeting_date_str(co, year - 1)
        prior_minutes_section = f"""**IV. Approval of Prior Minutes**
The minutes of the prior Annual Meeting of the Board of Directors held on {prior_date} were reviewed and approved by the Sole Director."""
    else:
        prior_minutes_section = f"""**IV. Approval of Prior Minutes**
This was the first Annual Meeting of the Board of Directors following incorporation of the Corporation in {inc_year}; no prior annual meeting of the Board was held and no prior annual board minutes were presented for approval."""

    if co.get("stockholder_meeting") == "annual_meeting_stockholders":
        call_intro = f"Immediately following the Annual Meeting of Stockholders of the Corporation held on {date} commencing at {STOCKHOLDER_MEETING_TIME}, "
    else:
        call_intro = ""

    remote_meeting_line = ""
    if co.get("virtual_ok", True):
        remote_meeting_line = "The Sole Director participated via communications equipment by means of which all persons participating in the meeting could hear each other, and such participation constituted presence in person at the meeting.\n"

    reliance_141e_line = reliance_standard(co)

    consent_cross_ref = ""
    if co.get("stockholder_meeting") == "written_consent":
        as_of_fmt = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
        lab = co.get("sole_stockholder_consent_exhibit_label")
        annex = f" (annexed as **{lab}**)" if lab else ""
        consent_cross_ref = f"""
**Stockholder Written Consent ({year})**  
The Sole Director noted that the **Written Consent of Sole Stockholder** dated {as_of_fmt}, adopting stockholder resolutions under **{_corp_law_section_ref(co, "228")}** for the year {year}, is **on file** with the minutes of the stockholders of the Corporation{annex}.

"""

    return f"""
**Minutes of the Annual Meeting of the Board of Directors**
{_corporation_parenthetical(co)}

**I. Meeting Information**
**Company Name:** {co_name}
**Principal Address:** {co['address']}
**Date:** {date}
**Time:** {BOARD_AGM_TIME}
**Place:** {place}
**Type of Meeting:** Annual Meeting of the Board of Directors

**II. Call to Order**
{call_intro}The Annual Meeting of the Board of Directors of {co_name} (the “Corporation”) was called to order at {BOARD_AGM_TIME} on {date} by {director_name}, acting as Sole Director, President, and Treasurer of the Corporation.

**III. Roll Call and Quorum**
**Director Present:**  
{director_name} (Sole Director)

**Director Absent:**  
None

The Sole Director being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the {_corporation_statute_name(co)}.  
The Sole Director confirmed that notice of the meeting was duly given or waived.
{remote_meeting_line}

{prior_minutes_section}

**V. Reports of Officers**

**President’s Report:**  
{_agm_president_report_body(co, office_locations, dev_locations, co_name, year)}

**Treasurer’s Report:**  
The Treasurer reported that the Corporation remains solvent and that certain outstanding obligations, including notes payable, are contingent and payable upon the occurrence of a future liquidity event, the timing of which has not yet been determined. The Sole Director acknowledged the status of such obligations and confirmed continued oversight of these matters. Franchise taxes and registered agent fees are paid and current. The Corporation has {issued} shares of common stock issued and outstanding at a par value of {co['par']} per share.

{reliance_141e_line}

**VI. Discussion Items**
The Sole Director discussed the Corporation’s transition plan for {year + 1}, including security audits, penetration testing, and commercialization readiness.

{_agm_resolutions_block(co, director_name, year)}
{consent_cross_ref}
**VIII. Adjournment**
There being no further business to come before the Board, the meeting was adjourned.

{signature_block(director_name, date)}
---
"""


def generate_special(co_name, year):
    co = companies[co_name]
    date = annual_meeting_date_str(co, year)
    place = meeting_place_line(co, date)

    director_name = "Derek E. Pappas"

    remote_meeting_line = ""
    if co.get("virtual_ok", True):
        remote_meeting_line = "The Sole Director participated via communications equipment by means of which all persons participating in the meeting could hear each other, and such participation constituted presence in person at the meeting.\n"

    reliance_141e_line = reliance_standard(co)

    record_date_resolution = ""
    if co.get("stockholder_meeting") == "annual_meeting_stockholders":
        rd = stockholder_annual_record_date_str(co, year)
        record_date_resolution = f"""
**Record Date for Annual Meeting of Stockholders ({_corp_law_section_ref(co, "213")})**  
RESOLVED, that **{rd}** is hereby fixed as the record date for determining the stockholders entitled to notice of and to vote at the Annual Meeting of Stockholders of the Corporation to be held on **{date}** commencing at **{STOCKHOLDER_MEETING_TIME}**, in accordance with the Corporation’s bylaws and the {_corporation_statute_name(co)}.

"""

    return f"""
**Minutes of the Special Meeting of the Board of Directors - {year}**
**{co_name}**
*(Board of Directors – {_jurisdiction(co)} corporation)*

**Meeting Details**
**Date of Meeting:** {date}
**Time of Meeting:** {SPECIAL_MEETING_TIME}
**Location of Meeting:** {place}
**Purpose:** Pre-annual review of international operations

**I. Call to Order:**
The Special Meeting of the Board of Directors of {co_name} (the “Corporation”) was called to order at {SPECIAL_MEETING_TIME} on {date} by {director_name}, acting as Sole Director of the Corporation.

**II. Roll Call and Quorum:**
**Director Present:** {director_name} (Sole Director)  
**Director Absent:** None  

The Sole Director being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the {_corporation_statute_name(co)}.  
The Sole Director confirmed that notice of the meeting was duly given or waived.
{remote_meeting_line}

{_special_resolutions_block(year, record_date_resolution)}
{reliance_141e_line}

**IV. Adjournment:**
There being no further business to come before the Board, the meeting was adjourned.

{signature_block(director_name, date)}
---"""


def generate_quarterly(co_name, year, quarter):
    co = companies[co_name]
    date = quarterly_meeting_date_str(co, year, quarter)
    place = meeting_place_line(co, date)

    dev_locations = development_locations()

    director_name = "Derek E. Pappas"

    remote_meeting_line = ""
    if co.get("virtual_ok", True):
        remote_meeting_line = "The Sole Director participated via communications equipment by means of which all persons participating in the meeting could hear each other, and such participation constituted presence in person at the meeting.\n"

    reliance_141e_line = reliance_standard(co)

    return f"""
**Minutes of the Quarterly Governance Meeting - {year} {quarter}**
**{co_name}**
*(Board of Directors – {_jurisdiction(co)} corporation)*

**Meeting Details**
**Date of Meeting:** {date}
**Time of Meeting:** {QUARTERLY_MEETING_TIME}
**Location of Meeting:** {place}

**I. Call to Order:**
The Quarterly Governance Meeting of the Board of Directors of {co_name} (the “Corporation”) was called to order at {QUARTERLY_MEETING_TIME} on {date} by {director_name}, acting as Sole Director of the Corporation.

**II. Roll Call and Quorum:**
**Director Present:** {director_name} (Sole Director)  
**Director Absent:** None  

The Sole Director being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the {_corporation_statute_name(co)}.  
The Sole Director confirmed that notice of the meeting was duly given or waived.
{remote_meeting_line}

**III. Business Review:**
The Sole Director reviewed quarterly infrastructure stability and confirmed that all assets, including software and related intellectual property, created during the quarter in the development centers located in {dev_locations} are properly titled to and are the exclusive property of the Corporation.

{reliance_141e_line}

{_quarterly_resolutions_block(co)}

**V. Adjournment:**
There being no further business to come before the Board, the meeting was adjourned.

{signature_block(director_name, date)}
---"""

def generate_quarterly_summary(company_name_year, year, quarter, co_name):
    """Generate a summary of the quarterly meeting for reporting purposes."""
    co = companies[co_name]
    qdate = quarterly_meeting_date_str(co, year, quarter)
    quarterly_docx = f"{company_name_year}_quarterly_{year}_{quarter}.docx"
    quarterly_content = generate_quarterly(co_name, year, quarter)
    print(f"Writing Quarterly meeting minutes to {quarterly_docx}")
    write_docx_from_minutes(quarterly_content, quarterly_docx, qdate, co_name)
    print(f"Generating file for {co_name} {year} {quarter}")


def generate_annual_meeting_stockholders(co_name, year):
    """Formal annual meeting minutes for corporations with more than one stockholder (e.g. DATA RECORD SCIENCE, INC.)."""
    co = companies[co_name]
    date = annual_meeting_date_str(co, year)
    record_date = stockholder_annual_record_date_str(co, year)
    place = meeting_place_line(co, date)
    issued = co["shares_issued"].get(year, co["shares_issued"].get(2025))

    chair = "Derek E. Pappas"
    election_standard = co.get("director_election_standard", "plurality")
    election_sentence = (
        "Directors were elected by a plurality of the votes cast by the shares present in person or by proxy and entitled to vote."
        if election_standard == "plurality"
        else "Directors were elected by the requisite vote under the Corporation’s bylaws and applicable law."
    )

    roll_block = format_stockholders_roll_call_block(co)
    record_date_source = (
        f"The Chairperson confirmed that **{record_date}** had been fixed as the **record date** for determining the stockholders entitled to vote at this meeting "
        f"by the Board of Directors pursuant to resolutions adopted at the **Special Meeting of the Board of Directors** held on **{date}** "
        f"(as reflected in the minutes of such meeting), in accordance with the Corporation’s bylaws and the {_corporation_statute_name(co)}."
    )

    return f"""
**Minutes of the Annual Meeting of Stockholders**
**{co_name}**
{_corporation_parenthetical(co)}

**I. Meeting Information**
**Company Name:** {co_name}
**Principal Address:** {co['address']}
**Date:** {date}
**Time:** {STOCKHOLDER_MEETING_TIME}
**Place:** {place}
**Record Date (stockholders entitled to vote; {_corp_law_section_ref(co, "213")}):** {record_date}
**Type of Meeting:** Annual Meeting of Stockholders

**II. Call to Order and Organization**
The Annual Meeting of Stockholders of {co_name} (the “Corporation”) was called to order commencing at {STOCKHOLDER_MEETING_TIME} on {date}. Pursuant to the Corporation’s bylaws, {chair}, acting as President of the Corporation, served as Chairperson of the meeting, and the Secretary (or a person designated by the Chairperson) served as Secretary of the meeting.

**III. Roll Call and Quorum**
{record_date_source}

The following stockholders were present in person or by remote participation (as permitted under the Corporation’s bylaws and applicable law) and were entitled to vote at the meeting:

{roll_block}

The Chairperson declared that a quorum of stockholders was present and that the meeting was duly constituted to transact business.
The Chairperson further confirmed that any stockholders participating remotely were able to hear and be heard contemporaneously and that the Corporation had reasonable means to verify that each such person was a stockholder or proxyholder entitled to vote at the meeting.

**Stock Ledger / Voting List; Proxies (bylaws and applicable law)**
The Chairperson confirmed that an **alphabetized list of the names of the stockholders of record** entitled to vote at this meeting (or a certified extract of the stock ledger) as of the record date was produced and made available for inspection by stockholders at the meeting in accordance with the Corporation’s bylaws, and that **proxies** and votes received in accordance with the bylaws were accepted for shares entitled to vote in accordance with such proxies.

{_annual_stockholder_notice_section_iv(co)}

**V. Reports**
The Chairperson presented and summarized the Corporation’s **operational and financial highlights** for the fiscal year. Stockholders had a reasonable opportunity to **ask questions** regarding the Chairperson’s report.

**VI. Election of Directors**
The following resolution was presented and adopted by the stockholders by the requisite vote under the Corporation’s bylaws and applicable law:

**Election of Director**  
RESOLVED, that {chair} is hereby elected as a director of the Corporation, to serve until the next annual meeting of stockholders and until such director’s successor is duly elected and qualified.

{election_sentence}

**VII. Shares Outstanding**
The Chairperson noted for the record that the Corporation had {issued} shares of common stock issued and outstanding at a par value of {co['par']} per share as of the date of the meeting.

**VIII. Adjournment**
There being no further business properly brought before the meeting, the meeting was adjourned.

**Signature:**

**Chairperson of the Meeting:** {chair}

**Signature:**
_____________________

**Date:** {date}
---
"""


def majority_stockholder_written_consent_ratification_markdown(
    company_name_year: str, year: int, co_name: str
) -> str:
    """Markdown for majority stockholder written consent (ratification; action by written consent)."""
    co = companies[co_name]
    board_date = annual_meeting_date_str(co, year)
    as_of = datetime.strptime(board_date, "%Y-%m-%d").strftime("%B %d, %Y")
    mechanics = f"""**Written Consent Mechanics**
This Written Consent is intended to be delivered to the Corporation and to become effective in accordance with the {_corporation_statute_name(co)} and the Corporation’s bylaws, including any timing requirements applicable to the delivery of consents bearing dated signatures. The Corporation is authorized and directed to file this Written Consent with the minutes of the proceedings of the stockholders of the Corporation and to give any prompt notice required by applicable law, the certificate of incorporation, and the bylaws."""
    return f"""
**{co_name}.**
**Written Consent of Majority Stockholders**
**Action by Written Consent of Stockholders**
({_corp_law_section_ref(co, "228")})

The undersigned, being the stockholders of {co_name}, a {_jurisdiction(co)} corporation (the "Corporation"), holding not less than the minimum number of votes that would be necessary to authorize the following action at a meeting at which all shares entitled to vote thereon were present and voted, hereby adopt the following resolutions by written consent pursuant to the {_corporation_statute_name(co)}, effective as of the date set forth below.

**Ratification of Annual Board Meeting**
RESOLVED, that all actions taken and resolutions adopted by the Board of Directors of the Corporation at the Annual Meeting of the Board of Directors held on {as_of} (or as otherwise recorded in the minutes of such meeting), including the approval of financial statements, the budget for the ensuing fiscal year, officer actions, and banking authorizations, are hereby ratified, confirmed, and approved in all respects.

**Notice to Non-Consenting Stockholders**
RESOLVED, that the Corporation is authorized and directed to provide prompt notice of the taking of the foregoing corporate action by written consent, to the extent required by applicable law, the Corporation’s certificate of incorporation, and the Corporation’s bylaws.

{mechanics}

**Effective Date**
This Written Consent shall be effective as of {as_of}, and shall be filed with the minutes of the proceedings of the stockholders of the Corporation.

**Stockholders:**
______________________________

______________________________

**Date:** {as_of}
---
"""


def generate_majority_stockholder_written_consent_ratification(company_name_year: str, year: int, co_name: str):
    """Majority stockholder written consent ratifying same-year annual board actions, for multi-stockholder corporations."""
    co = companies[co_name]
    board_date = annual_meeting_date_str(co, year)
    content = majority_stockholder_written_consent_ratification_markdown(company_name_year, year, co_name)
    output = f"{company_name_year}_majority_stockholders_written_consent_ratification_of_annual_board_actions.docx"
    print(f"Writing Majority Stockholders Written Consent (ratification) to {output}")
    write_docx_from_minutes(content, output, board_date, co_name)

def sanitize_company_name(name):
    # remove the comma from company name for file naming
    safe_name = name.replace(", ", "_").replace(" ", "_")
    
    # remove a dot at the end
    if safe_name.endswith("."):
        safe_name = safe_name[:-1]
    
    # remove any remaining dots
    

    # remove "Inc" or "inc" from the end
    if safe_name.lower().endswith("inc"):
        safe_name = safe_name[:-3]
    
    # lowercase the company name for file naming
    safe_name = safe_name.lower()
    
    # remove trailing underscores
    safe_name = safe_name.rstrip('_')
    
    # replace . with underscore
    safe_name = safe_name.replace('.', '_')
    
    return safe_name



def generate_annual(company_name_year: str, co_name: str, year: int):
    co = companies[co_name]
    mdate = annual_meeting_date_str(co, year)
    agm_title = f"{company_name_year}_agm"
    agm_docx = f"{agm_title}.docx"
    agm_content = generate_agm(co_name, year)
    print(f"Writing AGM minutes to {agm_docx}")
    write_docx_from_minutes(agm_content, agm_docx, mdate, co_name)

    _summary, detail_items = accomplishments_for_year(co_name, year)
    exhibit = co.get("agm_president_report_operating_exhibit_label")
    if detail_items and not exhibit:
        exhibit = "Exhibit B"
    addendum_path = f"{company_name_year}_agm_operating_addendum.docx"
    if detail_items and exhibit:
        _generate_agm_operating_addendum_docx(company_name_year, co_name, year, exhibit, detail_items)
    elif os.path.isfile(addendum_path):
        os.remove(addendum_path)


def generate_special_meeting(company_name_year: str, co_name: str, year: int):
    """Generate special meeting minutes."""
    co = companies[co_name]
    mdate = annual_meeting_date_str(co, year)
    special_title = f"{company_name_year}_yearly_special_meeting"
    special_docx = f"{special_title}.docx"
    special_content = generate_special(co_name, year)
    print(f"Writing Special meeting minutes to {special_docx}")
    write_docx_from_minutes(special_content, special_docx, mdate, co_name)


def sole_stockholder_written_consent_markdown(co_name: str, year: int) -> str:
    """Markdown for sole stockholder written consent (action by written consent)."""
    co = companies[co_name]
    display_name = minutes_display_name(co_name)
    date = annual_meeting_date_str(co, year)
    as_of = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
    shareholder_term = "Sole Stockholder"
    voting_shares = co.get(
        "voting_shares_description",
        "all of the outstanding shares of the Corporation entitled to vote on the following matters",
    )
    bylaws_ack = co.get("stockholder_consent_bylaws_acknowledgment")
    bylaws_ack_block = f"\n{bylaws_ack}\n" if bylaws_ack else ""
    mech_suffix = co.get("stockholder_consent_bylaws_mechanics_suffix")
    mech_tail = f" {mech_suffix}" if mech_suffix else ""
    mechanics = f"""**Written Consent Mechanics**
This Written Consent is intended to be delivered to the Corporation and to become effective in accordance with the {_corporation_statute_name(co)} and the Corporation’s bylaws, including any timing requirements applicable to the delivery of consents bearing dated signatures.{mech_tail} The Corporation is authorized and directed to file this Written Consent with the minutes of the proceedings of the stockholders of the Corporation and to give any prompt notice required by applicable law, the certificate of incorporation, and the bylaws (to the extent applicable)."""
    consent_heading = (
        f"({_corp_law_section_ref(co, '228')}; annual meeting of stockholders)"
        if _jurisdiction(co) == "DE"
        else "(annual meeting of stockholders)"
    )
    return f"""
**{display_name}**
**Written Consent of {shareholder_term}**
**Action by Written Consent of Stockholders**
{consent_heading}

The undersigned, being the {shareholder_term.lower()} of {display_name}, a {_jurisdiction(co)} corporation (the "Corporation"), and holding {voting_shares}, hereby adopts the following resolutions by written consent of the stockholders pursuant to the {_corporation_statute_name(co)}, effective without a meeting to the same extent as if adopted at a duly held meeting. The undersigned acknowledges that, to the best of the undersigned’s knowledge, the Corporation’s certificate of incorporation does not prohibit stockholder action by written consent as contemplated hereby, including action by the holders of outstanding shares of capital stock having not less than the minimum number of votes that would be necessary to authorize or take such action at a meeting at which all shares entitled to vote thereon were present and voted.{bylaws_ack_block}
**Approval of Board Actions**
RESOLVED, that all actions taken and resolutions adopted by the Board of Directors of the Corporation at the Annual Meeting of the Board of Directors held on {as_of} (or as otherwise recorded in the minutes of such meeting), including but not limited to the approval of financial statements, budgets, officer actions, and banking authorizations, are hereby ratified, confirmed, and approved in all respects.

**Annual Meeting of Stockholders**
RESOLVED, that the matters set forth in this Written Consent, including ratification of the Board’s actions taken at the annual board meeting referenced above, constitute or supplement, as applicable, the business addressed for purposes of the annual meeting of stockholders for the year {year} to the extent permitted by the {_corporation_statute_name(co)}, the certificate of incorporation, and the bylaws of the Corporation, and the undersigned waives any requirement to convene a separate annual meeting of stockholders for such year solely to duplicate the matters resolved herein.

{mechanics}

**Effective Date**
This Written Consent shall be effective as of {as_of}, and shall be filed with the minutes of the proceedings of the stockholders of the Corporation.

**Stockholder Certification**
{shareholder_term}:
Derek E. Pappas

**Signature:** ___________________________
**Date:** {as_of}
---"""


def generate_written_consent(company_name_year: str, year: int, company_name: str):
    """Generate sole stockholder written consent under applicable corporate law (.docx)."""
    co = companies[company_name]
    date = annual_meeting_date_str(co, year)
    content = sole_stockholder_written_consent_markdown(company_name, year)
    output = f"{company_name_year}_written_consent_in_lieu_of_annual_meeting.docx"
    print(f"Writing Stockholder Written Consent to {output}")
    write_docx_from_minutes(content, output, date, company_name)


def generate_stockholder_side(company_name_year: str, year: int, co_name: str):
    co = companies[co_name]
    kind = co.get("stockholder_meeting", "written_consent")
    if kind == "annual_meeting_stockholders":
        mdate = annual_meeting_date_str(co, year)
        out = f"{company_name_year}_annual_meeting_of_stockholders.docx"
        print(f"Writing Annual Meeting of Stockholders minutes to {out}")
        write_docx_from_minutes(generate_annual_meeting_stockholders(co_name, year), out, mdate, co_name)
        generate_stockholder_waiver_of_notice_annual_meeting(company_name_year, year, co_name)
        generate_notice_of_annual_stockholder_meeting(company_name_year, year, co_name)
        generate_majority_stockholder_written_consent_ratification(company_name_year, year, co_name)
    else:
        generate_written_consent(company_name_year, year, co_name)
    

import argparse


def _company_years_for_calendar(co: dict, years: tuple[int, ...]) -> list[int]:
    start = max(co.get("minutes_start_year", co.get("inc_year", min(years))), min(years))
    return [y for y in years if y >= start]


def write_company_calendars(output_dir: str = "calendars", years: tuple[int, ...] = (2022, 2023, 2024, 2025, 2026)) -> None:
    """
    Produce one .txt file per company with meetings grouped by date.

    Format:
    - Company name at top
    - For each date: date on its own line
    - Then indented lines: "<Company> - <Meeting Name> - <Time>"
    - One blank line between dates
    """
    os.makedirs(output_dir, exist_ok=True)

    quarterly_month = {"Q1": 3, "Q2": 6, "Q3": 9, "Q4": 12}

    unified_entries: list[tuple[str, str, str, str]] = []
    # tuple: (date_iso, time_str, company_name, meeting_label)

    for co_name, co in companies.items():
        entries_by_date: dict[str, list[str]] = {}

        for year in _company_years_for_calendar(co, years):
            annual_date = annual_meeting_date_str(co, year)
            # Special meeting template currently uses the same date as the annual board meeting.
            special_date = annual_date

            if co.get("stockholder_meeting") == "annual_meeting_stockholders":
                entries_by_date.setdefault(annual_date, []).append(f"{co_name} - Annual Meeting of Stockholders - {STOCKHOLDER_MEETING_TIME}")
                entries_by_date.setdefault(annual_date, []).append(f"{co_name} - Annual Meeting of the Board of Directors - {BOARD_AGM_TIME}")
                entries_by_date.setdefault(annual_date, []).append(f"{co_name} - Majority Stockholders Written Consent (Ratification) - {STOCKHOLDER_MEETING_TIME}")

                unified_entries.append((annual_date, STOCKHOLDER_MEETING_TIME, co_name, "Annual Meeting of Stockholders"))
                unified_entries.append((annual_date, BOARD_AGM_TIME, co_name, "Annual Meeting of the Board of Directors"))
                unified_entries.append((annual_date, STOCKHOLDER_MEETING_TIME, co_name, "Majority Stockholders Written Consent (Ratification)"))
            else:
                entries_by_date.setdefault(annual_date, []).append(f"{co_name} - Annual Meeting of the Board of Directors - {BOARD_AGM_TIME}")
                entries_by_date.setdefault(annual_date, []).append(f"{co_name} - Stockholder Written Consent - {STOCKHOLDER_MEETING_TIME}")

                unified_entries.append((annual_date, BOARD_AGM_TIME, co_name, "Annual Meeting of the Board of Directors"))
                unified_entries.append((annual_date, STOCKHOLDER_MEETING_TIME, co_name, "Stockholder Written Consent"))

            entries_by_date.setdefault(special_date, []).append(
                f"{co_name} - Yearly Special Meeting (Board) - {SPECIAL_MEETING_TIME}"
            )
            unified_entries.append((special_date, SPECIAL_MEETING_TIME, co_name, "Yearly Special Meeting (Board)"))

            for q in ("Q1", "Q2", "Q3", "Q4"):
                q_date = quarterly_meeting_date_str(co, year, q)
                entries_by_date.setdefault(q_date, []).append(
                    f"{co_name} - Quarterly Meeting (Board) {q} - {QUARTERLY_MEETING_TIME}"
                )
                unified_entries.append((q_date, QUARTERLY_MEETING_TIME, co_name, f"Quarterly Meeting (Board) {q}"))

        lines: list[str] = [co_name, ""]
        for d in sorted(entries_by_date.keys()):
            lines.append(d)
            for item in entries_by_date[d]:
                lines.append(f"  {item}")
            lines.append("")  # blank line between dates

        out_path = os.path.join(output_dir, f"{sanitize_company_name(co_name)}_calendar.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines).rstrip() + "\n")

    # Unified calendar + conflict check across companies (same date + same time, different companies)
    by_date: dict[str, list[tuple[str, str, str]]] = {}
    by_slot: dict[tuple[str, str], list[tuple[str, str]]] = {}
    # by_slot[(date,time)] => [(company, meeting_label), ...]

    for d, t, co_name, label in unified_entries:
        by_date.setdefault(d, []).append((t, co_name, label))
        by_slot.setdefault((d, t), []).append((co_name, label))

    conflicts: list[tuple[str, str, list[tuple[str, str]]]] = []
    for (d, t), items in sorted(by_slot.items()):
        companies_in_slot = {co for co, _ in items}
        if len(companies_in_slot) > 1:
            conflicts.append((d, t, items))

    unified_lines: list[str] = ["Unified Meeting Calendar", ""]
    if conflicts:
        unified_lines.append("Conflict Summary (same date + time across companies)")
        for d, t, items in conflicts:
            unified_lines.append(f"{d} {t}")
            for co_name, label in items:
                unified_lines.append(f"  {co_name} - {label} - {t}")
            unified_lines.append("")
        unified_lines.append("---")
        unified_lines.append("")
    else:
        unified_lines.append("Conflict Summary: none detected (across companies)")
        unified_lines.append("")
        unified_lines.append("---")
        unified_lines.append("")

    for d in sorted(by_date.keys()):
        unified_lines.append(d)
        for t, co_name, label in sorted(by_date[d], key=lambda x: (x[0], x[1], x[2])):
            unified_lines.append(f"  {co_name} - {label} - {t}")
        unified_lines.append("")

    unified_path = os.path.join(output_dir, "unified_calendar.txt")
    with open(unified_path, "w", encoding="utf-8") as f:
        f.write("\n".join(unified_lines).rstrip() + "\n")

    conflicts_path = os.path.join(output_dir, "conflicts.txt")
    with open(conflicts_path, "w", encoding="utf-8") as f:
        if not conflicts:
            f.write("No conflicts detected (same date + time across different companies).\n")
        else:
            f.write("Conflicts detected (same date + time across different companies):\n\n")
            for d, t, items in conflicts:
                f.write(f"{d} {t}\n")
                for co_name, label in items:
                    f.write(f"  {co_name} - {label} - {t}\n")
                f.write("\n")


def print_schedule(years=(2022, 2023, 2024, 2025, 2026)):
    """Print the computed meeting schedule without generating .docx files."""
    print("Schedule (all times local):")
    for year in years:
        print(f"\nYear {year}")
        for co_name, co in companies.items():
            if year < co.get("minutes_start_year", co.get("inc_year", year)):
                continue
            board_date = annual_meeting_date_str(co, year)
            if co.get("stockholder_meeting") == "annual_meeting_stockholders":
                stock_date = annual_meeting_date_str(co, year)
                print(
                    f"- {co_name}: Stockholders {stock_date} {STOCKHOLDER_MEETING_TIME}; "
                    f"Board {board_date} {BOARD_AGM_TIME}"
                )
            else:
                print(f"- {co_name}: Board {board_date} {BOARD_AGM_TIME}; Written consent dated {board_date}")


# Between meeting bodies in the per-company compilation: one empty paragraph (“hard” break) in the .docx output.
MEETING_BOOK_SEPARATOR = "\n\n"


def _minute_book_line_to_paragraph_xml(line: str) -> str:
    """Escape for ReportLab Paragraph XML; convert **bold** to <b>."""
    s = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)


def _write_minute_book_pdf(markdown: str, pdf_path: str) -> None:
    """Letter-size PDF, continuous page numbers in footer (single volume)."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import inch
        from reportlab.platypus import HRFlowable, Paragraph, SimpleDocTemplate, Spacer
    except ModuleNotFoundError as e:
        raise RuntimeError(
            "minute book PDF requires reportlab (see pyproject.toml). "
            "Install project deps: poetry install"
        ) from e

    styles = getSampleStyleSheet()
    body_style = ParagraphStyle(
        "MinuteBookBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10,
        leading=12,
        spaceAfter=4,
        alignment=TA_LEFT,
    )

    story: list = []
    for raw in markdown.splitlines():
        line = raw.rstrip()
        if not line.strip():
            story.append(Spacer(1, 10))
        elif line.strip() == "---":
            story.append(Spacer(1, 6))
            story.append(
                HRFlowable(
                    width=letter[0] - 1.5 * inch,
                    thickness=0.5,
                    color=colors.HexColor("#bbbbbb"),
                    hAlign="CENTER",
                )
            )
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(_minute_book_line_to_paragraph_xml(line), body_style))

    def _page_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.drawRightString(letter[0] - 0.75 * inch, 0.55 * inch, f"Page {canvas.getPageNumber()}")
        canvas.restoreState()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.85 * inch,
        onFirstPage=_page_footer,
        onLaterPages=_page_footer,
    )
    doc.build(story)


def _markdown_chunks_for_calendar_year(company_name_year: str, co_name: str, year: int) -> list[str]:
    """Same meeting set/order as `generate_all` for one year: AGM (+ addendum if any), special, stockholder pack, board waiver, quarterlies."""
    co = companies[co_name]
    chunks: list[str] = [generate_agm(co_name, year).rstrip()]
    _summary, detail_items = accomplishments_for_year(co_name, year)
    exhibit = co.get("agm_president_report_operating_exhibit_label")
    if detail_items and not exhibit:
        exhibit = "Exhibit B"
    if detail_items and exhibit:
        chunks.append(agm_operating_addendum_markdown(co_name, year, exhibit, detail_items).rstrip())
    chunks.append(generate_special(co_name, year).rstrip())
    if co.get("stockholder_meeting") == "annual_meeting_stockholders":
        chunks.append(generate_annual_meeting_stockholders(co_name, year).rstrip())
        chunks.append(
            stockholder_waiver_of_notice_annual_meeting_markdown(company_name_year, year, co_name).rstrip()
        )
        chunks.append(notice_of_annual_stockholder_meeting_markdown(company_name_year, year, co_name).rstrip())
        chunks.append(
            majority_stockholder_written_consent_ratification_markdown(company_name_year, year, co_name).rstrip()
        )
    else:
        chunks.append(sole_stockholder_written_consent_markdown(co_name, year).rstrip())
    chunks.append(board_waiver_of_notice_markdown(company_name_year, year, co_name).rstrip())
    for quarter in ("Q1", "Q2", "Q3", "Q4"):
        chunks.append(generate_quarterly(co_name, year, quarter).rstrip())
    return chunks


def generate_company_all_meetings_book(
    safe_company_name: str,
    co_name: str,
    years: tuple[int, ...],
    books_dir: str,
) -> None:
    """Compiled minute book per company: .docx (editable) + .pdf (distribution), written to `books_dir`."""
    co = companies[co_name]
    start_year = co.get("minutes_start_year", co.get("inc_year", min(years)))
    applicable = [y for y in years if y >= start_year]
    if not applicable:
        return
    parts: list[str] = [
        f"""**Minute book compilation — all meetings**
**{minutes_display_name(co_name)}**
*(single document: all meetings generated for calendar years {applicable[0]} through {applicable[-1]})*

---
""".strip()
    ]
    for y in applicable:
        parts.append(f"**Calendar year {y}**")
        cny = f"{safe_company_name}_{y}"
        parts.extend(_markdown_chunks_for_calendar_year(cny, co_name, y))
    book = MEETING_BOOK_SEPARATOR.join(p for p in parts if p)
    os.makedirs(books_dir, exist_ok=True)
    out_docx = os.path.join(books_dir, f"{safe_company_name}_all_meetings_book.docx")
    out_pdf = os.path.join(books_dir, f"{safe_company_name}_all_meetings_book.pdf")
    mdate = annual_meeting_date_str(co, applicable[-1])
    print(f"Writing compiled minute book to {out_docx}")
    write_docx_from_minutes(book, out_docx, mdate, co_name)
    print(f"Writing compiled minute book PDF to {out_pdf}")
    _write_minute_book_pdf(book, out_pdf)


def generate_all(output_root: str, years=(2022, 2023, 2024, 2025, 2026)):
    print(f"Current working directory: {os.getcwd()}")
    root_dir = os.path.join(os.getcwd(), output_root)
    os.makedirs(root_dir, exist_ok=True)
    books_dir = os.path.join(root_dir, "books")
    os.makedirs(books_dir, exist_ok=True)

    for name in companies.keys():
        print(f"Company {name} Current working directory: {os.getcwd()}")

        os.chdir(root_dir)
        safe_company_name = sanitize_company_name(name)

        company_dir = f"{safe_company_name}"
        os.makedirs(company_dir, exist_ok=True)
        os.chdir(company_dir)

        start_year = companies[name].get(
            "minutes_start_year", companies[name].get("inc_year", min(years))
        )
        year_prefix = re.compile(rf"^{re.escape(safe_company_name)}_(\d{{4}})_")
        for entry in os.listdir("."):
            if not entry.endswith(".docx"):
                continue
            m = year_prefix.match(entry)
            if m and int(m.group(1)) < start_year:
                os.remove(entry)

        for year in years:
            if year < companies[name].get("minutes_start_year", companies[name].get("inc_year", year)):
                continue
            company_name_year = f"{safe_company_name}_{year}"

            generate_annual(company_name_year, name, year)
            generate_special_meeting(company_name_year, name, year)
            generate_stockholder_side(company_name_year, year, name)
            generate_board_waiver_of_notice(company_name_year, year, name)

            for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                generate_quarterly_summary(company_name_year, year, quarter, name)

        generate_company_all_meetings_book(safe_company_name, name, years, books_dir)


def main():
    parser = argparse.ArgumentParser(description="Generate corporate meeting minutes (.docx).")
    parser.add_argument(
        "--print-schedule",
        action="store_true",
        help="Print computed annual meeting dates/times without generating documents.",
    )
    parser.add_argument(
        "--write-calendars",
        action="store_true",
        help="Write per-company meeting calendar .txt files (does not generate .docx).",
    )
    parser.add_argument(
        "--output-root",
        default="generated",
        help="Output folder (relative to current working directory). Default: generated",
    )
    parser.add_argument(
        "--calendar-output-dir",
        default="calendars",
        help="Calendar output folder (relative to current working directory). Default: calendars",
    )
    args = parser.parse_args()

    if args.print_schedule:
        print_schedule()
        return
    if args.write_calendars:
        write_company_calendars(output_dir=args.calendar_output_dir)
        return

    generate_all(output_root=args.output_root)


if __name__ == "__main__":
    main()
