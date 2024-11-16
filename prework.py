import csv

from py2neo import Node, Relationship

from System.graph_inject import initial
from crawlers.wikicrawler import parse_description


def prework(graph):
    graph.delete_all()
    with open('data/nbooks/torture(4).csv', 'r', encoding='utf-8') as f:
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

    initial(graph,'admin',1)
    initial(graph,'bob',2)

    graph.run(f'''
    MATCH (u:user), (c:concept)
    WHERE u.id = {1} AND c.name = '哈希表'
    MERGE (u)-[r:click]->(c)
    ON CREATE SET r.click_count = 1
    ON MATCH SET r.click_count = r.click_count + 1
    ''')

    concepts = ['哈希表','堆','并查集','栈','二叉树','线性表','队列']
    mp = parse_description(concepts)
    for k,v in mp.items():
        query = '''
            merge(c:concept {name:$name})
            set c.description = $description
        '''
        graph.run(query,name=k,description=v)