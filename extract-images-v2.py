import asyncio
import os
import re
import requests
from urllib.parse import urlparse, unquote
from playwright.async_api import async_playwright

pages = [
    "https://docs.zeliot.in/condense/introduction-to-condense/what-is-condense",
    "https://docs.zeliot.in/condense/introduction-to-condense/features-of-condense",
    "https://docs.zeliot.in/condense/introduction-to-condense/condense-architecture",
    "https://docs.zeliot.in/condense/introduction-to-condense/why-condense",
    "https://docs.zeliot.in/condense/introduction-to-condense/key-benefits-of-condense",
    "https://docs.zeliot.in/condense/introduction-to-condense/condense-use-cases",
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
    "https://docs.zeliot.in/condense/v2.4.0/getting-started/what-is-condense",
    "https://docs.zeliot.in/condense/v2.4.0/getting-started/features-of-condense",
    "https://docs.zeliot.in/condense/v2.4.0/getting-started/condense-architecture",
    "https://docs.zeliot.in/condense/v2.4.0/getting-started/why-condense",
    "https://docs.zeliot.in/condense/v2.4.0/getting-started/key-benefits-of-condense",
    "https://docs.zeliot.in/condense/v2.4.0/getting-started/condense-use-cases",
    "https://docs.zeliot.in/condense/v2.4.0/condense-guide/condense-console/create-your-organization",
    "https://docs.zeliot.in/condense/v2.4.0/condense-guide/condense-console/invite-members",
    "https://docs.zeliot.in/condense/v2.4.0/condense-guide/condense-console/roles-and-permissions",
    "https://docs.zeliot.in/condense/v2.4.0/condense-guide/condense-core/create-your-workspace",
    "https://docs.zeliot.in/condense/v2.4.0/condense-guide/condense-core/deploy-an-input-connector",
    "https://docs.zeliot.in/condense/v2.4.0/condense-guide/condense-core/deploy-an-output-connector",
    "https://docs.zeliot.in/condense/v2.4.0/condense-guide/condense-core/deploy-a-custom-transform",
    "https://docs.zeliot.in/condense/v2.4.0/deep-dive/connectors",
    "https://docs.zeliot.in/condense/v2.4.0/deep-dive/transforms",
    "https://docs.zeliot.in/condense/v2.4.0/deep-dive/pipelines",
    "https://docs.zeliot.in/condense/v2.4.0/fully-managed-kafka/kafka-management",
    "https://docs.zeliot.in/condense/v2.4.0/fully-managed-kafka/kafka-connect",
    "https://docs.zeliot.in/condense/v2.4.0/apis/kafka-management-apis",
    "https://docs.zeliot.in/condense/v2.4.0/other-features/settings",
    "https://docs.zeliot.in/condense/v2.4.0/overview/build-your-first-pipeline",
    "https://docs.zeliot.in/condense/v2.4.0/overview/byoc/what-is-byoc",
]

os.makedirs("images/gitbook", exist_ok=True)

# Map from gitbook CDN token -> local path
# We'll match by the upload token in the URL
token_to_local = {}
cdn_to_local = {}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        # Intercept network requests to capture real image URLs
        real_urls = {}

        async def handle_response(response):
            url = response.url
            if ("gitbook" in url or "firebasestorage" in url) and response.status == 200:
                content_type = response.headers.get("content-type", "")
                if "image" in content_type:
                    real_urls[url] = True

        page.on("response", handle_response)

        for page_url in pages:
            print(f"Visiting: {page_url}")
            real_urls.clear()
            try:
                await page.goto(page_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)

                # Also get img src attributes
                imgs = await page.eval_on_selector_all("img", "els => els.map(e => e.src)")
                for img in imgs:
                    if img and not img.startswith("data:"):
                        real_urls[img] = True

                # Download each real image URL
                for img_url in list(real_urls.keys()):
                    # Extract the upload token from the URL
                    token_match = re.search(r'uploads%2F([^%/]+)%2F([^?&"]+)', img_url)
                    if not token_match:
                        token_match = re.search(r'uploads/([^/]+)/([^?&"]+)', img_url)
                    
                    if token_match:
                        token = token_match.group(1)
                        filename = unquote(token_match.group(2)).replace(" ", "-")
                    else:
                        filename = f"image_{abs(hash(img_url))}.png"
                        token = filename

                    local_path = f"images/gitbook/{filename}"
                    
                    if not os.path.exists(local_path):
                        try:
                            r = requests.get(img_url, timeout=15)
                            if r.status_code == 200:
                                with open(local_path, "wb") as f:
                                    f.write(r.content)
                                print(f"  Saved: {filename}")
                            else:
                                print(f"  Failed ({r.status_code}): {filename}")
                                continue
                        except Exception as e:
                            print(f"  Error: {e}")
                            continue
                    
                    token_to_local[token] = f"/images/gitbook/{filename}"

            except Exception as e:
                print(f"  Page error: {e}")

        await browser.close()

    # Save mapping to file
    with open("token-map.txt", "w") as f:
        for token, local in token_to_local.items():
            f.write(f"{token}|{local}\n")

    print(f"\nDone! Saved {len(token_to_local)} mappings to token-map.txt")

asyncio.run(main())
