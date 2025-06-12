from sentence_transformers import SentenceTransformer
import json
import os

model = SentenceTransformer('all-MiniLM-L6-v2')  # Free transformer model

def generate_embeddings(input_path, output_path):
    with open(input_path, "r", encoding="utf-8") as f:
        texts = f.read().split('\n\n')  # Customize this based on how your text is chunked

    embeddings = model.encode(texts, show_progress_bar=True)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "texts": texts,
            "embeddings": embeddings.tolist()
        }, f, indent=2)

    print(f"✅ Saved {len(embeddings)} embeddings to {output_path}")

if __name__ == "__main__":
    base_dir = os.path.dirname(__file__)  # Path to the folder where embed_data.py exists
    discourse_input = os.path.join(base_dir, "../data/processed/cleaned_discourse.txt")
    course_input = os.path.join(base_dir, "../data/processed/cleaned_course_content.txt")

    discourse_output = os.path.join(base_dir, "../data/embeddings/discourse_embeddings.json")
    course_output = os.path.join(base_dir, "../data/embeddings/course_embeddings.json")


    generate_embeddings(discourse_input, discourse_output)
    generate_embeddings(course_input, course_output)
