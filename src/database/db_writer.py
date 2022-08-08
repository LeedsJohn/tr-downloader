"""
John Leeds
db_writer.py
8/7/2022

Interface to write to tr predictor database
"""
import sqlite3
import time

class Writer:
    def __init__(self):
        self.con = sqlite3.connect('../../data/database.db')
        self.cur = self.con.cursor()

    def addUser(self, username, layout):
        text = """INSERT INTO users (username, join_date, last_action, layout,
        num_races, num_chars, num_typo, total_time, start_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        vals = [username, int(time.time()), int(time.time()), layout, 0, 0, 0,
                0, 0]
        self.cur.execute(text, vals)
        self.con.commit()
    
    def updateWords(self, uid, word, time, typo = False):
        self.updateStats("words", uid, word, time, typo)

    def updateChar_pairs(self, uid, word, time, typo = False):
        self.updateStats("char_pairs", uid, word, time, typo)

    def updateChars(self, uid, word, time, typo = False):
        self.updateStats("chars", uid, word, time, typo)

    def updateStats(self, table, uid, word, time, typo = False):
        """
        Updates either the words, char_pairs, or chars table
        Adds a new row if necessary, else updates
        """
        col = table[:-1] # the column is equal to the table without the s
        def checkWord(uid, word):
            query = f"""SELECT * FROM {table}
                WHERE user_id = ? AND {col} = ?;"""
            res = self.cur.execute(query, [uid, word])
            return True if res.fetchone() else False
        
        if not checkWord(uid, word):
            query = f"""INSERT INTO {table} (user_id, {col}, num_typed, time,
                       num_typo, typo_time)
                       VALUES (?, ?, ?, ?, ?, ?);"""
            if not typo:
                data = [uid, word, 1, time, 0, 0]
            else:
                data = [uid, word, 0, 0, 1, time]
            self.cur.execute(query, data)
        else:
            data = [time, uid, word]
            if not typo:
                query = f"""UPDATE {table}
                           SET num_typed = num_typed + 1,
                               time = time + ?
                           WHERE user_id = ? AND {col} = ?;"""
            else:
                query = f"""UPDATE {table} 
                           SET num_typo = num_typo + 1,
                               typo_time = typo_time + ?
                           WHERE user_id = ? AND {col} = ?;"""
            self.cur.execute(query, data)
        self.con.commit()

    def updateText(self, text_id, text, time, acc):
        acc = int(acc * 10)
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
