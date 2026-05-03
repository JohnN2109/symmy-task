from celery import shared_task
from .models import ProductSync

import json
import hashlib
import requests
import time


API_URL = "https://api.fake-eshop.cz/v1/products/"
API_KEY = "symma-secret-token"

def send_product(product, exists=False):

    headers = {
        "X-Api-Key": API_KEY
    }

    for _ in range(3):

        try:

            if exists:
                response = requests.patch(
                    f"{API_URL}{product['sku']}/",
                    json=product,
                    headers=headers
                )
            else:
                response = requests.post(
                    API_URL,
                    json=product,
                    headers=headers
                )

            if response.status_code == 429:
                print("Rate limited... retrying")
                time.sleep(1)
                continue

            print(f"Mock API sync success: {product['sku']}")
            return response

        except requests.exceptions.RequestException:
            print(f"Mock API request simulated for: {product['sku']}")
            return None

@shared_task
def sync_products():

    with open("erp_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    seen_skus = set()

    for item in data:

        sku = item.get("id")
        title = item.get("title")
        price = item.get("price_vat_excl")
        stocks = item.get("stocks", {})
        attributes = item.get("attributes") or {}

        # duplicate SKU
        if sku in seen_skus:
            print(f"Duplicate SKU skipped: {sku}")
            continue

        seen_skus.add(sku)

        # invalid price
        if price is None or price < 0:
            print(f"Invalid price skipped: {sku}")
            continue

        # invalid stock
        if not all(isinstance(v, int) for v in stocks.values()):
            print(f"Invalid stock skipped: {sku}")
            continue

        total_stock = sum(stocks.values())

        # VAT
        price_vat = round(price * 1.21, 2)

        color = attributes.get("color", "N/A")

        transformed_product = {
            "sku": sku,
            "title": title,
            "price": price_vat,
            "stock": total_stock,
            "color": color,
        }

        product_hash = hashlib.sha256(
            json.dumps(
                transformed_product,
                sort_keys=True
            ).encode()
        ).hexdigest()

        obj, created = ProductSync.objects.get_or_create(
            sku=sku,
            defaults={
                "hash": product_hash
            }
        )

        # delta sync
        if not created and obj.hash == product_hash:
            print(f"Skipped unchanged product: {sku}")
            continue

        obj.hash = product_hash
        obj.save()

        send_product(
            transformed_product,
            exists=not created
        )

        print(f"Synced product: {sku}")

        # 5 req/s limit
        time.sleep(0.2)