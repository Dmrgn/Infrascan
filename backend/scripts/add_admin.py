import sqlite3
import sys
con = sqlite3.connect("../data/user.sqlite", check_same_thread=False)
cur = con.cursor()

res = cur.execute("SELECT * FROM user WHERE email = (?)", (sys.argv[1],))
print("Num users found:",res.rowcount)

if res.rowcount != 1:
    print("Error:\n\tInvalid number of users found.")
    quit()

user = res.fetchone()

print("User name:", user[0])
print("Email:", user[1])
print("Tokens:", user[3])

if user[3] == -1:
    print("Error:\n\tUser is already an admin.")
    quit()

cur.execute("UPDATE user SET tokens = (?) WHERE email = (?)", (-1, user[1]))
con.commit()

print("User is now an admin.")