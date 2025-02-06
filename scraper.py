# ===============================================
# 📌 How It Works - Website Scraper
# ===============================================
# This module extracts text from the target website, including:
# ✅ Homepage content
# ✅ Main navigation pages (up to 10 per menu section)
#
# 🚀 Key Functions:
# 1️⃣ get_navigation_links(target_website)  
#    → Extracts main menu links from <nav>, <header>, and other common selectors.
# 2️⃣ extract_text_from_url(url)  
#    → Fetches and cleans visible text from a given webpage.
# 3️⃣ scrape_target_website(target_website, max_pages=10)  
#    → Scrapes the homepage and main pages for content, limiting total pages.
#
# 🛠️ Optimizations:
# ✅ Ensures only internal links from the main domain are considered.
# ✅ Uses time.sleep(2) between requests to prevent aggressive crawling.
# ✅ Extracts only meaningful text (paragraphs) to avoid noise.
# ✅ Handles errors gracefully—continues scraping even if a page fails.
# ===============================================


import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

def get_navigation_links(target_website, max_links_per_menu=10):
    """Extracts main navigation links from the target website."""
    try:
        print(f"🔍 Crawling {target_website} to extract key navigation links...")
        response = requests.get(target_website, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ Find all navigation elements (common classes used for nav menus)
        possible_nav_selectors = ["nav", "header", ".menu", ".navigation", ".nav"]
        nav_links = set()

        for selector in possible_nav_selectors:
            for nav in soup.select(selector):
                for link in nav.find_all("a", href=True):
                    full_url = urljoin(target_website, link["href"])
                    if target_website in full_url:  # ✅ Keep only internal links
                        nav_links.add(full_url)

        # ✅ Limit the number of links per menu section
        nav_links = list(nav_links)[:max_links_per_menu]

        if not nav_links:
            print("⚠️ No navigation links found. Analyzing homepage only.")
            return []

        print(f"✅ Extracted {len(nav_links)} navigation links.")
        return nav_links

    except requests.RequestException as e:
        print(f"❌ Failed to fetch navigation links: {e}")
        return []

def extract_text_from_url(url):
    """Extracts text content from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # ✅ Extract visible text from <p> elements
        text_content = ' '.join([p.get_text(strip=True) for p in soup.find_all("p")])
        return text_content

    except requests.RequestException as e:
        print(f"❌ Failed to extract text from {url}: {e}")
        return ""

def scrape_target_website(target_website, max_pages=10):
    """Scrapes the homepage and main navigation pages for content."""
    print(f"🔍 Crawling {target_website} to extract key information...")

    # ✅ Get main navigation links
    nav_links = get_navigation_links(target_website, max_links_per_menu=max_pages)

    # ✅ Always include the homepage in the scrape
    pages_to_scrape = [target_website] + nav_links

    scraped_text = ""
    for idx, page_url in enumerate(pages_to_scrape):
        if idx >= max_pages:  # ✅ Limit the number of pages scraped
            break

        print(f"📄 Scraping: {page_url}")
        text = extract_text_from_url(page_url)
        if text:
            scraped_text += f"📄 {page_url}\n{text}\n\n"

        time.sleep(2)  # ✅ Prevent aggressive crawling

    return scraped_text
