from flask import Flask, request, make_response, jsonify
import os
import rediscluster
import requests
import json
import uuid
import threading

def connect():
    startup_nodes = [{ "host": os.environ.get("FLASK_REDIS_HOST"), "port": os.environ.get("FLASK_REDIS_PORT")}]
    redis_pool = rediscluster.ClusterConnectionPool(max_connections=5, startup_nodes=startup_nodes, skip_full_coverage_check=True, decode_responses=True)
    return redis_pool

r = rediscluster.RedisCluster(connection_pool=connect())

app = Flask(__name__)

@app.route('/postOrder/<user>', methods = ['POST'])
def postOrder(user):
    data = request.get_json()
    order = createOrder(data['user'], data['total'], data['location'])
    r.hset("orders:" + user , order['id'], str(order))
    r.xadd("order:created", order)
    resp = make_response(json.dumps(order))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/getOrder/<user>/<orderid>', methods = ['GET'])
def getOrder(user, orderid):
    order = r.hget("orders:" + user, orderid)
    resp = make_response(jsonify(order))
    resp.headers['Content-Type'] = 'application/json'
    return resp

@app.route('/getOrders/<user>', methods = ['GET'])
def getOrders(user):
    items = []
    for order in r.hscan_iter("orders:" + user, match='*'):
        items.append(order[1])
    resp = make_response(json.dumps(items))
    resp.headers['Content-Type'] = 'application/json'
    return resp

def createOrder(user, total, location):
    return {
        'id': uuid.uuid4().hex,
        'user': user,
        'total': total,
        'location' : location,
        'source' : os.getpid(),
        'status' : "created"
    }

def processDeliveryEvent(item):
    user =  item['user']
    id = item['id']
    order = r.hget("orders:" + user, id)
    r.hset("orders:" + user, id, json.dumps(item))
    return True
    
def startOrderListener():
    try:
        groupname = "orderworkers"
        streamname = "delivery:events"
        r.xgroup_create(streamname, groupname, mkstream=True)
    except:
        print("group exists")
    while True:
        records = r.xreadgroup(groupname, os.getpid(), {streamname: '>'}, None, 0)
        for record in records:
            processDeliveryEvent(record[1][0][1])
            print(record)
            print(r.xack(groupname, streamname, record[1][0][0]))
    startOrderListener()

if __name__ == "__main__":
    thread = threading.Thread(target=startOrderListener)
    thread.daemon = True
    thread.start()
    app.run(host ='0.0.0.0', port = 5000, debug = True)