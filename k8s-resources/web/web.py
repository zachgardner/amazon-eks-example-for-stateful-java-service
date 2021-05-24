import requests
import json
from flask import Flask, render_template, request, jsonify, make_response

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")
    
if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True) 

@app.route('/profile/<user>')
def profile(user):
    url =  'http://profile/getProfile/' + user
    head = {"Content-Type": "application/json"}
    resp = requests.get(url,headers=head)
    if resp.status_code == 200:
        return render_template("profile.html", response=resp.json())
    else:
        return render_template("profile.html", response="")

@app.route('/postProfile/<user>', methods = ['POST'])
def postProfile(user):
    url =  'http://profile/postProfile/' + user
    head = {"Content-Type": "application/json"}
    resp = requests.post(url, json=request.get_json(), headers=head)
    return resp.text

@app.route('/order/<user>')
def order(user):
    return render_template("order.html")

@app.route('/getSession/<user>')
def getSession(user):
    data = requests.get('http://sessions/getSession/' + user)
    return data.text
    
@app.route('/postSession/<user>', methods = ['POST'])
def postSession(user):
    url =  'http://sessions/postSession/' + user
    head = {"Content-Type": "application/json"}
    resp = requests.post(url, json=request.get_json(), headers=head)
    return resp.text

@app.route('/getOrder/<user>/<orderid>')
def getOrder(user, orderid):
    response = requests.get('http://order/getOrder/' + user + "/" + orderid)
    return response.json()

@app.route('/getOrders/<user>')
def getOrders(user):
    response = requests.get('http://order/getOrders/' + user)
    resp = make_response(jsonify(response.text))
    resp.head = {"Content-Type": "application/json"}
    return resp

@app.route('/orders/<user>')
def orders(user):
    return render_template("orders.html")


@app.route('/postOrder/<user>', methods = ['POST'])
def postOrder(user):
    url =  'http://order/postOrder/' + user
    head = {"Content-Type": "application/json"}
    resp = requests.post(url, json=request.get_json(), headers=head)
    return resp.text

@app.route('/simulation/')
def simulation():
    return render_template("simulation.html")
