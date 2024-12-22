from py2neo import Node
from System.graph_inject import initial_user


def create_user_node(id, name, role, graph):
    existing_user = graph.nodes.match("user", id=id).first()
    if existing_user:
        return 0
    user_node = Node("user", id=id, name=name, role=role)
    graph.create(user_node)
    initial_user(graph, name, id, role)
    print(f"用户节点已创建: id={id}, name={name}, role={role}")
    return 1
