import os
from datetime import datetime

INPUT_DIR = "data/raw/html_markdown"
OUTPUT_FILE = "data/processed/cleaned_course_content.txt"

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
    return chunks

def process_markdown_files():
    print("🔍 Reading markdown files...")
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

    all_chunks = []
    for filename in os.listdir(INPUT_DIR):
        if filename.endswith(".md"):
            filepath = os.path.join(INPUT_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            chunks = chunk_text(content)
            for chunk in chunks:
                all_chunks.append(chunk.strip())

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        for chunk in all_chunks:
            out.write(chunk + "\n\n---\n\n")

    print(f"✅ Done. Saved {len(all_chunks)} chunks to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_markdown_files()
