"""
John Leeds
remake_db.py
8/17/2002

Script to delete and remake database for tr predictor
"""

import sqlite3
import create_tables as ct

def confirm():
    answer = input("Type 'delete' if you really want to delete the database: ")
    return answer == "delete"

def delete_tables():
    con = sqlite3.connect('../data/database.db')
    cur = con.cursor()
    query = """SELECT name FROM sqlite_master
               WHERE type='table';"""
    res = cur.execute(query)
    for tab in res.fetchall():
        query = f"""DROP TABLE {tab[0]};"""
        cur.execute(query)
    con.close()

def main():
    if not confirm():
        return
    delete_tables()
    ct.makeTables()
    
if __name__ == "__main__":
    main()
