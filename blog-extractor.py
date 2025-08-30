from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
import time

# ✅ List of blog URLs
urls = [
    "https://lazymonkey.in/blog/role-of-ai-in-healthcare/"
]

# ✅ Setup headless Chrome browser
def get_driver():
    options = Options()
    options.add_argument("--headless")  # Run in background
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ✅ Fetch blog content using Selenium
def fetch_blog(url):
    driver = get_driver()
    try:
        driver.get(url)
        time.sleep(5)  # wait for JavaScript to load (adjust if needed)
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Get title
        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else "No Title"

        # Get content
        content_tag = soup.find("div", class_="mainContent") or soup.find("article")  #in class=" " ,find tag in which blog is, copy that class name and paste here. for eg: article-main-wrap is the class in which main content of the blog is present. 
        content_html = str(content_tag) if content_tag else ""
        content_text = content_tag.get_text(strip=True) if content_tag else ""

        # Get categories/tags
        categories = [cat.get_text(strip=True) for cat in soup.select(".cat-links a")]
        tags = [tag.get_text(strip=True) for tag in soup.select(".tags-links a")]

        # Get images
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
    finally:
        driver.quit()

# ✅ Create WXR (WordPress) XML
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
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post["title"]
        ET.SubElement(item, "link").text = post["url"]
        ET.SubElement(item, "content:encoded").text = f"<![CDATA[{post['html']}"
        ET.SubElement(item, "wp:post_date").text = post["publish_date"].strftime("%Y-%m-%d %H:%M:%S")
        ET.SubElement(item, "wp:post_type").text = "post"
        ET.SubElement(item, "wp:status").text = "publish"

        for cat in post["categories"]:
            cat_el = ET.SubElement(item, "category", {"domain": "category", "nicename": cat.lower().replace(" ", "-")})
            cat_el.text = cat

        for tag in post["tags"]:
            tag_el = ET.SubElement(item, "category", {"domain": "post_tag", "nicename": tag.lower().replace(" ", "-")})
            tag_el.text = tag

        for img_url in post["images"]:
            attachment = ET.SubElement(channel, "item")
            ET.SubElement(attachment, "title").text = "Image"
            ET.SubElement(attachment, "link").text = img_url
            ET.SubElement(attachment, "wp:post_type").text = "attachment"
            ET.SubElement(attachment, "wp:attachment_url").text = img_url

    tree = ET.ElementTree(rss)
    tree.write(filename, encoding="utf-8", xml_declaration=True)
    print(f"✅ Export complete → {filename} created")

# ✅ Main logic
posts = []
for url in urls:
    post = fetch_blog(url)
    if post:
        posts.append(post)

if posts:
    create_wxr(posts)
else:
    print("⚠️ No valid posts found to export.")
