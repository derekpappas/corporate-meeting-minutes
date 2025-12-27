import json
from datetime import datetime
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
    ("2025-02-15", "2025-04-28", "Lantana, FL"),
    ("2025-04-28", "2025-12-31", "Wayne, Pennsylvania")
]

companies = {
    "Hippo, Inc": {
        "address": "30 N Gould St Ste 21106, Sheridan, WY 82801",
        "par": "$.0001",
        "inc_year": 2022,
        "shares_issued": {2022: "8,000,000", 2023: "8,160,000", 2024: "8,160,000", 2025: "8,160,000"}
    },
    "Ritual Growth, Inc.": {
        "address": "30 N Gould St Ste 27616, Sheridan, WY 82801",
        "par": "$.0001",
        "inc_year": 2022,
        "shares_issued": {2022: "4,000,000", 2023: "4,000,000", 2024: "4,000,000", 2025: "4,000,000"}
    },
    "DATA RECORD SCIENCE, INC.": {
        "address": "30 N Gould St Ste 24165, Sheridan, WY 82801",
        "par": "0.001",
        "inc_year": 2022,
        "shares_issued": {2022: "5,346,132", 2023: "5,346,132", 2024: "5,346,132", 2025: "5,346,132"}
    },
    "TeamBoost.ai, Inc.": {
        "address": "30 N Gould St Ste 23049, Sheridan, WY 82801",
        "par": "$.0001",
        "inc_year": 2022,
        "shares_issued": {2022: "10,000,000", 2023: "10,000,000", 2024: "10,000,000", 2025: "10,000,000"}
    }
}

from datetime import date

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

# 2. HELPER LOGIC
def get_location(date_str):
    target = datetime.strptime(date_str, "%Y-%m-%d")
    for start, end, loc in locations_timeline:
        s_dt = datetime.strptime(start, "%Y-%m-%d")
        e_dt = datetime.strptime(end, "%Y-%m-%d")
        if s_dt <= target <= e_dt:
            return loc
    return "Wayne, Pennsylvania"

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
    date = f"{year}-12-15"
    loc = get_location(date)
    issued = co["shares_issued"].get(year, "4,000,000")

    # select locations for the given year
    locations = office_locations_for_year(locations_timeline, year)

    # normalize and format for template insertion
    office_locations = normalize_locations(locations)

    director_name = "Derek E. Pappas"

    return f"""
**Minutes of the Annual Meeting of the Board of Directors**
*(Delaware Corporation)*

**I. Meeting Information**
**Company Name:** {co_name}
**Principal Address:** {co['address']}
**Date:** {date}
**Time:** 1:00 PM
**Place:** {loc}, via digital communication
**Type of Meeting:** Annual Meeting of the Board of Directors

**II. Call to Order**
The Annual Meeting of the Board of Directors of {co_name} (the “Corporation”) was called to order at 1:00 PM on {date} by {director_name}, acting as Sole Director, President, and Treasurer of the Corporation.

**III. Roll Call and Quorum**
**Director Present:**  
{director_name} (Sole Director)

**Director Absent:**  
None

The Sole Director being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the Delaware General Corporation Law.  
The Sole Director confirmed that notice of the meeting was duly given or waived.

**IV. Approval of Prior Minutes**
The minutes of the prior Annual Meeting of the Board of Directors held on {year - 1}-12-15 were reviewed and approved by the Sole Director.

**V. Reports of Officers**

**President’s Report:**  
The Sole Director reported on the Corporation’s operational and engineering activities for the fiscal year, including centralized management of globally distributed development and the use of operational office location(s) during the fiscal year, with operations conducted from {office_locations}, while confirming that management, oversight, and decision-making remained centralized and continuously recorded through the Corporation’s official records. All software, algorithms, and intellectual property developed during the year, regardless of development location, were reaffirmed as the exclusive property of the Corporation.

**Treasurer’s Report:**  
The Treasurer reported that the Corporation remains solvent and that certain outstanding obligations, including notes payable, are contingent and payable upon the occurrence of a future liquidity event, the timing of which has not yet been determined. The Sole Director acknowledged the status of such obligations and confirmed continued oversight of these matters. Franchise taxes and registered agent fees are paid and current. The Corporation has {issued} shares of common stock issued and outstanding at a par value of {co['par']} per share.

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
    date = f"{year}-12-15"
    loc = get_location(date)

    director_name = "Derek E. Pappas"

    return f"""
**Minutes of the Special Meeting of the Board of Directors - {year}**
**{co_name}**
*(Board of Directors – Delaware Corporation)*

**Meeting Details**
**Date of Meeting:** {date}
**Time of Meeting:** 11:00 AM
**Location of Meeting:** {loc}
**Purpose:** Pre-AGM Review of International Operations

**I. Call to Order:**
The Special Meeting of the Board of Directors of {co_name} (the “Corporation”) was called to order at 11:00 AM on {date} by {director_name}, acting as Sole Director of the Corporation.

**II. Roll Call and Quorum:**
**Director Present:** {director_name} (Sole Director)  
**Director Absent:** None  

The Sole Director being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the Delaware General Corporation Law.  
The Sole Director confirmed that notice of the meeting was duly given or waived.

**III. Resolution:**
Upon consideration, the Sole Director adopted the following resolution:

RESOLVED, that all operational and management decisions made during the Corporation’s international operations cycle for the year {year} are hereby ratified, confirmed, and approved in all respects.

**IV. Adjournment:**
There being no further business to come before the Board, the meeting was adjourned.

{signature_block(director_name, date)}
---"""


def generate_quarterly(co_name, year, quarter):
    co = companies[co_name]
    # Standardizing on April 1st for the main quarterly governance check
    date = f"{year}-04-01"
    loc = get_location(date)

    present_list = "Derek E. Pappas"

    return f"""
**Minutes of the Quarterly Governance Meeting - {year} {quarter}**
**{co_name}**
*(Board of Directors – Delaware Corporation)*

**Meeting Details**
**Date of Meeting:** {date}
**Location of Meeting:** {loc}

**I. Call to Order:**
The Quarterly Governance Meeting of the Board of Directors of {co_name} (the “Corporation”) was called to order on {date} by the Chairperson of the Board.

**II. Roll Call and Quorum:**
**Directors Present:** {present_list}  

A majority of the directors of the Corporation being present, a quorum was present, and the meeting was duly constituted to transact business in accordance with the Delaware General Corporation Law.  
The Board confirmed that notice of the meeting was duly given or waived by all directors.

**III. Business Review:**
The Board reviewed quarterly infrastructure stability and confirmed that all assets, including software and related intellectual property, created during the quarter in {loc} are properly titled to and are the exclusive property of the Corporation.

**IV. Resolution:**
Upon motion duly made and seconded, the following resolution was adopted by the affirmative vote of a majority of the directors present:

RESOLVED, that all operational, infrastructure, and intellectual property assets created during the quarter are hereby ratified, confirmed, and approved as assets of the Corporation.

**V. Adjournment:**
There being no further business to come before the Board, the meeting was adjourned.

{signature_block("Chairperson of the Board", date)}
---"""

def generate_quarterly_summary(company_name_year, year, quarter):
    """Generate a summary of the quarterly meeting for reporting purposes."""
    # Write Quarterly meeting minutes
    quarterly_docx = f"{company_name_year}_quarterly_{year}_{quarter}.docx"
    quarterly_content = generate_quarterly(name, year, quarter)
    print(f"Writing Quarterly meeting minutes to {quarterly_docx}")
    write_docx_from_minutes(quarterly_content, quarterly_docx)
    print(f"Generating file for {name} {year} {quarter} in dir: {company_dir}")

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



def generate_annual(name, year):
    # Write AGM minutes
    agm_title = f"{company_name_year}_agm"
    agm_docx = f"{agm_title}.docx"
    agm_content = generate_agm(name, year)
    print(f"Writing AGM minutes to {agm_docx}")
    write_docx_from_minutes(agm_content, agm_docx)

def generate_special_meeting(name, year):
    """Generate special meeting minutes."""
    # Write Special meeting minutes
    special_title = f"{company_name_year}_yearly_special_meeting"
    special_docx = f"{special_title}.docx"
    special_content = generate_special(name, year)
    print(f"Writing Special meeting minutes to {special_docx}")
    write_docx_from_minutes(special_content, special_docx)

def generate_written_consent(company_name_year: str, year: int, company_name: str):
    """Generate Stockholder Written Consent in Lieu of Annual Meeting (.docx)."""
    date = f"{year}-12-15"
    as_of = datetime.strptime(date, "%Y-%m-%d").strftime("%B %d, %Y")
    shareholder_term = "Majority Stockholder" if company_name == "DATA RECORD SCIENCE, INC." else "Sole Stockholder"

    content = f"""
**{company_name}.**
**Written Consent of {shareholder_term}**
**In Lieu of Annual Meeting**
(Delaware General Corporation Law §211)

The undersigned, being the {shareholder_term.lower()} of {company_name}, a Delaware corporation (the "Corporation"), hereby adopts the following resolutions by Written Consent in Lieu of an Annual Meeting of Stockholders, pursuant to Section 211 of the Delaware General Corporation Law:

**Approval of Board Actions**
RESOLVED, that all actions taken and resolutions adopted by the Board of Directors of the Corporation at the Annual Meeting of the Board of Directors held on {as_of}, including but not limited to the approval of financial statements, budgets, officer actions, and banking authorizations, are hereby ratified, confirmed, and approved in all respects.

**Waiver of Annual Meeting**
RESOLVED, that the undersigned hereby waives the requirement of holding a formal annual meeting of stockholders for the year {year}.

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
    

import os
# pwd
print(f"Current working directory: {os.getcwd()}")
pwd = os.getcwd()

root_dir = f"{pwd}/generated"
# create root directory if it doesn't exist
os.makedirs(root_dir, exist_ok=True)

for name in companies.keys():
    print(f"Company {name} Current working directory: {os.getcwd()}")

    os.chdir(root_dir)
    safe_company_name = sanitize_company_name(name)
    
    company_dir = f"{safe_company_name}"
    os.makedirs(company_dir, exist_ok=True)
    # cd to company_dir    
    os.chdir(company_dir)
    
    for year in [2022, 2023, 2024, 2025]:
        company_name_year = f"{safe_company_name}_{year}"

        # Generate AGM minutes first
        generate_annual(name, year)

        # Generate special meeting minutes
        generate_special_meeting(name, year)

        # Generate Written Consent (.docx)
        generate_written_consent(company_name_year, year, name)
        
        for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            generate_quarterly_summary(company_name_year, year, quarter)
