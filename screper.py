import feedparser
import json
import requests
from bs4 import BeautifulSoup
import os

def scrape_jobs():
    all_jobs = []
    print("📡 Scraping started on GitHub Server...")

    # 1. SarkariResult RSS (Sabse stable)
    try:
        feed = feedparser.parse("https://sarkariresult.com.cm/")
        for entry in feed.entries[:15]:
            all_jobs.append({
                "title": entry.title,
                "link": entry.link,
                "source": "SarkariResult"
            })
        print("✅ SarkariResult data fetched.")
    except Exception as e:
        print(f"❌ SR Error: {e}")

    # 2. Internshala (Mobile User Agent bypass)
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'}
        r = requests.get("https://internshala.com/jobs/fresher-jobs/", headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        cards = soup.find_all('div', class_='individual_holding')
        for card in cards[:10]:
            title = card.find('h3').text.strip()
            link = "https://internshala.com" + card.find('a')['href']
            all_jobs.append({"title": title, "link": link, "source": "Internshala"})
        print("✅ Internshala data fetched.")
    except Exception as e:
        print(f"❌ Internshala Error: {e}")

    # Save to data.json
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, indent=4, ensure_ascii=False)
    print(f"🚀 Total {len(all_jobs)} jobs saved to data.json")

if __name__ == "__main__":
    scrape_jobs()