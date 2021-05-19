from flask import Flask, request
import os
import rediscluster
import requests
import json
import uuid

def connect():
    startup_nodes = [{ "host": os.environ.get("FLASK_REDIS_HOST"), "port": os.environ.get("FLASK_REDIS_PORT")}]
    redis_pool = rediscluster.ClusterConnectionPool(max_connections=5, startup_nodes=startup_nodes, skip_full_coverage_check=True, decode_responses=True)
    return redis_pool

r = rediscluster.RedisCluster(connection_pool=connect())

app = Flask(__name__)
  
@app.route('/postOrder/<user>/<total>', methods = ['POST'])
def postOrder(user, total):
    order = createOrder(user, total)
    r.hset("orders:" + user , order['id'], str(order))
    r.xadd("order:created", order)
    return json.dumps(order)
  
@app.route('/getOrder/<user>/<orderid>', methods = ['GET'])
def getOrder(user, orderid):
    order = json.loads(r.hget("orders:" + user, orderid))
    return json.dumps(order)

@app.route('/getOrders/<user>', methods = ['GET'])
def getOrders(user):
    items = []
    for order in r.hscan_iter("orders:" + user, match='*'):
        items.append(json.loads(order))
    return json.dumps(items)

def createOrder(user, total):
    return {
        'id': uuid.uuid4().hex,
        'user': user,
        'order_total': total
    }

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 
    
