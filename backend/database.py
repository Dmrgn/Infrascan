import sqlite3
import bcrypt
import validate_email
import time
import yagmail
import json

from constants import *
import stats

with open("./data/keys.json") as f:
    data = json.load(f)
    email_password = data["email"]

yag = yagmail.SMTP(EMAIL_ADDRESS, email_password)
con = sqlite3.connect("./data/user.sqlite", check_same_thread=False)
cur = con.cursor()

"""
super users have tokens = -1

user table is (name, email, password, tokens, stats)
session table is (email, secret, session_time)
email_code table is (code, secret, name, email, password)
"""

# TODO: check if device matches list of
# recognized devices for extra security
def validate_user(secret):
    # check database to see if the user is logged in
    res = cur.execute("SELECT * FROM session WHERE secret = (?)", (secret,))
    user = res.fetchone()
    # check if user exists
    if user is None:
        return {"error": "Please login to continue", "login":True}
    email = user[0]
    # check if the session time is valid
    if time.time()-user[2] >= 60*SESSION_LENGTH:
        cur.execute("DELETE FROM session WHERE email = (?)", (email,))
        con.commit()
        return {"error": "Session expired", "login":True} 
    # extend session time
    cur.execute("UPDATE session SET session_time = (?) WHERE email = (?)", (time.time(), email))
    con.commit()
    # user is validated
    return {"error": None, "email": email}

# consumes a token from the user's account
def use_token(secret):
    # make sure user is logged in
    validate_response = validate_user(secret)
    if validate_response["error"] != None:
        return validate_response
    email = validate_response["email"]
    # get user with validated email
    res = cur.execute("SELECT * FROM user WHERE email = (?)", (email,))
    user = res.fetchone()
    # check if there are tokens left
    tokens_left = user[3]
    if tokens_left == 0:
        return {"error":"No tokens remaining"}
    # update stats
    current_stats = stats.get_stats(email)["stats"]
    stats.update_stat(email, "tokens_used", current_stats["tokens_used"]+1)
    # check if super user
    if tokens_left == -1:
        return {"error": None}
    # subtract a token
    cur.execute("UPDATE user SET tokens = (?) WHERE email = (?)", (tokens_left-1, email))
    con.commit()
    return {"error":None, "email":email}

# logs in the user with the specified email + password
def login(email, password, device):
    # check if the email exists
    if not validate_email.validate_email(email.strip()):
        return {"error": "Please enter a valid email address"}
    # find user with specified email
    res = cur.execute("SELECT * FROM user WHERE email = (?)", (email,))
    user = res.fetchone()
    # check if user exists
    if user is None:
        return {"error": "No user was found with the specified email address"}
    # validate the users password
    if not bcrypt.checkpw(password.encode(), user[2].encode()):
        return {"error": "The email address or password is incorrect"}
    res = cur.execute("SELECT * FROM session WHERE email = (?)", (email,))
    session = res.fetchone()
    secret = ""
    if not session is None:
        # update existing session entry
        secret = session[1]
        cur.execute("UPDATE session SET session_time = (?) WHERE email = (?)", (time.time(), email))
        con.commit()
    else:
        # create new session entry
        secret = bcrypt.gensalt().decode()
        cur.execute("INSERT INTO session VALUES (?, ?, ?)", (email, secret, time.time()))
        con.commit()
    # update stats
    current_stats = stats.get_stats(email)["stats"]
    if not device in current_stats["devices"]:
        stats.append_stat(email, "devices", device)
    stats.update_stat(email, "last_login", time.time())
    # return the generated secret
    return {"error": None, "secret": secret, "stats": stats.get_stats(email)["stats"]}

# starts the registration process for a user
def register(name, email, password):
    # check if the name is valid
    if not is_valid_name(name):
        return {"error":"Name is too long or contains invalid characters"}
    # check if the email exists
    if not validate_email.validate_email(email.strip()):
        return {"error": "Please enter a valid email address"}
    # check if the email already exists
    res = cur.execute("SELECT * FROM user WHERE email = (?)", (email,))
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
    cur.execute("INSERT INTO email_code VALUES (?, ?, ?, ?, ?)", (email_code, secret, name, email, password))
    con.commit()
    return {"error": None, "secret": secret}

# confirms the email code provided by a user
# during the registration process
def emailcode(email_code, secret, device):
    # check if the secret exists in the database
    res = cur.execute("SELECT * FROM email_code WHERE secret = (?)", (secret,))
    user = res.fetchone()
    if user is None:
        return {"error":"Secret not found in the database", "login": True}
    # check if the email_code matches
    if user[0] != email_code:
        # remove email code from database
        cur.execute("DELETE FROM email_code WHERE secret = (?)", (secret,))
        con.commit()
        return {"error":"Incorrect email verification code", "login": True}
    email = user[3]
    password = user[4]
    # remove email code from database
    cur.execute("DELETE FROM email_code WHERE email = (?)", (email,))
    con.commit()
    # create enter in user database
    num_tokens = NUM_DEFAULT_TOKENS
    created_stats = stats.create_stats()
    encrypted_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    cur.execute("INSERT INTO user VALUES (?, ?, ?, ?, ?)", (user[2], email, encrypted_password, num_tokens, created_stats))
    con.commit()
    # update stats
    current_stats = stats.get_stats(email)["stats"]
    if not device in current_stats["devices"]:
        stats.append_stat(email, "devices", device)
    # login user
    return login(email, password, device)

# sends an email to the user with
# their email confirmation code
def send_email_code(name, email, email_code):
    contents = [f'Hi, {name}! Here is your email verification code: {email_code}']
    yag.send(email, 'Infrascan Email Verification Code', contents)
    return True

# checks if the user's inputed name is valid
def is_valid_name(name):
    if len(name) > 20:
        return False
    for char in name:
        if not char in VALID_NAME_CHARS:
            return False
    return True

# cur.execute("DROP TABLE user")
# cur.execute("CREATE TABLE user(name, email, password, tokens, stats)")
# cur.execute("CREATE TABLE session(email, secret, session_time)")
# cur.execute("CREATE TABLE email_code(code, secret, name, email, password)")
# cur.execute("""
#     INSERT INTO user VALUES
#         ('Daniel Morgan', 'danielrmorgan11@gmail.com', 'password'),
#         ('Morgan Daniel', 'danielrmorgan12@gmail.com', 'password1')
# """)
# con.commit()

# res = cur.execute("SELECT * FROM user WHERE email = 'danielrmorgan11@gmail.com'")
# print(res.fetchone())

# cur.execute("UPDATE user SET tokens = (?) WHERE email = (?)", (-1, "danielrmorgan11@gmail.com"))
# con.commit()