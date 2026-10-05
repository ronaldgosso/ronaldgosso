import os, re, html, urllib.request
import xml.etree.ElementTree as ET

USER_ID = os.environ.get("GOODREADS_USER_ID", "204814205")
SHELF   = os.environ.get("GOODREADS_SHELF", "read")
NUM     = int(os.environ.get("GOODREADS_NUM_BOOKS", "3"))
KEY     = os.environ.get("GOODREADS_KEY", "")   # optional, see note below
TITLE   = os.environ.get("GOODREADS_TITLE", "Ronald's bookshelf")
README  = os.environ.get("README_PATH", "README.md")

url = (f"https://www.goodreads.com/review/list_rss/{USER_ID}"
       f"?shelf={SHELF}&sort=date_added&order=d&per_page={NUM}")
if KEY:
    url += f"&key={KEY}"

req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
root = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())

e = html.escape
shelf_url = f"https://www.goodreads.com/review/list/{USER_ID}?shelf={SHELF}"

rows = []
for item in root.iter("item"):
    if len(rows) >= NUM:
        break
    title  = (item.findtext("title") or "").strip()
    author = (item.findtext("author_name") or "").strip()
    cover  = (item.findtext("book_image_url") or "").strip()
    link   = (item.findtext("link") or shelf_url).strip()
    rows.append(f"""  <tr>
    <td width="70" align="center"><a href="{e(link)}"><img src="{e(cover)}" width="50" alt="{e(title)}"></a></td>
    <td><a href="{e(link)}"><b>{e(title)}</b></a><br><sub>by {e(author)}</sub></td>
  </tr>""")

block = f"""<table>
  <tr><th colspan="2" align="center"><a href="{e(shelf_url)}">{e(TITLE)}</a></th></tr>
{chr(10).join(rows)}
  <tr><td colspan="2" align="center"><sub>via <a href="https://www.goodreads.com/">Goodreads</a></sub></td></tr>
</table>"""

text = open(README, encoding="utf-8").read()
new = re.sub(r"(<!-- GOODREADS:START -->).*?(<!-- GOODREADS:END -->)",
             lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}",
             text, flags=re.S)

if new != text:
    open(README, "w", encoding="utf-8").write(new)
    print("README updated")
else:
    print("No changes")
