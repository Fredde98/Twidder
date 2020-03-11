"""This file will contain all the functions that access and control
the database and shall contain some SQLscripts. This file will be used
by the server to access the database.​This file shall NOT contain any
domain functions like signin orsignup and shall only contain
data-centric functionality like find_user(), remove_user(),
create_post() and.... E.g.Implementing sign_in() inserver.pyshall
involve a call to find_user() implemented in database_helper.py .

"""

import sqlite3
from sqlite3 import Error
from flask import jsonify

def create_connection(db):

    conn = None

    try:
        conn = sqlite3.connect(db)
        
    except Error as e:
        print(e)

    return conn

database = "database.db"

#validera sign in
#fixa fel om användare inte finns
#get parametrar

#lab1

#log in

#TODO fixa type_error
def create_user(content):
    conn = create_connection(database)
    values = None
    
    try:
        username = content["username"]
        password = content["password"]
        first_name = content["first_name"]
        family_name = content["family_name"]
        gender = content["gender"]
        city = content["city"]
        country = content["country"]
        values = (username, password, first_name, family_name, gender, city, country)
        for x in values:
            if(len(x) < 1):
                raise KeyError
        if( len(password) < 5):
            raise KeyError
       
    except KeyError as e:
        response = jsonify({"success": False, "message": "Could not create user, missing data"})
        return response

    try:
        sql = ''' INSERT INTO users(username, password, first_name, family_name, gender, city, country) VALUES(?,?,?,?,?,?,?) '''

        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        response = jsonify({"success": True, "message": "Successfully signed up."})
    except Error as e:
        print(e)
        response = jsonify({"success": False, "message": "Could not create user. Database error"})
        return response

    return response
        
def list_factory(cursor, row): #För att få en lista istället för tuple från sql
    l = []
    
    for idx, col in enumerate(cursor.description):
        l.append(row[idx] )
        #d[col[0]] = row[idx]

        return l
def get_user_count():

    conn = create_connection(database)
    user = None
    
    sql = 'select username from users '

    # try:
    cur = conn.cursor()
    cur.execute(sql)
    user = cur.fetchall()
    return len(user)
    conn.commit()

        
  
    
def get_user(username):
    conn = create_connection(database)

    user = None
    
    sql = 'select * from users where username =?'

    try:
        cur = conn.cursor()
        cur.execute(sql, (username,))
        user = cur.fetchone()
        user = list(user)
        del user[1]
        conn.commit()
        
    except Error as e:
        print(e)
        response = jsonify({"success": False, "message": "Could not fetch user. Database error"})
        return response
    
    except TypeError as e:
        response = jsonify({"success": False, "message": "Could not fetch user. No such user"})
        print(e)
        return response

    response = jsonify({"success": True, "message": "Successfully fetched user.", "user" : user})
    
    return response

def change_password(content):
    try:
        if(check_password(content["username"], content["old_password"] ) ):
            conn = create_connection(database)
            sql = "update users set password =? where username =?"
            cur = conn.cursor()
            values = (content["new_password"], content["username"])
            cur.execute(sql, values)
            conn.commit()
        else:
            response = jsonify({"success": False, "message": "Incorrect username or password."})
            
            return response
        
    except KeyError as e:
        response = jsonify({"success": False, "message": "Missing data."})
        
    except Error as e:
        response = jsonify({"success": False, "message": "Could not change password. Database error"})
        print(e)
                           
    response = jsonify({"success": True, "message": "Successfully changed password."})

    return response

def get_messages(email):
    
    conn = create_connection(database)
    messages = None

    sql = 'select * from messages where to_user =?'
    
    try:
        cur = conn.cursor()
        cur.execute(sql, (email,))
        messages = cur.fetchall()
        #print(messages)
        conn.commit()
        
    except Error as e:
        print(e)
        response = jsonify({"success": False, "message": "Could not fetch messages. Database error"})
        return response

    response = jsonify({"success": True, "message": "Successfully fetched messages.", "messages" : messages})
   
    return response

def create_message(from_email, to_email, message):

    conn = create_connection(database)
    values = (from_email, to_email, message)
   
    try:
        sql = ''' INSERT INTO messages(from_user, to_user, message) VALUES(?, ?, ?) '''

        cur = conn.cursor()
        cur.execute(sql, values)
        conn.commit()
        response = jsonify({"success": True, "message": "Successfully created message."})
        
    except Error as e:
        print(e)
        response = jsonify({"success": False, "message": "Could not create message. Database error"})
        return response
    
    return response

def check_password(email,password):
    conn = create_connection(database)
    user = None
    
    sql = 'select * from users where username =?'
    
    try:
        cur = conn.cursor()
        cur.execute(sql, (email,))
        user = cur.fetchone()
        conn.commit()
        if(user == None):
            raise Error

    except Error as e:
        
        print(e)
        return False
   
    return password == user[1]

