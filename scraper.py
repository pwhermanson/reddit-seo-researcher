import requests
from bs4 import BeautifulSoup
import time

def get_navigation_links(target_website):
    """Extracts the main navigation links from the target website homepage."""
    try:
        response = requests.get(target_website, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        nav_links = set()
        for nav in soup.find_all("nav"):
            for link in nav.find_all("a", href=True):
                full_url = requests.compat.urljoin(target_website, link["href"])
                if target_website in full_url and full_url not in nav_links:
                    nav_links.add(full_url)

        return list(nav_links)
    except requests.RequestException as e:
        print(f"❌ Failed to fetch navigation links: {e}")
        return []

def extract_text_from_url(url):
    """Fetches and extracts main text content from a webpage."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        for script in soup(["script", "style"]):
            script.extract()

        text = " ".join(soup.stripped_strings)
        return text[:5000]
    except requests.RequestException as e:
        print(f"❌ Failed to extract text from {url}: {e}")
        return ""

def scrape_target_website(target_website):
    """Scrapes the target website's homepage and navigation pages."""
    print(f"🔍 Crawling {target_website} to extract key information...")

    nav_links = get_navigation_links(target_website)
    if not nav_links:
        print("⚠️ No navigation links found. Analyzing homepage only.")
        nav_links = [target_website]

    scraped_text = ""
    for link in nav_links[:5]:  
        print(f"📄 Scraping: {link}")
        text = extract_text_from_url(link)
        if text:
            scraped_text += text + "\n\n"
        time.sleep(2)

    return scraped_text
