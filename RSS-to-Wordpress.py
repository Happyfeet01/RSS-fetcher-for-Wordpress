import os
import feedparser
import openai
import requests
from requests.auth import HTTPBasicAuth
from itertools import cycle

# OpenAI API-Schlüssel setzen
api_key = 'sekret-api-key'
client = openai.OpenAI(api_key=api_key)

# WordPress-Zugangsdaten
WORDPRESS_URL = 'https://your-wordpress.blog'
WORDPRESS_USER = 'user'
WORDPRESS_PASSWORD = 'passwort'

# ID der Kategorie "News" in WordPress
NEWS_CATEGORY_ID = 1  # Ersetze dies mit der tatsächlichen Kategorie-ID

def parse_rss_feed(url):
    feed = feedparser.parse(url)
    articles = []
    for entry in feed.entries:
        article = {
            'title': entry.title,
            'link': entry.link,
            'published': entry.published,
            'summary': entry.summary
        }
        articles.append(article)
    return articles

def summarize_article(title, summary):
    prompt = (
        f"Hier ist ein ausführlicher Artikel:\n\n"
        f"Titel: {title}\n\n"
        f"{summary}\n\n"
        f"Schreibe eine lange und detaillierte Zusammenfassung dieses Artikels auf Deutsch, "
        f"einschließlich der wichtigsten Punkte und aller relevanten Details:\n\n"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist ein hilfsbereiter Assistent."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800  # Weiter erhöhte Anzahl der maximalen Tokens
    )
    return response.choices[0].message.content.strip()

def post_to_wordpress(title, summary, link):
    post = {
        'title': title,
        'content': f"{summary}<br><br><a href='{link}'>Weiterlesen</a>",
        'status': 'draft',  # Status auf 'draft' ändern
        'categories': [NEWS_CATEGORY_ID]  # Kategorie "News" hinzufügen
    }
    response = requests.post(
        f"{WORDPRESS_URL}/wp-json/wp/v2/posts",
        json=post,
        auth=HTTPBasicAuth(WORDPRESS_USER, WORDPRESS_PASSWORD)
    )
    if response.status_code == 201:
        print(f"Entwurf erfolgreich gespeichert: {title}")
    else:
        print(f"Fehler beim Speichern des Entwurfs: {response.content}")

# Liste von RSS-Feed-URLs
rss_urls = [
    "https://www.heise.de/rss/heise-atom.xml",
    "https://rss.golem.de/rss.php?r=sw&feed=RSS2.0",
    "https://www.computerbase.de/rss/news.xml",
    "https://t3n.de/rss.xml",
    "https://winfuture.de/rss/news.rss"
]

# Abrufen und Verarbeiten der RSS-Feeds
articles = []
for rss_url in rss_urls:
    articles.extend(parse_rss_feed(rss_url))

# Mischen der Artikel und Auswählen der ersten zwei
articles = sorted(articles, key=lambda x: x['published'])
posted_articles = 0
for article in cycle(articles):
    if posted_articles >= 2:
        break
    summarized = summarize_article(article['title'], article['summary'])
    post_to_wordpress(article['title'], summarized, article['link'])
    posted_articles += 1
