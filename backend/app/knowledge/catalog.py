"""
Structured scheme catalog.

This is the primary knowledge source for retrieval, browse, and eligibility.
Each record is a scheme-level document with official URLs and machine-readable
eligibility rules. Extra PDF/Chroma chunks are treated as supplements only.
"""

from __future__ import annotations

import copy
from functools import lru_cache
from typing import Any, Dict, List, Optional

SCHEME_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "pm-kisan",
        "name": "PM-KISAN",
        "full_name": "Pradhan Mantri Kisan Samman Nidhi",
        "name_hindi": "प्रधानमंत्री किसान सम्मान निधि",
        "aliases": [
            "pm kisan",
            "pmkisan",
            "kisan samman nidhi",
            "farmer 6000",
            "kisan yojana",
        ],
        "category": "Agriculture",
        "scheme_type": "central",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "description": "Income support for landholding farmer families across India. The amount is paid in three instalments through Direct Benefit Transfer.",
        "benefits": "Direct income support of Rs. 6,000 per year, paid as Rs. 2,000 every four months into the farmer's bank account.",
        "benefit_amount": "Rs. 6,000 per year",
        "eligibility_summary": "Landholding farmer families with cultivable land. Government employees and income-tax payers are excluded.",
        "eligibility": {
            "occupations": ["farmer"],
            "has_land": True,
            "exclude_income_tax_payer": True,
        },
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity verification", "is_mandatory": True},
            {"name": "Land records", "description": "Proof of cultivable land", "is_mandatory": True},
            {"name": "Bank account details", "description": "For Direct Benefit Transfer", "is_mandatory": True},
        ],
        "application_process": "Register at pmkisan.gov.in with Aadhaar, land details, and bank account. Village-level officials can also register farmers. Track instalments on the same portal.",
        "apply_url": "https://pmkisan.gov.in/",
        "helpline": "155261 / 011-23381092",
        "tags": ["farmer", "agriculture", "dbt", "income support", "land"],
        "last_updated": "2026-01-15",
    },
    {
        "id": "pmfby",
        "name": "PM Fasal Bima Yojana",
        "full_name": "Pradhan Mantri Fasal Bima Yojana",
        "name_hindi": "प्रधानमंत्री फसल बीमा योजना",
        "aliases": ["fasal bima", "crop insurance", "pmfby", "crop insurance scheme"],
        "category": "Agriculture",
        "scheme_type": "central",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "description": "Crop insurance against non-preventable natural risks such as drought, flood, pest, and cyclone. Farmers pay a low premium; the rest is shared by Centre and State.",
        "benefits": "Insurance cover for notified crops. Farmer premium is 2% for kharif, 1.5% for rabi food and oilseed crops, and 5% for annual commercial or horticultural crops.",
        "benefit_amount": "Sum insured as notified per crop and area",
        "eligibility_summary": "All farmers growing notified crops in notified areas, including sharecroppers and tenant farmers where state rules allow.",
        "eligibility": {"occupations": ["farmer"]},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity proof", "is_mandatory": True},
            {"name": "Land or tenancy proof", "description": "Sowing details", "is_mandatory": True},
            {"name": "Bank account and sowing certificate", "description": "For claim credit", "is_mandatory": True},
        ],
        "application_process": "Enrol through the bank that issued the Kisan Credit Card, a CSC, or pmfby.gov.in before the cut-off date for the season.",
        "apply_url": "https://pmfby.gov.in/",
        "helpline": "14447",
        "tags": ["farmer", "insurance", "crop", "drought", "flood"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "kcc",
        "name": "Kisan Credit Card",
        "full_name": "Kisan Credit Card Scheme",
        "name_hindi": "किसान क्रेडिट कार्ड",
        "aliases": ["kcc", "kisan credit", "farmer loan card", "crop loan"],
        "category": "Agriculture",
        "scheme_type": "central",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "description": "Short-term credit for crop production, post-harvest expenses, and farm maintenance. Interest subvention is available on timely repayment.",
        "benefits": "Revolving credit at concessional rates, with interest subvention for prompt repayment and coverage under crop insurance where linked.",
        "benefit_amount": "Credit limit based on cropping pattern and land holding",
        "eligibility_summary": "Farmers, tenant farmers, sharecroppers, and self-help groups of farmers who need production credit.",
        "eligibility": {"occupations": ["farmer"]},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "KYC", "is_mandatory": True},
            {"name": "Land or tenancy documents", "description": "Scale of finance", "is_mandatory": True},
            {"name": "Passport photo and bank KYC", "description": "Account opening", "is_mandatory": True},
        ],
        "application_process": "Apply at a bank branch, PACS, or through Jan Samarth. The bank assesses the scale of finance and issues the card.",
        "apply_url": "https://www.jansamarth.in/",
        "helpline": None,
        "tags": ["farmer", "credit", "loan", "kcc"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "pmksy",
        "name": "PM Krishi Sinchayee Yojana",
        "full_name": "Pradhan Mantri Krishi Sinchayee Yojana",
        "name_hindi": "प्रधानमंत्री कृषि सिंचाई योजना",
        "aliases": ["pmksy", "per drop more crop", "drip irrigation", "micro irrigation"],
        "category": "Agriculture",
        "scheme_type": "central",
        "ministry": "Ministry of Agriculture and Farmers Welfare",
        "description": "Expands irrigation coverage and water-use efficiency through micro-irrigation, watershed works, and 'Har Khet Ko Pani'.",
        "benefits": "Subsidy on drip and sprinkler systems, plus support for water harvesting and field irrigation infrastructure.",
        "benefit_amount": "State-notified subsidy on micro-irrigation systems",
        "eligibility_summary": "Farmers, including small and marginal farmers, installing notified micro-irrigation systems on eligible land.",
        "eligibility": {"occupations": ["farmer"]},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity", "is_mandatory": True},
            {"name": "Land records", "description": "Plot details", "is_mandatory": True},
            {"name": "Bank account", "description": "Subsidy transfer", "is_mandatory": True},
        ],
        "application_process": "Apply through the state agriculture or horticulture department portal, or the PMKSY MIS used by the state.",
        "apply_url": "https://pmksy.gov.in/",
        "helpline": None,
        "tags": ["farmer", "irrigation", "water", "drip"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "pm-jay",
        "name": "Ayushman Bharat PM-JAY",
        "full_name": "Pradhan Mantri Jan Arogya Yojana",
        "name_hindi": "प्रधानमंत्री जन आरोग्य योजना",
        "aliases": [
            "ayushman",
            "ayushman bharat",
            "pmjay",
            "pm jay",
            "jan arogya",
            "health insurance",
            "ayushman card",
        ],
        "category": "Health",
        "scheme_type": "central",
        "ministry": "Ministry of Health and Family Welfare",
        "description": "Public health cover for hospitalisation at empaneled public and private hospitals. Treatment is cashless at the hospital for listed packages.",
        "benefits": "Health cover of up to Rs. 5 lakh per family per year for secondary and tertiary hospitalisation.",
        "benefit_amount": "Up to Rs. 5 lakh per family per year",
        "eligibility_summary": "Families identified from SECC 2011 and later expansions notified by the Centre and states. Check eligibility on the beneficiary portal before applying.",
        "eligibility": {"income_max": 300000, "is_bpl": True},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity of family members", "is_mandatory": True},
            {"name": "Ration card", "description": "Family verification where asked", "is_mandatory": False},
        ],
        "application_process": "Check eligibility at mera.pmjay.gov.in. If eligible, get the Ayushman card at a CSC, empaneled hospital, or Ayushman desk. Use it at empaneled hospitals for cashless care.",
        "apply_url": "https://www.pmjay.gov.in/",
        "helpline": "14555 / 1800-111-565",
        "tags": ["health", "insurance", "hospital", "bpl", "ayushman"],
        "last_updated": "2026-01-12",
    },
    {
        "id": "jsy",
        "name": "Janani Suraksha Yojana",
        "full_name": "Janani Suraksha Yojana",
        "name_hindi": "जननी सुरक्षा योजना",
        "aliases": ["jsy", "institutional delivery", "pregnant woman scheme"],
        "category": "Health",
        "scheme_type": "central",
        "ministry": "Ministry of Health and Family Welfare",
        "description": "Cash assistance to encourage institutional delivery among pregnant women, especially in low-performing states.",
        "benefits": "Cash incentive for delivery in a government or accredited private health facility. Amounts differ for rural and urban areas and by state category.",
        "benefit_amount": "Rs. 1,400 rural / Rs. 1,000 urban in LPS (typical NHM rates)",
        "eligibility_summary": "Pregnant women delivering in a government or accredited institution. Focus is BPL and low-performing states.",
        "eligibility": {"gender": "female"},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity", "is_mandatory": True},
            {"name": "MCP card / hospital records", "description": "Pregnancy and delivery proof", "is_mandatory": True},
            {"name": "Bank account", "description": "DBT", "is_mandatory": True},
        ],
        "application_process": "Enrol at the ANM, ASHA, or government hospital during antenatal care. The facility processes the incentive after delivery.",
        "apply_url": "https://nhm.gov.in/",
        "helpline": "104",
        "tags": ["health", "maternal", "women", "delivery"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "pmay-g",
        "name": "PMAY-G",
        "full_name": "Pradhan Mantri Awaas Yojana Gramin",
        "name_hindi": "प्रधानमंत्री आवास योजना ग्रामीण",
        "aliases": ["pmay g", "pmay gramin", "rural housing", "awaas yojana rural", "pucca house"],
        "category": "Housing",
        "scheme_type": "central",
        "ministry": "Ministry of Rural Development",
        "description": "Financial assistance to rural families who are houseless or live in kutcha houses, for construction of a pucca house.",
        "benefits": "Assistance of Rs. 1.20 lakh in plains and Rs. 1.30 lakh in hilly, difficult, and IAP areas, paid in instalments linked to construction stages.",
        "benefit_amount": "Rs. 1.20 lakh plains / Rs. 1.30 lakh hilly areas",
        "eligibility_summary": "Rural households that are houseless or live in kutcha houses, as identified from SECC and Awaas+ processes. Not for families that already own a pucca house.",
        "eligibility": {"is_bpl": True},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity", "is_mandatory": True},
            {"name": "Job card / rural residence proof", "description": "MGNREGA or local verification", "is_mandatory": False},
            {"name": "Bank account", "description": "Instalments", "is_mandatory": True},
        ],
        "application_process": "Names come from the Awaas+ / Gram Sabha list. Confirm status on pmayg.nic.in and complete geo-tagged construction stages through the Gram Panchayat.",
        "apply_url": "https://pmayg.nic.in/",
        "helpline": "1800-11-6446",
        "tags": ["housing", "rural", "pucca", "bpl"],
        "last_updated": "2026-01-18",
    },
    {
        "id": "pmay-u",
        "name": "PMAY-U",
        "full_name": "Pradhan Mantri Awas Yojana Urban",
        "name_hindi": "प्रधानमंत्री आवास योजना शहरी",
        "aliases": ["pmay u", "pmay urban", "urban housing", "clss", "housing for all"],
        "category": "Housing",
        "scheme_type": "central",
        "ministry": "Ministry of Housing and Urban Affairs",
        "description": "Urban housing support through subsidy on home loans, in-situ slum redevelopment, and affordable housing projects, as notified under the current PMAY-U period.",
        "benefits": "Interest subsidy on eligible home loans and support for identified urban housing projects. Exact subsidy depends on income category (EWS, LIG, MIG) and the vertical you apply under.",
        "benefit_amount": "Interest subsidy as notified for the income category",
        "eligibility_summary": "Urban residents without pucca housing, within notified income ceilings for EWS, LIG, or MIG. A family should not already own a pucca house in India.",
        "eligibility": {"income_max": 1800000},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity", "is_mandatory": True},
            {"name": "Income proof", "description": "Category", "is_mandatory": True},
            {"name": "Affidavit of no pucca house", "description": "Eligibility", "is_mandatory": True},
        ],
        "application_process": "Apply through the PMAY-U portal or a participating bank for the credit-linked subsidy. Municipal bodies handle project-based components.",
        "apply_url": "https://pmaymis.gov.in/",
        "helpline": "1800-11-3377",
        "tags": ["housing", "urban", "loan", "subsidy"],
        "last_updated": "2026-01-18",
    },
    {
        "id": "mgnrega",
        "name": "MGNREGA",
        "full_name": "Mahatma Gandhi National Rural Employment Guarantee Act",
        "name_hindi": "महात्मा गांधी राष्ट्रीय ग्रामीण रोजगार गारंटी अधिनियम",
        "aliases": ["nrega", "mnrega", "100 days work", "rural employment", "job card"],
        "category": "Employment",
        "scheme_type": "central",
        "ministry": "Ministry of Rural Development",
        "description": "Legal guarantee of 100 days of unskilled manual work per rural household in a financial year, at the notified wage rate.",
        "benefits": "Up to 100 days of wage employment per household per year. Wages are paid to the worker's bank or post office account.",
        "benefit_amount": "100 days of work at the state-notified MGNREGA wage",
        "eligibility_summary": "Adult members of rural households willing to do unskilled manual work. Apply for a job card at the Gram Panchayat.",
        "eligibility": {"occupations": ["unemployed", "farmer", "self-employed"]},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity", "is_mandatory": True},
            {"name": "Passport photos and residence proof", "description": "Job card", "is_mandatory": True},
            {"name": "Bank or post office account", "description": "Wage credit", "is_mandatory": True},
        ],
        "application_process": "Apply for a job card at the Gram Panchayat. Demand work in writing. Work should be provided within 15 days, or unemployment allowance is due.",
        "apply_url": "https://nrega.nic.in/",
        "helpline": "1800-345-22-44",
        "tags": ["employment", "rural", "wages", "job card"],
        "last_updated": "2026-01-15",
    },
    {
        "id": "pmkvy",
        "name": "PMKVY",
        "full_name": "Pradhan Mantri Kaushal Vikas Yojana",
        "name_hindi": "प्रधानमंत्री कौशल विकास योजना",
        "aliases": ["skill india", "pmkvy", "free skill training", "kaushal vikas"],
        "category": "Skills & Training",
        "scheme_type": "central",
        "ministry": "Ministry of Skill Development and Entrepreneurship",
        "description": "Short-term skill training and certification aligned to NSQF, with a focus on wage or self-employment outcomes.",
        "benefits": "Free or subsidised training, assessment, and certification at empaneled centres. Some courses include placement support.",
        "benefit_amount": "Course fee paid by government for eligible candidates",
        "eligibility_summary": "Indian citizens, typically school dropouts or unemployed youth in the notified age band for the course. Check the specific PMKVY guidelines for the current phase.",
        "eligibility": {"occupations": ["unemployed", "student"], "age_min": 15, "age_max": 45},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity", "is_mandatory": True},
            {"name": "Education certificate", "description": "Course eligibility", "is_mandatory": False},
            {"name": "Bank account", "description": "If stipend is payable", "is_mandatory": False},
        ],
        "application_process": "Find a nearby Training Centre on skillindia.gov.in or the PMKVY dashboard and enrol for a notified job role.",
        "apply_url": "https://www.pmkvyofficial.org/",
        "helpline": "088000-55555",
        "tags": ["skill", "training", "youth", "employment"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "mudra",
        "name": "PM MUDRA Yojana",
        "full_name": "Pradhan Mantri MUDRA Yojana",
        "name_hindi": "प्रधानमंत्री मुद्रा योजना",
        "aliases": ["mudra", "mudra loan", "shishu kishore tarun", "small business loan"],
        "category": "Business & Entrepreneurship",
        "scheme_type": "central",
        "ministry": "Ministry of Finance",
        "description": "Collateral-free loans to non-corporate, non-farm micro enterprises through banks, NBFCs, and MFIs.",
        "benefits": "Loans under Shishu (up to Rs. 50,000), Kishore (Rs. 50,001 to Rs. 5 lakh), and Tarun (Rs. 5 lakh to Rs. 10 lakh), with Tarun Plus in later expansions as notified.",
        "benefit_amount": "Up to Rs. 10 lakh (higher slabs as currently notified)",
        "eligibility_summary": "Non-farm micro businesses such as shopkeepers, traders, small manufacturers, and service providers. Not for farm crop loans.",
        "eligibility": {"occupations": ["self-employed", "employee"]},
        "documents_required": [
            {"name": "Aadhaar and PAN", "description": "KYC", "is_mandatory": True},
            {"name": "Business proof or plan", "description": "Activity", "is_mandatory": True},
            {"name": "Bank statements", "description": "Where asked", "is_mandatory": False},
        ],
        "application_process": "Apply at a bank, SFB, or NBFC, or through Jan Samarth / Udyamimitra. The lender assesses the activity and sanctions the MUDRA loan.",
        "apply_url": "https://www.mudra.org.in/",
        "helpline": "1800-180-1111",
        "tags": ["loan", "business", "msme", "self-employed"],
        "last_updated": "2026-01-12",
    },
    {
        "id": "pmegp",
        "name": "PMEGP",
        "full_name": "Prime Minister's Employment Generation Programme",
        "name_hindi": "प्रधानमंत्री रोजगार सृजन कार्यक्रम",
        "aliases": ["pmegp", "kvic loan", "factory setup subsidy"],
        "category": "Business & Entrepreneurship",
        "scheme_type": "central",
        "ministry": "Ministry of Micro, Small and Medium Enterprises",
        "description": "Credit-linked subsidy to set up new micro enterprises in manufacturing or services, implemented by KVIC, KVIB, and District Industries Centres.",
        "benefits": "Margin money subsidy of 15% to 35% of project cost, depending on category and location, on bank-financed projects up to the notified ceiling.",
        "benefit_amount": "15-35% subsidy on eligible project cost",
        "eligibility_summary": "Individuals above 18 years. For manufacturing projects above Rs. 10 lakh and service projects above Rs. 5 lakh, at least VIII standard pass. Only new units.",
        "eligibility": {"occupations": ["unemployed", "self-employed"], "age_min": 18},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity", "is_mandatory": True},
            {"name": "Project report", "description": "Unit plan", "is_mandatory": True},
            {"name": "Caste or special category certificate", "description": "Higher subsidy", "is_mandatory": False},
            {"name": "Education certificate", "description": "If project exceeds threshold", "is_mandatory": False},
        ],
        "application_process": "Apply online at kviconline.gov.in/pmegpeportal. The application is forwarded to a bank after sponsoring by KVIC/KVIB/DIC.",
        "apply_url": "https://www.kviconline.gov.in/pmegpeportal/",
        "helpline": "011-23411558",
        "tags": ["business", "subsidy", "msme", "self-employed"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "standup-india",
        "name": "Stand-Up India",
        "full_name": "Stand-Up India Scheme",
        "name_hindi": "स्टैंड-अप इंडिया",
        "aliases": ["standup india", "sc st women loan", "greenfield enterprise loan"],
        "category": "Business & Entrepreneurship",
        "scheme_type": "central",
        "ministry": "Ministry of Finance",
        "description": "Bank loans for greenfield enterprises in manufacturing, services, or trading, set up by SC, ST, or women entrepreneurs.",
        "benefits": "Composite loan between Rs. 10 lakh and Rs. 1 crore, including term loan and working capital, with a repayment window up to 7 years.",
        "benefit_amount": "Rs. 10 lakh to Rs. 1 crore",
        "eligibility_summary": "SC, ST, or woman entrepreneur, 18 years or older, for a greenfield project. The borrower should not be in default with any bank or financial institution.",
        "eligibility": {"occupations": ["self-employed"], "age_min": 18, "gender": "female"},
        "documents_required": [
            {"name": "Aadhaar and PAN", "description": "KYC", "is_mandatory": True},
            {"name": "Caste certificate if SC/ST", "description": "Category", "is_mandatory": False},
            {"name": "Project report", "description": "Greenfield unit", "is_mandatory": True},
        ],
        "application_process": "Apply through a scheduled commercial bank or the Stand-Up India portal. Each branch is expected to support at least one SC/ST and one woman borrower.",
        "apply_url": "https://www.standupmitra.in/",
        "helpline": "1800-180-1111",
        "tags": ["loan", "women", "sc", "st", "business"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "pmjdy",
        "name": "PM Jan Dhan Yojana",
        "full_name": "Pradhan Mantri Jan Dhan Yojana",
        "name_hindi": "प्रधानमंत्री जन धन योजना",
        "aliases": ["jan dhan", "pmjdy", "zero balance account", "jan dhan account"],
        "category": "Financial Inclusion",
        "scheme_type": "central",
        "ministry": "Ministry of Finance",
        "description": "Basic savings bank accounts with RuPay debit card, overdraft facility after satisfactory operation, and accident insurance cover as notified.",
        "benefits": "Zero-balance savings account, RuPay card, DBT readiness, and accident insurance of Rs. 2 lakh on eligible RuPay cards.",
        "benefit_amount": "Account access plus Rs. 2 lakh accident cover on eligible cards",
        "eligibility_summary": "Any Indian citizen who does not have a bank account. There is no income ceiling.",
        "eligibility": {},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "KYC", "is_mandatory": True},
            {"name": "Passport photo", "description": "Account opening", "is_mandatory": True},
        ],
        "application_process": "Open the account at any bank branch, Business Correspondent, or IPPB. Link Aadhaar for DBT.",
        "apply_url": "https://pmjdy.gov.in/",
        "helpline": "1800-11-0001",
        "tags": ["bank", "inclusion", "dbt", "rupay"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "apy",
        "name": "Atal Pension Yojana",
        "full_name": "Atal Pension Yojana",
        "name_hindi": "अटल पेंशन योजना",
        "aliases": ["apy", "atal pension", "unorganised pension"],
        "category": "Financial Inclusion",
        "scheme_type": "central",
        "ministry": "Ministry of Finance",
        "description": "Contributory pension for workers in the unorganised sector, with a guaranteed monthly pension from age 60.",
        "benefits": "Guaranteed monthly pension of Rs. 1,000 to Rs. 5,000 from age 60, depending on contribution and entry age. Spouse pension and return of corpus to nominee on death after 60, as per rules.",
        "benefit_amount": "Rs. 1,000 to Rs. 5,000 per month after 60",
        "eligibility_summary": "Indian citizens aged 18 to 40 with a savings bank account. Income-tax payers are not eligible under current rules.",
        "eligibility": {"age_min": 18, "age_max": 40, "occupations": ["self-employed", "unemployed", "farmer", "employee"]},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "KYC", "is_mandatory": True},
            {"name": "Bank account", "description": "Auto-debit of contribution", "is_mandatory": True},
            {"name": "Mobile number", "description": "Alerts", "is_mandatory": True},
        ],
        "application_process": "Enrol at your bank branch or through net/mobile banking where APY is enabled. Choose the pension slab and complete auto-debit mandate.",
        "apply_url": "https://www.npscra.nsdl.co.in/scheme-details.php",
        "helpline": "1800-110-069",
        "tags": ["pension", "unorganised", "retirement"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "pmjjby",
        "name": "PM Jeevan Jyoti Bima Yojana",
        "full_name": "Pradhan Mantri Jeevan Jyoti Bima Yojana",
        "name_hindi": "प्रधानमंत्री जीवन ज्योति बीमा योजना",
        "aliases": ["pmjjby", "life insurance 2 lakh", "jeevan jyoti"],
        "category": "Financial Inclusion",
        "scheme_type": "central",
        "ministry": "Ministry of Finance",
        "description": "Annual renewable term life insurance offered through banks and post offices, with a low premium auto-debited from the account.",
        "benefits": "Life cover of Rs. 2 lakh in case of death due to any cause, for a premium of Rs. 436 per year as currently notified.",
        "benefit_amount": "Rs. 2 lakh life cover",
        "eligibility_summary": "Indian citizens aged 18 to 50 with a bank or post office account who consent to auto-debit.",
        "eligibility": {"age_min": 18, "age_max": 50},
        "documents_required": [
            {"name": "Aadhaar-linked bank account", "description": "Premium debit", "is_mandatory": True},
            {"name": "Consent form", "description": "Enrolment", "is_mandatory": True},
        ],
        "application_process": "Give the PMJJBY consent form at your bank or enrol through internet banking / the bank app.",
        "apply_url": "https://financialservices.gov.in/beta/en/pmjjby",
        "helpline": "1800-180-1111",
        "tags": ["insurance", "life", "bank"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "pmsby",
        "name": "PM Suraksha Bima Yojana",
        "full_name": "Pradhan Mantri Suraksha Bima Yojana",
        "name_hindi": "प्रधानमंत्री सुरक्षा बीमा योजना",
        "aliases": ["pmsby", "accident insurance", "suraksha bima"],
        "category": "Financial Inclusion",
        "scheme_type": "central",
        "ministry": "Ministry of Finance",
        "description": "Annual accident insurance through banks and post offices, covering death and disability due to accident.",
        "benefits": "Rs. 2 lakh for accidental death or total disability, and Rs. 1 lakh for partial disability, for a premium of Rs. 20 per year as currently notified.",
        "benefit_amount": "Rs. 2 lakh accidental death cover",
        "eligibility_summary": "Indian citizens aged 18 to 70 with a bank or post office account and auto-debit consent.",
        "eligibility": {"age_min": 18, "age_max": 70},
        "documents_required": [
            {"name": "Aadhaar-linked bank account", "description": "Premium debit", "is_mandatory": True},
            {"name": "Consent form", "description": "Enrolment", "is_mandatory": True},
        ],
        "application_process": "Submit the PMSBY form at the bank or enrol digitally where the bank offers it.",
        "apply_url": "https://financialservices.gov.in/beta/en/pmsby",
        "helpline": "1800-180-1111",
        "tags": ["insurance", "accident", "bank"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "ujjwala",
        "name": "PM Ujjwala Yojana",
        "full_name": "Pradhan Mantri Ujjwala Yojana",
        "name_hindi": "प्रधानमंत्री उज्ज्वला योजना",
        "aliases": ["ujjwala", "lpg scheme", "free gas connection", "pmuy"],
        "category": "Women & Child",
        "scheme_type": "central",
        "ministry": "Ministry of Petroleum and Natural Gas",
        "description": "LPG connections for women from poor households, to reduce cooking on firewood and dung cake.",
        "benefits": "Deposit-free LPG connection, first refill and stove support as notified under the current phase, plus targeted refill subsidies when active.",
        "benefit_amount": "Deposit-free connection and notified refill support",
        "eligibility_summary": "Adult woman from a poor household that does not already have an LPG connection, as per SECC / Ujjwala eligibility lists and OMCs' rules.",
        "eligibility": {"gender": "female", "is_bpl": True},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Woman beneficiary", "is_mandatory": True},
            {"name": "BPL / ration / SECC proof", "description": "Poverty criterion", "is_mandatory": True},
            {"name": "Bank account", "description": "Subsidy", "is_mandatory": True},
            {"name": "Passport photo and address proof", "description": "Connection", "is_mandatory": True},
        ],
        "application_process": "Apply at an LPG distributor or through the Ujjwala / OMC portal. The distributor issues the connection after field verification.",
        "apply_url": "https://www.pmuy.gov.in/",
        "helpline": "1906",
        "tags": ["lpg", "women", "cooking", "bpl"],
        "last_updated": "2026-01-12",
    },
    {
        "id": "ssy",
        "name": "Sukanya Samriddhi Yojana",
        "full_name": "Sukanya Samriddhi Account",
        "name_hindi": "सुकन्या समृद्धि योजना",
        "aliases": ["sukanya", "ssy", "girl child savings", "beti account"],
        "category": "Women & Child",
        "scheme_type": "central",
        "ministry": "Ministry of Finance",
        "description": "Small-savings account for a girl child, with tax benefits under the notified sections and a higher interest rate set by the government each quarter.",
        "benefits": "High interest, tax deduction on deposits (as notified), and tax-exempt interest and maturity under current small-savings rules.",
        "benefit_amount": "Interest rate notified quarterly by DEA",
        "eligibility_summary": "Girl child below 10 years. Account opened by the parent or legal guardian. Maximum two accounts per family, with exceptions for twins or triplets.",
        "eligibility": {"gender": "female", "age_max": 10},
        "documents_required": [
            {"name": "Girl child's birth certificate", "description": "Age", "is_mandatory": True},
            {"name": "Aadhaar of child and guardian", "description": "KYC", "is_mandatory": True},
            {"name": "Address proof of guardian", "description": "Account", "is_mandatory": True},
        ],
        "application_process": "Open the account at a post office or authorised bank branch with birth certificate and KYC.",
        "apply_url": "https://www.indiapost.gov.in/",
        "helpline": "1800-266-6868",
        "tags": ["girl child", "savings", "women", "tax"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "pmmvy",
        "name": "PMMVY",
        "full_name": "Pradhan Mantri Matru Vandana Yojana",
        "name_hindi": "प्रधानमंत्री मातृ वंदना योजना",
        "aliases": ["pmmvy", "maternity benefit", "pregnant woman 5000"],
        "category": "Women & Child",
        "scheme_type": "central",
        "ministry": "Ministry of Women and Child Development",
        "description": "Cash maternity benefit for wage loss during pregnancy and lactation, paid in instalments linked to ANC and child vaccination.",
        "benefits": "Cash benefit of Rs. 5,000 in instalments for the first living child, in addition to JSY where applicable. Later expansions for the second child (girl) follow notified rules.",
        "benefit_amount": "Rs. 5,000 in instalments",
        "eligibility_summary": "Pregnant and lactating women for the first living child, subject to current PMMVY guidelines. Government employees with similar maternity benefits may be excluded.",
        "eligibility": {"gender": "female"},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Woman and husband where asked", "is_mandatory": True},
            {"name": "MCP card", "description": "ANC", "is_mandatory": True},
            {"name": "Bank account", "description": "DBT", "is_mandatory": True},
        ],
        "application_process": "Register at the Anganwadi or approved PMMVY software with MCP details. Instalments follow ANC, delivery, and immunisation milestones.",
        "apply_url": "https://pmmvy.wcd.gov.in/",
        "helpline": "011-23382389",
        "tags": ["women", "maternity", "anganwadi", "dbt"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "bbbp",
        "name": "Beti Bachao Beti Padhao",
        "full_name": "Beti Bachao Beti Padhao",
        "name_hindi": "बेटी बचाओ बेटी पढ़ाओ",
        "aliases": ["bbbp", "beti bachao", "girl child education"],
        "category": "Women & Child",
        "scheme_type": "central",
        "ministry": "Ministry of Women and Child Development",
        "description": "Advocacy and district-level action to improve the child sex ratio and keep girls in school. It is not a direct cash transfer to families.",
        "benefits": "Awareness, district interventions, and convergence with scholarships and school schemes. Individual cash is not the main benefit.",
        "benefit_amount": "No direct individual cash transfer",
        "eligibility_summary": "The programme works through districts and institutions. Families should look at Sukanya Samriddhi, scholarships, and state girl-child schemes for money benefits.",
        "eligibility": {"gender": "female"},
        "documents_required": [],
        "application_process": "There is no household application form. Use linked schemes such as Sukanya Samriddhi or National Scholarship Portal for individual benefits.",
        "apply_url": "https://wcd.nic.in/",
        "helpline": "1098",
        "tags": ["girl child", "education", "awareness"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "nsap-oap",
        "name": "NSAP Old Age Pension",
        "full_name": "Indira Gandhi National Old Age Pension Scheme",
        "name_hindi": "इंदिरा गांधी राष्ट्रीय वृद्धावस्था पेंशन योजना",
        "aliases": ["old age pension", "ignoaps", "nsap", "vridha pension"],
        "category": "Social Welfare",
        "scheme_type": "central",
        "ministry": "Ministry of Rural Development",
        "description": "Monthly pension for elderly persons belonging to households below the poverty line, with state top-ups in many states.",
        "benefits": "Central contribution of Rs. 200 per month (60-79 years) and Rs. 500 per month (80+), often topped up by the state government.",
        "benefit_amount": "Rs. 200-500 central share per month, plus state top-up",
        "eligibility_summary": "BPL persons aged 60 years or more. States may add extra conditions or higher pensions.",
        "eligibility": {"age_min": 60, "is_bpl": True},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Identity and age", "is_mandatory": True},
            {"name": "BPL / ration / SECC proof", "description": "Poverty", "is_mandatory": True},
            {"name": "Bank account", "description": "Pension credit", "is_mandatory": True},
        ],
        "application_process": "Apply at the Gram Panchayat, municipal office, or the state social welfare portal. Many states use their own pension portals on top of NSAP.",
        "apply_url": "https://nsap.nic.in/",
        "helpline": None,
        "tags": ["pension", "elderly", "bpl", "social welfare"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "nfsa",
        "name": "NFSA / PDS ration",
        "full_name": "National Food Security Act",
        "name_hindi": "राष्ट्रीय खाद्य सुरक्षा अधिनियम",
        "aliases": ["ration card", "pds", "nfsa", "food security", "antodaya", "aay"],
        "category": "Social Welfare",
        "scheme_type": "central",
        "ministry": "Ministry of Consumer Affairs, Food and Public Distribution",
        "description": "Legal entitlement to subsidised foodgrains for eligible households through the Public Distribution System.",
        "benefits": "Priority households receive 5 kg of foodgrain per person per month at Rs. 3/2/1 per kg for rice, wheat, and coarse grains. Antyodaya households receive 35 kg per month.",
        "benefit_amount": "5 kg per person per month (PHH) or 35 kg (AAY)",
        "eligibility_summary": "Households identified by the state as Priority or Antyodaya under NFSA. Coverage is up to 75% of the rural and 50% of the urban population.",
        "eligibility": {"is_bpl": True},
        "documents_required": [
            {"name": "Aadhaar of family members", "description": "ePoS authentication", "is_mandatory": True},
            {"name": "Existing ration card or application", "description": "Inclusion", "is_mandatory": True},
            {"name": "Residence proof", "description": "FPS area", "is_mandatory": True},
        ],
        "application_process": "Apply at the local Food and Civil Supplies office or the state ration-card portal. States manage inclusion lists.",
        "apply_url": "https://nfsa.gov.in/",
        "helpline": "1967",
        "tags": ["ration", "food", "pds", "bpl"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "pm-svanidhi",
        "name": "PM SVANidhi",
        "full_name": "PM Street Vendor's AtmaNirbhar Nidhi",
        "name_hindi": "पीएम स्वनिधि",
        "aliases": ["svanidhi", "street vendor loan", "thela loan"],
        "category": "Business & Entrepreneurship",
        "scheme_type": "central",
        "ministry": "Ministry of Housing and Urban Affairs",
        "description": "Working-capital loans for street vendors in urban areas, with interest subsidy and digital-payment incentives.",
        "benefits": "First tranche working-capital loan of Rs. 10,000, with higher subsequent tranches on timely repayment, plus 7% interest subsidy and cashback on digital payments as notified.",
        "benefit_amount": "Rs. 10,000 first loan, higher later tranches",
        "eligibility_summary": "Street vendors in ULBs who were vending on or before the notified date and have a vending certificate or Letter of Recommendation.",
        "eligibility": {"occupations": ["self-employed"]},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "KYC", "is_mandatory": True},
            {"name": "Vending certificate or LoR", "description": "Vendor identity", "is_mandatory": True},
            {"name": "Bank account", "description": "Loan credit", "is_mandatory": True},
        ],
        "application_process": "Apply through the ULB, a CSPs, or pmsvanidhi.mohua.gov.in. A lending institution sanctions the working-capital loan.",
        "apply_url": "https://pmsvanidhi.mohua.gov.in/",
        "helpline": "14445",
        "tags": ["street vendor", "loan", "urban", "self-employed"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "pm-surya-ghar",
        "name": "PM Surya Ghar",
        "full_name": "PM Surya Ghar Muft Bijli Yojana",
        "name_hindi": "प्रधानमंत्री सूर्य घर मुफ्त बिजली योजना",
        "aliases": ["surya ghar", "rooftop solar", "free electricity solar", "pm solar"],
        "category": "Rural Development",
        "scheme_type": "central",
        "ministry": "Ministry of New and Renewable Energy",
        "description": "Central subsidy for household rooftop solar, so families can generate electricity for self-use and export surplus.",
        "benefits": "Central financial assistance on rooftop solar capacity, with a typical design goal of up to 300 units of free electricity a month depending on system size and usage.",
        "benefit_amount": "CFA as notified for 1-3 kW systems",
        "eligibility_summary": "Households with a suitable roof and an electricity connection. The consumer should apply through the national portal and a registered vendor.",
        "eligibility": {},
        "documents_required": [
            {"name": "Electricity consumer number", "description": "DISCOM", "is_mandatory": True},
            {"name": "Aadhaar Card", "description": "Identity", "is_mandatory": True},
            {"name": "Bank account", "description": "Subsidy", "is_mandatory": True},
            {"name": "Roof ownership / NOC", "description": "Installation", "is_mandatory": True},
        ],
        "application_process": "Apply on pmsuryaghar.gov.in, choose a registered vendor, install the system, and claim CFA after DISCOM net-metering.",
        "apply_url": "https://pmsuryaghar.gov.in/",
        "helpline": "15555 / 1800-180-3333",
        "tags": ["solar", "electricity", "rooftop", "subsidy"],
        "last_updated": "2026-01-20",
    },
    {
        "id": "pm-vishwakarma",
        "name": "PM Vishwakarma",
        "full_name": "PM Vishwakarma Yojana",
        "name_hindi": "पीएम विश्वकर्मा",
        "aliases": ["vishwakarma", "artisan scheme", "carpenter blacksmith potter"],
        "category": "Skills & Training",
        "scheme_type": "central",
        "ministry": "Ministry of Micro, Small and Medium Enterprises",
        "description": "Recognition, skilling, toolkit, and credit support for traditional artisans and craftspeople in notified trades.",
        "benefits": "PM Vishwakarma certificate and ID, basic and advanced training with stipend, toolkit incentive, and collateral-free credit at concessional interest as notified.",
        "benefit_amount": "Toolkit incentive plus concessional loans in two tranches",
        "eligibility_summary": "Artisans in 18 notified trades, aged 18+, engaged in the trade using hands and tools, and not having availed similar MSME loan benefits in a look-back period.",
        "eligibility": {"occupations": ["self-employed"], "age_min": 18},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "eKYC", "is_mandatory": True},
            {"name": "Bank account and mobile", "description": "DBT", "is_mandatory": True},
            {"name": "Trade self-declaration", "description": "Verification by Gram Panchayat / ULB", "is_mandatory": True},
        ],
        "application_process": "Register on pmvishwakarma.gov.in with Aadhaar eKYC. The Gram Panchayat or ULB verifies the trade, then benefits are unlocked in stages.",
        "apply_url": "https://pmvishwakarma.gov.in/",
        "helpline": "1800-267-7317",
        "tags": ["artisan", "skill", "credit", "toolkit"],
        "last_updated": "2026-01-15",
    },
    {
        "id": "nsp",
        "name": "National Scholarship Portal",
        "full_name": "National Scholarships",
        "name_hindi": "राष्ट्रीय छात्रवृत्ति पोर्टल",
        "aliases": [
            "scholarship",
            "nsp",
            "pre metric",
            "post metric",
            "student scholarship",
            "minority scholarship",
        ],
        "category": "Education",
        "scheme_type": "central",
        "ministry": "Ministry of Education / various ministries",
        "description": "Single window for central and some state scholarships, including pre-matric, post-matric, merit-cum-means, and ministry-specific student aid.",
        "benefits": "Tuition, maintenance, and in some cases mess or book allowance, as defined by each scholarship scheme on NSP.",
        "benefit_amount": "Varies by scheme",
        "eligibility_summary": "Students who meet the scheme-specific income, class, category, and institute-verification rules. Each NSP scheme has its own form.",
        "eligibility": {"occupations": ["student"]},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Student KYC", "is_mandatory": True},
            {"name": "Income certificate", "description": "Parental income", "is_mandatory": True},
            {"name": "Caste / minority certificate if claimed", "description": "Category", "is_mandatory": False},
            {"name": "Marksheet and institute ID", "description": "Verification", "is_mandatory": True},
            {"name": "Bank account in student name", "description": "DBT", "is_mandatory": True},
        ],
        "application_process": "Register on scholarships.gov.in, select the scheme, fill the form, and submit before the deadline. The institute and state/ministry verify the application.",
        "apply_url": "https://scholarships.gov.in/",
        "helpline": "0120-6619540",
        "tags": ["education", "student", "scholarship"],
        "last_updated": "2026-01-12",
    },
    {
        "id": "pm-poshan",
        "name": "PM POSHAN",
        "full_name": "Pradhan Mantri Poshan Shakti Nirman",
        "name_hindi": "प्रधानमंत्री पोषण शक्ति निर्माण",
        "aliases": ["mid day meal", "mdm", "pm poshan", "school meal"],
        "category": "Education",
        "scheme_type": "central",
        "ministry": "Ministry of Education",
        "description": "Hot cooked meals for children in government and government-aided schools from pre-primary to Class VIII, to improve nutrition and attendance.",
        "benefits": "Free hot cooked meal on school days, with nutrition standards notified by the Centre.",
        "benefit_amount": "One meal per school day",
        "eligibility_summary": "Children enrolled in government and government-aided schools in the covered classes. Families do not apply separately.",
        "eligibility": {"occupations": ["student"]},
        "documents_required": [],
        "application_process": "No separate application. Enrolment in a covered school is sufficient. Contact the school or District Education Officer for service issues.",
        "apply_url": "https://pmposhan.education.gov.in/",
        "helpline": None,
        "tags": ["education", "nutrition", "school"],
        "last_updated": "2026-01-08",
    },
    {
        "id": "jal-jeevan",
        "name": "Jal Jeevan Mission",
        "full_name": "Jal Jeevan Mission",
        "name_hindi": "जल जीवन मिशन",
        "aliases": ["jjm", "har ghar jal", "tap water", "piped water"],
        "category": "Rural Development",
        "scheme_type": "central",
        "ministry": "Ministry of Jal Shakti",
        "description": "Functional household tap connections with regular water supply in rural homes, planned and monitored through the JJM dashboard.",
        "benefits": "Piped drinking water connection at the household, typically designed for 55 litres per capita per day.",
        "benefit_amount": "Household tap connection",
        "eligibility_summary": "Rural households in villages covered by the state's Jal Jeevan plan. This is a public infrastructure programme, not an individual cash scheme.",
        "eligibility": {},
        "documents_required": [
            {"name": "Aadhaar / residence proof", "description": "Where the GP collects household data", "is_mandatory": False}
        ],
        "application_process": "Work through the Gram Panchayat and Public Health Engineering / RWS department. Track village status on ejalshakti.gov.in.",
        "apply_url": "https://ejalshakti.gov.in/jjm/",
        "helpline": None,
        "tags": ["water", "rural", "infrastructure"],
        "last_updated": "2026-01-12",
    },
    {
        "id": "e-shram",
        "name": "e-Shram",
        "full_name": "e-Shram national database of unorganised workers",
        "name_hindi": "ई-श्रम",
        "aliases": ["eshram", "unorganised worker card", "labour card", "e shram"],
        "category": "Employment",
        "scheme_type": "central",
        "ministry": "Ministry of Labour and Employment",
        "description": "National database and Universal Account Number for unorganised workers, used to seed social-security and welfare benefits.",
        "benefits": "Universal Account Number, a digital identity for unorganised workers, and a gateway to accidental insurance and future welfare schemes as notified.",
        "benefit_amount": "UAN plus linked welfare as notified",
        "eligibility_summary": "Unorganised workers aged 16 to 59, including gig and platform workers, who are not EPFO/ESIC members (with limited exceptions as notified).",
        "eligibility": {"occupations": ["self-employed", "unemployed", "farmer"], "age_min": 16, "age_max": 59},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "eKYC", "is_mandatory": True},
            {"name": "Bank account and mobile", "description": "DBT seeding", "is_mandatory": True},
        ],
        "application_process": "Self-register on eshram.gov.in or at a CSC. Download the e-Shram card after OTP and Aadhaar authentication.",
        "apply_url": "https://eshram.gov.in/",
        "helpline": "14434",
        "tags": ["labour", "unorganised", "uan", "gig"],
        "last_updated": "2026-01-12",
    },
    {
        "id": "nrlm",
        "name": "DAY-NRLM",
        "full_name": "Deendayal Antyodaya Yojana - National Rural Livelihoods Mission",
        "name_hindi": "दीनदयाल अंत्योदय योजना राष्ट्रीय ग्रामीण आजीविका मिशन",
        "aliases": ["nrlm", "aajeevika", "shg scheme", "self help group"],
        "category": "Rural Development",
        "scheme_type": "central",
        "ministry": "Ministry of Rural Development",
        "description": "Organises rural poor women into Self Help Groups, with revolving funds, bank linkage, and livelihood support.",
        "benefits": "SHG formation, community investment funds, interest subvention on SHG loans in eligible states, and livelihood services.",
        "benefit_amount": "Revolving fund and CIF as per NRLM norms",
        "eligibility_summary": "Rural poor households, with a focus on women. Identification follows the state's PIP / SECC process.",
        "eligibility": {"gender": "female", "is_bpl": True},
        "documents_required": [
            {"name": "Aadhaar Card", "description": "Member KYC", "is_mandatory": True},
            {"name": "Bank account (SHG)", "description": "Fund credit", "is_mandatory": True},
        ],
        "application_process": "Join or form an SHG through the Village Organisation / SRLM staff. There is no standalone national consumer form.",
        "apply_url": "https://aajeevika.gov.in/",
        "helpline": None,
        "tags": ["women", "shg", "rural", "livelihood"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "startup-india",
        "name": "Startup India",
        "full_name": "Startup India Seed Fund and DPIIT recognition",
        "name_hindi": "स्टार्टअप इंडिया",
        "aliases": ["startup india", "dpiit startup", "seed fund"],
        "category": "Business & Entrepreneurship",
        "scheme_type": "central",
        "ministry": "Department for Promotion of Industry and Internal Trade",
        "description": "DPIIT recognition for eligible startups, which unlocks tax benefits, easier compliance, and access to seed and fund-of-funds programmes as notified.",
        "benefits": "Recognition certificate, eligible tax and IPR benefits, and a path to Startup India Seed Fund through incubators.",
        "benefit_amount": "Benefits vary by notification and incubator",
        "eligibility_summary": "DPIIT-defined startups: incorporated as a private limited company, LLP, or partnership, not older than 10 years, turnover under Rs. 100 crore, and working on innovation or improvement of products/services/processes.",
        "eligibility": {"occupations": ["self-employed"]},
        "documents_required": [
            {"name": "Certificate of incorporation", "description": "Company/LLP", "is_mandatory": True},
            {"name": "PAN and directors' KYC", "description": "Entity", "is_mandatory": True},
            {"name": "Innovation write-up", "description": "Recognition", "is_mandatory": True},
        ],
        "application_process": "Register the entity, then apply for DPIIT recognition on startupindia.gov.in. Seed Fund is applied via an eligible incubator.",
        "apply_url": "https://www.startupindia.gov.in/",
        "helpline": None,
        "tags": ["startup", "business", "innovation"],
        "last_updated": "2026-01-10",
    },
    {
        "id": "myscheme",
        "name": "myScheme",
        "full_name": "myScheme.gov.in scheme finder",
        "name_hindi": "माई स्कीम",
        "aliases": ["myscheme", "scheme finder", "official catalogue"],
        "category": "Social Welfare",
        "scheme_type": "central",
        "ministry": "Ministry of Electronics and Information Technology",
        "description": "Official Government of India catalogue that lists thousands of central and state schemes with eligibility filters. Use it to confirm details after a Sahay recommendation.",
        "benefits": "Searchable official scheme pages, eligibility checks, and links to the implementing ministry or state portal.",
        "benefit_amount": "Not a benefit scheme itself",
        "eligibility_summary": "Open to everyone as a discovery portal.",
        "eligibility": {},
        "documents_required": [],
        "application_process": "Search by category, gender, state, or scheme name at myscheme.gov.in and follow the implementing department's apply link.",
        "apply_url": "https://www.myscheme.gov.in/",
        "helpline": None,
        "tags": ["catalogue", "search", "official"],
        "last_updated": "2026-01-20",
    },
]


def _search_text(scheme: Dict[str, Any]) -> str:
    parts = [
        scheme.get("id", ""),
        scheme.get("name", ""),
        scheme.get("full_name", ""),
        scheme.get("name_hindi", ""),
        " ".join(scheme.get("aliases") or []),
        scheme.get("category", ""),
        scheme.get("ministry", ""),
        scheme.get("description", ""),
        scheme.get("benefits", ""),
        scheme.get("eligibility_summary", ""),
        scheme.get("application_process", ""),
        " ".join(scheme.get("tags") or []),
    ]
    return " ".join(str(part) for part in parts if part)


def _with_search_blob(scheme: Dict[str, Any]) -> Dict[str, Any]:
    record = copy.deepcopy(scheme)
    record["search_text"] = _search_text(record)
    return record


@lru_cache(maxsize=1)
def load_catalog() -> List[Dict[str, Any]]:
    """Return a deep-copied catalog with search blobs attached."""
    return [_with_search_blob(scheme) for scheme in SCHEME_CATALOG]


def list_schemes(
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    schemes = load_catalog()
    if category:
        needle = category.lower()
        schemes = [s for s in schemes if s.get("category", "").lower() == needle]
    if search:
        needle = search.lower()
        schemes = [
            s
            for s in schemes
            if needle in s.get("search_text", "").lower()
        ]
    return [copy.deepcopy(s) for s in schemes]


LEGACY_IDS = {
    "pm-ayushman": "pm-jay",
    "pm-awas-gramin": "pmay-g",
    "pm-awas": "pmay-g",
    "ayushman-bharat": "pm-jay",
}


def get_scheme(scheme_id: str) -> Optional[Dict[str, Any]]:
    if not scheme_id:
        return None
    needle = LEGACY_IDS.get(scheme_id.strip().lower(), scheme_id.strip().lower())
    for scheme in load_catalog():
        if scheme["id"] == needle:
            return copy.deepcopy(scheme)
        aliases = [scheme["name"].lower(), scheme.get("full_name", "").lower()]
        aliases.extend(a.lower() for a in scheme.get("aliases") or [])
        if needle in aliases:
            return copy.deepcopy(scheme)
    return None


def match_eligibility(scheme: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    """Score a user profile against a scheme's structured rules."""
    rules = scheme.get("eligibility") or {}
    matched: List[str] = []
    missing: List[str] = []
    checked = 0

    occupations = [item.lower() for item in rules.get("occupations") or []]
    occupation = (profile.get("occupation") or "").lower()
    if occupations:
        checked += 1
        if occupation and occupation in occupations:
            matched.append(f"Occupation matches ({occupation})")
        elif occupation:
            missing.append("Occupation: " + ", ".join(occupations))

    if rules.get("age_min") is not None:
        checked += 1
        age = profile.get("age")
        if age is not None and age >= rules["age_min"]:
            matched.append(f"Age is at least {rules['age_min']}")
        elif age is not None:
            missing.append(f"Minimum age {rules['age_min']}")

    if rules.get("age_max") is not None:
        checked += 1
        age = profile.get("age")
        if age is not None and age <= rules["age_max"]:
            matched.append(f"Age is at most {rules['age_max']}")
        elif age is not None:
            missing.append(f"Maximum age {rules['age_max']}")

    if rules.get("income_max") is not None:
        checked += 1
        income = profile.get("income")
        if income is not None and income <= rules["income_max"]:
            matched.append("Income is within the listed ceiling")
        elif income is not None:
            missing.append(f"Income should be at most Rs. {int(rules['income_max']):,}")

    if rules.get("gender"):
        checked += 1
        gender = (profile.get("gender") or "").lower()
        if gender and gender == rules["gender"]:
            matched.append("Gender matches")
        elif gender:
            missing.append(f"This scheme is targeted at {rules['gender']} applicants")

    if rules.get("is_bpl"):
        checked += 1
        if profile.get("is_bpl"):
            matched.append("BPL / SECC-linked household")
        else:
            missing.append("Usually requires BPL / SECC inclusion")

    if rules.get("has_land"):
        checked += 1
        if profile.get("has_land"):
            matched.append("Landholding matches")
        elif profile.get("has_land") is False:
            missing.append("Requires cultivable land")

    if rules.get("states"):
        checked += 1
        state = profile.get("state")
        if state and state in rules["states"]:
            matched.append(f"Available in {state}")
        elif state:
            missing.append(f"Not listed for {state}")

    if checked == 0:
        score = 0.55
    else:
        score = len(matched) / checked
        if not matched and not occupation and profile.get("age") is None:
            score = 0.45
    return {
        "match_score": round(score, 3),
        "matched_criteria": matched,
        "missing_criteria": missing,
    }


def catalog_stats() -> Dict[str, Any]:
    schemes = load_catalog()
    categories = sorted({s["category"] for s in schemes})
    return {
        "scheme_count": len(schemes),
        "categories": categories,
        "source": "curated_catalog",
    }
