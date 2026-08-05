<<<<<<< HEAD
# 多功能文本处理网关服务

轻量级、自包含的多功能文本处理网关，将文本工具箱、网页正文提取、离线信息挖掘整合为统一 RESTful API，支持 Docker 一键部署，全程离线运行。

## 功能

| 模块 | 功能 | 依赖 |
| :--- | :--- | :--- |
| 文本工具箱 | 拼音转换 / 中文分词 / 繁简转换 / 字数统计 | `pypinyin` `jieba` `OpenCC` |
| 网页正文提取 | 输入 URL，提取标题与纯文本正文 | `requests` `readability-lxml` `beautifulsoup4` |
| 离线信息挖掘 | 身份证号码解析、手机号码归属地查询 | 本地 CSV + `phone.dat` |

## 项目结构

```
├── app/
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置（API_KEY / DATA_DIR 环境变量）
│   ├── security.py          # API Key 校验依赖
│   ├── schemas.py           # Pydantic 请求/响应模型
│   ├── routers/             # text / extract / info 路由
│   ├── engines/             # 各功能引擎实现
│   └── data/                # 离线数据（CSV + phone.dat）
├── scripts/download_data.py # 离线数据下载脚本
├── Dockerfile
└── requirements.txt
```

## 快速开始

### 1. 准备数据

```bash
python scripts/download_data.py
```

或手动将以下文件放入 `app/data/`：

- `provinces.csv` / `cities.csv` / `areas.csv`：行政区划（[modood/Administrative-divisions-of-China](https://github.com/modood/Administrative-divisions-of-China)）
- `phone.dat`：手机号归属地（[xluohome/phonedata](https://github.com/xluohome/phonedata)）

缺失数据时服务仍可启动，仅身份证/手机号接口返回 503。

### 2. 本地运行

```bash
pip install -r requirements.txt
set API_KEY=your-secret-key
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

访问 `http://localhost:8000/docs` 查看交互式 API 文档。

### 3. Docker 部署

```bash
docker build -t text-gateway .
docker run -d -p 8080:8000 -e API_KEY=your-secret-key --name text-gateway text-gateway
```

健康检查：`GET /` 返回服务状态与数据加载情况。

## API 说明

所有接口需在请求头携带 `X-API-Key: <密钥>`（未设置环境变量时默认为 `dev-insecure-key`）。

| 方法 | 端点 | 请求体 | 说明 |
| :--- | :--- | :--- | :--- |
| POST | `/api/tool/text` | `{"text": "..."}` | 拼音、分词、繁体、字数 |
| POST | `/api/tool/extract` | `{"url": "..."}` | 抓取网页并提取标题与正文 |
| POST | `/api/tool/idcard` | `{"id_card": "..."}` | 解析省市区、出生日期、性别 |
| POST | `/api/tool/phone` | `{"phone": "..."}` | 查询省份、城市、运营商、区号、邮编 |

### 示例

```bash
curl -X POST http://localhost:8000/api/tool/text \
  -H "Content-Type: application/json" -H "X-API-Key: your-secret-key" \
  -d '{"text": "你好世界"}'
```

```bash
curl -X POST http://localhost:8000/api/tool/phone \
  -H "Content-Type: application/json" -H "X-API-Key: your-secret-key" \
  -d '{"phone": "13800138000"}'
```

## 配置项

| 环境变量 | 默认值 | 说明 |
| :--- | :--- | :--- |
| `API_KEY` | `dev-insecure-key` | API 访问密钥（生产环境必须修改） |
| `DATA_DIR` | `app/data` | 离线数据目录 |

## 数据格式说明

**身份证**：由三个 CSV（省/市/区三级）构建 `code -> name` 映射，身份证前 2/4/6 位匹配；同时校验第 18 位校验码与出生日期合法性。

**手机号**：`phone.dat` 为 xluohome 二进制格式（头部 8 字节 + 记录区 + 索引区，索引每条 9 字节，二分查找），卡类型编码：1 移动 / 2 联通 / 3 电信 / 4-6 各虚拟 / 7 广电 / 8 广电虚拟。