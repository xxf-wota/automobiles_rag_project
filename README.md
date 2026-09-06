# Automobiles RAG Project

基于 RAG（检索增强生成）架构的汽车领域智能问答系统，支持多领域意图识别、混合检索与知识图谱增强。

## 项目架构

```
automobiles_rag_project/
├── fastapi/                    # 后端服务（FastAPI + LangChain）
│   ├── ai/                     # 模型加载模块（LLM、Embedding、Chroma、Reranker、Ollama）
│   ├── automobiles_chroma/     # ChromaDB 向量数据库持久化目录
│   ├── chat/                   # 聊天模块
│   │   ├── controller/         # 接口层
│   │   ├── dao/                # 数据访问层
│   │   ├── entity/             # 数据实体
│   │   ├── service/            # 业务逻辑层
│   │   ├── tools/              # Agent 工具（Neo4j 知识图谱查询）
│   │   └── utils/              # 工具类（BM25、RRF、意图识别）
│   ├── common/                 # 公共模块（MySQL、Redis、Neo4j 连接）
│   ├── create_data/            # 数据构建与向量化入库
│   ├── users/                  # 用户模块（注册、登录、封禁管理）
│   ├── utils/                  # 工具类（JWT、权限控制、Session）
│   ├── main.py                 # 应用入口
│   ├── .env                    # 环境变量（本地开发）
│   ├── .env.docker             # 环境变量（Docker 部署）
│   ├── dockerfile              # 后端 Dockerfile
│   └── requirements.txt        # Python 依赖
├── rag_app/                    # 前端服务（Vue3 + Vite + Element Plus）
│   ├── src/                    # 前端源码
│   ├── dist/                   # 构建产物
│   ├── Dockerfile              # 前端 Dockerfile（多阶段构建 + Nginx）
│   ├── nginx.conf              # Nginx 配置
│   └── package.json            # Node.js 依赖
└── README.md
```

## 技术栈

### 后端

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| LLM 框架 | LangChain |
| 大语言模型 | 通义千问（DashScope API，qwen3.7-plus） |
| 意图识别 | Ollama（qwen2.5:7b） |
| 向量化模型 | paraphrase-multilingual-MiniLM-L12-v2 |
| 重排序模型 | bge-reranker-large-v1 |
| 向量数据库 | ChromaDB |
| 知识图谱 | Neo4j |
| 关系数据库 | MySQL |
| 缓存 | Redis |
| 认证 | JWT + 邮箱验证码 |

### 前端

| 类别 | 技术 |
|------|------|
| 框架 | Vue 3 |
| 构建工具 | Vite 8 |
| UI 组件库 | Element Plus |
| 路由 | Vue Router 4 |
| Markdown 渲染 | marked + DOMPurify |
| HTTP 客户端 | Axios |
| 静态服务 | Nginx（Docker 多阶段构建） |

## 核心功能

### 1. 多领域意图识别

系统自动识别用户问题所属领域，支持：
- **汽车领域**：车辆部件、品牌、驾驶、购车、保养维修等
- **医疗领域**：疾病、症状、药物、检查、治疗等
- **天气领域**：天气查询、预报等
- **闲聊**：日常对话

### 2. 混合检索与 RRF 融合

- **向量检索**：基于 ChromaDB 的语义相似度搜索
- **BM25 关键词检索**：基于分词的关键词匹配
- **RRF（倒数排名融合）**：将两种检索结果融合排序
- **重排序**：使用 bge-reranker-large-v1 对候选文档精排

### 3. 知识图谱增强

- 医疗领域通过 Neo4j 知识图谱提供结构化查询（疾病-症状-药物-检查等关联关系）
- LangChain Agent 自动生成 Cypher 查询语句

### 4. 上下文压缩

- 智能压缩历史对话上下文，控制 token 用量
- 保留最近 N 轮原始对话，早期对话自动生成摘要

### 5. 用户系统

- 邮箱验证码注册 / 密码登录
- JWT 认证与权限控制
- 管理员用户封禁管理

### 6. 流式输出

- 对话接口采用 SSE（Server-Sent Events）流式推送
- 前端实时渲染 Markdown 格式回复

## 快速开始

### 环境要求

- Python 3.12+
- Node.js 22+
- MySQL 8.0+
- Redis
- Neo4j（可选，用于医疗知识图谱）
- Ollama（可选，用于意图识别，也可以使用 DashScope 替代）
- NVIDIA GPU（推荐，用于向量化和重排序加速）

### 1. 克隆项目

```bash
git clone <repository-url>
cd automobiles_rag_project
```

### 2. 后端配置

#### 安装依赖

```bash
cd fastapi
pip install -r requirements.txt
```

#### 配置环境变量

复制 `.env` 文件并根据实际环境修改配置：

```bash
cp .env .env.local
```

主要配置项说明：

| 变量 | 说明 |
|------|------|
| `MYSQL_HOST` | MySQL 主机地址 |
| `MYSQL_USER` | MySQL 用户名 |
| `MYSQL_PASSWORD` | MySQL 密码 |
| `MYSQL_DATABASE` | MySQL 数据库名 |
| `REDIS_HOST` | Redis 主机地址 |
| `NEO4J_URL` | Neo4j 连接地址 |
| `CHROMA_PATH` | ChromaDB 持久化路径 |
| `COLLECTION_NAME` | ChromaDB 集合名称 |
| `RERANKER_MODEL_PATH` | 重排序模型路径 |
| `LLM_MODEL_NAME` | 大模型名称 |
| `EMBEDDING_MODEL` | 向量化模型路径 |
| `OLLAMA_MODEL_NAME` | Ollama 意图识别模型名称 |
| `OLLAMA_BASE_URL` | Ollama 服务地址 |
| `DASHSCOPE_API_KEY` | 阿里云 DashScope API Key |
| `SECRET_KEY` | JWT 签名密钥 |

#### 下载模型

需要下载以下模型到本地：

- **向量化模型**：[paraphrase-multilingual-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)
- **重排序模型**：[bge-reranker-large-v1](https://huggingface.co/BAAI/bge-reranker-large)

#### 初始化数据库

确保 MySQL 中已创建对应数据库，并执行建表语句（见项目 SQL 初始化脚本）。

#### 构建向量数据库

```bash
cd fastapi
python -m create_data.AutomobilesDataBuild
```

#### 启动后端服务

```bash
cd fastapi
python main.py
```

服务默认运行在 `http://localhost:8000`，API 文档见 `http://localhost:8000/docs`。

### 3. 前端配置

```bash
cd rag_app
npm install
npm run dev
```

前端开发服务器默认运行在 `http://localhost:5173`。

### 4. 前端构建

```bash
cd rag_app
npm run build
```

构建产物输出到 `rag_app/dist/` 目录。

## Docker 部署

### 后端

```bash
cd fastapi
docker build -f dockerfile -t rag-server .

docker run -d --name rag-server --gpus all -p 8000:8000 \
  --env-file .env.docker \
  -v /path/to/paraphrase-multilingual-MiniLM-L12-v2:/app/models/embedding:ro \
  -v /path/to/bge-reranker-large-v1:/app/models/reranker:ro \
  -v /path/to/automobiles_chroma:/app/models/chroma \
  rag-server
```

### 前端

```bash
cd rag_app
docker build -t rag-app .
docker run -d --name rag-app -p 8080:8080 rag-app
```

## API 接口概览

### 用户模块 `/users`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/users/sendEmail` | 发送邮箱验证码 |
| GET | `/users/checkCode` | 验证邮箱验证码 |
| GET | `/users/emailPassword` | 密码登录 |
| GET | `/users/forgetPassword` | 忘记密码 |
| POST | `/users/register` | 用户注册 |
| GET | `/users/banUser` | 封禁用户（管理员） |
| GET | `/users/unbanUser` | 解封用户（管理员） |
| GET | `/users/getAllUsers` | 获取所有用户（管理员） |

### 聊天模块 `/chat`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/chat/chat` | 流式聊天（SSE） |
| POST | `/chat/saveConversation` | 保存聊天记录 |

### 历史记录模块 `/history`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/history/getHistoryList` | 获取历史记录列表 |
| DELETE | `/history/deleteHistory` | 删除历史记录 |

## RAG 流程

```
用户输入问题
    │
    ▼
意图识别（Ollama / qwen2.5:7b）
    │
    ├── 汽车领域 ──→ 向量检索（ChromaDB）+ BM25 检索 ──→ RRF 融合 ──→ 重排序
    │
    ├── 医疗领域 ──→ Neo4j 知识图谱查询（Agent 自动生成 Cypher）
    │
    ├── 天气领域 ──→ 高德天气 API
    │
    └── 闲聊 ──→ 直接 LLM 对话
    │
    ▼
上下文压缩（智能摘要 + 滑动窗口）
    │
    ▼
LLM 生成（通义千问 qwen3.7-plus）
    │
    ▼
SSE 流式输出到前端
```

## 数据来源

- **汽车之家.csv**：车型参数数据（GBK 编码）
- **汽车大师问答摘要.csv**：维修保养问答数据（UTF-8 编码）
- **Neo4j 医疗知识图谱**：疾病、症状、药物、检查、科室等关联数据
