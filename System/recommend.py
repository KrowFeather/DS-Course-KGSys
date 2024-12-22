import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def recommend_items(user_index, df, item_similarity_df, top_n=3):
    print(df.shape)
    user_ratings = df.iloc[user_index-1]
    rated_items = user_ratings[user_ratings > 0].index.tolist()  # 获取用户评分过的物品
    # print(rated_items)
    # 创建一个字典来存储推荐分数
    recommendation_scores = {}

    for item in rated_items:
        similar_items = item_similarity_df[item]
        # print(similar_items)
        for similar_item, similarity in similar_items.items():
            # print(similar_item, similarity)
            if similar_item not in rated_items:
                if similar_item not in recommendation_scores:
                    recommendation_scores[similar_item] = 0
                recommendation_scores[similar_item] += similarity * user_ratings[item]
    # print(recommendation_scores)
    # 根据得分排序，选择得分最高的物品作为推荐
    recommended_items = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)
    # print(recommended_items)
    result_list = [k for (k,v) in recommended_items]
    # print(result_list)
    if len(result_list) < top_n:
        for i in range(top_n - len(result_list)):
            for j in range(len(df.columns)):
                if df.columns[j] not in result_list:
                    result_list.append(df.columns[j])
    return result_list[:top_n]


def parse_recommend(graph, uid):
    result = graph.run(f'''
    MATCH (u:user)-[r:click]->(c:concept)
    RETURN u.id,c.name,r.click_count
    order by u.id
    ''')
    data = []
    for record in result:
        data.append((record["u.id"], record["c.name"], record["r.click_count"]))
    df = pd.DataFrame(data, columns=["user", "concept", "click_count"])
    matrix = df.pivot_table(index="user", columns="concept", values="click_count", fill_value=0)
    matrix.columns.name = None
    df = matrix
    item_similarity = cosine_similarity(df.T)  # 转置矩阵计算物品之间的相似度
    item_similarity_df = pd.DataFrame(item_similarity, index=df.columns, columns=df.columns)
    print("\n物品之间的相似度矩阵:")
    print(item_similarity_df)
    recommended_items = recommend_items(uid, df, item_similarity_df, top_n=3)
    print("\n为User1推荐的物品:")
    for item in recommended_items:
        print(f"{item}")
    return recommended_items