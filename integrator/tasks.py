import json
import hashlib
import requests
import time
from pathlib import Path

from celery import shared_task

from .models import ProductSync

def generate_hash(product: dict) -> str:
    product_string = str(sorted(product.items()))
    return hashlib.sha256(product_string.encode()).hexdigest()

def transform_product(item):
    stocks = item.get("stocks", {})

    total_stock = 0
    for value in stocks.values():
        if isinstance(value, int):
            total_stock += value

    attributes = item.get("attributes") or {}

    price = item.get("price_vat_excl") or 0

    return {
        "sku": item.get("id"),
        "name": item.get("title"),
        "price": round(price * 1.21, 2),
        "stock": total_stock,
        "color": attributes.get("color", "N/A"),
    }
@shared_task
def sync_products():
    base_dir = Path(__file__).resolve().parent.parent
    file_path = base_dir / "erp_data.json"

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        product = transform_product(item)
        product_hash = generate_hash(product)

        obj, created = ProductSync.objects.get_or_create(
            sku=product["sku"],
            defaults={"hash": product_hash}
        )

        if not created and obj.hash == product_hash:
            print(f"SKIP {product['sku']}")
            continue

        print(f"SEND {product['sku']}")
        send_to_eshop(product, exists=not created)

        obj.hash = product_hash
        obj.save()


def send_to_eshop(product, exists=False):
    headers = {
        "X-Api-Key": "symma-secret-token"
    }

    url = "https://api.fake-eshop.cz/v1/products/"

    if exists:
        url = f"https://api.fake-eshop.cz/v1/products/{product['sku']}/"

    for _ in range(3):
        response = requests.post(url, json=product, headers=headers)

        if response.status_code == 429:
            time.sleep(1)
            continue

        return response        