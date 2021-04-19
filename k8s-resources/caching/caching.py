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
  
@app.route('/getUserScore')
def getUserScore():
    return "welcome to the flask tutorials"
  
@app.route('/getTopScores')
def getTopScores():
    return "welcome to the flask tutorials"

@app.route('/postScore')
def postScore():
    return "welcome to the flask tutorials"

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 