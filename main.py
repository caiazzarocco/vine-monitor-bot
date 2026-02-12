import os
import time
import json
import requests
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

VINE_URL = "https://www.amazon.it/vine/vine-items?queue=potluck"

CHECK_INTERVAL = 300  # 5 minuti


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    requests.post(url, data=payload)


def load_previous_products():
    if not os.path.exists("products.json"):
        return []
    with open("products.json", "r") as f:
        return json.load(f)


def save_products(products):
    with open("products.json", "w") as f:
        json.dump(products, f)


def scrape_vine_products():
    products = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(VINE_URL)
        page.wait_for_timeout(5000)

        items = page.query_selector_all("div.vvp-item-product-title-container")

        for item in items:
            title = item.inner_text().strip()
            products.append(title)

        browser.close()

    return products


def main():
    send_telegram_message("🚀 Vine Monitor avviato!")

    while True:
        try:
            current_products = scrape_vine_products()
            previous_products = load_previous_products()

            new_products = list(set(current_products) - set(previous_products))
            removed_products = list(set(previous_products) - set(current_products))

            for product in new_products:
                send_telegram_message(f"🟢 NUOVO PRODOTTO:\n{product}")

            for product in removed_products:
                send_telegram_message(f"🔴 PRODOTTO RIMOSSO:\n{product}")

            save_products(current_products)

        except Exception as
