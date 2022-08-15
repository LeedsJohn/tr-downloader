"""
John Leeds
db_writer.py
8/7/2022

Interface to write to tr predictor database
"""
import sqlite3
import time
import database.process_lists as pl

class Writer:
    def __init__(self):
        self.con = sqlite3.connect('../data/database.db')
        self.cur = self.con.cursor()

    def addUser(self, username, layout):
        username, layout = username.lower(), layout.lower()
        text = """INSERT INTO users (username, join_date, last_action, layout,
        num_races, num_chars, num_typo, total_time, start_time, downloaded)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        vals = [username, int(time.time()), int(time.time()), layout, 0, 0, 0,
                0, 0, -1]
        self.cur.execute(text, vals)
        self.con.commit()
    
    def addRaceNum(self, username, num):
        username = username.lower()
        def getOldRaces():
            query = """SELECT downloaded FROM users
                       WHERE username = ?"""
            res = self.cur.execute(query, [username]).fetchone()
            if res:
                return res[0]
        newRaces = pl.addToRaces(getOldRaces(), num)
        query = """UPDATE users
                   SET downloaded = ?
                   WHERE username = ?"""
        self.cur.execute(query, [newRaces, username])
        self.con.commit()

    def updateWords(self, uid, word, race_index, time, typo = False):
        self.updateStats("words", uid, word, race_index, time, typo)

    def updateChar_pairs(self, uid, word, race_index, time, typo = False):
        self.updateStats("char_pairs", uid, word, race_index, time, typo)

    def updateChars(self, uid, word, race_index, time, typo = False):
        self.updateStats("chars", uid, word, race_index, time, typo)

    def updateStats(self, table, uid, word, race_index, time, typo = False):
        """
        Updates either the words, char_pairs, or chars table
        Adds a new row if necessary, else updates
        """
        col = table[:-1] # the column is equal to the table without the s
        entry = [race_index, time, "+"]
        if typo:
            entry[2] = "-"

        def getEntry(uid, word):
            query = f"""SELECT * FROM {table}
                WHERE user_id = ? AND {col} = ?;"""
            res = self.cur.execute(query, [uid, word])
            return res.fetchone()
        
        oldRow = getEntry(uid, word)
        if not oldRow:
            query = f"""INSERT INTO {table} (user_id, {col}, num_typed, time,
                       num_typo, typo_time, log)
                       VALUES (?, ?, ?, ?, ?, ?, ?);"""
            if not typo:
                data = [uid, word, 1, time, 0, 0, pl.toString([entry])]
            else:
                data = [uid, word, 0, 0, 1, time, pl.toString([entry])]
            self.cur.execute(query, data)
            self.con.commit()
            return
        
        data = pl.addToLog(oldRow[6], col, entry)
        query = f"""UPDATE {table}
                    SET num_typed = num_typed + ?,
                        time = time + ?,
                        num_typo = num_typo + ?,
                        typo_time = typo_time + ?,
                        log = ?
                    WHERE user_id = ? AND {col} = ?;"""
        data = [data[3], data[1], data[4], data[2], data[0], uid, word]
        self.cur.execute(query, data)
        self.con.commit()
                            
    def updateText(self, text_id, text, time, acc):
        acc = int(acc * 1000)
        def checkText(text_id):
            query = """SELECT * from texts
                       WHERE text_id = ?;"""
            res = self.cur.execute(query, [text_id])
            return True if res.fetchone() else False
        if not checkText(text_id):
            query = """INSERT INTO texts
            (text_id, text, num_typed, total_time, total_acc)
            VALUES (?, ?, ?, ?, ?);"""
            self.cur.execute(query, [text_id, text, 1, time, acc])
        else:
            query = """UPDATE texts
                       SET num_typed = num_typed + 1,
                           total_time = total_time + ?,
                           total_acc = total_acc + ?
                        WHERE text_id = ?;"""
            self.cur.execute(query, [time, acc, text_id])
        self.con.commit()

    def addRace(self, uid, race_index, text_id, date, registered, unlagged,
            adjusted, acc, log):
        def formatLog(log):
            # turn log into string
            # split inner lists with leftwards arrow, outer with up arrow
            log = [[str(c) for c in e] for e in log]
            log = [chr(8592).join(e) for e in log]
            log = chr(8593).join(log)
            return log

        query = """INSERT INTO races
                   (user_id, race_index, text_id, date, registered, unlagged,
                   adjusted, acc, typing_log)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        log = formatLog(log)
        data = [uid, race_index, text_id, date, registered, unlagged, adjusted,
                acc, log]
        self.cur.execute(query, data)
        self.con.commit()
