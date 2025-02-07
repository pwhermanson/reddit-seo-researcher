# ===============================================
# 📌 How It Works - Google Sheets Integration
# ===============================================
# This module handles authentication and data writing to Google Sheets.
#
# 🚀 Key Functions:
# 1️⃣ authenticate_google_sheets()  → Authenticates using a service account.
# 2️⃣ add_industry_tab(spreadsheet, industry_summary)  → Creates a new tab with business profile data.
# 3️⃣ add_subreddit_tab(spreadsheet, subreddits)  → Creates a new tab with the top 3 relevant subreddits.
#
# 🛠️ Optimizations:
# ✅ Uses batch_update() to reduce API calls & avoid quota limits.
# ✅ Automatically retries on quota errors (APIError 429).
# ✅ Ensures all data is structured and written efficiently.
# ===============================================

import gspread
from gspread.exceptions import APIError
import time

def authenticate_google_sheets():
    """Authenticates and returns a Google Sheets client."""
    try:
        service_account_info = json.loads(os.getenv("GOOGLE_SHEETS_CREDENTIALS"))
        creds = gspread.service_account_from_dict(service_account_info)
        return creds
    except Exception as e:
        print(f"❌ Google Sheets authentication failed: {e}")
        return None

def add_industry_tab(spreadsheet, industry_summary, analyzed_pages):
    """Creates a new tab in Google Sheets with structured business profile information."""
    try:
        # ✅ Create a new worksheet for Industry Analysis
        industry_worksheet = spreadsheet.add_worksheet(title="Industry Analysis", rows="20", cols="2")

        # ✅ Extract individual sections from OpenAI response
        lines = industry_summary.split("\n")
        structured_data = {
            "Industry & Niche": "",
            "Main Products/Services": "",
            "Target Audience": "",
            "Audience Segments": "",
            "Top 3 Competitors": "",
            "Key Themes from Website": "",
        }

        current_section = None

        for line in lines:
            line = line.strip()
            if "**Industry & Niche:**" in line:
                current_section = "Industry & Niche"
            elif current_section == "Industry & Niche" and line.strip():
                structured_data["Industry & Niche"] += line.strip() + " "
            elif line.startswith("**Main Products/Services:**"):
                current_section = "Main Products/Services"
            elif line.startswith("**Target Audience:**"):
                current_section = "Target Audience"
            elif line.startswith("**Audience Segments:**"):
                current_section = "Audience Segments"
            elif line.startswith("**Top 3 Competitors:**"):
                current_section = "Top 3 Competitors"
            elif line.startswith("**Key Themes from Website:**"):
                current_section = "Key Themes from Website"
            elif current_section and line:
                structured_data[current_section] += line + "\n"

        # ✅ Ensure structured data is properly cleaned
        structured_data = {k: v.strip() if v else "❌ Missing Data" for k, v in structured_data.items()}

        # ✅ Format the structured data properly for Google Sheets
        data = [
            ["Category", "Details"],
            ["Industry & Niche", structured_data["Industry & Niche"]],
            ["Main Products/Services", structured_data["Main Products/Services"]],
            ["Target Audience", structured_data["Target Audience"]],
            ["Audience Segments", structured_data["Audience Segments"]],
            ["Top 3 Competitors", structured_data["Top 3 Competitors"]],
            ["Primary Website Pages Analyzed", "\n".join(analyzed_pages) if analyzed_pages else "❌ No Pages Analyzed"],
            ["Key Themes from Website", structured_data["Key Themes from Website"]]
        ]

        # ✅ Optimized batch update for performance
        industry_worksheet.update("A1:B{}".format(len(data)), data)

        print("✅ Industry Analysis tab updated with structured formatting.")

    except APIError as e:
        if "Quota exceeded" in str(e):
            print("⏳ Quota exceeded. Retrying in 30 seconds...")
            time.sleep(30)
            add_industry_tab(spreadsheet, industry_summary, analyzed_pages)
        else:
            print(f"❌ Failed to add Industry Analysis tab: {e}")

def add_subreddit_tab(spreadsheet, subreddits):
    """Creates a new tab in Google Sheets with subreddit recommendations, formatted properly."""
    try:
        subreddit_worksheet = spreadsheet.add_worksheet(title="Relevant Subreddits", rows="10", cols="2")
        subreddit_worksheet.append_row(["Subreddit", "URL"])  # ✅ Updated headers

        formatted_subreddits = [[sub, f"https://www.reddit.com/{sub}"] for sub in subreddits]

        # ✅ Batch update for performance
        subreddit_worksheet.update("A2:B{}".format(len(formatted_subreddits) + 1), formatted_subreddits)

        print("✅ Relevant Subreddits tab updated with proper formatting and links.")

    except APIError as e:
        if "Quota exceeded" in str(e):
            print("⏳ Quota exceeded. Retrying in 30 seconds...")
            time.sleep(30)
            return add_subreddit_tab(spreadsheet, subreddits)
        else:
            print(f"❌ Failed to add Subreddit Analysis tab: {e}")
