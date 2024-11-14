import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# 1. 创建用户-物品评分矩阵
data = {
    'Item1': [5, 3, 0, 0, 1],
    'Item2': [4, 0, 0, 2, 1],
    'Item3': [0, 2, 3, 4, 0],
    'Item4': [0, 0, 0, 5, 4],
    'Item5': [1, 1, 0, 4, 5]
}

# 用户评分数据框
df = pd.DataFrame(data, index=['User1', 'User2', 'User3', 'User4', 'User5'])
print("用户-物品评分矩阵:")
print(df)

# 2. 计算物品之间的余弦相似度
item_similarity = cosine_similarity(df.T)  # 转置矩阵计算物品之间的相似度
item_similarity_df = pd.DataFrame(item_similarity, index=df.columns, columns=df.columns)

print("\n物品之间的相似度矩阵:")
print(item_similarity_df)


# 3. 为用户生成推荐：基于物品的协同过滤推荐
# 我们以User1为例，推荐尚未评分的物品

def recommend_items(user_index, df, item_similarity_df, top_n=3):
    user_ratings = df.iloc[user_index]  # 获取当前用户的评分
    rated_items = user_ratings[user_ratings > 0].index.tolist()  # 获取用户评分过的物品

    # 创建一个字典来存储推荐分数
    recommendation_scores = {}

    for item in rated_items:
        # 找到与用户评分过的物品相似的其他物品
        similar_items = item_similarity_df[item]

        for similar_item, similarity in similar_items.items():
            if similar_item not in rated_items:  # 排除用户已经评分过的物品
                if similar_item not in recommendation_scores:
                    recommendation_scores[similar_item] = 0
                recommendation_scores[similar_item] += similarity * user_ratings[item]  # 加权得分

    # 根据得分排序，选择得分最高的物品作为推荐
    recommended_items = sorted(recommendation_scores.items(), key=lambda x: x[1], reverse=True)

    return recommended_items[:top_n]


# 以User1为例进行推荐
user_index = 0  # User1对应的索引
recommended_items = recommend_items(user_index, df, item_similarity_df, top_n=3)

print("\n为User1推荐的物品:")
for item, score in recommended_items:
    print(f"{item} (推荐得分: {score:.2f})")
