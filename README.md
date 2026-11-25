# TOOLSHOP 接口自动化测试

基于 **pytest + requests** 的接口自动化测试项目，覆盖 TOOLSHOP 演示电商站的鉴权与商品查询模块。

## 被测对象

| 项 | 地址 |
|---|---|
| 前端站点 | <https://practicesoftwaretesting.com> |
| 后端 API | <https://api.practicesoftwaretesting.com> |
| 接口文档 | Swagger UI（OpenAPI 3.2，API 5.0.0） |

## 技术栈

Python 3.13 · pytest 9.2 · requests 2.34 · pytest-html

## 目录结构

```
api-test/
├── config.py            # 被测地址 + 测试账号（已 gitignore，不进仓库）
├── conftest.py          # 公共 fixture：登录、鉴权头、商品数据
├── pytest.ini           # pytest 配置
├── requirements.txt     # 依赖
└── tests/
    ├── test_auth.py     # 鉴权：401 / 403 / 200
    └── test_products.py # 商品：分页、越界、详情
```

## 用例覆盖

共 **10 条**：

| 模块 | 用例 | 验证点 |
|---|---|---|
| 鉴权 | `test_without_token_returns_401` | 不带 token 访问受保护接口 → 401 |
| 鉴权 | `test_with_token_admin_endpoint_returns_403` | 普通用户访问管理员接口 → 403（越权防护） |
| 鉴权 | `test_with_token_own_resource_returns_200` | 带 token 访问自己的资源 → 200 |
| 商品 | `test_pagination_returns_200` ×3 | 第 1 / 2 / 最后一页都返回 200 |
| 商品 | `test_last_page_item_count` | 最后一页条数 = `total - per_page × (last_page - 1)` |
| 商品 | `test_pagination_out_of_range` | 越界页码 → 200，`data` 为空列表 |
| 商品 | `test_product_detail_success` | 动态取 id 查详情 → 200，且返回的 id 与请求一致 |
| 商品 | `test_product_detail_not_found` | 不存在的 id → 404 |

## 怎么跑

```bash
pip install -r requirements.txt
python -m pytest -v
```

生成 HTML 报告：

```bash
python -m pytest --html=report/report.html --self-contained-html
```

> 要在 `api-test` 目录下执行。`pytest` 是从当前所在位置往下找用例的。

## 设计上的四个决定

**1. 不硬编码商品 id。**
演示站会定期重灌数据，写死的 id 第二天就 404。改成 `first_product_id` fixture 从列表接口动态取。

**2. 期望值从接口算，不从脑子里算。**
公共演示站有别人在造数据，商品总数会变。`test_last_page_item_count` 用公式现算，总量变成 63 还是 630 都能正确断言。

**3. token 会自愈。**
演示站会清库，账号随时消失。fixture 里先登录，遇到 401 就自动注册再登录。

**4. 断言只写在能失败的地方。**
空函数、永远为真的断言，不算测试。

## 踩过的坑（真实记录）

1. **空函数也会 PASSED** —— 函数体只有 `pass`，pytest 依然打绿。先证明测试会失败，再相信它会通过。
2. **`parametrize` 的参数表在导入期求值** —— 把 `len(response.json()["data"]) > 0` 写进参数表会抛 `NameError`，那一刻 `response` 还不存在。数据归数据，判断归判断。
3. **硬编码 id 失效** —— 演示站重灌数据，商品 id 整批换掉，昨天绿的用例今天全红。
4. **账号被清库** —— 昨天能登录的账号，今天返回 401。
5. **公共站数据漂移** —— 商品总数从 50 涨到 63，写死的「最后一页 5 条」必然失败。

这五个都不是语法错误，是真实测试工作里的问题。

## 待补充

- [ ] 购物车 → 下单 → 发票全链路
- [ ] 搜索与筛选参数组合
- [ ] 参数校验（422）批量用例
- [ ] 接口响应时间断言
