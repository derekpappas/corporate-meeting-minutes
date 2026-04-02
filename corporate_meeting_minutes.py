from datetime import date, datetime, timedelta
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
STOCKHOLDER_MEETING_TIME = "1:00 PM"
BOARD_AGM_TIME = "1:00 PM"
QUARTERLY_MEETING_TIME = "1:00 PM"
SPECIAL_MEETING_TIME = "12:00 PM"

companies = {
    "Hippo, Inc": {
        "address": "30 N Gould St Ste 21106, Sheridan, WY 82801",
        "par": "$.0001",
        "inc_year": 2022,
        "minutes_start_year": 2022,
        "director_election_standard": "plurality",
        "shares_issued": {2022: "8,000,000", 2023: "8,160,000", 2024: "8,160,000", 2025: "8,160,000"},
        "annual_day_offset": 0,
        "meeting_stagger_day": 0,
        "stockholder_meeting": "written_consent",
        "use_timeline_place": True,
        "virtual_ok": True,
    },
    "Ritual Growth, Inc.": {
        "address": "30 N Gould St Ste 27616, Sheridan, WY 82801",
        "par": "$.0001",
        "inc_year": 2022,
        "minutes_start_year": 2022,
        "shares_issued": {2022: "4,000,000", 2023: "4,000,000", 2024: "4,000,000", 2025: "4,000,000"},
        "annual_day_offset": 1,
        "meeting_stagger_day": 1,
        "stockholder_meeting": "written_consent",
        "use_timeline_place": True,
        "virtual_ok": True,
    },
    "DATA RECORD SCIENCE, INC.": {
        "address": "30 N Gould St Ste 24165, Sheridan, WY 82801",
        "par": "$0.001",
        # Originally incorporated in Delaware in 2006 (as Yoterra, Inc.), later renamed to Data Record Science, Inc.
        "inc_year": 2006,
        "minutes_start_year": 2022,
        "director_election_standard": "plurality",
        "shares_issued": {2022: "5,346,132", 2023: "5,346,132", 2024: "5,346,132", 2025: "5,346,132"},
        "annual_day_offset": 2,
        "meeting_stagger_day": 2,
        "stockholder_meeting": "annual_meeting_stockholders",
        "use_timeline_place": True,
        "virtual_ok": True,
    },
    "TeamBoost.ai, Inc.": {
        "address": "30 N Gould St Ste 23049, Sheridan, WY 82801",
        "par": "$.0001",
        # Filed January 30, 2023 (Delaware).
        "inc_year": 2023,
        "minutes_start_year": 2023,
        "shares_issued": {2023: "10,000,000", 2024: "10,000,000", 2025: "10,000,000"},
        "annual_day_offset": 3,
        "meeting_stagger_day": 3,
        "stockholder_meeting": "written_consent",
        "use_timeline_place": True,
        "virtual_ok": True,
    },
}

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


def signature_block(name, date):
    return f"""**Signature:**

**Director Name:** {name}

**Signature:**
_____________________ 

**Date:** {date}
**Name:** {name}"""

# 3. OUTPUT HELPERS

def write_docx_from_minutes(content: str, filepath: str):
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

    reliance_141e_line = (
        "In taking the actions reflected in these minutes, the Sole Director relied in good faith on information, opinions, reports, and statements presented by officers of the Corporation and other persons as to matters the Sole Director reasonably believed were within such persons’ professional or expert competence, as contemplated by Section 141(e) of the Delaware General Corporation Law.\n"
    )

    return f"""
**Minutes of the Annual Meeting of the Board of Directors**
*(Delaware Corporation)*

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

The Sole Director being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the Delaware General Corporation Law.  
The Sole Director confirmed that notice of the meeting was duly given or waived.
{remote_meeting_line}

{prior_minutes_section}

**V. Reports of Officers**

**President’s Report:**  
The Sole Director reported on the Corporation’s operational and engineering activities for the fiscal year, including centralized management of globally distributed development and the use of operational office location(s) during the fiscal year, with operations conducted from {office_locations} and development from {dev_locations}, while confirming that management, oversight, and decision-making remained centralized and continuously recorded through the Corporation’s official records. All software, algorithms, and intellectual property developed during the year, regardless of development location, were reaffirmed as the exclusive property of the Corporation.

**Treasurer’s Report:**  
The Treasurer reported that the Corporation remains solvent and that certain outstanding obligations, including notes payable, are contingent and payable upon the occurrence of a future liquidity event, the timing of which has not yet been determined. The Sole Director acknowledged the status of such obligations and confirmed continued oversight of these matters. Franchise taxes and registered agent fees are paid and current. The Corporation has {issued} shares of common stock issued and outstanding at a par value of {co['par']} per share.

{reliance_141e_line}

**VI. Discussion Items**
The Sole Director discussed the Corporation’s transition plan for {year + 1}, including security audits, penetration testing, and commercialization readiness.

**VII. Resolutions**
Upon consideration, the Sole Director adopted the following resolutions:

**Approval of Financial Reports**  
RESOLVED, that the financial statements for the fiscal year {year} are hereby approved.

**Approval of {year + 1} Budget**  
RESOLVED, that the operating, engineering, and marketing budget for the fiscal year {year + 1} is hereby approved.

**Banking Authorization**  
RESOLVED, that {director_name} is authorized to open, maintain, and manage one or more corporate bank accounts in the name of the Corporation at JPMorgan Chase Bank, N.A., and any successor institution, and to act as the sole authorized signatory with full authority to execute all related documents.

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

    reliance_141e_line = (
        "In taking the actions reflected in these minutes, the Sole Director relied in good faith on information, opinions, reports, and statements presented by officers of the Corporation and other persons as to matters the Sole Director reasonably believed were within such persons’ professional or expert competence, as contemplated by Section 141(e) of the Delaware General Corporation Law.\n"
    )

    return f"""
**Minutes of the Special Meeting of the Board of Directors - {year}**
**{co_name}**
*(Board of Directors – Delaware Corporation)*

**Meeting Details**
**Date of Meeting:** {date}
**Time of Meeting:** {SPECIAL_MEETING_TIME}
**Location of Meeting:** {place}
**Purpose:** Pre-AGM Review of International Operations (held prior to this corporation’s annual stockholder and board meetings for {year})

**I. Call to Order:**
The Special Meeting of the Board of Directors of {co_name} (the “Corporation”) was called to order at {SPECIAL_MEETING_TIME} on {date} by {director_name}, acting as Sole Director of the Corporation.

**II. Roll Call and Quorum:**
**Director Present:** {director_name} (Sole Director)  
**Director Absent:** None  

The Sole Director being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the Delaware General Corporation Law.  
The Sole Director confirmed that notice of the meeting was duly given or waived.
{remote_meeting_line}

**III. Resolution:**
Upon consideration, the Sole Director adopted the following resolution:

RESOLVED, that all operational and management decisions made during the Corporation’s international operations cycle for the year {year} are hereby ratified, confirmed, and approved in all respects.

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

    reliance_141e_line = (
        "In taking the actions reflected in these minutes, the Sole Director relied in good faith on information, opinions, reports, and statements presented by officers of the Corporation and other persons as to matters the Sole Director reasonably believed were within such persons’ professional or expert competence, as contemplated by Section 141(e) of the Delaware General Corporation Law.\n"
    )

    return f"""
**Minutes of the Quarterly Governance Meeting - {year} {quarter}**
**{co_name}**
*(Board of Directors – Delaware Corporation)*

**Meeting Details**
**Date of Meeting:** {date}
**Time of Meeting:** {QUARTERLY_MEETING_TIME}
**Location of Meeting:** {place}

**I. Call to Order:**
The Quarterly Governance Meeting of the Board of Directors of {co_name} (the “Corporation”) was called to order at {QUARTERLY_MEETING_TIME} on {date} by {director_name}, acting as Sole Director of the Corporation.

**II. Roll Call and Quorum:**
**Director Present:** {director_name} (Sole Director)  
**Director Absent:** None  

The Sole Director being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the Delaware General Corporation Law.  
The Sole Director confirmed that notice of the meeting was duly given or waived.
{remote_meeting_line}

**III. Business Review:**
The Sole Director reviewed quarterly infrastructure stability and confirmed that all assets, including software and related intellectual property, created during the quarter in the development centers located in {dev_locations} are properly titled to and are the exclusive property of the Corporation.

{reliance_141e_line}

**IV. Resolution:**
Upon consideration, the Sole Director adopted the following resolution:

RESOLVED, that all operational, infrastructure, and intellectual property assets created during the quarter are hereby ratified, confirmed, and approved as assets of the Corporation.

**V. Adjournment:**
There being no further business to come before the Board, the meeting was adjourned.

{signature_block(director_name, date)}
---"""

def generate_quarterly_summary(company_name_year, year, quarter, co_name):
    """Generate a summary of the quarterly meeting for reporting purposes."""
    quarterly_docx = f"{company_name_year}_quarterly_{year}_{quarter}.docx"
    quarterly_content = generate_quarterly(co_name, year, quarter)
    print(f"Writing Quarterly meeting minutes to {quarterly_docx}")
    write_docx_from_minutes(quarterly_content, quarterly_docx)
    print(f"Generating file for {co_name} {year} {quarter}")


def generate_annual_meeting_stockholders(co_name, year):
    """Formal annual meeting minutes for corporations with more than one stockholder (e.g. DATA RECORD SCIENCE, INC.)."""
    co = companies[co_name]
    date = annual_meeting_date_str(co, year)
    board_date = date
    place = meeting_place_line(co, date)
    board_as_of = datetime.strptime(board_date, "%Y-%m-%d").strftime("%B %d, %Y")
    issued = co["shares_issued"].get(year, co["shares_issued"].get(2025))

    chair = "Derek E. Pappas"
    election_standard = co.get("director_election_standard", "plurality")
    election_sentence = (
        "Directors were elected by a plurality of the votes cast by the shares present in person or by proxy and entitled to vote."
        if election_standard == "plurality"
        else "Directors were elected by the requisite vote under the Corporation’s bylaws and applicable law."
    )

    return f"""
**Minutes of the Annual Meeting of Stockholders**
**{co_name}**
*(Delaware Corporation)*

**I. Meeting Information**
**Company Name:** {co_name}
**Principal Address:** {co['address']}
**Date:** {date}
**Time:** {STOCKHOLDER_MEETING_TIME}
**Place:** {place}
**Type of Meeting:** Annual Meeting of Stockholders

**II. Call to Order and Organization**
The Annual Meeting of Stockholders of {co_name} (the “Corporation”) was called to order commencing at {STOCKHOLDER_MEETING_TIME} on {date}. Pursuant to the Corporation’s bylaws, {chair}, acting as President of the Corporation, served as Chairperson of the meeting, and the Secretary (or a person designated by the Chairperson) served as Secretary of the meeting.

**III. Roll Call and Quorum**
The following stockholders were present in person or by remote participation (as permitted under the Corporation’s bylaws and the Delaware General Corporation Law) and were entitled to vote at the meeting:

**Stockholders Present:**  
The stockholders of the Corporation holding a majority of the outstanding shares of the Corporation entitled to vote at the meeting.

**Stockholders Absent:**  
None.

The Chairperson declared that a quorum of stockholders was present and that the meeting was duly constituted to transact business.
The Chairperson further confirmed that any stockholders participating remotely were able to hear and be heard contemporaneously and that the Corporation had reasonable means to verify that each such person was a stockholder or proxyholder entitled to vote at the meeting.

**IV. Notice**
The Chairperson confirmed that notice of this meeting had been duly given in accordance with the Corporation’s bylaws and the Delaware General Corporation Law, or that any required notice had been waived in writing by the requisite holders.

**V. Reports**
The Chairperson reported briefly on the Corporation’s operational activities for the fiscal year.

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


def generate_majority_stockholder_written_consent_ratification(company_name_year: str, year: int, co_name: str):
    """Majority stockholder written consent ratifying same-year annual board actions (DGCL §228), for multi-stockholder corporations."""
    co = companies[co_name]
    board_date = annual_meeting_date_str(co, year)
    as_of = datetime.strptime(board_date, "%Y-%m-%d").strftime("%B %d, %Y")

    mechanics = f"""**Section 228 Mechanics**
This Written Consent is intended to be delivered to the Corporation and to become effective in accordance with Section 228 of the DGCL and the Corporation’s bylaws, including any timing requirements applicable to the delivery of consents bearing dated signatures. The Corporation is authorized and directed to file this Written Consent with the minutes of the proceedings of the stockholders of the Corporation and to give any prompt notice required to non-consenting stockholders under Section 228 of the DGCL, the certificate of incorporation, and the bylaws."""

    content = f"""
**{co_name}.**
**Written Consent of Majority Stockholders**
**Action by Written Consent of Stockholders**
(Delaware General Corporation Law §228)

The undersigned, being the stockholders of {co_name}, a Delaware corporation (the "Corporation"), holding not less than the minimum number of votes that would be necessary to authorize the following action at a meeting at which all shares entitled to vote thereon were present and voted, hereby adopt the following resolutions by written consent pursuant to Section 228 of the Delaware General Corporation Law (the "DGCL"), effective as of the date set forth below.

**Ratification of Annual Board Meeting**
RESOLVED, that all actions taken and resolutions adopted by the Board of Directors of the Corporation at the Annual Meeting of the Board of Directors held on {as_of} (or as otherwise recorded in the minutes of such meeting), including the approval of financial statements, the budget for the ensuing fiscal year, officer actions, and banking authorizations, are hereby ratified, confirmed, and approved in all respects.

**Notice to Non-Consenting Stockholders**
RESOLVED, that the Corporation is authorized and directed to provide prompt notice of the taking of the foregoing corporate action by written consent, to the extent required by Section 228 of the DGCL, the Corporation’s certificate of incorporation, and the Corporation’s bylaws.

{mechanics}

**Effective Date**
This Written Consent shall be effective as of {as_of}, and shall be filed with the minutes of the proceedings of the stockholders of the Corporation.

**Stockholders:**
______________________________

______________________________

**Date:** {as_of}
---"""

    output = f"{company_name_year}_majority_stockholders_written_consent_ratification_of_annual_board_actions.docx"
    print(f"Writing Majority Stockholders Written Consent (ratification) to {output}")
    write_docx_from_minutes(content, output)

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
    agm_title = f"{company_name_year}_agm"
    agm_docx = f"{agm_title}.docx"
    agm_content = generate_agm(co_name, year)
    print(f"Writing AGM minutes to {agm_docx}")
    write_docx_from_minutes(agm_content, agm_docx)


def generate_special_meeting(company_name_year: str, co_name: str, year: int):
    """Generate special meeting minutes."""
    special_title = f"{company_name_year}_yearly_special_meeting"
    special_docx = f"{special_title}.docx"
    special_content = generate_special(co_name, year)
    print(f"Writing Special meeting minutes to {special_docx}")
    write_docx_from_minutes(special_content, special_docx)


def generate_written_consent(company_name_year: str, year: int, company_name: str):
    """Generate sole stockholder written consent under DGCL § 228 (.docx)."""
    co = companies[company_name]
    date = annual_meeting_date_str(co, year)
    as_of = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
    shareholder_term = "Sole Stockholder"
    voting_shares = co.get(
        "voting_shares_description",
        "all of the outstanding shares of the Corporation entitled to vote on the following matters",
    )

    mechanics = f"""**Section 228 Mechanics**
This Written Consent is intended to be delivered to the Corporation and to become effective in accordance with Section 228 of the DGCL and the Corporation’s bylaws, including any timing requirements applicable to the delivery of consents bearing dated signatures. The Corporation is authorized and directed to file this Written Consent with the minutes of the proceedings of the stockholders of the Corporation and to give any prompt notice required under Section 228 of the DGCL, the certificate of incorporation, and the bylaws (to the extent applicable)."""

    content = f"""
**{company_name}.**
**Written Consent of {shareholder_term}**
**Action by Written Consent of Stockholders**
(Delaware General Corporation Law §228; annual meeting of stockholders under §211)

The undersigned, being the {shareholder_term.lower()} of {company_name}, a Delaware corporation (the "Corporation"), and holding {voting_shares}, hereby adopts the following resolutions by written consent of the stockholders pursuant to Section 228 of the Delaware General Corporation Law (the "DGCL"), effective without a meeting to the same extent as if adopted at a duly held meeting. The undersigned acknowledges that, to the best of the undersigned’s knowledge, the Corporation’s certificate of incorporation does not prohibit stockholder action by written consent as contemplated hereby, including action by the holders of outstanding shares of capital stock having not less than the minimum number of votes that would be necessary to authorize or take such action at a meeting at which all shares entitled to vote thereon were present and voted.

**Approval of Board Actions**
RESOLVED, that all actions taken and resolutions adopted by the Board of Directors of the Corporation at the Annual Meeting of the Board of Directors held on {as_of} (or as otherwise recorded in the minutes of such meeting), including but not limited to the approval of financial statements, budgets, officer actions, and banking authorizations, are hereby ratified, confirmed, and approved in all respects.

**Annual Meeting of Stockholders**
RESOLVED, that the matters set forth in this Written Consent, including ratification of the Board’s actions taken at the annual board meeting referenced above, constitute or supplement, as applicable, the business addressed for purposes of the annual meeting of stockholders for the year {year} to the extent permitted by the DGCL, the certificate of incorporation, and the bylaws of the Corporation, and the undersigned waives any requirement to convene a separate annual meeting of stockholders for such year solely to duplicate the matters resolved herein.

{mechanics}

**Effective Date**
This Written Consent shall be effective as of {as_of}, and shall be filed with the minutes of the proceedings of the stockholders of the Corporation.

**Stockholder Certification**
{shareholder_term}:
Derek E. Pappas

**Signature:** ___________________________
**Date:** {as_of}
---"""
    output = f"{company_name_year}_written_consent_in_lieu_of_annual_meeting.docx"
    print(f"Writing Stockholder Written Consent to {output}")
    write_docx_from_minutes(content, output)


def generate_stockholder_side(company_name_year: str, year: int, co_name: str):
    co = companies[co_name]
    kind = co.get("stockholder_meeting", "written_consent")
    if kind == "annual_meeting_stockholders":
        out = f"{company_name_year}_annual_meeting_of_stockholders.docx"
        print(f"Writing Annual Meeting of Stockholders minutes to {out}")
        write_docx_from_minutes(generate_annual_meeting_stockholders(co_name, year), out)
        generate_majority_stockholder_written_consent_ratification(company_name_year, year, co_name)
    else:
        generate_written_consent(company_name_year, year, co_name)
    

import os
import argparse


def _company_years_for_calendar(co: dict, years: tuple[int, ...]) -> list[int]:
    start = max(co.get("minutes_start_year", co.get("inc_year", min(years))), min(years))
    return [y for y in years if y >= start]


def write_company_calendars(output_dir: str = "calendars", years: tuple[int, ...] = (2024, 2025, 2026)) -> None:
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
                entries_by_date.setdefault(annual_date, []).append(f"{co_name} - Stockholder Written Consent (DGCL §228) - {STOCKHOLDER_MEETING_TIME}")

                unified_entries.append((annual_date, BOARD_AGM_TIME, co_name, "Annual Meeting of the Board of Directors"))
                unified_entries.append((annual_date, STOCKHOLDER_MEETING_TIME, co_name, "Stockholder Written Consent (DGCL §228)"))

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


def print_schedule(years=(2024, 2025, 2026)):
    """Print the computed meeting schedule without generating .docx files."""
    print("Schedule (all times local):")
    for year in years:
        print(f"\nYear {year}")
        for co_name, co in companies.items():
            if year < co.get("inc_year", year):
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


def generate_all(output_root: str, years=(2024, 2025, 2026)):
    print(f"Current working directory: {os.getcwd()}")
    root_dir = os.path.join(os.getcwd(), output_root)
    os.makedirs(root_dir, exist_ok=True)

    for name in companies.keys():
        print(f"Company {name} Current working directory: {os.getcwd()}")

        os.chdir(root_dir)
        safe_company_name = sanitize_company_name(name)

        company_dir = f"{safe_company_name}"
        os.makedirs(company_dir, exist_ok=True)
        os.chdir(company_dir)

        for year in years:
            if year < companies[name].get("inc_year", year):
                continue
            company_name_year = f"{safe_company_name}_{year}"

            generate_annual(company_name_year, name, year)
            generate_special_meeting(company_name_year, name, year)
            generate_stockholder_side(company_name_year, year, name)

            for quarter in ["Q1", "Q2", "Q3", "Q4"]:
                generate_quarterly_summary(company_name_year, year, quarter, name)


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
