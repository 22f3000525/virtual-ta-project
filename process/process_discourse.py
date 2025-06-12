import json
import os

# Load the data
with open("discourse_posts.json", "r", encoding="utf-8") as f:
    data = json.load(f)

topics = data.get("topic_list", {}).get("topics", [])

cleaned_chunks = []

for topic in topics:
    title = topic.get("title", "")
    created_at = topic.get("created_at", "")
    slug = topic.get("slug", "")
    topic_id = topic.get("id")

    topic_url = f"https://discourse.onlinedegree.iitm.ac.in/t/{slug}/{topic_id}"

    # Just store title, date and a link to the topic for now
    chunk = f"Title: {title}\nDate: {created_at}\nLink: {topic_url}\n"
    cleaned_chunks.append(chunk)

# Save the cleaned data
os.makedirs("data/processed", exist_ok=True)
with open("data/processed/cleaned_discourse.txt", "w", encoding="utf-8") as f:
    for chunk in cleaned_chunks:
        f.write(chunk + "\n---\n")

print(f"✅ Saved {len(cleaned_chunks)} cleaned chunks to data/processed/cleaned_discourse.txt")
