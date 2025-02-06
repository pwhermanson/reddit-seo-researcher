import os
import praw
import gspread
import openai
import requests
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

# --- Initialize APIs ---
openai.api_key = os.getenv("OPENAI_API_KEY")  # OpenAI API Key
keywordinsights_api_key = os.getenv("KEYWORDINSIGHTS_API_KEY")  # Store in GitHub Secrets

# --- Reddit API Initialization ---
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="seo-researcher",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

# --- Authenticate with Google Sheets ---
SCOPES = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", SCOPES)
client = gspread.authorize(credentials)
spreadsheet = client.open("Reddit SEO Research")

# --- Step 1: Scrape Reddit Questions ---
def scrape_reddit_questions(subreddit_name, limit=10):
    """Scrape questions from Reddit."""
    subreddit = reddit.subreddit(subreddit_name)
    questions = [post.title for post in subreddit.hot(limit=limit) if post.title.endswith("?")]
    return questions

subreddits = ["marketing", "Entrepreneur", "SaaS"]
all_questions = [q for sub in subreddits for q in scrape_reddit_questions(sub)]

# --- Step 2: Clean Questions Using OpenAI ---
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

# --- Save Cleaned Data to Google Sheets ---
worksheet = spreadsheet.worksheet("Cleaned Questions")
worksheet.clear()
worksheet.append_row(["Raw Reddit Questions", "Cleaned Questions"])
for raw, cleaned in zip(all_questions, cleaned_questions):
    worksheet.append_row([raw, cleaned])

print(f"Saved {len(cleaned_questions)} cleaned questions to Google Sheets!")

# --- Step 3: Send Questions to KeywordInsights API ---
def send_to_keywordinsights(questions):
    """Send cleaned questions to KeywordInsights API for clustering."""
    url = "https://api.keywordinsights.ai/cluster"
    payload = {
        "api_key": keywordinsights_api_key,
        "questions": questions,
        "language": "en",
        "cluster_mode": "topical"  # Adjust as needed
    }
    response = requests.post(url, json=payload)
    return response.json() if response.status_code == 200 else None

cluster_data = send_to_keywordinsights(cleaned_questions)

if cluster_data:
    # --- Step 4: Save KeywordInsights Data to Google Sheets ---
    def save_dataframe_to_sheets(df, sheet_name):
        """Save a pandas DataFrame to Google Sheets."""
        sheet = spreadsheet.worksheet(sheet_name)
        sheet.clear()
        sheet.append_row(df.columns.tolist())  # Add headers
        for row in df.values.tolist():
            sheet.append_row(row)

    # Convert response to DataFrames
    df_cluster_rank = pd.DataFrame(cluster_data.get("Cluster, Rank", []))
    df_pivot_table = pd.DataFrame(cluster_data.get("Pivot Table By Keyword", []))
    df_topical_cluster = pd.DataFrame(cluster_data.get("Topical Cluster", []))
    df_cluster_data = pd.DataFrame(cluster_data.get("Cluster Data", []))

    # Save all tabs to Google Sheets
    save_dataframe_to_sheets(df_cluster_rank, "Cluster, Rank")
    save_dataframe_to_sheets(df_pivot_table, "Pivot Table By Keyword")
    save_dataframe_to_sheets(df_topical_cluster, "Topical Cluster")
    save_dataframe_to_sheets(df_cluster_data, "Cluster Data")

    print("KeywordInsights data saved to Google Sheets!")

# --- Step 5: Identify Top 10 Relevant Questions Using OpenAI ---
def find_top_10_relevant_questions():
    """Identify the 10 most relevant questions from clustered data."""
    df = df_pivot_table  # Use pivot table for ranking
    if df.empty:
        return []
    
    top_10 = df.head(10)["Keyword"].tolist()  # Assuming "Keyword" column contains questions
    return top_10

top_10_questions = find_top_10_relevant_questions()

# Save Top 10 Questions to Google Sheets
worksheet = spreadsheet.worksheet("10 Relevant Questions")
worksheet.clear()
worksheet.append_row(["Most Relevant Questions"])
for question in top_10_questions:
    worksheet.append_row([question])

print("Top 10 relevant questions saved to Google Sheets!")
