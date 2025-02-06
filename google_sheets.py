import gspread
import json
import os
from google.oauth2.service_account import Credentials

def authenticate_google_sheets():
    """Authenticate with Google Sheets using a Service Account."""
    try:
        service_account_info = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if not service_account_info:
            print("❌ GOOGLE_SHEETS_CREDENTIALS is missing.")
            exit(1)

        creds = Credentials.from_service_account_info(json.loads(service_account_info), scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        return gspread.authorize(creds)

    except Exception as e:
        print(f"❌ Google Sheets authentication failed: {e}")
        exit(1)

def add_industry_tab(spreadsheet, industry_details):
    """Creates a new tab in Google Sheets with structured industry data."""
    try:
        industry_worksheet = spreadsheet.add_worksheet(title="Industry Analysis", rows="10", cols="2")
        industry_worksheet.append_row(["Category", "Details"])

        for detail in industry_details:
            if ":" in detail:
                category, value = detail.split(":", 1)
                industry_worksheet.append_row([category.strip(), value.strip()])
            else:
                industry_worksheet.append_row([detail.strip(), ""])

        print("✅ Industry Analysis tab added to Google Sheets.")
    except Exception as e:
        print(f"❌ Failed to add Industry Analysis tab: {e}")

def add_subreddit_tab(spreadsheet, subreddits):
    """Creates a new tab in Google Sheets with subreddit recommendations."""
    try:
        subreddit_worksheet = spreadsheet.add_worksheet(title="Relevant Subreddits", rows="10", cols="1")
        subreddit_worksheet.append_row(["Top 3 Subreddits"])

        for subreddit in subreddits:
            subreddit_worksheet.append_row([subreddit])

        print("✅ Subreddit recommendations added to Google Sheets.")
    except Exception as e:
        print(f"❌ Failed to add Subreddit Analysis tab: {e}")
