import google.generativeai as palm
import asyncio
from playwright.async_api import async_playwright
import config

async def scrape_reviews(url):
    reviews = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.set_viewport_size({"width": 800, "height": 3200})
        await page.goto(url)
        await page.wait_for_selector(".jftiEf")

        elements = await page.query_selector_all(".jftiEf")
        for element in elements:
            try:
                await page.wait_for_selector(".w8nwRe")
                more_btn = await element.query_selector(".w8nwRe")
                if more_btn:
                    await more_btn.click()
                    await page.wait_for_timeout(5000)
            except Exception as e:
                print(f"Error clicking 'More' button: {e}")
                pass

            try:
                await page.wait_for_selector(".MyEned")
                snippet = await element.query_selector(".MyEned")
                if snippet:
                    text = await snippet.text_content()
                    reviews.append(text)
            except Exception as e:
                print(f"Error extracting review text: {e}")
                pass

        await browser.close()
    return reviews

def summarize(reviews, model):
    prompt = (
        "I collected some reviews of a place I was considering visiting. "
        "Can you summarize the reviews for me? I want to generally know what people "
        "like and dislike. The reviews are below:\n"
    )
    for review in reviews:
        prompt += "\n" + review

    completion = palm.generate_text(
        model=model,
        prompt=prompt,
        temperature=0,
        max_output_tokens=300,
    )

    return completion.result

if __name__ == "__main__":
    palm.configure(api_key=config.PALM_KEY)
    models = [m for m in palm.list_models() if "generateText" in m.supported_generation_methods]
    model = models[0].name

    url = input("Enter a url: ")

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    reviews = loop.run_until_complete(scrape_reviews(url))

    result = summarize(reviews, model)
    print(result)
