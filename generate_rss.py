import feedgenerator
import requests
from datetime import datetime
from pathlib import Path

LINKS_FILE = "links.txt"
OUTPUT_DIR = Path("feeds")
OUTPUT_DIR.mkdir(exist_ok=True)

YOUTUBE_OEMBED = "https://www.youtube.com/oembed?format=json&url="

def is_youtube(url):
    return "youtube.com" in url or "youtu.be" in url

def get_youtube_meta(url):
    r = requests.get(YOUTUBE_OEMBED + url, timeout=10)
    r.raise_for_status()
    return r.json()

feeds = {}
current_category = None

for line in Path(LINKS_FILE).read_text().splitlines():
    line = line.strip()

    if not line or line.startswith("#"):
        continue

    if line.endswith(":"):
        current_category = line[:-1].strip().lower()
        feeds[current_category] = []
        continue

    if current_category is None:
        continue  # ignore links before first category

    feeds[current_category].append(line)

for category, links in feeds.items():
    feed = feedgenerator.Rss201rev2Feed(
        title=f"My {category.capitalize()} Archive",
        link="https://github.com/YOUR_USERNAME/YOUR_REPO",
        description=f"Personal archive for {category}",
        language="en",
        lastBuildDate=datetime.utcnow(),
    )

    for url in links:
        title = url
        description = ""

        try:
            if is_youtube(url):
                meta = get_youtube_meta(url)
                title = meta["title"]
                description = f"By {meta['author_name']}"
        except Exception:
            description = "Metadata unavailable"

        feed.add_item(
            title=title,
            link=url,
            description=description,
            unique_id=url,
            pubdate=datetime.utcnow(),
        )

    out_file = OUTPUT_DIR / f"{category}.xml"
    with out_file.open("w", encoding="utf-8") as f:
        feed.write(f, "utf-8")

    print(f"Generated {out_file}")
