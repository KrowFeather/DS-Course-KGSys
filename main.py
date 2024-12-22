import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from py2neo import Graph

from System.graph_inject import getDS, getAlgos
from System.recommend import parse_recommend
from xuanke.create_class import create_class_for_user
from xuanke.select_class import select_class
from TuiJian.TuiJian import get_top_5_concepts, match_with_tag_list
from create.create_stu import create_user_node

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
@cross_origin()
def getRecommend():
    uid = request.args['id']
    uid = int(uid)
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
    item = [{'id': record['id'], 'value': record['c.name']} for record in res]
    return jsonify(item)


@app.route('/api/concepts/<cid>', methods=["GET"])
def getConceptDetail(cid):
    query = '''
    match(c:concept)
    where id(c) = toInteger($id)
    return c.name,c.detailed_desc
    '''
    res = graph.run(query, id=cid)
    result = [{'name': record['c.name'], 'detailed_desc': record['c.detailed_desc']} for record in res]
    return jsonify(result[0])


# 新增路由，用于创建班级
@app.route('/api/create_class', methods=["POST"])
def create_class():
    data = request.get_json()
    user_id = data.get('user_id')
    role = data.get('role')
    course_name = data.get('course_name')
    capacity = data.get('capacity')

    print(f"Received role: {role}")

    if role == 'teacher':
        role_ = 1
    elif role == 'student':
        role_ = 0
    else:
        role_ = 2

    # 权限验证
    if role_ != 1:
        print(f"Permission denied. Invalid role: {role}")
        return jsonify({"error": "Permission denied. Invalid role."}), 403

    # 权限验证通过后创建班级
    class_id = create_class_for_user(graph, user_id, role_, capacity, course_name)
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
    print(user_id)
    print(type(user_id))

    if role == 'teacher':
        role_ = 1
    elif role == 'student':
        role_ = 0
    else:
        role_ = 2

    # 假设你通过 user_id 查询对应的课程数据
    if role_ == 1:
        query = f'''
                MATCH (u:user {{id: {user_id}}})-[:own]->(c:Class)
                RETURN c.class_id, c.course_name, c.capacity
            '''
        result = graph.run(query).data()
    elif role_ == 0:
        query = f'''
                MATCH (c:Class)-[:selection]->(u:user {{id: {user_id}}})
                MATCH (owner:user)-[:own]->(c)
                RETURN c.class_id, c.course_name, c.capacity, owner.name
            '''
        result = graph.run(query).data()
    # 返回查询到的课程数据
    return jsonify(result)


# 新增路由，用于加入班级
@app.route('/api/join_class', methods=["POST"])
def join_class():
    user_id = request.json.get('user_id')
    role = request.json.get('role')  # 用户角色
    class_id = request.json.get('class_id')  # 班级号

    if role == 'teacher':
        role_ = 1
    elif role == 'student':
        role_ = 0
    else:
        role_ = 2

    # 调用 select_class 函数加入班级
    result = select_class(graph, user_id, role_, class_id)
    print(result)

    if result:
        if result == 'exsist':
            return jsonify({'class_id': '0'})
        return jsonify({'class_id': class_id}), 200
    else:
        return jsonify({"error": "Failed to join class or class does not exist."}), 400


# 推荐tag练习
@app.route('/get_tag_exercises', methods=['POST'])
def get_tag_exercises():
    try:
        data = request.get_json()

        if data is None:
            return jsonify({'error': 'Invalid JSON format'}), 400

        cname = data.get('CName', '')

        if not cname:
            return jsonify({'error': 'CName is required'}), 400

        tag_list = './data/tag_list.csv'
        exercises = './data/all_exercises.csv'

        df_tag = pd.read_csv(tag_list, encoding='utf-8')

        result = df_tag[df_tag['CName'] == cname]

        if not result.empty:
            ename = result['EName'].iloc[0]
            print(f"Found EName: {ename}")  # 打印找到的 EName

            df_exercises = pd.read_csv(exercises, encoding='utf-8')

            df_exercises['tag'] = df_exercises['tag'].fillna('').astype(str)

            print(f"Tags in all_exercises:\n{df_exercises['tag'].head()}")  # 打印tag列前几行数据
            matching_exercises = df_exercises[df_exercises['tag'].str.contains(ename, na=False, regex=False)]

            if not matching_exercises.empty:
                exercises_data = []
                for _, row in matching_exercises.iterrows():
                    exercises_data.append({
                        'text': row['text'],
                        'level': row['level'],
                        'url': row['url']
                    })
                # 返回number和匹配的练习数据，确保number是int类型
                return jsonify({
                    'exercises': exercises_data
                })

            return jsonify({'error': 'No exercises found for this tag'}), 404

        return jsonify({'error': 'CName not found'}), 404

    except Exception as e:
        # 打印详细的异常信息
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/get_all_exercises', methods=['GET'])
def get_all_exercises():
    file_path = './data/all_exercises.csv'
    try:
        df = pd.read_csv(file_path)
        selected_columns = df[['text', 'level', 'url']]
        exercises_list = selected_columns.to_dict(orient='records')

        return jsonify(exercises_list)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/search_exercises', methods=['POST'])
def search_exercises():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON format'}), 400

        # 获取搜索字符串
        EXERCISES_FILE = './data/all_exercises.csv'
        search_text = data.get('search_text', '').strip()
        if not search_text:
            return jsonify({'error': 'Search text is required'}), 400

        df_exercises = pd.read_csv(EXERCISES_FILE, encoding='utf-8')

        matching_exercises = df_exercises[df_exercises['text'].str.contains(search_text, case=False, na=False)]

        exercises_data = []
        for _, row in matching_exercises.iterrows():
            exercises_data.append({
                'text': row['text'],
                'level': row['level'],
                'url': row['url']
            })

        return jsonify({'exercises': exercises_data})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/top5_concepts', methods=['GET'])
def top_5_concepts():
    # 调用处理函数获取前五个点击量最高的concept
    matched_cnames = get_top_5_concepts(graph)

    return jsonify(matched_cnames)


@app.route('/process_data', methods=['GET'])
def process_graph_data():
    # 获取前五个点击量最高的concept
    concepts = get_top_5_concepts(graph)

    matched_cnames = match_with_tag_list(concepts, graph)
    return matched_cnames


@app.route('/create_user_node', methods=['POST'])
def create_stu():
    try:
        data = request.get_json()

        if not data or 'id' not in data or 'username' not in data or 'role' not in data:
            return jsonify({'error': '缺少 id 或 username 字段'}), 400
        user_id = data['id']
        user_name = data['username']
        role_ = data['role']
        if role_ == 'student':
            role = 0
        elif role_ == 'teacher':
            role = 1
        else:
            role = 2

        flag = create_user_node(id=user_id, name=user_name, role=role, graph=graph)
        if flag == 0:
            return jsonify({'message': f'用户已存在，创建失败'})
        else:
            return jsonify({'message': f'用户节点已创建: id={user_id}, name={user_name}, role={role_}'}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/findStudents', methods=['POST'])
@cross_origin()
def findStudents():
    # 获取前端传来的class_id
    class_id = request.json.get('classID')
    if not class_id:
        return jsonify({"error": "class_id is required"}), 400
    print(class_id)
    # 查询Class节点和与其相关的User节点，通过click关系获取click_count属性
    query = """
        MATCH (c:Class {class_id: $class_id})-[:selection]->(u:user)
        OPTIONAL MATCH (u)-[cl:click]->(con:concept)
        WHERE cl.click_count <> 0
        RETURN u.name AS user_name, COUNT(cl) AS click_count
    """

    # 执行查询
    result = graph.run(query, class_id=class_id)
    print(result)

    # 获取查询结果
    response_data = []
    for record in result:
        user_name = record["user_name"]
        total_click_count = record["click_count"]
        response_data.append({"name": user_name, "click_count": total_click_count})
    print(response_data)
    return jsonify(response_data)


if __name__ == "__main__":
    # prework(graph)
    app.run(debug=True)
