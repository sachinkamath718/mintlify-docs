import asyncio
import os
import re
import requests
from urllib.parse import urlparse
from playwright.async_api import async_playwright

# All your doc URLs
pages = [
    "https://docs.zeliot.in/condense/introduction-to-condense/what-is-condense",
    "https://docs.zeliot.in/condense/introduction-to-condense/features-of-condense",
    "https://docs.zeliot.in/condense/introduction-to-condense/condense-architecture",
    "https://docs.zeliot.in/condense/introduction-to-condense/why-condense",
    "https://docs.zeliot.in/condense/introduction-to-condense/key-benefits-of-condense",
    "https://docs.zeliot.in/condense/fully-managed-kafka/kafka-management",
    "https://docs.zeliot.in/condense/fully-managed-kafka/kafka-connect",
    "https://docs.zeliot.in/condense/condense-app-getting-started/connectors",
    "https://docs.zeliot.in/condense/condense-app-getting-started/transforms",
    "https://docs.zeliot.in/condense/condense-app-getting-started/pipelines",
    "https://docs.zeliot.in/condense/condense-app-getting-started/settings",
    "https://docs.zeliot.in/condense/condense-app-getting-started/split-utility",
    "https://docs.zeliot.in/condense/condense-app-getting-started/alert-utility",
    "https://docs.zeliot.in/condense/condense-app-getting-started/ksqldb",
    "https://docs.zeliot.in/condense/condense-app-getting-started/campaigns",
    "https://docs.zeliot.in/condense/condense-app-getting-started/activity-auditor",
    "https://docs.zeliot.in/condense/condense-app-getting-started/kafka-topics",
    "https://docs.zeliot.in/condense/condense-app-getting-started/private-version-control",
    "https://docs.zeliot.in/condense/condense-app-getting-started/resource-utilization",
    "https://docs.zeliot.in/condense/condense-app-getting-started/sso-single-sign-on-creating-an-account-logging-into-the-condense-app",
    "https://docs.zeliot.in/condense/condense-app-getting-started/features-of-condense-app",
    "https://docs.zeliot.in/condense/condense-deployment/bring-your-own-cloud-byoc",
    "https://docs.zeliot.in/condense/condense-deployment/bring-your-own-cloud-byoc/deployment-from-aws-marketplace",
    "https://docs.zeliot.in/condense/condense-deployment/bring-your-own-cloud-byoc/deployment-from-gcp-marketplace",
    "https://docs.zeliot.in/condense/condense-deployment/bring-your-own-cloud-byoc/deployment-from-azure-marketplace",
    "https://docs.zeliot.in/condense/connectors-in-condense/available-connectors",
    "https://docs.zeliot.in/condense/connectors-in-condense/upcoming-connectors",
    "https://docs.zeliot.in/condense/future-roadmap-and-development/whats-planned",
    "https://docs.zeliot.in/condense/future-roadmap-and-development/whats-coming",
]

os.makedirs("images/gitbook", exist_ok=True)

url_map = {}  # original gitbook CDN url -> local path

async def extract(page_url, page):
    print(f"Visiting: {page_url}")
    await page.goto(page_url, wait_until="networkidle")
    
    # Get all image src attributes
    imgs = await page.eval_on_selector_all("img", "els => els.map(e => e.src)")
    
    for img_url in imgs:
        if not img_url or img_url.startswith("data:"):
            continue
        
        # Download the image
        try:
            r = requests.get(img_url, timeout=10)
            if r.status_code == 200:
                # Create filename from URL
                parsed = urlparse(img_url)
                filename = parsed.path.split("/")[-1].split("?")[0]
                if not filename or "." not in filename:
                    filename = f"image_{abs(hash(img_url))}.png"
                
                local_path = f"images/gitbook/{filename}"
                
                # Handle duplicates
                counter = 1
                base, ext = os.path.splitext(local_path)
                while os.path.exists(local_path) and open(local_path, "rb").read() != r.content:
                    local_path = f"{base}_{counter}{ext}"
                    counter += 1
                
                with open(local_path, "wb") as f:
                    f.write(r.content)
                
                url_map[img_url] = f"/{local_path}"
                print(f"  Downloaded: {filename}")
        except Exception as e:
            print(f"  Failed: {img_url[:60]}... ({e})")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        for page_url in pages:
            await extract(page_url, page)
            await asyncio.sleep(1)
        
        await browser.close()
    
    print(f"\nDownloaded {len(url_map)} images")
    print("Now update MDX files...")
    
    # Now we need to map these back to the broken CDN URLs in MDX files
    # Print the mapping for manual review
    for orig, local in url_map.items():
        print(f"{orig} -> {local}")

asyncio.run(main())
