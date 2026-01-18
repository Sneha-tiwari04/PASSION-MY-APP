import feedparser
import json

def scrape_jobs():
    all_jobs = []
    print("📡 Scraping Google News for Jobs...")

    # Google News se Sarkari Jobs ka RSS (Ye 100% chalta hai)
    rss_url = "https://news.google.com/rss/search?q=sarkari+result+jobs+india&hl=en-IN&gl=IN&ceid=IN:en"
    
    try:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:15]:
            all_jobs.append({
                "title": entry.title,
                "link": entry.link,
                "source": "Google News (Sarkari)"
            })
        print(f"✅ Found {len(all_jobs)} jobs!")
    except Exception as e:
        print(f"❌ Error: {e}")

    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(all_jobs, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    scrape_jobs()