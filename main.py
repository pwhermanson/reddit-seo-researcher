""# ===============================================
# Project: Reddit SEO Researcher
#
# Project Structure:
# reddit-seo-researcher/
# │── main.py  # ✅ Parent script that calls all modules
# │── scraper.py  # ✅ Website scraping functions
# │── openai_analysis.py  # ✅ OpenAI API interactions
# │── google_sheets.py  # ✅ Google Sheets authentication & writing functions
# │── utils.py  # ✅ Helper functions (like text formatting)
# │── requirements.txt  # ✅ List of required Python packages
# ===============================================

import re
import scraper
import openai_analysis
import google_sheets
import sys

# ✅ Get Target Website from GitHub Actions Input
if len(sys.argv) < 2:
    print("❌ Error: No target website provided.")
    exit(1)

target_website = sys.argv[1].strip()

# ✅ Remove 'https://' or 'http://' for clean filename use
clean_target_website = re.sub(r"https?://", "", target_website)

# ✅ Ensure 'https://' is included for requests (scraping & API calls)
if not target_website.startswith(("http://", "https://")):
    target_website = f"https://{target_website}"

print(f"🔍 Using cleaned filename: {clean_target_website}")
print(f"🔍 Using full URL for requests: {target_website}")

# ✅ Authenticate Google Sheets
client = google_sheets.authenticate_google_sheets()

# ✅ Debugging: List all available spreadsheets
print("🔍 Available Google Sheets:")
for sheet in client.openall():
    print(f"- {sheet.title}")

# ✅ Attempt to open the correct spreadsheet
spreadsheet_name = f"Reddit SEO Research | {clean_target_website}"
try:
    spreadsheet = client.open(spreadsheet_name)
    print(f"✅ Successfully opened: {spreadsheet_name}")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"❌ Error: Google Sheet '{spreadsheet_name}' not found.")
    print("📌 Ensure the sheet exists and the service account has Editor access.")
    exit(1)

# ✅ Scrape Website
scraped_text = scraper.scrape_target_website(target_website)

# ✅ Analyze with OpenAI
industry_summary = openai_analysis.analyze_with_openai(scraped_text)

# ✅ Store in Google Sheets
google_sheets.add_industry_tab(spreadsheet, industry_summary, analyzed_pages)

# ✅ Fetch Relevant Subreddits
subreddits = openai_analysis.get_relevant_subreddits(industry_summary)
google_sheets.add_subreddit_tab(spreadsheet, subreddits)

print("✅ Process completed successfully!")


