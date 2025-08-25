import xml.etree.ElementTree as ET
from pprint import pprint

xml_data = """<album title="Abbey Road" artist="The Beatles">
  <track number="1" duration="4:20">
    <title>Come Together</title>
    <genre>Rock</genre>
  </track>
  <track number="2" duration="3:29">
    <title>Something</title>
    <genre>Rock</genre>
  </track>
  <track number="7" duration="3:05" rating="5_stars">
    <title>Here Comes the Sun</title>
    <genre>Folk Rock</genre>
  </track>
</album>"""

root = ET.fromstring(xml_data)

album = {
    "title": root.attrib.get("title"),
    "artist": root.attrib.get("artist"),
    "tracks": []
}

for tr in root.findall("track"):
    track = dict(tr.attrib)  # number, duration, (optional) rating
    track["title"] = tr.findtext("title", default="").strip()
    track["genre"] = tr.findtext("genre", default="").strip()
    album["tracks"].append(track)

pprint(album)
