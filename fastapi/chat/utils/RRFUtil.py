# 将向量检索和BM25检索融合的工具
from langchain_core.documents import Document

def rrf(vector_result, bm25_results):
    # 合并向量检索和BM25检索的结果
    # score_dict：存储分数的字典
    score_dict = {}
    # 存储文档的字典
    docs_dict = {}
    # 处理向量检索的结果
    for index, item in enumerate(vector_result, start=1):
        # 使用get方法可以避免没有此键时的错误
        score_dict[item.id] = score_dict.get(item.id, 0) + (1/(60+index))
        docs_dict[item.id] = item

    # 处理BM25检索的结果
    for index, item in enumerate(bm25_results, start=1):
        # 使用get方法可以避免没有此键时的错误
        score_dict[item.id] = score_dict.get(item.id, 0) + (1/(60+index))
        docs_dict[item.id] = item

    print(score_dict)
    print(docs_dict)

    # 排序
    # 将键值对取出，根据分数排序，降序排序
    sortd_index = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
    # print(sortd_index)
    # item[0]是文档id
    result = [docs_dict[item[0]] for item in sortd_index]
    return result









