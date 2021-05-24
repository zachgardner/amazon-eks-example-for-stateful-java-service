from flask import Flask, request
import os
import rediscluster
import requests
import json
import random
import threading
import logging
import time

def connect():
    startup_nodes = [{ "host": os.environ.get("FLASK_REDIS_HOST"), "port": os.environ.get("FLASK_REDIS_PORT")}]
    redis_pool = rediscluster.ClusterConnectionPool(max_connections=5, startup_nodes=startup_nodes, skip_full_coverage_check=True, decode_responses=True)
    return redis_pool

r = rediscluster.RedisCluster(connection_pool=connect())

logging.basicConfig(filename='record.log', level=logging.DEBUG, format=f'%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app = Flask(__name__)

def processOrder(order):
    item = json.loads(order)
    app.logger.debug('Loading Item')
    if random.random() < .1:
        item['status'] = "exception"
    else:
        item['status'] = "success"
    app.logger.debug('Status Set')
    time.sleep(5)
    return item
     
def startDeliveryListener():
    app.logger.info('Starting Listener')
    groupname = "deliveryworkers"
    streamname = "order:created"
    try:
        r.xgroup_create(streamname, deliveryworkers, mkstream=True)
    except: 
        app.logger.debug('Consumer Group Exists')
    while True:
        records = r.xreadgroup(groupname, os.getpid(), {streamname: '>'}, None, 0) 
        for record in records:
            app.logger.debug('Reading Stream')
            order = json.dumps(record[1][0][1])
            r.xadd("delivery:events", processOrder(order))  
            r.xack(groupname, streamname, record[1][0][0])
            app.logger.debug('Processed Stream:') 
    startDeliveryListener()

  
@app.route('/deliveries/<user>')
def getProfile(user):
    return user
        
if __name__ == "__main__":
    app.logger.debug('Starting App')
    thread = threading.Thread(target=startDeliveryListener)
    thread.daemon = True
    thread.start()
    app.run(host ='0.0.0.0', port = 5000, debug = True) 