from flask import Flask, request
import os
import rediscluster
import requests
import json
import boto3

def connect():
    startup_nodes = [{ "host": os.environ.get("FLASK_REDIS_HOST"), "port": os.environ.get("FLASK_REDIS_PORT")}]
    redis_pool = rediscluster.ClusterConnectionPool(max_connections=5, startup_nodes=startup_nodes, skip_full_coverage_check=True, decode_responses=True)
    return redis_pool
    
r = rediscluster.RedisCluster(connection_pool=connect())

dynamodb = boto3.resource('dynamodb',  region_name='us-east-1')

app = Flask(__name__)

@app.route('/postProfile/<user>', methods = ['POST'])
def postProfile(user):
    data = request.get_json()
    data['ProfileID'] = user
    put_profile_to_ddb(user, data)
    key = "profile:" + user
    r.hmset(key, data)
    return str(r.hgetall(key))
  
@app.route('/getProfile/<user>')
def getProfile(user):
    key = "profile:" + user
    if (r.exists(key) > 0):
        return json.dumps(r.hgetall(key))
    else:
        r.hmset(key, get_profile_from_ddb(user))
        return getProfile(user)

def put_profile_to_ddb(user, data):
    table = dynamodb.Table(os.environ.get("DDB_TABLE_NAME"))
    response = table.put_item(
       Item=data
    )
    return json.dumps(response)

def get_profile_from_ddb(user):
    table = dynamodb.Table(os.environ.get("DDB_TABLE_NAME"))
    response = table.get_item(Key={'ProfileID': user})
    return response['Item']

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 
    
    