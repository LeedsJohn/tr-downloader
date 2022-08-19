"""
John Leeds
add_race.py
8/8/2022

Function to download a race and add it to the database
"""
import time
from downloader.downloader import Downloader
from database.db_writer import Writer
from database.db_reader import Reader

def addRace(username, text, log, num, avoidDuplicates = True):
    writer = Writer()
    writer.con.isolation_level = None
    writer.cur.execute("begin")
    reader = Reader()
    if avoidDuplicates and reader.completedRace(username, num):
        writer.con.close()
        reader.con.close()
        print("already added")
        return False
    writer.incrementRacecount(username)
    writer.addRaceNum(username, num)
    uid = reader.getUserID(username)
    addChars(uid, text, log, num, writer, reader)
    addCPs(uid, text, log, num, writer, reader)
    addWords(uid, text, log, num, writer, reader)
    print("added")
    writer.cur.execute("commit")
    writer.con.close()
    reader.con.close()

def addWords(uid, text, log, num, wr, re):
    start = -1
    cur = ""
    i = 1
    for e in log:
        if e[2]:
            cur += e[0]
        else:
            cur = removeTypo(cur, e[0])
        start += 1
        if cur == text[:i]:
            i += 1
            if cur[-1] == " ":
                cur = cur[:-1]
                break
    time = 0
    typo = False
    word = ""
    for e in log[start:]:
        time += e[1]
        if e[2]:
            cur += e[0]
            word += e[0]
        else:
            cur = removeTypo(cur, e[0])
            word = removeTypo(word, e[0])
            typo = True
        if cur == text[:i]:
            if i == len(text) or text[i] == " ":
                wr.updateWords(uid, word, num, time, typo)
                time = 0
                typo = False
                word = ""
            i += 1
    if cur != text:
        print(f" CUR: {cur}\nTEXT: {text}")
        print("\n\nTHERE SOME WHACK STUFF GOING ON\n\n")

def addCPs(uid, text, log, num, wr, re):
    cur = ""
    time = log[0][1] * -1 # Negate start time
    typo = False
    i = 1
    for e in log:
        time += e[1]
        if e[2]:
            cur += e[0]
        else:
            cur = removeTypo(cur, e[0])
            typo = True
        if cur == text[:i]:
            i += 1
            if len(cur) > 1:
                wr.updateChar_pairs(uid, cur[-2:], num, time, typo)
            time = 0
            typo = False

def addChars(uid, text, log, num, wr, re):
    i = 2 
    cur = ""
    start = 0
    # ignore first character
    for e in log:
        if e[2]:
            cur += e[0]
        else:
            cur = removeTypo(cur, e[0])
        start += 1
        if cur == text[0]:
            break

    time = 0
    typo = False
    for e in log[start:]:
        time += e[1]
        if e[2]:
            cur += e[0]
        else:
            cur = removeTypo(cur, e[0])
            typo = True
        if cur == text[:i]:
            wr.updateChars(uid, e[0], num, time, typo)
            i += 1
            time = 0
            typo = False


def removeTypo(typed, remove):
    for i in range(len(typed) - 1, -1, -1):
        if typed[i] == remove:
            return typed[:i] + typed[i + 1:]
    return typed

wr = Writer()
# wr.addUser("poem", "azerty")
dl = Downloader()
# num = 15181 
# info = dl.getInfo("nothisisjohn", num)
# addRace("nothisisjohn", info["text"], info["typedText"], num)
# time.sleep(2.1)
badRaces = [167761]
for race in badRaces:
    print(race)
    info = dl.getInfo("poem", race)
    addRace("poem", info["text"], info["typedText"], race, False)
    time.sleep(2.1)
wr.con.close()
