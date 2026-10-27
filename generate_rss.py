
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

for heading in soup.find_all(["h1", "h2", "h3"]):
    link = heading.find("a", href=True)

    if not link:
        link = heading.find_parent("a", href=True)

    if not link:
        continue

    title = heading.get_text(" ", strip=True)
    url = urljoin(BASE_URL, link["href"]).split("#")[0]

    if not title or "intelligence.sri.ro" not in url:
        continue

    if url.rstrip("/") == BASE_URL.rstrip("/") or url in seen:
        continue

    seen.add(url)

    item = SubElement(channel, "item")
    SubElement(item, "title").text = title
    SubElement(item, "link").text = url
    SubElement(item, "guid").text = url

    count += 1
    if count >= 50:
        break

if count == 0:
    raise RuntimeError("Nu au fost identificate articole.")

ElementTree(rss).write(
    "feed.xml",
    encoding="utf-8",
    xml_declaration=True
)

print(f"Flux RSS generat: {count} articole")
