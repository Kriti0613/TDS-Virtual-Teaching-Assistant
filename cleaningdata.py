import os
import json
from pathlib import Path
from bs4 import BeautifulSoup

COURSE_DIR = "tds_pages_md"
DISCOURSE_DIR = "data"
OUTPUT_FILE = "processed_chunks.jsonl"
METADATA_FILE = "metadata.json"

def clean_markdown(md_text):
    return md_text.replace("\n", " ").replace("#", "").strip()

def split_text(text, max_words=200):
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i+max_words])

def load_metadata():
    with open(METADATA_FILE, "r") as f:
        return json.load(f)

def process_course_content(metadata):
    print("Checking course content...")
    for entry in metadata:
        file_path = os.path.join(COURSE_DIR, entry["filename"])
        if not os.path.exists(file_path):
            print(f"Missing file: {file_path}")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read().strip()
            if not raw:
                print(f"Empty file: {file_path}")
                continue

            text = clean_markdown(raw)
            chunks = list(split_text(text))
            if not chunks:
                print(f"No chunks produced: {file_path}")
                continue

            print(f"Processed: {entry['title']} — {len(chunks)} chunks")

            for chunk in chunks:
                yield {
                    "content": chunk,
                    "source": "course",
                    "title": entry["title"],
                    "url": entry["original_url"],
                    "type": "text"
                }


DISCOURSE_DIR = "data" 

def process_discourse_content():
    for filename in os.listdir(DISCOURSE_DIR):
        if not filename.endswith(".json") or filename == "discourse.json":
            continue

        filepath = os.path.join(DISCOURSE_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        posts = data.get("posts") or data.get("post_stream", {}).get("posts", [])
        print(f"{filename}: {len(posts)} posts")
        if not posts:
            continue

        for post in posts:
            text = post.get("content", "").strip()
            if not text:
                print(f"Empty content in {filename}, post {post.get('post_id')}")
                continue

            for chunk in split_text(text):
                print(f"Yielding chunk from {filename}, post {post.get('post_id')}: {chunk[:40]}...")
                yield {
                    "content": chunk,
                    "source": "discourse",
                    "title": data.get("title", filename),
                    "url": f"https://discourse.onlinedegree.iitm.ac.in/t/{data.get('slug', 'unknown')}/{data.get('id')}",
                    "type": "text"
                }
                
def save_chunks():
    os.makedirs("data", exist_ok=True)
    count = 0

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        metadata = load_metadata()
        print(f"Loaded metadata: {len(metadata)} items")
        for entry in process_course_content(metadata):
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")
            count += 1

        discourse_count = 0
        for entry in process_discourse_content():
            out.write(json.dumps(entry, ensure_ascii=False) + "\n")
            count += 1
            discourse_count += 1

    print(f"Saved {count} total chunks ({count - discourse_count} from course, {discourse_count} from discourse)")


if __name__ == "__main__":
    save_chunks()
