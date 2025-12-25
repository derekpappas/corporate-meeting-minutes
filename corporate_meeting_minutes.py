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

    bank_clause = ""
    voting_bank = ""
    if year == co["inc_year"]:
        bank_clause = "\n**VI. Banking Resolution:**\nThe Board hereby authorizes Derek E. Pappas to open corporate bank accounts at Chase Bank and acts as the sole signatory."
        voting_bank = "The motion to authorize Chase Bank accounts passed unanimously."

    return f"""
**{year} Annual General Meeting**
**Minutes of the Annual Meeting of Directors - {year}**
**{co_name}**

**Meeting Details**
**Company Name:** {co_name}
**Address:** {co['address']}
**Date of Meeting:** {date}
**Time of Meeting:** 1:00 PM
**Location of Meeting:** {loc} (via Digital Communication)
**Purpose of Meeting:** Annual meeting

**I. Call to Order:**
The Annual Meeting of Directors of {co_name} was called to order at 1:00 PM on {date} by Derek E. Pappas.

**II. Roll Call:**
**Directors Present:** Derek E. Pappas.
**Directors Absent:** none.

**III. Approval of the Minutes from the Last Meeting:**
The minutes of the previous Annual Meeting held on {year-1}-12-15 were reviewed and approved.

**IV. Reports:**
**Chairperson's Report:** Derek E. Pappas provided a comprehensive update on the {year} global management cycle, noting oversight across multiple international locations. The Director confirmed that despite the geographical rotation, all management decisions were centralized and recorded via corporate digital channels. The Board reviewed the successful completion of engineering milestones during the year, including scaling of back-end infrastructure. The Director reaffirmed that all work product, including source code and algorithmic designs developed in international jurisdictions, is owned solely by the Corporation.
**Treasurer's Report:** Derek E. Pappas presented the financial statements for the fiscal year {year}. The Corporation remains debt-free. A Statement of Solvency was issued, and the Director confirmed that the Franchise Tax and Registered Agent fees for the current year are fully paid. {issued} shares issued at {co['par']} par.{bank_clause}

**V. Discussion Items:**
The Board discussed the {year+1} transition plan as the company moves toward commercial readiness. Plans for final security penetration testing and third-party audits were reviewed.

**VI. Voting Items:**
The motion to approve the {year} financial reports was passed unanimously. The motion to approve the {year+1} engineering and marketing budget was passed unanimously. {voting_bank}

**VII. Adjournment:**
The meeting was adjourned at 1:30 PM.

{signature_block('Derek E. Pappas', date)}
---"""

def generate_special(co_name, year):
    co = companies[co_name]
    date = f"{year}-12-15"
    loc = get_location(date)
    return f"""
**Minutes of the Special Meeting of the Board of Directors - {year}**
**{co_name}**

**Meeting Details**
**Date of Meeting:** {date}
**Time of Meeting:** 11:00 AM
**Location of Meeting:** {loc}
**Purpose:** Pre-AGM Review of International Operations

**I. Call to Order:**
Meeting called to order at 11:00 AM.

**II. Resolution:**
The Board reviewed and ratified all operational decisions made during the international nomad cycle for the year {year}.

{signature_block('Derek E. Pappas', date)}
---"""

def generate_quarterly(co_name, year, quarter):
    co = companies[co_name]
    # Standardizing on April 1st for the main quarterly governance check
    date = f"{year}-04-01"
    loc = get_location(date)
    return f"""
**Minutes of the Quarterly Governance Meeting - {year} {quarter}**
**{co_name}**

**Meeting Details**
**Date of Meeting:** {date}
**Location of Meeting:** {loc}

**I. Business Review:**
The Director reviewed quarterly infrastructure stability and confirmed that all assets created in {loc} are correctly titled to the Corporation.

{signature_block('Derek E. Pappas', date)}
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

        for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            generate_quarterly_summary(company_name_year, year, quarter)
