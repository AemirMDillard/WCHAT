from flask import Flask, Blueprint, redirect, request, send_file, make_response, render_template, jsonify # type: ignore
from uuid import uuid4
import os
import redis # type: ignore
import sqlite3
import string
import hashlib
import random 
import database
import json 

app = Flask(__name__)
r = redis.Redis(host='localhost', decode_responses=True)
messages = []

@app.route("/")
def index():
    '''
        Handles the default route
    '''
    return redirect("/login")

@app.errorhandler(404)
def route_not_found(e):
    return send_file(os.path.join('static', '404.html')), 404

"""
This function and route handles logging in. It gives error messages and 
doesn't allow certain kinds of usernames. This function also sets the user cookies
and then redirects to the homepage
"""
@app.route("/login", methods=['GET', 'POST'])
def login():
    '''
        Allows login with a POST request
    '''
    if request.method == "GET":
        return render_template('login.j2')
    elif request.method == "POST":
        fields = ['mode', 'username', 'password']
        for f in fields:
            if f not in request.form:
                return "ERROR"
    
        verb = ''

        # login user
        if request.form.get('mode') == 'login':
            verb = 'LOGIN'
            password = request.form.get('password')
            username = request.form.get('username')
            print("Logging In:", username)
            # gets password from database and formats it into a string return
            if database.validate_password(username, password) == False:
                message = "Password Invalid. Please try again."
                return render_template('login.j2',error=message)
            #SETS USER TOKEN
            cookie = uuid4()
            r.set(f'{cookie}', f'{username}')

            response = make_response(redirect('/homepage'))
            response.set_cookie('sessiontoken', str(cookie))

            return response
            
        elif request.form.get('mode') == 'register':
            verb = 'REGISTER'
            username = request.form.get('username')
            password = request.form.get('password')
            usernameexists = database.username_found(username)

            print(usernameexists)
            if len(username) < 5:
                message = "Your username should be between 5 - 12 characters."
                return render_template('login.j2',error=message)
            if len(username) > 12:
                message = "Your username should be between 5 - 12 characters."
                return render_template('login.j2',error=message)
            if usernameexists == False:
                database.register_new_user(username, password)
                #SETS USER TOKEN
                cookie = uuid4()
                r.set(f'{cookie}', f'{username}')
                response = make_response(redirect('/homepage'))
                response.set_cookie('sessiontoken', str(cookie))

                return response
            if usernameexists == "Account Exists" or usernameexists == True:
                print("Server Knows Account Exists")
                message = "This account already exists. Please login."
                return render_template('login.j2',error=message)
        
            else:
                message = "username already exists"
                return render_template('login.j2',error=message)
    
        else:
            return "ERROR"

        print(f"MODE: {verb} {request.form.get('username')} {request.form.get('password')}") 

    return redirect('/homepage')

"""
This route just tells you what your username is
"""
@app.route("/homepage", methods=['GET', 'POST'])
def homepage():
    cookie = request.cookies.get('sessiontoken')
    username = r.get(f"{cookie}")
    if username == None:
        message = "please login."
        return render_template('login.j2',error=message)
    """
    Always sends render template
    """
    return render_template('homepage.j2', sessiontoken=cookie)

"""
This route logs the user out.
"""
@app.route("/logout", methods=['GET', 'POST'])
def logout():
    cookie = request.cookies.get('sessiontoken')
    r.delete(f"{cookie}") 
    return redirect("/login")

"""
This route goes to the chat page
"""
@app.route("/chat", methods=['GET', 'POST'])
def chat():
    cookie = request.cookies.get('sessiontoken')
    username = r.get(f"{cookie}")
    if username == None:
        message = "please login."
        return render_template('login.j2',error=message)

    global messages
    print(f"{username} has started a chat")
    if request.method == "GET":
        if len(messages) > 1:
            messageslist = list(messages)
            return render_template('chatpage.j2', defaultmessages=jsonify({"messages": messageslist}))
        else:
            return render_template('chatpage.j2')
    if request.method == "POST":
        return render_template('chatpage.j2', defaultmessages=messages)
    

@app.route("/sendmessage", methods=['POST'])
def sendmessage():
    cookie = request.cookies.get('sessiontoken')
    username = r.get(f"{cookie}")
    if username == None:
        message = "please login."
        return render_template('login.j2',error=message)
    # Get the message from the request body
    message = request.json.get('message')
    user2 = request.json.get('username')
    message = f"{username}: {message}"
    database.add_message(username, user2, message)
    messageslist = database.get_messages(username, user2)
    if user2 == None:
        return
    return jsonify({"messages": messageslist})

@app.route("/chathistory", methods=['POST'])
def chathistory():
    cookie = request.cookies.get('sessiontoken')
    username = r.get(f"{cookie}")
    user2 = request.json.get('username')
    messageslist = database.get_messages(username, user2)
    return jsonify({"messages": messageslist})

#this function sends the user the quiz when redirected to the route /quiz.html
@app.route("/quiz.html", methods=["GET", "POST"])
def takequiz():
    if request.method == "POST":
        cookie = request.cookies.get('sessiontoken')
        username = r.get(f"{cookie}")
        userid = str(username)
        pelvicpain= "q1" in request.form
        discharge = "q2" in request.form
        bodyhair = "q3" in request.form
        bowel = "q4" in request.form
        intercourse ="q5" in request.form
        irregular = "q6" in request.form
        hotflashes = "q7" in request.form
        dryness = "q8" in request.form
        chills = "q9" in request.form
        sweats = "q10" in request.form
        sleep = "q11" in request.form
        mood = "q12" in request.form
        weight = "q13" in request.form
        metabolism = "q14" in request.form
        hair = "q15" in request.form
        dryskin = "q16" in request.form
        breast = "q17" in request.form
        abdominal = "q18" in request.form
        bleeding = "q19" in request.form
        spotting = "q20" in request.form
        deepvoice = "q21" in request.form
        muscle ="q22" in request.form
        bald = "q23" in request.form
        bleedingintercourse = "q24" in request.form
        appetite = "q25" in request.form
        fertility = "q26" in request.form
        fqbowel = "q27" in request.form
        backpain = "q28" in request.form
        thymed = "m1" in request.form
        antdep = "m2" in request.form
        bc = "m3" in request.form
        database.submitform(userid, thymed,bc,antdep, pelvicpain,discharge,bodyhair,bowel,intercourse,weight,irregular,hotflashes,dryness,chills, sweats,sleep,mood,metabolism, hair, dryskin, breast, abdominal, bleeding, spotting, deepvoice, muscle, bald, bleedingintercourse, appetite, fertility, fqbowel, backpain)
        return redirect('/results')
    return send_file("quiz.html")

"""This function is what allows for the diagnosis to happen after the form is submitted. First, it makes the username the userid 
to be used and stored the database. Then it takes all of the checkboxes from the form and retrieves its
boolean value. Then the database.submitform() function takes in all of the symptoms and userid to actually enter
everything into the database. Then, the if statements check for different diseases and according to if it 
is true or false, it adds it to the final_diagnoses list which is sent as an async function to results.html """
@app.route("/diagnosis", methods=["GET"])
def return_diagnosis():
    cookie = request.cookies.get('sessiontoken')
    username = r.get(f"{cookie}")
    userid = str(username)
    final_diagnoses = []
    if database.checkendo(userid) == True:
        final_diagnoses.append("You may be at a risk for endometriosis")
    else:
        final_diagnoses.append("You are not at a risk for endometriosis.")

    if database.checkovarian(userid) == True:
        final_diagnoses.append("You may be at a risk for ovarian cysts")
    else:
        final_diagnoses.append("You are not at a risk for ovarian cysts.")

    if database.checkpcos(userid) == True:
        final_diagnoses.append("You may be at a risk for PCOS")
    else:
        final_diagnoses.append("You are not at a risk for PCOS")

    if database.checkpolyps(userid) == True:
        final_diagnoses.append("You may be at a risk for Polyps")
    else:
        final_diagnoses.append("You are not at a risk for Polyps")
    if database.check_medications(userid) == True:
        final_diagnoses.append("You may be experiencing symptoms because of the medication you are taking.")
    print(final_diagnoses)
    return jsonify({"final_diagnoses": final_diagnoses})



@app.route("/active-users", methods=['GET'])
def activeusers():
    global messages
    userslist = database.getusers()
    print(f"users: {userslist}")
    return jsonify({"messages": userslist})

@app.route("/currentuser", methods=['GET'])
def currentuser():
    cookie = request.cookies.get('sessiontoken')
    username = r.get(f"{cookie}")
    username = f"YOU ARE CURRENTLY LOGGED IN AS: {username}"
    return jsonify({"username": username})
        
@app.route("/results", methods=['GET'])
def results():
    return send_file("results.html")

app.run(host="0.0.0.0", port=8022, debug=True)