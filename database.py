import sqlite3
import os
import redis # type: ignore
import sqlite3
import string
import hashlib
import random 

r = redis.Redis(host='localhost', port=8022, decode_responses=True)

def execute_query(query):
    connection = sqlite3.connect("accounts.db")
    cursor = connection.cursor()
    cursor.execute(query)
    for row in cursor:
        return ('\t'.join(str(column).replace('|', '\t') for column in row))
    connection.close()

def cexecute_query(query):
    connection = sqlite3.connect("conversations.db")
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    for row in cursor:
        return ('\t'.join(str(column).replace('|', '\t') for column in row))
    connection.close()

#creates a connection to the symptom db, connects to the cursos executes the query and then closes the connection
def sexecute_query(query):
    connection = sqlite3.connect("symptom.db")
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    connection.close()
   
    
# creates account and profile tables
accounts = '''
CREATE TABLE IF NOT EXISTS accounts (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    hashpassword TEXT,
    salt TEXT
);
'''
execute_query(accounts)


conversations = '''
CREATE TABLE IF NOT EXISTS conversations (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT NOT NULL,
    conversationid TEXT NOT NULL,
    messages TEXT
);
'''
cexecute_query(conversations)

symptom = """
    CREATE TABLE IF NOT EXISTS symptom (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    userid TEXT,
    thyroid BOOLEAN,
    birthcontrol BOOLEAN,
    antidepressants BOOLEAN,
    pelvicpain BOOLEAN,
    discharge BOOLEAN,
    bodyhair BOOLEAN,
    bowel BOOLEAN,
    intercourse BOOLEAN,
    irregular BOOLEAN,
    hotflashes BOOLEAN,
    dryness BOOLEAN,
    chills BOOLEAN,
    sweats BOOLEAN,
    sleep BOOLEAN,
    mood BOOLEAN,
    weight BOOLEAN,
    metabolism BOOLEAN,
    hair BOOLEAN,
    dryskin BOOLEAN,
    breast BOOLEAN,
    abdominal BOOLEAN,
    bleeding BOOLEAN,
    spotting BOOLEAN,
    deepvoice BOOLEAN,
    muscle BOOLEAN,
    bald BOOLEAN,
    bleedingintercourse BOOLEAN,
    appetite BOOLEAN,
    fertility BOOLEAN,
    fqbowel BOOLEAN,
    backpain BOOLEAN);
    """
sexecute_query(symptom)


"""
This function determines if the password and username match with each other. 
It should return a boolean
"""
def validate_password(username, password):
    #connection = sqlite3.connect("accounts.db")
    # gets password from database and formats it into a string return
    conn = sqlite3.connect("accounts.db")

    # select and salt user password
    querysalt = "SELECT salt FROM accounts WHERE username = ?"
    cur = conn.cursor()
    cur.execute(querysalt, (username,))
    conn.commit()
    querysalt = cur.fetchone()[0]
    print(f"The salt that {username} is logging in with is {str(querysalt)}")
    cur.close()
    conn.close()

    if not querysalt:
        return False
    
    password += str(querysalt)
    # hash user password
    hashAlgo = hashlib.sha256()
    hashAlgo.update(password.encode())
    hashpassword = hashAlgo.hexdigest()
    print(f"The hashpassword that {username} is logging in with is {hashpassword}")
    conn = sqlite3.connect("accounts.db")
    querypassword = "SELECT hashpassword FROM accounts WHERE username = ?"
    cur = conn.cursor()
    cur.execute(querypassword, (username,))
    conn.commit()
    querypassword = cur.fetchone()[0]
    cur.close()
    conn.close()

    # compare password
    print(f"query: {querypassword} vs hash: {hashpassword}")
    if querypassword == hashpassword:
        return True
    elif querypassword != hashpassword:
        print("Error: password is incorrect")
        return False

"""
This function adds a user to the database and takes a string of the username and 
the password. It returns a boolean or a string that describes what happened.
"""
def register_new_user(username, password):
    # establishes connection to accounts database
    salt = str(''.join(random.choices(string.printable, k = 10)))
    saltedpassword = password + salt
    hashAlgo = hashlib.sha256()
    hashAlgo.update(saltedpassword.encode())
    hashpassword = hashAlgo.hexdigest()
    print(f"The hashed password for {username} is {hashpassword}")
    
    # ensures that the username doesn't exist in the database
    if username_found(username) == True:
        # tells the server that the username exists
        return "Account Exists"

    # inse.rts info to the user table
    insert = "INSERT INTO accounts (username, hashpassword, salt) VALUES(?,?,?)"

    conn = sqlite3.connect("accounts.db")
    cur = conn.cursor()
    print(f"The salt that {username} is registering with with is {salt}")
    cur.execute(insert, (username, hashpassword, salt))
    conn.commit()
    cur.close()
    conn.close()

    if validate_password(username, password) == True:
        print(f"user {username} registered and in the database")

    return True

"""
This function looks for a username and returns a boolean
"""
# determines if username exists
def username_found(username):
    try:
        # inserts info to the user table
        insert = "SELECT username FROM accounts WHERE username = ?"
        conn = sqlite3.connect("accounts.db")
        cur = conn.cursor()
        cur.execute(insert, (username,))
        conn.commit()
        queryusername = cur.fetchone()[0]
        cur.close()
        conn.close()
    
        if queryusername == username:
            # username found
            print(f"Username Found: {queryusername}")
            return True
        else:
            # username not found
            print("Username Not Found")
            return False
    except: 
        print("Username Search Failed")
        return False

"""
This function gets all the users in the database
This function should return a list
"""

def getusers():
    # inserts info to the user table
    insert = "SELECT username FROM accounts"
    conn = sqlite3.connect("accounts.db")
    cur = conn.cursor()
    cur.execute(insert)
    conn.commit()
    usernames = list(cur.fetchall())
    cur.close()
    conn.close()
    usernames = [item[0] for item in usernames if item[0]]
    return usernames

"""
This function takes in two users and looks for conversations between them. 
It should return a list of every message
"""
def get_messages(user1, user2):
    # inserts info to the user table
    print(f"ATTEMPTING TO GET MESSAGES BETWEEN {user1} and {user2}")
    insert = "SELECT messages FROM conversations WHERE (user1 = ? AND user2 = ?) OR (user1 = ? AND user2 = ?)"
    conn = sqlite3.connect("conversations.db")
    cur = conn.cursor()
    cur.execute(insert, (user1, user2, user2, user1))
    conn.commit()
    messages = cur.fetchall()
    cur.close()
    conn.close()
    if messages == None:
        conn = sqlite3.connect("conversations.db")
        cur = conn.cursor()
        # Conversation doesn't exist, insert a new row
        insert = "INSERT INTO conversations (user1, user2, messages) VALUES(?,?,?)"
        cur.execute(insert, (user1, user2, ""))
        conn.commit()
        messages = ""
        cur.close()
        conn.close()

    # should be a tuple
    return list(messages)

"""
This function takes two users and a message and adds that user to the database.
This function doesn't return anything.
"""
def add_message(user1, user2, message):
    if user2 == None:
        return 
    
    if message == None:
        return
    
    # create new message list
    oldmessages = get_messages(user1, user2)

    oldmessages.append(message)

    messageslist = oldmessages
    messagesstring = str(messageslist)

    if oldmessages == None:
        messageslist = [message]
        messagesstring = str(messageslist)

    # SQL INSERT statement to add a new message
    insert = "INSERT INTO conversations (user1, user2, messages) VALUES (?,?,?)"
    # Connect to the SQLite database
    conn = sqlite3.connect("conversations.db")
    cur = conn.cursor()
    cur.execute(insert, (user1, user2, str(message)))
    conn.commit()
    # Close the cursor and connection
    cur.close()
    conn.close()

    return 


"""Checks to see if the user has inputted any medication they are taking and returns true of they are on
any one of them""" 
def check_medications(userid):
    connection = sqlite3.connect("symptom.db")
    crsr = connection.cursor()
    crsr.execute("""SELECT COUNT(*) FROM symptom WHERE userid =? AND (thyroid = 1 OR birthcontrol = 1 OR antidepressants = 1);""",(userid,))
    num = crsr.fetchone()[0]
    connection.commit()
    connection.close()
    if int(num) < 1:
        print("false")
        return False
    else:
        print("true")
        return True

"""Parameter is the userid. This checks the number of symptoms the user shows for ovarian cyst
by taking the count of how many symptoms are returned from the database which are associated with ovarian cyst.
If the count is less than 2, it returns false as they are not at risk for it. If its greater it returns true."""
def checkovarian(userid):
    connection = sqlite3.connect("symptom.db")
    crsr = connection.cursor()
    crsr.execute("""SELECT COUNT(*) FROM symptom WHERE userid = ? AND (pelvicpain =1 OR intercourse=1 OR bowel=1 OR fertility=1 OR appetite=1 OR fqbowel=1);""", (userid,))
    num = crsr.fetchone()[0]
    connection.commit()
    connection.close()
    if int(num) < 2:
        print("false")
        return False
    else:
        print("true")
        return True
"""Parameter is the userid. This checks the number of symptoms the user shows for pcos
by taking the count of how many symptoms are returned from the database which are associated with pcos.
If the count is less than 2, it returns false as they are not at risk for it. If its greater it returns true."""
def checkpcos(userid):
    connection = sqlite3.connect("symptom.db")
    crsr = connection.cursor()
    crsr.execute("""SELECT COUNT(*) FROM symptom WHERE userid =? AND (irregular=1 OR deepvoice=1 OR muscle=1 OR bald=1 OR bodyhair=1);""", (userid,))
    num = crsr.fetchone()[0]
    connection.commit()
    connection.close()
    if int(num) < 2:
        print("false")
        return False
    else:
        print("true")
        return True
"""Parameter is the userid. This checks the number of symptoms the user shows for endometriosis
by taking the count of how many symptoms are returned from the database which are associated with endometriosis.
If the count is less than 2, it returns false as they are not at risk for it. If its greater it returns true."""
def checkendo(userid):
    connection = sqlite3.connect("symptom.db")
    crsr = connection.cursor()
    crsr.execute("""SELECT COUNT(*) FROM symptom WHERE userid =? AND (abdominal=1 OR backpain=1 OR bleeding=1 OR bleedingintercourse=1 OR bowel=1);""", (userid,))
    num = crsr.fetchone()[0]
    connection.commit()
    connection.close()
    if int(num) < 2:
        print("false")
        return False
    else:
        print("true")
        return True
"""Parameter is the userid. This checks the number of symptoms the user shows for polyps
by taking the count of how many symptoms are returned from the database which are associated with polyps. 
If the count is less than 2, it returns false as they are not at risk for it. If its greater it returns true."""
def checkpolyps(userid):
    connection = sqlite3.connect("symptom.db")
    crsr = connection.cursor()
    sql = crsr.execute("""SELECT COUNT(*) FROM symptom WHERE userid=? AND (bleeding=1 OR bleedingintercourse=1 OR discharge=1 OR spotting=1);""",(userid,))
    print("SQL return:", sql)
    num = crsr.fetchone()[0]
    connection.commit()
    connection.close()
    if int(num) < 2:
        print("false")
        return False
    else:
        print("true")
        return True

"""This function takes all of the symptoms, medications, and userid as parameters and inserts all of the values into the symptom database.
The information is obtained from the form that is submitted so that this information can be accessed from the database 
for other functions."""
def submitform(userid, thymed,bc,antdep, pelvicpain,discharge,bodyhair,bowel,intercourse,weight,irregular,hotflashes,dryness,chills, sweats,sleep,mood,metabolism, hair, dryskin, breast, abdominal, bleeding, spotting, deepvoice, muscle, bald, bleedingintercourse, appetite, fertility, fqbowel, backpain):
    connection = sqlite3.connect("symptom.db")
    crsr = connection.cursor()
    crsr.execute("""INSERT INTO symptom (userid, thyroid, birthcontrol, antidepressants, pelvicpain,discharge,bodyhair,bowel,intercourse,weight,irregular,hotflashes,dryness,chills,sweats,sleep,mood,metabolism,hair,dryskin, breast, abdominal, bleeding, spotting, deepvoice, muscle, bald, bleedingintercourse, appetite, fertility, fqbowel, backpain) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);""",(userid, thymed,bc,antdep, pelvicpain,discharge,bodyhair,bowel,intercourse,weight,irregular,hotflashes,dryness,chills, sweats,sleep,mood,metabolism, hair, dryskin, breast, abdominal, bleeding, spotting, deepvoice, muscle, bald, bleedingintercourse, appetite, fertility, fqbowel, backpain))
    connection.commit()
    crsr.close()
