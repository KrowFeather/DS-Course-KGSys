import csv
import os
from py2neo import Graph

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建 CSV 文件的绝对路径
concept_csv_path = os.path.join(current_dir, '../data/concept_rel.csv')
tag_list_csv_path = os.path.join(current_dir, '../data/tag_list.csv')

def get_top_5_concepts(graph):
    query = """
    MATCH (u:user)-[r:click]->(c:concept)
    RETURN c, r.click_count
    ORDER BY r.click_count DESC
    LIMIT 5
    """
    result = graph.run(query)
    concepts = []
    for record in result:
        concept = record["c"]
        click_count = record["r.click_count"]
        concepts.append({
            "concept_name": concept["name"],  # Assuming concept node has a 'name' property
        })
    return concepts

def match_concepts_with_csv(concepts, csv_file_path):
    concept_c1_map = {}
    concept_name_set = {concept["concept_name"] for concept in concepts}

    with open(csv_file_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)  # 跳过表头
        for row in csv_reader:
            c1_value = row[0]
            c3_value = row[2]
            if c3_value in concept_name_set:
                if c3_value not in concept_c1_map:
                    concept_c1_map[c3_value] = set()
                concept_c1_map[c3_value].add(c1_value)

    return concept_c1_map

def read_tag_list_from_csv(tag_list_csv_path):
    tag_list = []

    with open(tag_list_csv_path, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            tag_list.append(row)

    return tag_list

def match_with_tag_list(concepts, graph):
    # 获取Neo4j的前五个concept和匹配的C1值
    concept_c1_map = match_concepts_with_csv(concepts, concept_csv_path)

    tag_list = read_tag_list_from_csv(tag_list_csv_path)

    matched_cnames = []  # 用于存储匹配的CName，形式为字典列表
    matched_cnames_set = set()  # 用于去重

    # 从tag_list中获取CName并进行匹配
    for row in tag_list:
        c_name = row['CName']
        for concept_name in concept_c1_map:
            if c_name in concept_name:
                # 检查是否已经存在于 matched_cnames_set 中
                if c_name not in matched_cnames_set:
                    matched_cnames.append({
                        "Matched CNames": c_name
                    })
                    matched_cnames_set.add(c_name)  # 添加到集合中以避免重复

    return matched_cnames