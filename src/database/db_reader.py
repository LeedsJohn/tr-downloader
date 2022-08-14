"""
John Leeds
db_reader.py
8/8/2022

Read from database for Type Racer Predictions
"""
import sqlite3

class Reader:
    def __init__(self):
        self.con = sqlite3.connect('../data/database.db')
        self.cur = self.con.cursor()

    def getUserID(self, username):
        """
        Receives a username
        Returns that user's ID
        Returns -1 if the username is not associated with an ID
        """
        username = username.lower()
        query = """SELECT rowid FROM users
                   WHERE username = ?;"""
        res = self.cur.execute(query, [username]).fetchone()
        if res:
            return res[0]
        return -1
    
    def getWord(self, s, uid):
        return self.getSegment("words", s, uid)

    def getChar_pairs(self, s, uid):
        return self.getSegment("char_pairs", s, uid)

    def getChars(self, s, uid):
        return self.getSegment("chars", s, uid)

    def getSegment(self, table, s, uid):
        typeOfSegment = table[:-1]
        query = f"""SELECT * FROM {table}
                   WHERE user_id = ? AND {typeOfSegment} = ?;"""
        res = self.cur.execute(query, [uid, s]).fetchone()
        if res:
            return res
        return -1
