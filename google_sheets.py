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

def add_industry_tab(spreadsheet, industry_summary):
    """Creates a new tab in Google Sheets with business profile information."""
    try:
        industry_worksheet = spreadsheet.add_worksheet(title="Industry Analysis", rows="10", cols="2")

        # ✅ Prepare data in batch (single API request)
        data = [
            ["Category", "Details"],
            ["Industry & Niche", industry_summary],
            ["Main Products/Services", "Extracting..."],
            ["Target Audience", "Extracting..."],
            ["Audience Segments", "Extracting..."],
            ["Top 3 Competitors", "Extracting..."]
        ]

        # ✅ Use `batch_update()` instead of multiple `append_row()` calls
        industry_worksheet.batch_update([{"range": f"A{idx+1}:B{idx+1}", "values": [row]} for idx, row in enumerate(data)])

        print("✅ Industry Analysis tab added to Google Sheets.")
    except APIError as e:
        if "Quota exceeded" in str(e):
            print("⏳ Quota exceeded. Retrying in 30 seconds...")
            time.sleep(30)  # ✅ Wait and retry
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
