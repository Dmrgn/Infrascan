import sqlite3
import bcrypt
import validate_email
import password_strength
import time
import yagmail
import json

from constants import *

with open("./data/keys.json") as f:
    data = json.load(f)
    email_password = data["email"]

yag = yagmail.SMTP(EMAIL_ADDRESS, email_password)
con = sqlite3.connect("./data/user.sqlite", check_same_thread=False)
cur = con.cursor()

# session length in minutes before having to login again
SESSION_LENGTH = 30
VALID_NAME_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 "
PASSWORD_POLICY = password_strength.PasswordPolicy.from_names(
    length=8,
    uppercase=1, 
    numbers=1,
    special=1,
    nonletters=0,
)

"""
user table is (name, email, password)
session table is (email, secret, session_time)
email_code table is (code, secret, name, email, password)
"""

def validate_user(secret):
    # check database to see if the user is logged in
    res = cur.execute(f"SELECT * FROM session WHERE secret = '{secret}'")
    user = res.fetchone()
    # check if user exists
    if user is None:
        return {"error": "Please login to continue", "login":True}
    email = user[0]
    # check if the session time is valid
    if time.time()-user[2] >= 60*SESSION_LENGTH:
        cur.execute(f"DELETE FROM session WHERE email = '{email}'")
        con.commit()
        return {"error": "Session expired", "login":True} 
    # extend session time
    cur.execute(f"""UPDATE session
                    SET session_time = {time.time()}
                    WHERE email = '{email}'""")
    con.commit()
    # user is validated
    return {"error": None}

def login(email, password):
    # check if the email exists
    if not validate_email.validate_email(email.strip()):
        return {"error": "Please enter a valid email address"}
    # find user with specified email
    res = cur.execute(f"SELECT * FROM user WHERE email = '{email}'")
    user = res.fetchone()
    # check if user exists
    if user is None:
        return {"error": "No user was found with the specified email address"}
    # validate the users password
    if not bcrypt.checkpw(password.encode(), user[2].encode()):
        return {"error": "The email address or password is incorrect"}
    
    res = cur.execute(f"SELECT * FROM session WHERE email = '{email}'")
    session = res.fetchone()
    secret = ""
    if not session is None:
        # update existing session entry
        secret = session[1]
        cur.execute(f"""UPDATE session
                    SET session_time = {time.time()}
                    WHERE email = '{email}'""")
        con.commit()
    else:
        # create new session entry
        secret = bcrypt.gensalt().decode()
        cur.execute(f"""INSERT INTO session VALUES
                        ('{email}', '{secret}', {time.time()})""")
        con.commit()
    # return the generated secret
    return {"error": None, "secret": secret}

def register(name, email, password):
    # check if the name is valid
    if not is_valid_name(name):
        return {"error":"Name is too long or contains invalid characters"}
    # check if the email exists
    if not validate_email.validate_email(email.strip()):
        return {"error": "Please enter a valid email address"}
    # check if the email already exists
    res = cur.execute(f"SELECT * FROM user WHERE email = '{email}'")
    user = res.fetchone()
    if not user is None:
        return {"error":"User with specified email already exists"}
    # check if the password is valid
    if len(PASSWORD_POLICY.test(password)) != 0:
        return {"error":"Password must be at least 8 characters long and contain at least 1: capital letter, number and symbol"}
    # create email verification data
    email_code = bcrypt.gensalt().decode()[-7:-1]
    secret = bcrypt.gensalt().decode()
    # send email
    if send_email_code(name, email, email_code) == None:
        return {"error":"An error occured while sending a verification email"}
    # create email verification entry
    cur.execute(f"""INSERT INTO email_code VALUES
                    ('{email_code}', '{secret}', '{name}', '{email}', '{password}')""")
    con.commit()
    return {"error": None, "secret": secret}

def emailcode(email_code, secret):
    # check if the secret exists in the database
    res = cur.execute(f"SELECT * FROM email_code WHERE secret = '{secret}'")
    user = res.fetchone()
    if user is None:
        return {"error":"Secret not found in the database", "login": True}
    # check if the email_code matches
    if user[0] != email_code:
        # remove email code from database
        cur.execute(f"DELETE FROM email_code WHERE secret = '{secret}'")
        con.commit()
        return {"error":"Incorrect email verification code", "login": True}
    # remove email code from database
    cur.execute(f"DELETE FROM email_code WHERE email = '{user[3]}'")
    con.commit()
    # create enter in user database
    cur.execute(f"""INSERT INTO user VALUES
                    ('{user[2]}', '{user[3]}', '{bcrypt.hashpw(user[4].encode(), bcrypt.gensalt()).decode()}')""")
    con.commit()
    # login user
    return login(user[3], user[4])

def send_email_code(name, email, email_code):
    contents = [f'Hi, {name}! Here is your email verification code: {email_code}']
    yag.send(email, 'Infrascan Email Verification Code', contents)
    return True

def is_valid_name(name):
    if len(name) > 20:
        return False
    for char in name:
        if not char in VALID_NAME_CHARS:
            return False
    return True

# cur.execute("DROP TABLE email_code")
# cur.execute("CREATE TABLE email_code(code, secret, name, email, password)")
# cur.execute("""
#     INSERT INTO user VALUES
#         ('Daniel Morgan', 'danielrmorgan11@gmail.com', 'password'),
#         ('Morgan Daniel', 'danielrmorgan12@gmail.com', 'password1')
# """)
# con.commit()

# res = cur.execute("SELECT * FROM user WHERE name = 'Daniel Morgan'")
# print(res.fetchall())