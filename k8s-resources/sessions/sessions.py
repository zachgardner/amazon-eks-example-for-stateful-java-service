from flask import Flask, request
import os
import rediscluster
import requests
import json
import pickle
import time

def connect():
    startup_nodes = [{ "host": os.environ.get("FLASK_REDIS_HOST"), "port": os.environ.get("FLASK_REDIS_PORT")}]
    redis_pool = rediscluster.ClusterConnectionPool(max_connections=5, startup_nodes=startup_nodes, skip_full_coverage_check=True, decode_responses=True)
    return redis_pool
    
r = rediscluster.RedisCluster(connection_pool=connect())

app = Flask(__name__)
  
@app.route('/getSession/<user>', methods = ['GET'])
def getSession(user):
    data = r.hgetall("session:" + user )
    return json.dumps(data)
  
@app.route('/postSession/<user>', methods = ['POST'])
def postSession(user):
    data = request.get_json()
    data['lastlogin'] = time.time()
    r.hmset("session:" + user, data)
    r.xadd("session:activity", data)
    r.incr("logins:" + user)
    return json.dumps(r.hgetall("session:" + user ))

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 