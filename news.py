# Handles external API requests and data normalization.
import requests
from datetime import datetime, timezone

NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"

# Mapping of local topic identifiers to NewsAPI categories.
TOPIC_CATEGORY = {
    "tech": "technology",
    "business": "business",
    "sports": "sports",
}

def fetch_topic(topic: str, api_key: str, page: int = 1, page_size: int = 50) -> list[dict]:
    """Fetches top headlines for a given topic and standardizes fields."""
    category = TOPIC_CATEGORY.get(topic, "technology")
    params = {
        "category": category,
        "page": page,
        "pageSize": page_size,
        "language": "en",
        "country": "us",
        "apiKey": api_key,
    }
    resp = requests.get(NEWSAPI_URL, params=params, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    items = []
    for it in (data.get("articles") or []):
        title = (it.get("title") or "").strip()
        url = (it.get("url") or "").strip()
        src = (it.get("source") or {}).get("name") or ""
        image = it.get("urlToImage")
        published = it.get("publishedAt") or ""
        items.append({
            "topic": topic,
            "title": title,
            "source": src,
            "url": url,
            "image_url": image,
            "published_at": published,
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        })
    return items
