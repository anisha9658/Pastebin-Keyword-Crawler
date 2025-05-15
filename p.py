import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time


ARCHIVE_URL = "https://pastebin.com/archive"
RAW_URL_TEMPLATE = "https://pastebin.com/raw/{}"
KEYWORDS = ["crypto", "bitcoin", "ethereum", "blockchain", "t.me"]
OUTPUT_FILE = "keyword_matches.jsonl"


def get_latest_paste_ids():
    response = requests.get(ARCHIVE_URL)
    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.select("table.maintable a")
    paste_ids = [link['href'].strip("/") for link in links if link['href'].startswith("/")]
    return paste_ids[:30]  


def fetch_paste_content(paste_id):
    raw_url = RAW_URL_TEMPLATE.format(paste_id)
    try:
        response = requests.get(raw_url, timeout=5)
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error fetching {paste_id}: {e}")
    return None


def find_keywords(text):
    found = [kw for kw in KEYWORDS if kw.lower() in text.lower()]
    return found

def save_result(data):
    with open(OUTPUT_FILE, "a", encoding='utf-8') as f:
        json.dump(data, f)
        f.write("\n")


def crawl():
    paste_ids = get_latest_paste_ids()
    print(f"Found {len(paste_ids)} paste IDs.")

    for pid in paste_ids:
        print(f"Checking paste ID: {pid}")
        content = fetch_paste_content(pid)
        if content:
            keywords_found = find_keywords(content)
            if keywords_found:
                result = {
                    "source": "pastebin",
                    "context": f"Found crypto-related content in Pastebin paste ID {pid}",
                    "paste_id": pid,
                    "url": RAW_URL_TEMPLATE.format(pid),
                    "discovered_at": datetime.utcnow().isoformat() + "Z",
                    "keywords_found": keywords_found,
                    "status": "pending"
                }
                save_result(result)
                print(f"-> Match found: {keywords_found}")
            else:
                print("-> No keywords found.")
        time.sleep(1)  


if __name__ == "__main__":
    crawl()
