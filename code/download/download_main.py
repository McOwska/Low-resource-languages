import requests
import os
from bs4 import BeautifulSoup
from urls import download_url, collection_url

FIRST_PAGE = 1
SEARCH_RESULTS_ID = 'search-results'
POST_ID = 'post-'
DOWNLOAD_DIR = "../data/v1"
VALID_AUDIOS = {"wave", "wav", "audio"}
AUDIO_EXTENSION = '.mp3'
VALID_TG = {""}
TG_EXTENSION = '.TextGrid'

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,pl;q=0.8",
})

page_number = FIRST_PAGE

def download_items(session, valid_types, item_search_results, file_extenstion):
    filtered_files = [
        f.select_one("a") for f in item_search_results.select(f"div[id^='{POST_ID}']")
        if (p := f.select_one("p")) and p.get_text(strip=True).lower() in valid_types
    ]
    
    for file in filtered_files[:2]:
        url = download_url(file.get("href"))
        file_name = file.get_text(strip=True)
        file_path = os.path.join(DOWNLOAD_DIR, item_name, file_name + file_extenstion)
        os.makedirs(os.path.join(DOWNLOAD_DIR, item_name), exist_ok=True)

        file_resp = session.get(url, timeout=30)
        file_resp.raise_for_status()

        with open(file_path, "wb") as f:
            f.write(file_resp.content)

        print("✅ Saved:", file_path)

while True:
    resp = session.get(collection_url(page_number), timeout=30)
    print(f'❯❯❯❯❯❯❯❯❯❯❯❯ Page {page_number} HTTP status:', resp.status_code)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    search_results = soup.select_one(f"div[id^='{SEARCH_RESULTS_ID}']")

    if not search_results:
        print('🎉🎉🎉 FINISHED DOWNLOADING 🎉🎉🎉')
        break

    items = search_results.select(f"div[id^='{POST_ID}']")

    for item in items[:2]:
        link_tag = item.select_one("a")
        item_name = item.select_one("h5").get_text(strip=True)
        if not link_tag:
            continue
        
        item_href = link_tag.get("href")
        item_resp = session.get(item_href, timeout=30)
        print(f'{item_name} HTTP status:', item_resp.status_code)
        item_resp.raise_for_status()

        item_soup = BeautifulSoup(item_resp.text, "html.parser")

        item_search_results = item_soup.select_one(f"div[id^='{SEARCH_RESULTS_ID}']")
        if not item_search_results:
            continue

        download_items(session, VALID_AUDIOS, item_search_results, AUDIO_EXTENSION)
        download_items(session, VALID_TG, item_search_results, TG_EXTENSION)
    
    page_number += 1



