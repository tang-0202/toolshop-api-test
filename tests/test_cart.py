import requests

from config import BASE_URL

FAKE_ID = "01ZZZZZZZZZZZZZZZZZZZZZZZZ"

def test_create_cart_returns_valid_id():
    
    response = requests.post(f"{BASE_URL}/carts", timeout=10)

    assert response.status_code == 201
    cart_id = response.json()["id"]
    assert isinstance(cart_id, str)
    assert len(cart_id) == 26


def test_add_item_then_read_cart(first_product_id):
    
    cart_id = requests.post(f"{BASE_URL}/carts", timeout=10).json()["id"]
    add = requests.post(
        f"{BASE_URL}/carts/{cart_id}",
        json={"product_id": first_product_id, "quantity": 2},
        timeout=10,
    )
    assert add.status_code == 200
    assert add.json()["result"] == "item added or updated"

    cart = requests.get(f"{BASE_URL}/carts/{cart_id}", timeout=10).json()

    assert len(cart["cart_items"]) == 1
    item = cart["cart_items"][0]
    assert item["product_id"] == first_product_id
    assert item["quantity"] == 2

def test_add_same_product_twice_accumulates(first_product_id):
    
    cart_id = requests.post(f"{BASE_URL}/carts", timeout=10).json()["id"]
    for _ in range(2):
        requests.post(
            f"{BASE_URL}/carts/{cart_id}",
            json={"product_id": first_product_id, "quantity": 2},
            timeout=10,
        )
    cart = requests.get(f"{BASE_URL}/carts/{cart_id}", timeout=10).json()
    assert len(cart["cart_items"]) == 1
    item = cart["cart_items"][0]
    assert item["product_id"] == first_product_id
    assert item["quantity"] == 4

def test_get_nonexistent_cart_returns_404():
    response = requests.get(
        f"{BASE_URL}/carts/{FAKE_ID}",
        timeout=10,
    )
    assert response.status_code == 404

def test_add_nonexistent_product_returns_404(first_product_id):
    
    cart_id = requests.post(f"{BASE_URL}/carts", timeout=10).json()["id"]
    response = requests.post(
        f"{BASE_URL}/carts/{cart_id}",
        json={"product_id": FAKE_ID, "quantity": 2},
        timeout=10,
    )

    assert response.status_code == 404