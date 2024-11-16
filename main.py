from flask import Flask, jsonify, request
from flask_cors import CORS
from py2neo import Graph

from System.graph_inject import getDS, getAlgos
from System.recommend import parse_recommend
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

@app.route("/api/addclick",methods=["POST"])
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

@app.route("/api/recommends",methods=["GET"])
def getRecommend():
    uid = request.args['id']
    res = parse_recommend(graph,uid)
    # print(res)
    result = []
    for item in res:
        query = '''
            match(c:concept {name:$name})
            return c.description
        '''
        ans = graph.run(query,name=item)
        desc = [record["c.description"] for record in ans]
        # print(ans)
        result.append({
            'name':item,
            'desc':desc[0]
        })
    return jsonify(result)


if __name__ == "__main__":
    prework(graph)
    app.run()