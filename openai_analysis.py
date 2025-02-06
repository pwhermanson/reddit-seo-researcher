# ==================================================
# 📌 How It Works - OpenAI Analysis
# ==================================================
# 1️⃣ The `analyze_with_openai()` function:
#    - Takes scraped website content as input.
#    - Sends it to OpenAI for analysis.
#    - Extracts structured business insights (Industry, Products, Audience, Competitors, etc.).
#    - Ensures OpenAI always returns a properly formatted response.
#    - Provides a default structured response if OpenAI fails.
#
# 2️⃣ The `get_relevant_subreddits()` function:
#    - Takes the industry summary as input.
#    - Sends it to OpenAI to identify **3 most relevant subreddits**.
#    - Extracts subreddit names in a clean format (`r/SubredditName`).
#    - Ensures results are structured correctly for use in other processes.
#
# ✅ Debugging:
#    - Logs raw OpenAI responses for visibility.
#    - Ensures structured extraction before storing in Google Sheets.
#    - Provides fallback responses in case of API failure.
# ==================================================


import openai
import os

# ✅ Set OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

def analyze_with_openai(scraped_text):
    """Analyzes website content using OpenAI to extract business insights."""
    
    prompt = f"""
    You are a business analyst. Analyze the following website content and provide a structured business profile:

    **Website Content:**
    {scraped_text}

    **Output Format (Return EXACTLY this structure):**
    **Industry & Niche:** [Industry summary]
    **Main Products/Services:** [List of main products/services]
    **Target Audience:** [Description of the target audience]
    **Audience Segments:** [List of audience segments]
    **Top 3 Competitors:** [Competitor names]
    **Key Themes from Website:** [Major themes extracted from content]
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )

        raw_response = response.choices[0].message.content.strip()
        print("🔍 Raw OpenAI Response:\n", raw_response)  # ✅ Debugging

        return raw_response  # ✅ Return raw response for structured extraction

    except Exception as e:
        print(f"❌ OpenAI API request failed: {e}")
        return """**Industry & Niche:** Unknown
**Main Products/Services:** Unknown
**Target Audience:** Unknown
**Audience Segments:** Unknown
**Top 3 Competitors:** Unknown
**Key Themes from Website:** Unknown"""

def get_relevant_subreddits(industry_summary):
    """Fetches the most relevant subreddits based on business profile."""
    
    prompt = f"""
    Given the following business profile:

    {industry_summary}

    Identify the **3 most relevant subreddits** where the target audience actively discusses related topics.
    
    **Return the exact format below (one subreddit per line, no numbering or explanations):**
    r/[Subreddit1]
    r/[Subreddit2]
    r/[Subreddit3]
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50
        )

        raw_response = response.choices[0].message.content.strip()
        print("🔍 Raw OpenAI Subreddit Response:\n", raw_response)  # ✅ Debugging

        subreddits = [s.strip() for s in raw_response.split("\n") if s.startswith("r/")]
        
        print("✅ Extracted Subreddits:", subreddits)  # ✅ Confirm correct subreddit extraction
        return subreddits

    except Exception as e:
        print(f"❌ OpenAI API request failed: {e}")
        return []
