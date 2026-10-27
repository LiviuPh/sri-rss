
import requests
from bs4 import BeautifulSoup
from email.utils import format_datetime
from datetime import datetime, timezone
from urllib.parse import urljoin
from xml.etree.ElementTree import Element, SubElement, ElementTree

BASE_URL = "https://intelligence.sri.ro/"
response = requests.get(
    BASE_URL,
    headers={"User-Agent": "Mozilla/5.0"},
    timeout=30
)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
rss = Element("rss", version="2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Intelligence SRI"
SubElement(channel, "link").text = BASE_URL
SubElement(channel, "description").text = "Articole publicate pe Intelligence SRI"
SubElement(channel, "lastBuildDate").text = format_datetime(
    datetime.now(timezone.utc)
)

seen = set()
count = 0

for article in soup.select("article"):
    heading = article.find(["h1", "h2", "h3"])
    link = article.find("a", href=True)

    if not heading or not link:
        continue

    title = heading.get_text(" ", strip=True)
    url = urljoin(BASE_URL, link["href"])

    if not title or url in seen:
        continue

    seen.add(url)
    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = url
    SubElement(item, "guid").text = url

    date = article.find("time")
    if date and date.get("datetime"):
        SubElement(item, "pubDate").text = date["datetime"]

    count += 1
    if count >= 30:
        break

if count == 0:
    raise RuntimeError("Nu au fost identificate articole. Structura paginii trebuie verificată.")

ElementTree(rss).write("feed.xml", encoding="utf-8", xml_declaration=True)
print(f"Flux RSS generat: {count} articole")
