import sqlite3
import sys
con = sqlite3.connect("../data/user.sqlite", check_same_thread=False)
cur = con.cursor()

res = cur.execute("SELECT * FROM user")

if res.rowcount == 0:
    print("Error:\n\tNo users found.")
    quit()

user = res.fetchall()
print("Num users found:", len(user))

for u in user:
    print("User name:", u[0])
    print("\tEmail:", u[1])
