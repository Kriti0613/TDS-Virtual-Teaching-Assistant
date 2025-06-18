from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import base64
import faiss
import numpy as np
import json
import io
from PIL import Image
import pytesseract
from sentence_transformers import SentenceTransformer

app = FastAPI()

# Load model, index, and data
model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("vector.index")
with open("chunks.json") as f:
    chunks = json.load(f)

class Query(BaseModel):
    question: str
    image: str | None = None

@app.post("/api/")
def query_virtual_ta(q: Query):
    question = q.question

    if q.image:
        try:
            image_data = base64.b64decode(q.image)
            image = Image.open(io.BytesIO(image_data))
            extracted_text = pytesseract.image_to_string(image)
            question += " " + extracted_text
        except Exception as e:
            return {"error": f"Failed to process image: {str(e)}"}

    q_embed = model.encode([question])
    D, I = index.search(np.array(q_embed).astype("float32"), 5)

    results = [chunks[i] for i in I[0] if i < len(chunks)]
    top_answer = results[0]["content"] if results else "No relevant answer found."

    return {
        "answer": top_answer,
        "references": [{"source": r["source"], "title": r.get("title", "")[:100]} for r in results[:3]]
    }

@app.get("/api/")
def read_root():
    return JSONResponse(content={"message": "TDS Virtual TA is live!"})
