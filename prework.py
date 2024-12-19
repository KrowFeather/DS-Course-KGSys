import csv
import json

from py2neo import Node, Relationship

from System.graph_inject import initial_user,initial_class


def prework(graph):
    graph.delete_all()
    with open('./data/concept_rel.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        data = list(reader)

    print(data[1])
    for i in range(1, len(data)):
        node = Node('concept', name=data[i][0])
        node1 = Node('concept', name=data[i][2])
        bel = Relationship(node, data[i][1], node1)
        graph.merge(node, 'concept', 'name')
        graph.merge(node1, 'concept', 'name')
        graph.merge(bel, 'concept', 'name')

    initial_user(graph,'TestStudent1',11111,0)
    initial_user(graph,'TestTeacher2',22222,1)

    graph.run(f'''
    MATCH (u:user), (c:concept)
    WHERE u.id = {1} AND c.name = '哈希表'
    MERGE (u)-[r:click]->(c)
    ON CREATE SET r.click_count = 1
    ON MATCH SET r.click_count = r.click_count + 1
    ''')

    with open('./data/all_desc.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        print(data)

    for item in data:
        query = '''
        merge(c:concept {name:$name})
        set c.brief_desc=$brief_desc, c.detailed_desc=$detailed_desc
        '''
        graph.run(query,name=item['name'],brief_desc=item['brief_description'],detailed_desc=item['detailed_description'])

    # with open('data/class.csv', 'r', encoding='utf-8') as f:
    #     reader = csv.reader(f)
    #     data = list(reader)
    #
    # # 从第二行开始处理数据，跳过表头
    # for i in range(1, len(data)):
    #     initial_class(graph,data[i][0],data[i][1],data[i][2])
    #
    #
    # # with open('data/teacher_class.csv', 'r', encoding='utf-8') as f:
    # #     reader = csv.reader(f)
    # #     data = list(reader)
    #
    #
    # for i in range(1, len(data)):
    #     teacher_id = int(data[i][0].strip())
    #     class_id = data[i][2].strip()
    #
    #     teacher_query = graph.run(f'''
    #                 MATCH (u:user)
    #                 WHERE u.id = {teacher_id}
    #                 RETURN u
    #             ''')
    #     teacher_node = teacher_query.evaluate()  # 返回查询到的节点
    #
    #     class_query = graph.run(f'''
    #                 MATCH (c:Class)
    #                 WHERE c.class_id = "{class_id}"
    #                 RETURN c
    #             ''')
    #     class_node = class_query.evaluate()  # 返回查询到的节点
    #     if teacher_node and class_node:
    #         # 创建教师与课程之间的 OWN 关系
    #         own_relation = Relationship(teacher_node, 'own', class_node)
    #
    #         # 合并关系到图数据库，防止重复创建
    #         graph.create(own_relation)
    #
    # print("所有教师与课程之间的 OWN 关系创建完成。")
    #
    # # with open('data/student_class.csv', 'r', encoding='utf-8') as f:
    # #     reader = csv.reader(f)
    # #     data = list(reader)
    #
    #
    # for i in range(1, len(data)):
    #     student_id = int(data[i][2].strip())
    #     class_id = data[i][0].strip()
    #
    #     student_query = graph.run(f'''
    #                 MATCH (u:user)
    #                 WHERE u.id = {student_id}
    #                 RETURN u
    #             ''')
    #     student_node = student_query.evaluate()  # 返回查询到的节点
    #
    #     class_query = graph.run(f'''
    #                 MATCH (c:Class)
    #                 WHERE c.class_id = "{class_id}"
    #                 RETURN c
    #             ''')
    #     class_node = class_query.evaluate()  # 返回查询到的节点
    #     if student_node and class_node:
    #         selection_relation = Relationship(class_node, 'selection', student_node)
    #
    #         # 合并关系到图数据库，防止重复创建
    #         graph.create(selection_relation)
    #
    # print("所有学生与课程之间的 SELECTION 关系创建完成。")

    # concepts = ['哈希表','堆','并查集','栈','二叉树','线性表','队列']
    # mp = parse_description(concepts)
    # for k,v in mp.items():
    #     query = '''
    #         merge(c:concept {name:$name})
    #         set c.description = $description
    #     '''
    #     graph.run(query,name=k,description=v)