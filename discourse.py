# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
#   "playwright",
#   "python-dotenv"
# ]
# ///

import json
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError
from urllib.parse import quote
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import os
import re
load_dotenv()

SAVE_DIR = "data"
os.makedirs(SAVE_DIR, exist_ok=True)

BASE_URL="https://discourse.onlinedegree.iitm.ac.in"
SEARCH_QUERY="#courses:tds-kb before:2025-04-14 after:2025-01-01"
cookie = os.getenv("DISCOURSE_COOKIE")

if not cookie:
    raise RuntimeError("DISCOURSE_COOKIE not set in .env")

cookie = cookie.strip()


SEARCH_URL = f"https://discourse.onlinedegree.iitm.ac.in/search.json?q={quote(SEARCH_QUERY)}"

headers = {
    "Cookie": cookie.strip(),
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest"
}
response = requests.get(SEARCH_URL, headers=headers)

def sanitize_filename(title):
    return re.sub(r'[\\/*?:"<>|]', "", title).strip().replace(" ", "_")[:100]

if response.status_code == 200:
    print("Logged in successfully!")
    data = response.json()
    with open(os.path.join(SAVE_DIR, "discourse.json"), "w") as f:
        json.dump(data, f, indent=4)
    print("JSON data saved to data/discourse.json")
    for topic in data.get("topic_list", {}).get("topics", [])[:5]:
        print(f"{topic['title']}")
else:
    print(f"Login failed or cookie expired. Status: {response.status_code}")
    print(response.text[:300])
    
def fetch_topic_json(topic_id, slug):
    topic_url = f"{BASE_URL}/t/{slug}/{topic_id}.json"
    try:
        resp = requests.get(topic_url, headers=headers)
        if resp.status_code != 200:
            print(f"Failed to fetch topic {topic_id}: {resp.status_code}")
            return None
        return resp.json()
    except Exception as e:
        print(f"Error fetching topic {topic_id}: {e}")
        return None
    
def extract_topic_details(topic_data):
    topic_id = topic_data["id"]
    topic_title = topic_data["title"]
    slug = topic_data["slug"]
    accepted_answer_id = topic_data.get("accepted_answer_post_id")

    posts_info = []
    reply_count_map = {}

    posts = topic_data.get("post_stream", {}).get("posts", [])

    for post in posts:
        reply_to = post.get("reply_to_post_number")
        if reply_to is not None:
            reply_count_map[reply_to] = reply_count_map.get(reply_to, 0) + 1

    for post in posts:
        post_info = {
            "topic_id": topic_id,
            "topic_title": topic_title,
            "post_id": post["id"],
            "post_number": post["post_number"],
            "author": post["username"],
            "created_at": post["created_at"],
            "updated_at": post.get("updated_at"),
            "reply_to_post_number": post.get("reply_to_post_number"),
            "is_reply": post.get("reply_to_post_number") is not None,
            "reply_count": reply_count_map.get(post["post_number"], 0),
            "like_count": post.get("like_count", 0),
            "is_accepted_answer": post["id"] == accepted_answer_id,
            "mentioned_users": [u["username"] for u in post.get("mentioned_users", [])],
            "url": f"{BASE_URL}/t/{slug}/{topic_id}/{post['post_number']}",
            "content": BeautifulSoup(post["cooked"], "html.parser").get_text()
        }
        posts_info.append(post_info)

    return {
        "topic_id": topic_id,
        "title": topic_title,
        "slug": slug,
        "created_at": topic_data["created_at"],
        "tags": topic_data.get("tags", []),
        "posts": posts_info
    }

def already_saved(topic_id): 
    filename = os.path.join(SAVE_DIR, f"{topic_id}.json") 
    return os.path.exists(filename)

def fetch_all_search_results():
    page = 1
    all_topics = []
    seen_ids = set()

    while True:
        print(f"Fetching page {page} of search results...")
        search_url = f"{BASE_URL}/search.json?q={quote(SEARCH_QUERY)}&page={page}"
        resp = requests.get(search_url, headers=headers)

        if resp.status_code != 200:
            print(f"Failed to fetch page {page}: {resp.status_code}")
            break

        data = resp.json()
        topics = data.get("topics", [])

        new_topics = [t for t in topics if t["id"] not in seen_ids]
        if not new_topics:
            print("No new topics found on this page. Done.")
            break

        for t in new_topics:
            seen_ids.add(t["id"])
            all_topics.append(t)

        page += 1

    return all_topics

def main():
    topics = fetch_all_search_results()
    print(f"Total unique topics found: {len(topics)}")

    for topic in topics:
        topic_id = topic["id"]
        title = topic.get("title", "untitled")
        slug = topic.get("slug", "")

        filename = os.path.join(SAVE_DIR, f"{topic_id}.json")

        if already_saved(topic_id):
            print(f"Skipping already saved topic ID: {topic_id}")
            continue
        print(f"Scraping: {title} (Topic ID: {topic_id})")
        
        topic_data = fetch_topic_json(topic_id, slug)
        if not topic_data:
            continue

        extracted_data = extract_topic_details(topic_data)

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(extracted_data, f, indent=2, ensure_ascii=False)

        print(f"Saved to {filename}")

if __name__ == "__main__":
    main()