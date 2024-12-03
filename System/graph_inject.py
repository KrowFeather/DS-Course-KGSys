from py2neo import Node, Relationship


def getDS(graph):
    query = graph.run(f'''
    MATCH (parent)-[:include]->(child)
    WHERE parent.name = '数据结构'
    RETURN child.name
    ''')
    child_names = [record["child.name"] for record in query]
    return child_names


def getAlgos(graph):
    query = graph.run(f'''
        MATCH (parent)-[:include]->(child)
        WHERE parent.name = '算法'
        RETURN child.name
        ''')
    child_names = [record["child.name"] for record in query]
    return child_names

def initial(graph,uname,uid,role):
    user = Node('user', name=uname, id=uid,role=role)
    graph.merge(user, 'user', 'name')
    query = graph.run(f'''
    MATCH (c:concept)
    RETURN c.name
    ''')
    names = [record["c.name"] for record in query]
    for item in names:
        node = Node('concept', name=item)
        bel = Relationship(user, 'click', node)
        graph.merge(bel, 'concept', 'name')
        graph.run('''
        MATCH (u:user)-[r:click]->(c:concept)
        SET r.click_count = 0
        ''')