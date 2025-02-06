import openai
import os

def analyze_with_openai(scraped_text):
    """Analyzes website content using OpenAI."""
    openai.api_key = os.getenv("OPENAI_API_KEY")

    prompt = f"""
    Based on the following website content, determine the industry, main products or services, and the target audience:
    
    {scraped_text}
    
    Provide a structured summary of the business:
    - Industry & Niche:
    - Main Products/Services:
    - Target Audience:
    - Audience Segments:
    - Top 3 Competitors:
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=250
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ OpenAI API request failed: {e}")
        return ""

def get_relevant_subreddits(industry_summary):
    """Fetches the most relevant subreddits based on business profile."""
    prompt = f"""
    Given the following business profile:

    {industry_summary}

    Identify the 3 most relevant subreddits where the target audience actively discusses related topics.
    Return only a list of subreddit names without explanations.
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )
        return response.choices[0].message.content.strip().split("\n")
    except Exception as e:
        print(f"❌ OpenAI API request failed: {e}")
        return []
