from flask import Flask, request
import os
import rediscluster
import requests
import json 

def connect():
    startup_nodes = [{ "host": "127.0.0.1", "port": "6383"}]
    redis_pool = rediscluster.ClusterConnectionPool(max_connections=5, startup_nodes=startup_nodes, skip_full_coverage_check=True, decode_responses=True)
    testy = rediscluster.RedisCluster(connection_pool=connect())
    print(testy.ping())
    return redis_pool

r = rediscluster.RedisCluster(connection_pool=connect())

app = Flask(__name__)

mySortedSet = "myGame"
  
@app.route('/postOrder/<user>/<restaurant>')
def postorder(user, order):
    r.zadd(mySortedSet, {user:order}) 
    event = "orderCreated"
    requests.get('http://events/postEvent?event=' + event + "&user=" + user)
    return "posted order for " + user
  
@app.route('/getRecentOrders/<topn>')
def getToporders(topn):
    orders = r.zrevrangebyorder(mySortedSet, 0, topn, withorders=True)
    return json.dumps(orders)
    
@app.route('/getUserOrder/<user>')
def getUserorder(user):
    order = r.zorder(mySortedSet, user)
    return "{" + user + " : " + str(order) + "}"

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 