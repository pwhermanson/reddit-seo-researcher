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
            print("❌ GOOGLE_SHEETS_CREDENTIALS is missing from environment variables.")
            exit(1)

        creds = Credentials.from_service_account_info(json.loads(service_account_info), scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ])
        return gspread.authorize(creds)

    except Exception as e:
        print(f"❌ Google Sheets authentication failed: {e}")
        exit(1)

# ✅ Initialize Google Sheets Client ---
client = authenticate_google_sheets()
try:
    spreadsheet = client.open(f"Reddit SEO Research | {target_website}")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"❌ Error: Google Sheet 'Reddit SEO Research | {target_website}' not found.")
    print("📌 Make sure the sheet exists and the service account has Editor access.")
    exit(1)

# --- Scrape Target Website ---
def scrape_target_website(target_website):
    """Scrapes the target website's homepage and navigation pages."""
    print(f"🔍 Crawling {target_website} to extract key information...")

    nav_links = get_navigation_links(target_website)
    if not nav_links:
        print("⚠️ No navigation links found. Analyzing homepage only.")
        nav_links = [target_website]

    scraped_text = ""
    for link in nav_links[:5]:  # Limit to first 5 navigation links
        print(f"📄 Scraping: {link}")
        text = extract_text_from_url(link)
        if text:
            scraped_text += text + "\n\n"
        time.sleep(2)  # Add delay to prevent server overload

    return scraped_text

# --- OpenAI API Setup ---
# ✅ Scrape website first
scraped_text = scrape_target_website(target_website)

# ✅ Then analyze the scraped text using OpenAI
industry_info = analyze_with_openai(scraped_text, spreadsheet)

# --- Initialize OpenAI API ---
import openai
import os

# OpenAI Analysis
def analyze_with_openai(scraped_text, spreadsheet):
    """Sends extracted website text to OpenAI API for analysis and stores results."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    prompt = f"""
    Based on the following website content, determine the industry, main products or services, and the target audience:
    
    {scraped_text}
    
    Provide a summary of the industry, business focus, and key details in 3-5 sentences.
    """
    
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )

    
       def extract_industry_details(industry_summary):
    """Extracts structured industry details from OpenAI's response."""
    prompt = f"""
    The following is a business profile summary:
    {industry_summary}

    Extract structured details:
    - Industry & Niche:
    - Main Products/Services:
    - Target Audience:
    - Audience Segments:
    - Top 3 Competitors:
    
    Return each category in a separate line.
    """

    response = openai.OpenAI().chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200
    )

    details = response.choices[0].message.content.strip().split("\n")
    return details

# ✅ Extract structured details 
structured_details = extract_industry_details(industry_summary)

# ✅ Store in Google Sheets (This section is not complete)
industry_worksheet = spreadsheet.add_worksheet(title="Industry Analysis", rows="10", cols="2")
industry_worksheet.append_row(["Category", "Details"])
for detail in structured_details:
    category, value = detail.split(":", 1)
    industry_worksheet.append_row([category.strip(), value.strip()])

print("✅ Industry Analysis tab added to Google Sheets.")
 
    except Exception as e:
        print(f"❌ Failed to add Industry Analysis tab: {e}")

def add_subreddit_tab_to_sheets(spreadsheet, subreddits):
    """Creates a new tab in Google Sheets with subreddit recommendations."""
    try:
        subreddit_worksheet = spreadsheet.add_worksheet(title="Relevant Subreddits", rows="10", cols="1")
        subreddit_worksheet.append_row(["Top 3 Subreddits"])
        for subreddit in subreddits:
            subreddit_worksheet.append_row([subreddit])
        print("✅ Subreddit recommendations added to Google Sheets.")
    except Exception as e:
        print(f"❌

# The section above is not complete --



        # Request subreddit recommendations
        subreddit_prompt = f"""
        Given the following business profile:
        
        {industry_summary}
        
        Identify the 3 most relevant subreddits where the target audience actively discusses related topics.
        Return only a list of subreddit names without explanations.
        """
        subreddit_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": subreddit_prompt}],
            max_tokens=50
        )
        
        subreddits = [
    s.strip().replace("r/", "").replace("-", "").strip()
    for s in subreddit_response.choices[0].message.content.strip().split("\n")
    if "r/" in s
]

        add_subreddit_tab_to_sheets(spreadsheet, subreddits)
        
        return industry_summary

    except Exception as e:
        print(f"❌ OpenAI API request failed: {e}")
        return ""


def analyze_with_openai(scraped_text, spreadsheet):
    """Sends extracted website text to OpenAI API for analysis and stores results."""
    openai.api_key = os.getenv("OPENAI_API_KEY")
    
    prompt = f"""
    Based on the following website content, determine the industry, main products or services, and the target audience:
    
    {scraped_text}
    
    Provide a summary of the industry, business focus, and key details in 3-5 sentences.
    """
    
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        
        industry_summary = response.choices[0].message.content.strip()
        print(f"✅ OpenAI Industry Analysis:\n{industry_summary}")
        add_industry_tab_to_sheets(spreadsheet, industry_summary)

        # Request subreddit recommendations
        subreddit_prompt = f"""
        Given the following business profile:
        
        {industry_summary}
        
        Identify the 3 most relevant subreddits where the target audience actively discusses related topics.
        Return only a list of subreddit names without explanations.
        """
        subreddit_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": subreddit_prompt}],
            max_tokens=50
        )
        
        subreddits = subreddit_response.choices[0].message.content.strip().split("\n")
        add_subreddit_tab_to_sheets(spreadsheet, subreddits)
        
        return industry_summary

    except Exception as e:
        print(f"❌ OpenAI API request failed: {e}")
        return ""


# ✅ Store subreddits in Google Sheets
worksheet = spreadsheet.add_worksheet(title="Identified Subreddits", rows="10", cols="3")
worksheet.append_row(["Subreddit", "Why It's Relevant", "Estimated Popularity"])

for sub in subreddits:
    worksheet.append_row([sub, "Suggested by OpenAI", "High"])

print("✅ Subreddits successfully added to Google Sheets.")

