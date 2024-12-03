import csv
import json

from py2neo import Node, Relationship

from System.graph_inject import initial


def prework(graph):
    graph.delete_all()
    with open('data/concept_rel.csv', 'r', encoding='utf-8') as f:
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

    initial(graph,'admin',1,0)
    initial(graph,'bob',2,1)

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

    # concepts = ['哈希表','堆','并查集','栈','二叉树','线性表','队列']
    # mp = parse_description(concepts)
    # for k,v in mp.items():
    #     query = '''
    #         merge(c:concept {name:$name})
    #         set c.description = $description
    #     '''
    #     graph.run(query,name=k,description=v)