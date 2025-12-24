import json
from datetime import datetime

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
**Minutes of the Annual Meeting of Directors - {year}**
**{co_name}**

**Meeting Details**
**Company Name:** {co_name}
**Address:** {co['address']}
**Date of Meeting:** {date}
**Time of Meeting:** 1:00 PM
**Location of Meeting:** {loc}

**I. Call to Order:**
Meeting called to order at 1:00 PM by Derek E. Pappas.

**II. Reports:**
**Chairperson's Report:** Reviewed the {year} management cycle. All IP developed in {loc} is corporate property.
**Treasurer's Report:** Presented financial statements. {issued} shares issued at {co['par']} par. Solvency confirmed.{bank_clause}

**III. Voting Items:**
Approved financial reports. {voting_bank}

**IV. Adjournment:**
Meeting adjourned at 1:30 PM.

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

# 4. EXECUTION
for name in companies.keys():
     # Write to files
    import os
    root_dir = "."
    os.chdir(root_dir)

    # remove the comma from company name for file naming
    safe_company_name = name.replace(", ", "_").replace(" ", "_")

    # remove "Inc" or "inc" from the end
    if safe_company_name.lower().endswith("inc"):
        safe_company_name = safe_company_name[:-3]

    # lowercase the company name for file naming
    safe_company_name = safe_company_name.lower()

    # remove trailing underscores
    safe_company_name = safe_company_name.rstrip('_')

    
    company_dir = f"{root_dir}/{safe_company_name}"
    os.makedirs(company_dir, exist_ok=True)
    # cd to company_dir    
    os.chdir(company_dir)
    
    for year in [2022, 2023, 2024, 2025]:
        company_name_year = f"{safe_company_name}_{year}"
        agm_title = f"{company_name_year}_agm"

        for quarter in ['Q1', 'Q2', 'Q3', 'Q4']:
            print(f"--- {name} {year} {quarter} ---")
            #
            print(f"Generating files for {name} {year} {quarter} in dir: {company_dir}")

            # Write AGM minutes
            agm_file = f"{agm_title}.txt"
            print(f"Writing AGM minutes to {agm_file}")
            with open(agm_file, "w") as f:
                f.write(generate_agm(name, year))

            special_title = f"{company_name_year}_yearly_special_meeting"

            # Write Special meeting minutes
            special_file = f"{special_title}.txt"
            print(f"Writing Special meeting minutes to {special_file}")
            with open(special_file, "w") as f:
                f.write(generate_special(name, year))
            
            # Write Quarterly meeting minutes
            quarterly_file = f"{company_name_year}_quarterly_{year}_{quarter}.txt"
            print(f"Writing Quarterly meeting minutes to {quarterly_file}")
            with open(quarterly_file, "w") as f:
                f.write(generate_quarterly(name, year, quarter))
            
            print(f"Written minutes for {name} {year} to files")