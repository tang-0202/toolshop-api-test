import requests

from config import BASE_URL


def lookup_address(postcode="1011AB", country="NL"):
    response = requests.get(
        f"{BASE_URL}/postcode-lookup",
        params={"postcode": postcode, "country": country},
        timeout=10,
    )
    assert response.status_code == 200
    return response.json()



def test_full_checkout_creates_invoice(first_product_id, auth_headers):
    cart_id = requests.post(f"{BASE_URL}/carts", timeout=10).json()["id"]
    requests.post(
            f"{BASE_URL}/carts/{cart_id}",
            json={"product_id": first_product_id, "quantity": 2},
            timeout=10,
        )
    cart = requests.get(f"{BASE_URL}/carts/{cart_id}", timeout=10).json()
    unit_price = cart["cart_items"][0]["product"]["price"]
    requests.post(
            f"{BASE_URL}/payment/check",
            json={"payment_method": "cash-on-delivery", "payment_details": {}},
            timeout=10,
        )
    addr = lookup_address()
    response = requests.post(
            f"{BASE_URL}/invoices",
            headers=auth_headers,
            json={
                "billing_street": addr["street"],
                "billing_city": addr["city"],
                "billing_state": addr["state"],
                "billing_country": addr["country"],
                "billing_postal_code": addr["postcode"],
                "payment_method": "cash-on-delivery",
                "payment_details": {},
                "cart_id": cart_id,
            },
            timeout=10,
        )

    assert response.status_code == 201
    assert response.json()["invoice_number"].startswith("INV-")
    assert abs(response.json()["total"] - unit_price * 2) < 0.01


def test_create_invoice_without_token_returns_401(first_product_id):
    cart_id = requests.post(f"{BASE_URL}/carts", timeout=10).json()["id"]
    requests.post(
            f"{BASE_URL}/carts/{cart_id}",
            json={"product_id": first_product_id, "quantity": 2},
            timeout=10,
        )
    requests.post(
            f"{BASE_URL}/payment/check",
            json={"payment_method": "cash-on-delivery", "payment_details": {}},
            timeout=10,
        )
    addr = lookup_address()
    response = requests.post(
            f"{BASE_URL}/invoices",
            json={
                "billing_street": addr["street"],
                "billing_city": addr["city"],
                "billing_state": addr["state"],
                "billing_country": addr["country"],
                "billing_postal_code": addr["postcode"],
                "payment_method": "cash-on-delivery",
                "payment_details": {},
                "cart_id": cart_id,
            },
            timeout=10,
        )

    assert response.status_code == 401