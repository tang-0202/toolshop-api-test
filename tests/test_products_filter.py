import pytest
import requests

from config import BASE_URL
def test_price_range():
    # ① 请求：打 /products，带区间参数
    response = requests.get(
        f"{BASE_URL}/products",
        params={"between": "price,10,20"},
        timeout=10,
    )
    # ② 状态码
    assert response.status_code == 200
    # ③ 取数据 —— data 是在这里"生"出来的，不是参数
    data = response.json()["data"]
    # ④ 断言数据真的符合条件
    assert all(10 <= p["price"] <= 20 for p in data)

def test_sort_prices_desc():
    response = requests.get(
        f"{BASE_URL}/products",
        params={"sort": "price,desc"},
        timeout=10,
    )
    assert response.status_code == 200
    data = response.json()["data"]
    prices = [p["price"] for p in data]
    assert prices == sorted(prices, reverse=True)

def test_filter_by_category():
    # ① 先拿一个"确实在用"的分类 id
    first = requests.get(
        f"{BASE_URL}/products", params={"page": 1}, timeout=10
    ).json()["data"][0]
    cid = first["category"]["id"]

    # ② 用它过滤
    response = requests.get(
        f"{BASE_URL}/products", params={"by_category": cid}, timeout=10
    )
    assert response.status_code == 200

    # ③ 断言每一条都属于这个分类
    data = response.json()["data"]
    assert len(data) > 0
    assert all(p["category"]["id"] == cid for p in data)