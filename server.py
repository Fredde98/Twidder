#This file shall contain all the server​ side remote procedures,
#implemented using Python and Flask.

from random import randint
from flask import jsonify, render_template, request, Flask, send_from_directory
import database_helper
import pathlib
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
import json
import os
app = Flask(__name__, static_url_path='')
app.debug = True

loggedInUsers = {}
loggedInConnections = {  }
count = 0

def updateStats(email):
    print("hej\n\n")
    print(int(os.environ.get("PORT", 5000)))
    print("hej\n\n")
    try:
        response = database_helper.get_messages(email)
        response = response.get_json()
        print(response)
        response = response["messages"]
        message_count = len(response)
        loggedCount = len(loggedInUsers)
        regCount = database_helper.get_user_count()
        
        message = json.dumps({"message_count" : message_count,
                              "loggedInCount" : loggedCount,
                              "registredCount" : regCount})
        user = loggedInConnections[email]
        ws = user[2]
        ws.send(message);
    except KeyError:
        print("I updateStats: Keyerror, förmodligen websocket som saknas")

def log_out(user):
    try:
        ws = user[2]
        ws.send("log_out")
        ws.close()
    except:
        print("Fail i log_out");

@app.route('/')
def render_client():
    return app.send_static_file("client.html")

@app.route('/sign_in', methods=[ 'POST'])
def login():
    print("hej\n\n")
    print(int(os.environ.get("PORT", 5000)))
    print("hej\n\n")
    content = request.get_json()
    username = content["username"]
    password = content["password"]
    global loggedInUsers
    global loggedInConnections
    if database_helper.check_password(username,password):
        letters = "abcdefghiklmnopqrstuvwwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        token = ""

        for  i in range(36):
            token += letters[randint(0,35)]
        
        loggedInUsers[token] = username
        if username in loggedInConnections:
            log_out(loggedInConnections[username])
            
            if loggedInConnections[username][1] in loggedInUsers:
                del loggedInUsers[loggedInConnections[username[1]]]
            del loggedInConnections[username]
                
        response = jsonify({"success": True, "message": "Successfully signed in.", "token": token})
   # web: python server.py
    else:
        response = jsonify({"success": False, "message": "Wrong username or password."})
    
    return response

@app.route('/sign_up', methods=['POST'])
def sign_up():
    content = request.get_json()
    res = database_helper.create_user(content)
    
    return res

@app.route('/sign_out', methods=['PUT'])
def sign_out():
    try:
        header = request.headers
        token = header["token"]
        
        del loggedInUsers[token]
        response = jsonify({"success": True, "message": "Successfully signed out."})

    except KeyError as e:
        response = jsonify({"success": False, "message": "No such token."})

    return response

@app.route('/change_password', methods=['PUT'])
def change_password():
    content = request.get_json()
   
    try:
        header = request.headers
        token = header["token"]
        old_password = content["old_password"]
        new_password = content["new_password"]
        content["username"] = loggedInUsers[token]
       
    except KeyError as e:
        response = jsonify({"success": False, "message": "Missing data."})
        return response
       
    if (len(new_password) < 5):
        return jsonify({"success": False, "message": "To short password."})
       
    return  database_helper.change_password(content )

@app.route('/get_user_data_by_token', methods=['GET'])
def get_user_data_by_token():
    try:
        header = request.headers
        token = header["token"]
        email = loggedInUsers[token]

    except KeyError as e:
        response = jsonify({"success": False, "message": "Missing data."})
        return response

    return database_helper.get_user(email)

@app.route('/get_user_data_by_email/<email>', methods=['GET'])
def get_user_data_by_email(email):
    try:
        params = request.args;
        header = request.headers
        token = header["token"]

    except KeyError as e:
        response = jsonify({"success": False, "message": "Missing data."})
        return response
    
    return database_helper.get_user(email)
        
@app.route('/get_user_messages_by_token', methods=['GET'])
def get_user_messages_by_token():
    try:
        header = request.headers
        print(header)
        token = header["token"]
        email = loggedInUsers[token]

    except KeyError as e:
        response = jsonify({"success": False, "message": "Missing data."})
        return response

    updateStats(email)
    response = database_helper.get_messages(email)
   
    return response
    
@app.route('/get_user_messages_by_email/<email>', methods=['GET'])
def get_user_messages_by_email(email):
    try:
        header = request.headers
        token = header["token"]

        if  token not in loggedInUsers.keys():
            raise KeyError

    except KeyError as e:
        response = jsonify({"success": False, "message": "Missing data."})
        return response

    updateStats(email)
    response = database_helper.get_messages(email)
    
    return response

@app.route('/post_message', methods=['POST'])
def post_message():
    content = request.get_json()       
    try:
        header = request.headers
        token = header["token"]
       
        message = content["message"]
        from_email = loggedInUsers[token]
        to_email = content["email"]
        
    except KeyError as e:
        response = jsonify({"success": False, "message": "Missing data."})
        return response
    
    return database_helper.create_message(from_email, to_email, message)

@app.route('/create_socket')
def api():
    global loggedInUsers
    global loggedInConnections
    
    if not request.environ.get('wsgi.websocket'):
        return ""
    
    ws = request.environ['wsgi.websocket']

    message = ws.receive()
    if message not in loggedInUsers:
        return ""

    email = loggedInUsers[message]
    loggedInConnections[email] = [email, message,  ws]
           
    try:
        while True:
            message = ws.receive()
            ws.send("__pong__")
    except:
        return ""

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', int(os.environ.get("PORT", 5000))), app, handler_class=WebSocketHandler)
    print("hej\n\n")
    print(int(os.environ.get("PORT", 5000)))
    print("hej\n\n")
    http_server.serve_forever()
