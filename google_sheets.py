# ===============================================
# 📌 How It Works - Google Sheets Integration
# ===============================================
# This module handles authentication and data writing to Google Sheets.
#
# 🚀 Key Functions:
# 1️⃣ authenticate_google_sheets() → Authenticates using a service account.
# 2️⃣ extract_industry_details() → Parses OpenAI response into structured data.
# 3️⃣ add_industry_tab(spreadsheet, industry_summary, analyzed_pages) → Creates a new tab with business profile data.
# 4️⃣ add_subreddit_tab(spreadsheet, subreddits) → Creates a new tab with the top 3 relevant subreddits.
#
# 🛠️ Optimizations:
# ✅ Uses batch_update() to reduce API calls & avoid quota limits.
# ✅ Automatically retries on quota errors (APIError 429).
# ✅ Ensures all data is structured and written efficiently.
# ===============================================

import gspread
import json  # ✅ Fix: Import missing json module
import os
import time
import re  # ✅ Added for improved text extraction
from gspread.exceptions import APIError

# ✅ Google Sheets Authentication
def authenticate_google_sheets():
    """Authenticates and returns a Google Sheets client."""
    try:
        service_account_info = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
        creds = gspread.service_account_from_dict(service_account_info)
        return creds
    except Exception as e:
        print(f"❌ Google Sheets authentication failed: {e}")
        return None  # ✅ Prevents crashes if authentication fails

# ✅ Extract Industry Details (Improved)
def extract_industry_details(industry_summary):
    """Extracts structured business details from OpenAI response."""
    structured_data = {
        "Industry & Niche": "❌ Missing Data",
        "Main Products/Services": "❌ Missing Data",
        "Target Audience": "❌ Missing Data",
        "Audience Segments": "❌ Missing Data",
        "Top 3 Competitors": "❌ Missing Data",
        "Key Themes from Website": "❌ Missing Data",
    }

    current_section = None
    lines = industry_summary.split("\n")

    for line in lines:
        line = line.strip()
        
        # ✅ Detect and assign each section properly
        if re.search(r"\b(Industry & Niche|Industry Overview|Business Type)\b", line, re.IGNORECASE):
            current_section = "Industry & Niche"
        elif re.search(r"\b(Main Products|Products & Services)\b", line, re.IGNORECASE):
            current_section = "Main Products/Services"
        elif re.search(r"\b(Target Audience|Ideal Customer|Target Market)\b", line, re.IGNORECASE):
            current_section = "Target Audience"
        elif re.search(r"\b(Audience Segments|User Groups)\b", line, re.IGNORECASE):
            current_section = "Audience Segments"
        elif re.search(r"\b(Top 3 Competitors|Market Rivals|Competition)\b", line, re.IGNORECASE):
            current_section = "Top 3 Competitors"
        elif re.search(r"\b(Key Themes from Website|Website Messaging|Brand Focus)\b", line, re.IGNORECASE):
            current_section = "Key Themes from Website"
        elif current_section and line:
            structured_data[current_section] += line + " "

    return structured_data  

    # ✅ Strip any trailing spaces and ensure empty fields are handled
for key in structured_data.keys():
    if "❌ Missing Data" in structured_data[key]:  
        structured_data[key] = structured_data[key].replace("❌ Missing Data", "").strip()  
    structured_data[key] = structured_data[key] if structured_data[key] else "❌ Missing Data"


# ✅ Add Industry Tab
def add_industry_tab(spreadsheet, industry_summary, analyzed_pages):
    """Creates a new tab in Google Sheets with structured business profile information."""
    try:
        # ✅ Extract structured details
        structured_data = extract_industry_details(industry_summary)

        # ✅ Create a new worksheet for Industry Analysis
        industry_worksheet = spreadsheet.add_worksheet(title="Industry Analysis", rows="20", cols="2")

        # ✅ Organize data into rows
        data = [
            ["Category", "Details"],
            ["Industry & Niche", structured_data["Industry & Niche"]],
            ["Main Products/Services", structured_data["Main Products/Services"]],
            ["Target Audience", structured_data["Target Audience"]],
            ["Audience Segments", structured_data["Audience Segments"]],
            ["Top 3 Competitors", structured_data["Top 3 Competitors"]],
            ["Primary Website Pages Analyzed", "\n".join(analyzed_pages) if analyzed_pages else "❌ No Pages Analyzed"],
            ["Key Themes from Website", structured_data["Key Themes from Website"]],
        ]

        # ✅ Write data efficiently using batch_update()
        industry_worksheet.batch_update([
            {"range": f"A{idx+1}:B{idx+1}", "values": [row]}
            for idx, row in enumerate(data)
        ])

        print("✅ Industry Analysis tab updated with structured formatting.")

    except APIError as e:
        if "Quota exceeded" in str(e):
            print("⏳ Quota exceeded. Retrying in 30 seconds...")
            time.sleep(30)
            add_industry_tab(spreadsheet, industry_summary, analyzed_pages)
        else:
            print(f"❌ Failed to add Industry Analysis tab: {e}")

# ✅ Add Subreddit Tab
def add_subreddit_tab(spreadsheet, subreddits, industry_summary):
    """Creates a new tab in Google Sheets with subreddit recommendations, formatted properly and validated by OpenAI."""
    try:
        if not spreadsheet:
            print("❌ No valid spreadsheet object. Skipping subreddit analysis.")
            return

        # ✅ OpenAI Validation - Ensures only 3 relevant subreddits
        validated_subreddits = validate_subreddits_with_openai(subreddits, industry_summary)

        if len(validated_subreddits) < 3:
            print("⚠️ OpenAI removed irrelevant subreddits. Fetching replacements...")
            validated_subreddits = fetch_additional_subreddits(validated_subreddits, industry_summary)

        if not validated_subreddits or len(validated_subreddits) < 3:
            print("❌ OpenAI failed to return 3 relevant subreddits. Exiting subreddit analysis.")
            return

        # ✅ Create a new worksheet for subreddit analysis
        subreddit_worksheet = spreadsheet.add_worksheet(title="Relevant Subreddits", rows="10", cols="3")
        subreddit_worksheet.append_row(["Subreddit", "URL", "Relevance Explanation"])  # ✅ Updated headers

        # ✅ Format subreddits with proper links and explanations
        formatted_subreddits = [[sub, f"https://www.reddit.com/{sub}", explanation] for sub, explanation in validated_subreddits]

        # ✅ Batch update for efficiency
        subreddit_worksheet.update("A2:C{}".format(len(formatted_subreddits) + 1), formatted_subreddits)

        print("✅ Relevant Subreddits tab updated with proper formatting, links, and explanations.")

    except APIError as e:
        if "Quota exceeded" in str(e):
            print("⏳ Quota exceeded. Retrying in 30 seconds...")
            time.sleep(30)
            return add_subreddit_tab(spreadsheet, subreddits, industry_summary)
        else:
            print(f"❌ Failed to add Subreddit Analysis tab: {e}")

def validate_subreddits_with_openai(subreddits, industry_summary):
    """Uses OpenAI to check subreddit relevance and provide explanations."""
    validate_prompt = f"""
    Given the target business profile:

    {industry_summary}

    And the following subreddit recommendations:

    {", ".join([f"r/{s}" for s in subreddits])}

    Check if each subreddit is highly relevant to the business profile. 
    - Remove any subreddit that is not **directly related** to the business or target audience.
    - If any subreddits are removed, replace them with **new, highly relevant subreddits** until exactly **3 strong recommendations** remain.
    - For each subreddit, provide a **brief explanation** (2 sentences max) of why it is relevant.

    Format the output like this:
    r/SubredditName - Explanation
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": validate_prompt}],
            max_tokens=150
        )
        validated_subs = response.choices[0].message.content.strip().split("\n")
        validated_subs = [sub.split(" - ") for sub in validated_subs if " - " in sub]

        return [(sub[0].strip(), sub[1].strip()) for sub in validated_subs]
    
    except Exception as e:
        print(f"❌ OpenAI API request failed during subreddit validation: {e}")
        return []


def fetch_additional_subreddits(existing_subreddits, industry_summary):
    """Fetches additional subreddits if OpenAI removed irrelevant ones."""
    prompt = f"""
    Given the target business profile:

    {industry_summary}

    The following subreddits have already been verified as relevant:
    {", ".join(existing_subreddits)}

    Find **additional subreddits** that are **highly relevant** to this business until the total reaches 3.
    Format the output like this:
    r/SubredditName - Explanation
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        new_subs = response.choices[0].message.content.strip().split("\n")
        new_subs = [sub.split(" - ") for sub in new_subs if " - " in sub]

        return existing_subreddits + [(sub[0].strip(), sub[1].strip()) for sub in new_subs]
    
    except Exception as e:
        print(f"❌ OpenAI API request failed while fetching additional subreddits: {e}")
        return existing_subreddits

