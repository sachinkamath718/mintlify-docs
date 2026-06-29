import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()

        async def handle_response(response):
            url = response.url
            if response.status == 200:
                content_type = response.headers.get("content-type", "")
                if "image" in content_type:
                    print(f"IMAGE: {url[:150]}")

        page.on("response", handle_response)

        await page.goto("https://docs.zeliot.in/condense/introduction-to-condense/what-is-condense", wait_until="networkidle")
        await asyncio.sleep(3)
        await browser.close()

asyncio.run(main())
