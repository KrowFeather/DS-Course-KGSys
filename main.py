from flask import Flask, jsonify, request
from flask_cors import CORS
from py2neo import Graph

from System.graph_inject import getDS, getAlgos
from System.recommend import parse_recommend
from xuanke.create_class import create_class_for_user
from xuanke.select_class import select_class


from prework import prework

app = Flask(__name__)
CORS(app)
graph = Graph('neo4j://localhost:7687', auth=('neo4j', '12345678'))


@app.route("/api/ds")
def getDataStructures():
    return jsonify(getDS(graph))


@app.route("/api/algos")
def getAlgorithms():
    return jsonify(getAlgos(graph))


@app.route("/api/addclick", methods=["POST"])
def clickConcept():
    id = request.json.get('id')
    # id = request.args['id']
    concept = request.json.get('concept')
    # concept = request.args['concept']
    graph.run(f'''
    MATCH (u:user), (c:concept)
    WHERE u.id = {id} AND c.name = '{concept}'
    MERGE (u)-[r:click]->(c)
    ON CREATE SET r.click_count = 1
    ON MATCH SET r.click_count = r.click_count + 1
    ''')
    print("ok")
    return jsonify("ok")


@app.route("/api/recommends", methods=["GET"])
def getRecommend():
    uid = request.args['id']
    res = parse_recommend(graph, uid)
    result = []
    for item in res:
        query = '''
            match(c:concept {name:$name})
            return c.brief_desc
        '''
        ans = graph.run(query, name=item)
        desc = [record["c.brief_desc"] for record in ans]
        result.append({
            'name': item,
            'desc': desc[0]
        })
    return jsonify(result)


@app.route('/api/concepts')
def getConcepts():
    query = '''
    match (c:concept)
    return id(c) as id, c.name
    '''
    res = graph.run(query)
    item = [{'id':record['id'],'value': record['c.name']} for record in res]
    return jsonify(item)


@app.route('/api/concepts/<cid>', methods=["GET"])
def getConceptDetail(cid):
    query = '''
    match(c:concept)
    where id(c) = toInteger($id)
    return c.name,c.detailed_desc
    '''
    res = graph.run(query, id=cid)
    result = [{'name':record['c.name'],'detailed_desc':record['c.detailed_desc']} for record in res]
    return jsonify(result[0])

# 新增路由，用于创建班级
@app.route('/api/create_class', methods=["POST"])
def create_class():
    data = request.get_json()
    user_id = data.get('user_id')
    role = data.get('role')
    course_name = data.get('course_name')
    capacity = data.get('capacity')

    print(f"Received role: {role}")  # 打印查看role

    # 权限验证
    if str(role) != '1':  # 假设role是字符串'1'
        print(f"Permission denied. Invalid role: {role}")
        return jsonify({"error": "Permission denied. Invalid role."}), 403

    # 权限验证通过后创建班级
    print('111')
    class_id = create_class_for_user(graph, user_id, role, capacity, course_name)
    print(class_id)

    if class_id:
        print(f"Class created successfully with ID: {class_id}")
        return jsonify({'class_id': class_id}), 200
    else:
        return jsonify({"error": "Failed to create class."}), 500


@app.route('/api/get_classes', methods=['GET'])
def get_classes():
    user_id = int(request.args.get('user_id'))
    role = request.args.get('role')
    # 假设你通过 user_id 查询对应的课程数据
    if role == '1':
        query = f'''
                MATCH (u:user {{id: {user_id}}})-[:own]->(c:Class)
                RETURN c.class_id, c.course_name, c.capacity
            '''
        result = graph.run(query).data()
    else:
        query = f'''
                MATCH (c:Class)-[:selection]->(u:user {{id: {user_id}}})
                RETURN c.class_id, c.course_name, c.capacity
            '''
        result = graph.run(query).data()
    # print(result)
    # 返回查询到的课程数据
    return jsonify(result)


# 新增路由，用于加入班级
@app.route('/api/join_class', methods=["POST"])
def join_class():
    user_id = request.json.get('user_id')
    role = request.json.get('role')  # 用户角色
    class_id = request.json.get('class_id')  # 班级号

    # 调用 select_class 函数加入班级
    result = select_class(graph, user_id, role, class_id)
    print(result)

    if result:
        if result == 'exsist':
            return jsonify({'class_id': '0'})
        return jsonify({'class_id': class_id}), 200
    else:
        return jsonify({"error": "Failed to join class or class does not exist."}), 400


if __name__ == "__main__":
    prework(graph)
    app.run(debug=True)
