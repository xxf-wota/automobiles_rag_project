from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from ai import LoadChroma
import jieba

# 中文停用词
STOP_WORDS = set([
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都",
    "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会",
    "着", "没有", "看", "好", "自己", "这", "那", "他", "她", "它", "们",
    "这个", "那个", "什么", "哪", "怎么", "吗", "呢", "吧", "啊", "哦",
    "还", "被", "把", "让", "从", "对", "与", "但", "而", "或", "所",
    "为", "以", "及", "可", "可以", "能", "能够", "应该", "需要", "已经",
    "虽然", "如果", "因为", "所以", "只是", "还是", "不过", "然后",
    "之", "其", "中", "等", "等等", "即", "使", "向", "将", "按", "当",
    "于", "由", "比", "除了", "关于", "以及", "并且", "此外", "另外",
    "过", "着", "来", "去", "做", "作", "像", "如", "如同", "由于",
])

# 分词函数
def tokenize(documents):
    # 将语料库进行分词
    tokens = jieba.cut(documents)
    # 过滤单词以及停用词
    return [token for token in tokens if token not in STOP_WORDS and len(token.strip()) > 1]

# 获取BM25对象和文档内容
def build_bm25_index(vector):
    # 分批查询所有文档，避免 SQLite "too many SQL variables" 错误
    batch_size = 500
    offset = 0
    all_documents = []
    all_metadatas = []
    while True:
        batch = vector.get(limit=batch_size, offset=offset)
        documents = batch.get("documents") or []
        if not documents:
            break
        all_documents.extend(documents)
        all_metadatas.extend(batch.get("metadatas") or [])
        offset += batch_size
        if len(documents) < batch_size:
            break
    # 处理文档内容
    # 文档内容需要list[Document(id="", page_content="", metadata="")]
    docs = [Document(id=index, page_content=doc, metadata=all_metadatas[index]) for index, doc in enumerate(all_documents)]
    # print(docs)

    # 分词
    documents_corpus = [tokenize(doc.page_content) for doc in docs]
    # 构建BM25对象
    bm25 = BM25Okapi(documents_corpus)
    return bm25, docs

# BM25检索
def bm25_retriever(bm25, question, docs, k=20):
    # 获取BM25分数
    scores = bm25.get_scores(tokenize(question))
    # print(scores)
    # 对分数进行排序并取出前k个文档
    sorted_docs = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)[:k]
    # print(sorted_docs)
    return [doc for score, doc in sorted_docs]



if __name__ == '__main__':
    # 加载向量数据库
    vector = LoadChroma.load_Chroma_conn()
    # 构建BM25索引
    bm25, docs = build_bm25_index(vector)
    # print(docs)
    results = bm25_retriever(bm25, "你好", docs)
    print(results)


