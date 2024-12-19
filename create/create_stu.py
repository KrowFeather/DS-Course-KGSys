from py2neo import Node

def create_user_node(id, name, graph):

    user_node = Node("user", id=id, name=name, role=0)
    graph.create(user_node)
    print(f"用户节点已创建: id={id}, name={name}, role=0")