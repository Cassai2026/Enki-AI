# -*- coding: utf-8 -*-
from playwright.sync_api import sync_playwright
import os
import time

facebook_page_url = "https://www.facebook.com/foodworxmcr"
output_folder = "D:\\Cassworld\\JARVIS AI\\facebook_scraped_posts"

os.makedirs(output_folder, exist_ok=True)

STATE_FILE = "fb_state.json"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    # FIRST RUN (no login saved yet)
    if not os.path.exists(STATE_FILE):
        print("First run detected - please login to Facebook.")

        context = browser.new_context()
        page = context.new_page()

        page.goto("https://facebook.com/login")

        input("Log into Facebook in the browser, then press ENTER here...")

        context.storage_state(path=STATE_FILE)
        print("Login saved!")

    # NORMAL RUN
    context = browser.new_context(storage_state=STATE_FILE)
    page = context.new_page()

    page.goto(facebook_page_url)

    time.sleep(6)

    # Scroll page
    for i in range(20):
        page.mouse.wheel(0, 5000)
        time.sleep(2)

    posts = page.locator("div[data-ad-preview='message']")
    count = posts.count()

    print("Posts found:", count)

    for i in range(count):
        text = posts.nth(i).inner_text()

        file_path = os.path.join(output_folder, f"post_{i}.txt")

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text)

        print("Saved post", i)

    browser.close()

print("Scraping finished.")