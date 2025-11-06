import requests
from bs4 import BeautifulSoup
import os

def get_download_url(url):
    id = url.split('/')[-2]
    return f'https://www.elararchive.org/download/file/{id}'

def collection_url(page):
    return f'https://www.elararchive.org/?pg={page}&name=SO_a863403a-0a7d-4c07-9252-dac4c6777054&hh_cmis_filter=imdi.mediaFileType/Audio|imdi.writtenFileType/Praat'

# ENTRY_URL = "https://www.elararchive.org/?name=SO_a863403a-0a7d-4c07-9252-dac4c6777054&hh_cmis_filter=imdi.mediaFileType/Audio|imdi.writtenFileType/Praat"
DOWNLOAD_DIR = "../data/v1"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

session = requests.Session()

session.headers.update({
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9,pl;q=0.8",
})

page_number = 7

while True:
    resp = session.get(collection_url(page_number), timeout=30)
    print("HTTP status:", resp.status_code)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    search_results = soup.select_one("div[id^='search-results']")
    if not search_results:
        print('FINISHED DOWNLOADING')
        break

    items = search_results.select("div[id^='post-']")
    print("Items found:", len(items))

    for item in items[:1]:
        link_tag = item.select_one("a")
        if not link_tag:
            continue
        
        item_href = link_tag.get("href")
        print("Found link:", item_href)
        item_resp = session.get(item_href, timeout=30)
        print("HTTP status:", item_resp.status_code)
        item_resp.raise_for_status()

        item_soup = BeautifulSoup(item_resp.text, "html.parser")

        item_search_results = item_soup.select_one("div[id^='search-results']")

        valid_audios = {"wave", "wav", "audio"}
        filtered_audios = [
            f.select_one("a") for f in item_search_results.select("div[id^='post-']")
            if (p := f.select_one("p")) and p.get_text(strip=True).lower() in valid_audios
        ]
        
        for file in filtered_audios[:1]:
            url = get_download_url(file.get("href"))
            file_name = file.get_text(strip=True)
            file_path = os.path.join(DOWNLOAD_DIR, file_name + '.mp3')

            file_resp = session.get(url, timeout=30)
            file_resp.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(file_resp.content)

            print("✅ Saved:", file_path)
        
        valid_tg = {""}
        filtered_tg = [
            f.select_one("a") for f in item_search_results.select("div[id^='post-']")
            if (p := f.select_one("p")) and p.get_text(strip=True).lower() in valid_tg
        ]
        
        for file in filtered_tg[:1]:
            url = get_download_url(file.get("href"))
            file_name = file.get_text(strip=True)
            file_path = os.path.join(DOWNLOAD_DIR, file_name + '.TextGrid')

            file_resp = session.get(url, timeout=30)
            file_resp.raise_for_status()

            with open(file_path, "wb") as f:
                f.write(file_resp.content)

            print("✅ Saved:", file_path)
    
    page_number += 1




# first_link = search_results.select_one("div[id^='post-'] a")
# if first_link:
#     print("Example item text:", first_link.get_text(strip=True)[:100])
#     print("Example item href:", first_link.get("href"))
