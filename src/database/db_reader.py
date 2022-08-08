"""
John Leeds
db_reader.py
8/8/2022

Read from database for Type Racer Predictions
"""

class Reader:
    def __init__(self):
        self.con = sqlite3.connect('../../data/database.db')
        self.cur = self.con.cursor()

    def getUserID(self, username):
        """
        Receives a username
        Returns that user's ID
        Returns -1 if the username is not associated with an ID
        """
        query = """SELECT rowid FROM users
                   WHERE username = ?;"""
        return self.cur.execute(query, [username]).fetchone()
    
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
        return self.cur.execute(query, [uid, s]).fetchone()
    
    def getRace(self, uid, race_index):
        query = """SELECT * FROM races
                   WHERE user_id = ? AND race_index = ?;"""
        return self.cur.execute(query, [uid, race_index]).fetchone()

    def getText(self, textID):
        query = """SELECT * FROM texts
                   WHERE text_id = ?;"""
        return self.cur.execute(query, [textID]).fetchone()
