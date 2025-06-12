from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import json
import os
import base64
from io import BytesIO
from PIL import Image

app = FastAPI()

# Add CORS middleware to allow requests from different origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load model and FAISS indexes once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")

base_dir = os.path.dirname(__file__)

with open(os.path.join(base_dir, "data/embeddings/course_embeddings.json"), "r", encoding="utf-8") as f:
    course_data = json.load(f)
course_index = faiss.read_index(os.path.join(base_dir, "data/indexes/course_index.faiss"))

with open(os.path.join(base_dir, "data/embeddings/discourse_embeddings.json"), "r", encoding="utf-8") as f:
    discourse_data = json.load(f)
discourse_index = faiss.read_index(os.path.join(base_dir, "data/indexes/discourse_index.faiss"))

DEFAULT_RESPONSE = {
    "answer": "Sorry, I couldn't understand the question format or the question is missing.",
    "links": []
}

@app.post("/api/")
async def answer_question(request: Request):
    try:
        # Fix: Parse JSON from string (Promptfoo sends string even with application/json)
        try:
            raw_body = await request.body()
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            return JSONResponse(content={
                "answer": "Invalid request format. Please send JSON with a 'question' field.",
                "links": []
            }, status_code=400)

        question = data.get("question", "").strip()
        image_base64 = data.get("image", None)

        if not question:
            return JSONResponse(content=DEFAULT_RESPONSE)

        # Optional: Decode image if provided
        if image_base64:
            try:
                if image_base64.startswith("file://"):
                    with open(image_base64.replace("file://", ""), "rb") as f:
                        image_data = f.read()
                else:
                    image_data = base64.b64decode(image_base64.split(",")[-1])

                image = Image.open(BytesIO(image_data))
                # Image can be processed here if needed
            except Exception as img_error:
                return JSONResponse(content={
                    "answer": "Invalid image format or failed to decode image.",
                    "links": []
                }, status_code=400)

        # Encode and search
        query_embedding = model.encode([question])[0].astype("float32")

        _, course_ids = course_index.search(np.array([query_embedding]), k=1)
        _, discourse_ids = discourse_index.search(np.array([query_embedding]), k=1)

        responses = []
        links = []

        if course_ids[0][0] >= 0:
            course_answer = course_data["texts"][course_ids[0][0]]
            responses.append(f"Course reference: {course_answer}")
            if "urls" in course_data and course_ids[0][0] < len(course_data["urls"]):
                links.append({"url": course_data["urls"][course_ids[0][0]], "text": "Course reference"})

        if discourse_ids[0][0] >= 0:
            discourse_answer = discourse_data["texts"][discourse_ids[0][0]]
            responses.append(f"Forum discussion: {discourse_answer}")
            if "urls" in discourse_data and discourse_ids[0][0] < len(discourse_data["urls"]):
                links.append({"url": discourse_data["urls"][discourse_ids[0][0]], "text": "Forum discussion"})

        if not responses:
            return JSONResponse(content={
                "answer": "I couldn't find a specific answer to your question in our materials.",
                "links": []
            })

        return JSONResponse(content={
            "answer": "\n\n".join(responses),
            "links": links
        })

    except json.JSONDecodeError:
        return JSONResponse(content={
            "answer": "Invalid request format. Please send JSON with a 'question' field.",
            "links": []
        }, status_code=400)

    except Exception as e:
        return JSONResponse(content={
            "answer": f"An error occurred while processing your request: {str(e)}",
            "links": []
        }, status_code=500)

@app.get("/")
def read_root():
    return {"message": "Hello! This is your Virtual TA."}