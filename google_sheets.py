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
    """Authenticates with Google Sheets using a service account."""
    try:
        from google.oauth2.service_account import Credentials
        import os
        import json

        # ✅ Load credentials from environment variable
        service_account_info = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        creds = Credentials.from_service_account_info(json.loads(service_account_info), scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])

        return gspread.authorize(creds)

    except Exception as e:
        print(f"❌ Google Sheets authentication failed: {e}")
        exit(1)

import gspread
from gspread.exceptions import APIError
import time

def add_industry_tab(spreadsheet, industry_summary):
    """Creates a new tab in Google Sheets with structured business profile information."""
    try:
        industry_worksheet = spreadsheet.add_worksheet(title="Industry Analysis", rows="10", cols="2")

        # ✅ Extract individual sections from OpenAI response
        lines = industry_summary.split("\n")
        structured_data = {
            "Industry & Niche": "",
            "Main Products/Services": "",
            "Target Audience": "",
            "Audience Segments": "",
            "Top 3 Competitors": ""
        }

        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("**Industry & Niche:**"):
                current_section = "Industry & Niche"
            elif line.startswith("**Main Products/Services:**"):
                current_section = "Main Products/Services"
            elif line.startswith("**Target Audience:**"):
                current_section = "Target Audience"
            elif line.startswith("**Audience Segments:**"):
                current_section = "Audience Segments"
            elif line.startswith("**Top 3 Competitors:**"):
                current_section = "Top 3 Competitors"
            elif current_section and line:
                structured_data[current_section] += line + "\n"

        # ✅ Format the structured data properly
        data = [
            ["Category", "Details"],
            ["Industry & Niche", structured_data["Industry & Niche"].strip()],
            ["Main Products/Services", structured_data["Main Products/Services"].strip()],
            ["Target Audience", structured_data["Target Audience"].strip()],
            ["Audience Segments", structured_data["Audience Segments"].strip()],
            ["Top 3 Competitors", structured_data["Top 3 Competitors"].strip()]
        ]

        # ✅ Use batch_update() for optimized writing
        industry_worksheet.batch_update([{"range": f"A{idx+1}:B{idx+1}", "values": [row]} for idx, row in enumerate(data)])

        print("✅ Industry Analysis tab updated with structured formatting.")
    except APIError as e:
        if "Quota exceeded" in str(e):
            print("⏳ Quota exceeded. Retrying in 30 seconds...")
            time.sleep(30)
            add_industry_tab(spreadsheet, industry_summary)
        else:
            print(f"❌ Failed to add Industry Analysis tab: {e}")


def add_subreddit_tab(spreadsheet, subreddits):
    """Creates a new tab in Google Sheets with subreddit recommendations."""
    try:
        subreddit_worksheet = spreadsheet.add_worksheet(title="Relevant Subreddits", rows="10", cols="1")

        # ✅ Prepare batch data
        data = [["Top 3 Subreddits"]] + [[sub] for sub in subreddits]

        # ✅ Use batch_update() for optimized writing
        subreddit_worksheet.batch_update([{"range": f"A{idx+1}", "values": [row]} for idx, row in enumerate(data)])

        print("✅ Subreddit recommendations added to Google Sheets.")
    except APIError as e:
        if "Quota exceeded" in str(e):
            print("⏳ Quota exceeded. Retrying in 30 seconds...")
            time.sleep(30)
            add_subreddit_tab(spreadsheet, subreddits)
        else:
            print(f"❌ Failed to add Subreddit Analysis tab: {e}")
