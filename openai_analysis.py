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
    """Fetches the most relevant subreddits based on the business profile and validates them."""
    
    # ✅ Step 1: Ask OpenAI for an initial list of subreddits
    generate_prompt = f"""
    Given the following business profile:

    {industry_summary}

    Identify the 5 most relevant subreddits where the target audience actively discusses related topics.
    Only return subreddit names in list format (e.g., r/Dentistry, r/DentalCare, etc.).
    """

    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": generate_prompt}],
            max_tokens=100
        )

        # ✅ Extract subreddit list
        subreddits = response.choices[0].message.content.strip().split("\n")
        subreddits = [s.strip().replace("r/", "").strip() for s in subreddits if s]

    except Exception as e:
        print(f"❌ OpenAI API request failed (Generating Subreddits): {e}")
        return []

    # ✅ Step 2: Validate the Subreddits with OpenAI
    validate_prompt = f"""
    Given the target business profile:

    {industry_summary}

    And the following subreddit recommendations:

    {", ".join([f"r/{s}" for s in subreddits])}

    Check if each subreddit is highly relevant to the business profile. 
    Remove any subreddit that is not **directly related** to the business or target audience.

    Then, for each subreddit that remains, provide a **brief explanation** (2 sentences max) of why it is relevant.

    Format the output like this:
    r/SubredditName - Explanation
    """

    try:
        validation_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": validate_prompt}],
            max_tokens=250
        )

        # ✅ Extract validated subreddit responses
        validated_subreddits = validation_response.choices[0].message.content.strip().split("\n")
        validated_subreddits = [s.strip() for s in validated_subreddits if " - " in s]

        # ✅ Separate subreddit names and explanations
        final_subreddits = []
        subreddit_explanations = {}

        for entry in validated_subreddits:
            parts = entry.split(" - ", 1)
            if len(parts) == 2:
                subreddit_name = parts[0].replace("r/", "").strip()
                explanation = parts[1].strip()
                final_subreddits.append(subreddit_name)
                subreddit_explanations[subreddit_name] = explanation

        return final_subreddits, subreddit_explanations

    except Exception as e:
        print(f"❌ OpenAI API request failed (Validating Subreddits): {e}")
        return [], {}
