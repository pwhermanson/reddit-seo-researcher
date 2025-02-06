import os
import sys
import json
import gspread
import praw
import openai
import requests
import pandas as pd
from google.oauth2.service_account import Credentials

# --- Get Target Website from GitHub Actions Input ---
if len(sys.argv) < 2:
    print("❌ Error: No target website provided.")
    exit(1)

target_website = sys.argv[1]  # ✅ Correct way to pass the target website from GitHub Actions
print(f"🔍 Processing SEO research for: {target_website}")

# --- Authenticate with Google Sheets Using a Service Account ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def authenticate_google_sheets():
    """Authenticate with Google Sheets using a Service Account."""
    try:
        service_account_info = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        if not service_account_info:
            print("❌ Error: GOOGLE_SHEETS_CREDENTIALS is missing from environment variables.")
            exit(1)

        # Load service account credentials from GitHub Secrets
        creds = Credentials.from_service_account_info(json.loads(service_account_info), scopes=SCOPES)
        return gspread.authorize(creds)

    except Exception as e:
        print(f"❌ Google Sheets authentication failed: {e}")
        exit(1)

# ✅ Initialize Google Sheets Client
client = authenticate_google_sheets()
try:
    spreadsheet = client.open(f"Reddit SEO Research | {target_website}")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"❌ Error: Google Sheet 'Reddit SEO Research | {target_website}' not found.")
    print("📌 Make sure the sheet exists and the service account has Editor access.")
    exit(1)

# --- OpenAI API Setup ---
import openai
import os

# Ensure your OpenAI API key is set in your environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

def get_best_subreddits(target_website):
    """Use OpenAI to analyze the target website and find the best 3 subreddits."""
    prompt = f"""
    You are an SEO expert with deep knowledge of Reddit communities.
    Analyze the target website: {target_website}.
    Step 1️⃣: Determine its primary industry and target audience.
    Step 2️⃣: Identify the top 3 most relevant subreddits where potential customers are actively discussing related topics.
    Step 3️⃣: Consider subreddit popularity, activity level, and alignment with the target website’s products or services.
    Step 4️⃣: Return only the subreddit names in a plain list format (one per line), with no extra text or numbers.
    """


    try:
        client = openai.OpenAI()  # ✅ Create an OpenAI client instance

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )

        raw_response = response.choices[0].message.content.strip()
        print(f"🔍 Raw OpenAI Response:\n{raw_response}")  # ✅ Debugging output

        subreddits = [s.strip().replace("r/", "").replace("-", "").strip() for s in raw_response.split("\n") if s.startswith("r/")]

        print(f"✅ Extracted Subreddits: {subreddits}")  # ✅ Confirm subreddits before storing

        return [s.replace("r/", "").strip() for s in subreddits if s]

    except Exception as e:
        print(f"❌ OpenAI API request failed: {e}")
        return []

# Example usage
target_website = "example.com"
subreddits = get_best_subreddits(target_website)

if not subreddits:
    print("⚠️ No subreddits were identified. Exiting script.")
    exit(1)

print(f"✅ OpenAI identified the best subreddits: {subreddits}")

# ✅ Store subreddits in Google Sheets
worksheet = spreadsheet.add_worksheet(title="Identified Subreddits", rows="10", cols="3")
worksheet.append_row(["Subreddit", "Why It's Relevant", "Estimated Popularity"])

for sub in subreddits:
    worksheet.append_row([sub, "Suggested by OpenAI", "High"])

print("✅ Subreddits successfully added to Google Sheets.")

