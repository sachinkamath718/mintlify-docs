import asyncio
import os
import re
import requests
from urllib.parse import unquote, urlparse, parse_qs
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

# Map: original filename -> proxy URL (to download from)
saved = {}

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if "~gitbook/image" in url and response.status == 200:
                # Extract the inner URL from the ?url= parameter
                qs = parse_qs(urlparse(url).query)
                inner_url = qs.get("url", [None])[0]
                if not inner_url:
                    return
                
                inner_url = unquote(inner_url)
                
                # Extract filename from inner URL
                match = re.search(r'%2F([^%?&]+\.(png|jpg|jpeg|gif|svg|webp))', inner_url, re.IGNORECASE)
                if not match:
                    match = re.search(r'/([^/?&]+\.(png|jpg|jpeg|gif|svg|webp))', inner_url, re.IGNORECASE)
                
                if match:
                    filename = unquote(match.group(1)).replace(" ", "-")
                else:
                    filename = f"image_{abs(hash(url))}.png"
                
                if filename not in saved:
                    saved[filename] = url

        page.on("response", handle_response)

        for page_url in pages:
            print(f"Visiting: {page_url}")
            try:
                await page.goto(page_url, wait_until="networkidle", timeout=30000)
                await asyncio.sleep(2)
            except Exception as e:
                print(f"  Error: {e}")

        await browser.close()

    print(f"\nFound {len(saved)} unique images, downloading...")
    
    session = requests.Session()
    session.headers.update({
        "Referer": "https://docs.zeliot.in/",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    })

    success = 0
    for filename, proxy_url in saved.items():
        local_path = f"images/gitbook/{filename}"
        if os.path.exists(local_path):
            success += 1
            continue
        try:
            r = session.get(proxy_url, timeout=15)
            if r.status_code == 200:
                with open(local_path, "wb") as f:
                    f.write(r.content)
                print(f"  Saved: {filename}")
                success += 1
            else:
                print(f"  Failed ({r.status_code}): {filename}")
        except Exception as e:
            print(f"  Error: {e}")

    print(f"\nDone! {success}/{len(saved)} images saved")

asyncio.run(main())
