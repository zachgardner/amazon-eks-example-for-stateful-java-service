from flask import Flask, request
import os
import rediscluster
import requests

def connect():
    startup_nodes = [{ "host": os.environ.get("FLASK_REDIS_HOST"), "port": os.environ.get("FLASK_REDIS_PORT")}]
    redis_pool = rediscluster.ClusterConnectionPool(max_connections=5, startup_nodes=startup_nodes, skip_full_coverage_check=True, decode_responses=True)
    return redis_pool
    
r = rediscluster.RedisCluster(connection_pool=connect())

app = Flask(__name__)
  
@app.route('/getSession')
def getSession():
    return r.get("session")
  
@app.route('/postSession')
def postSession():
    r.set("session","1")
    requests.get('http://events/?event=session&user=1')
    return r.get("session")

@app.route('/postSessionAttribute')
def postSessionAttribute():
    return "welcome to the flask tutorials"

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 