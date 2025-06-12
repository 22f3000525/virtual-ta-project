import os
import json
from datetime import datetime
from markdownify import markdownify as md
from urllib.parse import urljoin
from playwright.sync_api import sync_playwright

BASE_URL = "https://tds.s-anand.net/#/2025-01/"
BASE_ORIGIN = "https://tds.s-anand.net"
OUTPUT_DIR = "data/raw/html_markdown"
METADATA_FILE = "data/raw/html_metadata.json"

visited = set()
metadata = []

def sanitize_filename(title):
    return "".join(c if c.isalnum() else "_" for c in title)[:50]

def crawl_page(page, url):
    if url in visited:
        return
    visited.add(url)

    print(f"🔍 Visiting: {url}")
    try:
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector("article.markdown-section#main", timeout=10000)
        html = page.inner_html("article.markdown-section#main")
    except Exception as e:
        print(f"⚠️ Error loading {url}: {e}")
        return

    # Save to markdown file
    title = page.title().split(" - ")[0].strip() or f"page_{len(visited)}"
    filename = sanitize_filename(title)
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.md")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(md(html))

    metadata.append({
        "title": title,
        "filename": f"{filename}.md",
        "url": url,
        "timestamp": datetime.now().isoformat()
    })

    # Find internal links
    links = page.eval_on_selector_all("a[href]", "els => els.map(el => el.href)")
    for link in set(links):
        if BASE_ORIGIN in link and '/#/' in link:
            crawl_page(page, link)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print(f"🔍 Opening: {BASE_URL}")
        page.goto(BASE_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)  # wait 5 seconds for all links to appear

        crawl_page(page, BASE_URL)

        browser.close()

        # Save metadata
        os.makedirs(os.path.dirname(METADATA_FILE), exist_ok=True)
        with open(METADATA_FILE, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print(f"\n✅ Done. Crawled {len(metadata)} pages and saved metadata.")

if __name__ == "__main__":
    main()
