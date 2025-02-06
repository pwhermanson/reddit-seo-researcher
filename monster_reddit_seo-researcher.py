import os
import praw
import csv

# Initialize Reddit API with credentials from GitHub Secrets
reddit = praw.Reddit(
    client_id=os.getenv("REDDIT_CLIENT_ID"),
    client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
    user_agent="seo-researcher",
    username=os.getenv("REDDIT_USERNAME"),
    password=os.getenv("REDDIT_PASSWORD")
)

# List of subreddits to scrape
subreddits = ["marketing", "Entrepreneur", "SaaS"]

# Function to scrape questions
def scrape_reddit_questions(subreddit_name, limit=10):
    subreddit = reddit.subreddit(subreddit_name)
    questions = []
    for post in subreddit.hot(limit=limit):
        if post.title.endswith("?"):  # Only select questions
            questions.append(post.title)
    return questions

# Collect questions from all subreddits
all_questions = []
for sub in subreddits:
    all_questions.extend(scrape_reddit_questions(sub))

# Save to CSV
output_file = "reddit_questions.csv"
with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Question"])
    for question in all_questions:
        writer.writerow([question])

print(f"Scraped {len(all_questions)} questions and saved to {output_file}")
