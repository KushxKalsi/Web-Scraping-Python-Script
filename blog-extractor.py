import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# ✅ List your blog URLs here
urls = [
    # can also use multiple links
    "https://url1.com/",
    "https://url2.com/", 
]

# ✅ Function to fetch blog details
def fetch_blog(url):
    try:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")

        # Fetch title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"

        # Fetch main content (common WordPress selector)
        content_tag = soup.find("div", class_="the_content_wrapper") or soup.find("article")
        content_html = str(content_tag) if content_tag else ""
        content_text = content_tag.get_text(strip=True) if content_tag else ""

        # Fetch categories/tags if available
        categories = [cat.get_text(strip=True) for cat in soup.select(".cat-links a")] 
        tags = [tag.get_text(strip=True) for tag in soup.select(".tags-links a")]      

        # Fetch images
        images = [img["src"] for img in soup.find_all("img", src=True)]

        if not content_text:
            print(f"❌ Skipping {url} → no content found")
            return None

        return {
            "title": title,
            "html": content_html,
            "text": content_text,
            "images": images,
            "categories": categories,
            "tags": tags,
            "url": url,
            "publish_date": datetime.now(timezone.utc)
        }
    except Exception as e:
        print(f"❌ Failed {url}: {e}")
        return None

# ✅ Generate WXR XML
def create_wxr(posts, filename="blogs-export.xml"):
    rss = ET.Element("rss", {
        "version": "2.0",
        "xmlns:excerpt": "http://wordpress.org/export/1.2/excerpt/",
        "xmlns:content": "http://purl.org/rss/1.0/modules/content/",
        "xmlns:wfw": "http://wellformedweb.org/CommentAPI/",
        "xmlns:dc": "http://purl.org/dc/elements/1.1/",
        "xmlns:wp": "http://wordpress.org/export/1.2/"
    })

    channel = ET.SubElement(rss, "channel")
    ET.SubElement(channel, "title").text = "Imported Blog"
    ET.SubElement(channel, "link").text = "https://yourwordpresssite.com"
    ET.SubElement(channel, "description").text = "Imported blog posts"
    ET.SubElement(channel, "wp:wxr_version").text = "1.2"

    for post in posts:
        if not post:
            continue

        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post["title"]
        ET.SubElement(item, "link").text = post["url"]
        ET.SubElement(item, "content:encoded").text = f"<![CDATA[{post['html']}]]>"
        ET.SubElement(item, "wp:post_date").text = post["publish_date"].strftime("%Y-%m-%d %H:%M:%S")
        ET.SubElement(item, "wp:post_type").text = "post"
        ET.SubElement(item, "wp:status").text = "publish"

        # Categories
        for cat in post["categories"]:
            cat_el = ET.SubElement(item, "category", {"domain": "category", "nicename": cat.lower().replace(" ", "-")})
            cat_el.text = cat

        # Tags
        for tag in post["tags"]:
            tag_el = ET.SubElement(item, "category", {"domain": "post_tag", "nicename": tag.lower().replace(" ", "-")})
            tag_el.text = tag

        # Images as attachments
        for img_url in post["images"]:
            attachment = ET.SubElement(channel, "item")
            ET.SubElement(attachment, "title").text = "Image"
            ET.SubElement(attachment, "link").text = img_url
            ET.SubElement(attachment, "wp:post_type").text = "attachment"
            ET.SubElement(attachment, "wp:attachment_url").text = img_url

    tree = ET.ElementTree(rss)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"✅ Export complete → {filename} created")

# ✅ Fetch all posts
posts = [fetch_blog(url) for url in urls if fetch_blog(url)]
create_wxr(posts)

