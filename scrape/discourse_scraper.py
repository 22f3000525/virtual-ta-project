import requests
import json

BASE_URL = "https://discourse.onlinedegree.iitm.ac.in"
CATEGORY_ID = 34  # TDS forum
PAGE_URL = f"{BASE_URL}/c/courses/tds-kb/{CATEGORY_ID}.json"

def get_discourse_posts():
    print("Getting posts...")
    response = requests.get(PAGE_URL)
    
    if response.status_code != 200:
        print("Failed to fetch data!")
        return
    
    data = response.json()
    topics = data["topic_list"]["topics"]

    all_posts = []
    for topic in topics:
        post = {
            "id": topic["id"],
            "title": topic["title"],
            "slug": topic["slug"],
            "created_at": topic["created_at"]
        }
        all_posts.append(post)

    with open("discourse_posts.json", "w") as f:
        json.dump(all_posts, f, indent=2)

    print(f"✅ Saved {len(all_posts)} posts to discourse_posts.json")

# Run the scraper
get_discourse_posts()
