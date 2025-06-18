from fastapi import FastAPI
from pydantic import BaseModel
import base64
import faiss
import numpy as np
import json
import io
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer
import os
import requests
from mangum import Mangum

app = FastAPI()
model = None
index = None
chunks = []

def download_if_missing(url, filename):
    if not os.path.exists(filename):
        print(f"Downloading {filename} from {url} ...")
        r = requests.get(url)
        r.raise_for_status()
        with open(filename, "wb") as f:
            f.write(r.content)
        print(f"Saved {filename}.")

# Replace these URLs with your actual Hugging Face or S3 URLs
VECTOR_INDEX_URL = "https://huggingface.co/datasets/Kriti0613/vector.index/resolve/main/vector.index"
CHUNKS_JSON_URL = "https://huggingface.co/datasets/Kriti0613/vector.index/raw/main/chunks.json"

download_if_missing(VECTOR_INDEX_URL, "vector.index")
download_if_missing(CHUNKS_JSON_URL, "chunks.json")

index = faiss.read_index("vector.index")

with open("chunks.json") as f:
    chunks = json.load(f)

class Query(BaseModel):
    question: str
    image: str | None = None

@app.post("/api/")
def query_virtual_ta(q: Query):
    question = q.question

    # OCR if image is provided
    if q.image:
        try:
            image_data = base64.b64decode(q.image)
            image = Image.open(io.BytesIO(image_data))
            extracted_text = pytesseract.image_to_string(image)
            question += " " + extracted_text
        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}

    # Embed query
    q_embed = model.encode([question])
    D, I = index.search(np.array(q_embed).astype("float32"), 5)

    results = [chunks[i] for i in I[0] if i < len(chunks)]
    top_answer = results[0]["content"] if results else "No relevant answer found."

    return {
    "answer": top_answer,
    "links": [
        {
            "url": r["url"],
            "text": r.get("title", r.get("url"))[:100]
        } for r in results[:3] if r["source"] == "discourse"
    ]
}
@app.get("/api/")
def read_root():
    print("✅ /api/ GET endpoint hit!")
    return {"message": "TDS Virtual TA is live!"}

handler = Mangum(app)