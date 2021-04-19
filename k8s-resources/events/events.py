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


@app.route('/postEvent')
def postEvent():
    user = request.args.get('user')
    event = request.args.get('event')
    r.set(user, event);
    return r.get(user)
  
@app.route('/getEventsByUser')
def getEventsByUser():
    user = request.args.get('user')
    return user

@app.route('/getRecentEvents')
def getRecentEvents():
    event = request.args.get('event')
    return event

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 8080, debug = True) 