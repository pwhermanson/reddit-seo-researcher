import os
import praw
import gspread
import openai
import requests
import pandas as pd
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

# --- Get Target Website from Input ---
target_website = os.getenv("TARGET_WEBSITE")

if not target_website:
    print("❌ Error: No target website provided.")
    exit(1)

print(f"🔍 Identifying subreddits for: {target_website}")

# --- Authenticate with Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]

def authenticate_google_sheets():
    """Authenticate with Google Sheets using OAuth 2.0."""
    creds = None
    token_data = os.getenv("GOOGLE_SHEETS_TOKEN")
    
    if token_data:
        creds = Credentials.from_authorized_user_info(eval(token_data), SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            print("❌ Google Sheets authentication failed.")
            exit(1)
    
    return gspread.authorize(creds)

client = authenticate_google_sheets()
spreadsheet = client.open(f"Reddit SEO Research | {target_website}")

# --- OpenAI API Setup ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Step 1: Identify the Best 3 Subreddits (Using OpenAI) ---
def get_best_subreddits(target_website):
    """Use OpenAI to analyze the target website and find the best 3 subreddits."""
    prompt = f"""
    You are an expert at finding the best Reddit communities for different businesses. 
    Given the target website: {target_website}, analyze its industry, target audience, and business purpose.
    Suggest the 3 most relevant subreddits where potential customers or industry professionals actively engage.
    Return only a list of the 3 subreddit names without explanations.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": "You are a Reddit SEO research assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=50
    )

    subreddits = response["choices"][0]["message"]["content"].strip().split("\n")
    return [s.replace("r/", "").strip() for s in subreddits if s]

subreddits = get_best_subreddits(target_website)

# Store subreddits in Google Sheets
worksheet = spreadsheet.add_worksheet(title="Identified Subreddits", rows="10", cols="3")
worksheet.append_row(["Subreddit", "Why It's Relevant", "Estimated Popularity"])

for sub in subreddits:
    worksheet.append_row([sub, "Suggested by OpenAI", "High"])

print(f"✅ OpenAI identified the best subreddits: {subreddits}")

# --- Step 2: Scrape Reddit Questions ---
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="seo-researcher",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

def scrape_reddit_questions(subreddit_name, limit=10):
    """Scrape questions from Reddit."""
    subreddit = reddit.subreddit(subreddit_name)
    return [post.title for post in subreddit.hot(limit=limit) if post.title.endswith("?")]

all_questions = [q for sub in subreddits for q in scrape_reddit_questions(sub)]

# Save raw questions to Google Sheets
worksheet = spreadsheet.add_worksheet(title="Raw Reddit Questions", rows="500", cols="1")
worksheet.append_row(["Raw Reddit Questions"])
for question in all_questions:
    worksheet.append_row([question])

print(f"✅ Scraped {len(all_questions)} questions from Reddit.")

# --- Step 3: Clean Questions Using OpenAI ---
def clean_questions_with_openai(questions):
    """Use OpenAI to clean and simplify Reddit questions."""
    cleaned_questions = []
    for question in questions:
        prompt = f"Rewrite this question concisely: '{question}'"
        response = openai.Completion.create(
            model="gpt-4-turbo",
            prompt=prompt,
            max_tokens=50
        )
        cleaned_questions.append(response["choices"][0]["text"].strip())
    return cleaned_questions

cleaned_questions = clean_questions_with_openai(all_questions)

# Save Cleaned Questions to Google Sheets
worksheet = spreadsheet.add_worksheet(title="Cleaned Questions", rows="500", cols="2")
worksheet.append_row(["Raw Reddit Questions", "Cleaned Questions"])
for raw, cleaned in zip(all_questions, cleaned_questions):
    worksheet.append_row([raw, cleaned])

print(f"✅ Cleaned {len(cleaned_questions)} questions.")

# --- Step 4: Send Questions to KeywordInsights API ---
print("🚀 Sending cleaned questions to KeywordInsights API for clustering...")

keywordinsights_api_key = os.getenv("KEYWORDINSIGHTS_API_KEY")
url = "https://api.keywordinsights.ai/cluster"

payload = {
    "api_key": keywordinsights_api_key,
    "questions": cleaned_questions,
    "language": "en",
    "cluster_mode": "topical"
}

response = requests.post(url, json=payload)
cluster_data = response.json() if response.status_code == 200 else None

if cluster_data:
    def save_dataframe_to_sheets(df, sheet_name):
        """Save a pandas DataFrame to Google Sheets."""
        sheet = spreadsheet.add_worksheet(title=sheet_name, rows="500", cols="10")
        sheet.append_row(df.columns.tolist())  # Add headers
        for row in df.values.tolist():
            sheet.append_row(row)

    df_cluster_rank = pd.DataFrame(cluster_data.get("
