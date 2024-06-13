import os
import feedparser
import openai
import requests
from requests.auth import HTTPBasicAuth
from itertools import cycle

# OpenAI API-Schlüssel setzen
api_key = 'your-key'
client = openai.OpenAI(api_key=api_key)

# WordPress-Zugangsdaten
WORDPRESS_URL = 'https://domain.tld
WORDPRESS_USER = 'user'
WORDPRESS_PASSWORD = 'password'

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

def generate_tags(title, summary):
    prompt = (
        f"Hier ist ein Artikel:\n\n"
        f"Titel: {title}\n\n"
        f"{summary}\n\n"
        f"Erstelle eine Liste von Schlagwörtern (Tags), die relevant für diesen Artikel sind:\n\n"
    )
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Du bist ein hilfsbereiter Assistent."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=100
    )
    tags_text = response.choices[0].message.content.strip()
    tags = [tag.strip() for tag in tags_text.split(',')]
   
