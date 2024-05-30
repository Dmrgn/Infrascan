import sqlite3
import sys
con = sqlite3.connect("../data/user.sqlite", check_same_thread=False)
cur = con.cursor()

res = cur.execute("SELECT * FROM user WHERE email = (?)", (sys.argv[1],))

user = res.fetchone()

print(user)