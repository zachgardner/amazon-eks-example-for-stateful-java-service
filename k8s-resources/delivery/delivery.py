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


@app.route('/postDelivery')
def postEvent():
    user = request.args.get('user')
    event = "Delivery"
    r.xadd(event, {"user" : user})
    r.xadd(user, {"event": event})
    return event + " for  user " + user + " submitted"
  
@app.route('/getDeliveryByUser')
def getDeliveryByUser():
    user = request.args.get('user')
    read_samples = r.xread({user:b"0-0"})
    return str(read_samples)

@app.route('/newDeliveries')
def getNewDeliveries():
    r.xread("orders:created")
    read_samples = r.xread({user:b"0-0"})
    return str(read_samples)

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 