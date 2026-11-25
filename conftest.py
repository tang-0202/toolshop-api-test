"""
TOOLSHOP 接口自动化测试 —— 公共 fixture

conftest.py 是 pytest 的约定文件名：放在这里的 fixture，所有测试文件都能直接用，
不需要 import。这是它唯一的特殊之处。

现在这里有四个东西：
  token            —— 登录拿 token（账号没了会自己注册）
  auth_headers     —— 把 token 包成请求头
  first_product_id —— 动态拿一个真实商品的 id
  products_meta    —— 商品总数的元信息，给"分页"类断言算期望值用
"""

import pytest
import requests

from config import BASE_URL, TEST_USER


# ---------------------------------------------------------------- 内部工具
# 下划线开头的普通函数，不是 fixture，pytest 不会收集它。
# 拆出来只是因为下面要用两次。

def _try_login():
    return requests.post(f"{BASE_URL}/users/login", json=TEST_USER, timeout=10)


def _try_register():
    return requests.post(
        f"{BASE_URL}/users/register",
        json={
            "first_name": "Test",
            "last_name": "User",
            "email": TEST_USER["email"],
            "password": TEST_USER["password"],
        },
        timeout=10,
    )


# ---------------------------------------------------------------- fixture

# scope="session" 的意思是：整个测试过程只执行一次。
# 不加这个参数，默认每条用例都登录一次 —— 30 条用例就登录 30 次，
# 慢，而且会被服务端当成暴力破解。

@pytest.fixture(scope="session")
def token():
    """
    登录，拿到 access_token。账号没了就自动注册一个。

    为什么要"自愈"？
      这个演示站是公共的，会定期清库 —— 你今天早上注册的账号，晚上可能就没了。
      真实项目里也一样：测试环境的账号被同事删了、密码被重置了。

    做法：先登录；返回 401 就注册一次，再登录。关键看第二次。
    """

    response = _try_login()

    if response.status_code == 401:
        # 注册结果不用管：成功是 201，邮箱已存在是 422，两种都无所谓。
        _try_register()
        response = _try_login()

    # 登录本身也是一条用例。它挂了，后面所有用例都失去意义，
    # 所以要在这里就断言住，而不是等后面一堆 401。
    assert response.status_code == 200, (
        f"登录失败：{response.status_code} {response.text}"
    )

    return response.json()["access_token"]


@pytest.fixture(scope="session")
def auth_headers(token):
    """把 token 包成请求头，后面每条用例直接加 headers=auth_headers。"""

    # 注意 Bearer 后面有一个空格，这是 HTTP 的格式要求，少了就是 401。
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="session")
def first_product_id():
    """
    从商品列表里动态拿第一个商品的 id。

    为什么不写死一个 id？
      因为这个演示站会重新灌数据 —— 商品还是那些商品，但 id 会整体换一批。
      写死的 id 第二天就 404 了，而接口一点问题都没有。

    这个动作叫「接口串联」：用 A 接口的返回值，去当 B 接口的入参。
    真实项目里到处都是 —— 先下单拿订单号，再用订单号查订单。
    """

    response = requests.get(
        f"{BASE_URL}/products",
        params={"page": 1},
        timeout=10,
    )
    assert response.status_code == 200, f"取商品列表失败：{response.text}"

    products = response.json()["data"]
    assert products, "商品列表是空的，没法取 id"

    return products[0]["id"]


@pytest.fixture(scope="session")
def products_meta():
    """
    商品列表的元信息：总数、每页几条、最后一页是第几页。

    为什么需要它？
      断言里不能写死「第 6 页有 5 条」——这个站是公共的，别人随时在加商品。
      总数一变，第 6 页从 5 条就变成 9 条，你的用例红了，接口却完全正常。

      正确做法：先问接口「现在总共多少条」，再自己算期望值。
      这类测试叫「自描述测试」——它自己知道该期待什么，不依赖外部常量。
    """

    response = requests.get(
        f"{BASE_URL}/products",
        params={"page": 1},
        timeout=10,
    )
    assert response.status_code == 200, f"取商品列表失败：{response.text}"

    body = response.json()
    return {
        "total": body["total"],
        "per_page": body["per_page"],
        "last_page": body["last_page"],
    }
