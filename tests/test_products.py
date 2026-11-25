"""
W3D3 作业：参数化 + 商品接口

昨晚/今天你已经会写"一条用例"了。
今天学怎么用 1 个函数 + 1 张表，跑出 N 条用例。

运行：
    python -m pytest tests/test_products.py -v
"""

import pytest
import requests

from config import BASE_URL


# 真实商品 id（如果哪天 404 了，去 /products 列表里抄一个新的）
FAKE_ID = "01ZZZZZZZZZZZZZZZZZZZZZZZZ"


# ======================================================================
# 任务 1（我给你写好的范例，读它，然后照着做 2 和 3）
# ======================================================================

@pytest.mark.parametrize("page", [1, 2, 6])
def test_pagination_returns_200(page):
    response = requests.get(
        f"{BASE_URL}/products",
        params={"page": page},     # → 实际请求 .../products?page=1
        timeout=10,
    )

    assert response.status_code == 200
    assert response.json()["current_page"] == page


# ======================================================================
# 任务 2：越界页码（你写）
# ======================================================================

def test_last_page_item_count(products_meta):
    """最后一页有几条 = 总数 - 前面满页的部分"""
    last = products_meta["last_page"]
    total = products_meta["total"]
    per_page = products_meta["per_page"]

    response = requests.get(
        f"{BASE_URL}/products",
        params={"page": last},
        timeout=10,
    )
    assert response.status_code == 200

    expect = total - per_page * (last - 1)
    assert len(response.json()["data"]) == expect


def test_pagination_out_of_range(products_meta):
    """超出最后一页：200，但 data 是空列表"""
    page = products_meta["last_page"] + 5

    response = requests.get(
        f"{BASE_URL}/products",
        params={"page": page},
        timeout=10,
    )
    assert response.status_code == 200
    assert response.json()["data"] == []
# ======================================================================
# 任务 3：商品详情 —— 一条参数化，两种预期（你写）
# ======================================================================

def test_product_detail_success(first_product_id):
    # TODO 4：请求 f"{BASE_URL}/products/{product_id}"
    response = requests.get(
        f"{BASE_URL}/products/{first_product_id}",
        timeout=10,
    )
    # TODO 5：断言状态码 == expect_status
    assert response.status_code == 200
    # TODO 6（只在 200 时做）：断言返回的 "id" == product_id，
    #         证明它返的确实是我要的那个商品，而不是随便哪个
    assert response.json()["id"] == first_product_id 


def test_product_detail_not_found():
    response = requests.get(
        f"{BASE_URL}/products/{FAKE_ID}",
        timeout=10,
    )
    assert response.status_code == 404


# ======================================================================
# 加分题
# ======================================================================
#
# 1. 任务 2 的 expect_count 用了 None 打头，读起来别扭。
#    能不能换个更清楚的写法？（提示：拆成两条用例，或者用 pytest.param 配 id）
#
# 2. 跑的时候加 --collect-only，看看 pytest 一共收集到几条用例：
#       python -m pytest tests/test_products.py --collect-only -q
#    数一数，跟你手写的函数个数比一比。
