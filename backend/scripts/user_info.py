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

print(user)