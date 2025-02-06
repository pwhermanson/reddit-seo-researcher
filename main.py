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

import scraper
import openai_analysis
import google_sheets

# ✅ Get Target Website
target_website = "https://example.com"  # Replace with actual website

# ✅ Authenticate Google Sheets
client = google_sheets.authenticate_google_sheets()
spreadsheet = client.open(f"Reddit SEO Research | {target_website}")

# ✅ Scrape Website
scraped_text = scraper.scrape_target_website(target_website)

# ✅ Analyze with OpenAI
industry_summary = openai_analysis.analyze_with_openai(scraped_text)

# ✅ Store in Google Sheets
google_sheets.add_industry_tab(spreadsheet, industry_summary)

# ✅ Fetch Relevant Subreddits
subreddits = openai_analysis.get_relevant_subreddits(industry_summary)
google_sheets.add_subreddit_tab(spreadsheet, subreddits)

print("✅ Process completed successfully!")
