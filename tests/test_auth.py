"""
W3D2 作业：鉴权三连

把昨晚在 Swagger 里手点的三条用例，写成代码。

运行方式（在 api-test 目录下）：
    python -m pytest tests/test_auth.py -v

三条全绿 = 通过。
"""

import requests

from config import BASE_URL


# ======================================================================
# 用例 1：不带 token
# ======================================================================

def test_01_without_token_returns_401():

    # 发请求，不给 headers
    response = requests.get(f"{BASE_URL}/invoices", timeout=10)

    # TODO 2：断言状态码是 401
    assert response.status_code == 401


# ======================================================================
# 用例 2：带 token，但越权
# ======================================================================

def test_02_with_token_admin_endpoint_returns_403(auth_headers):
    """
    场景：普通用户带着 token，去访问管理员接口（获取所有用户列表）。
    预期：403 拒绝。

    注意这个用例的 fixture 参数 auth_headers —— 写了它，pytest 会自动
    先执行 conftest.py 里的 auth_headers，把结果塞进来。
    """

    # TODO 3：带 auth_headers 请求 f"{BASE_URL}/users"
    #         参考：requests.get(地址, headers=auth_headers, timeout=10)
    response = requests.get(f"{BASE_URL}/users", headers=auth_headers, timeout=10)
    # TODO 4：断言状态码是 403
    assert response.status_code == 403

# ======================================================================
# 用例 3：带 token，访问自己的资源
# ======================================================================

def test_03_with_token_own_resource_returns_200(auth_headers):
    """
    场景：普通用户带 token，访问自己有权限的接口（查自己的发票）。
    预期：200。

    前两条测"该拒的拒了没"，这条测"该放的放了没"。
    只有拒绝没有放行，说明不了什么 —— 一个把所有人都挡在门外的系统也"安全"。
    """

    # TODO 5：带 auth_headers 请求 f"{BASE_URL}/invoices"
    response = requests.get(f"{BASE_URL}/invoices", headers=auth_headers, timeout=10)
    # TODO 6：断言状态码是 200，
    #         并且响应里包含 "data" 这个键
    #         提示：response.json() 拿到 dict，用 in 判断
    #         参考：assert "data" in response.json()

    assert response.status_code == 200
    assert "data" in response.json()


# ======================================================================
# 加分题（做完三条再考虑，不做也行）
# ======================================================================
#
# 1. 让 test_01 和 test_03 共用一个地址变量，不要写两遍字符串。
#
# 2. 如果 test_02 真的返回了 200 —— 那不是你的代码错了，
#    是这个系统有越权漏洞。先别改代码，来告诉我。
