"""
John Leeds
add_race.py
8/8/2022

Function to download a race and add it to the database
"""
import time
import random
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
        print(f"{username} {num} - already added")
        return False
    writer.incrementRacecount(username)
    writer.addRaceNum(username, num)
    uid = reader.getUserID(username)
    addChars(uid, text, log, num, writer, reader)
    addCPs(uid, text, log, num, writer, reader)
    addWords(uid, text, log, num, writer, reader)
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
#         if e[2]:
        cur += e[0]
        word += e[0]
#         else:
#             cur = removeTypo(cur, e[0])
#             word = removeTypo(word, e[0])
#             typo = True
#         if cur == text[:i]:
#             if i == len(text) or text[i] == " ":
#                 wr.updateWords(uid, word, num, time, typo)
#                 time = 0
#                 typo = False
#                 word = ""
#             i += 1
    if cur != text:
        print(num)
        print(f"\n CUR: {cur}\nTEXT: {text}")
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
# wr.addUser("nothisisjohn", "dvorak")
# wr.addUser("professorxwing", "colemak")
dl = Downloader()
    

badRaces = [["professorxwing", 2407], ["poem", 163348]]
badRaces = [["poem", 163348]]
badRaces = [["nothisisjohn", i] for i in range(15263, 15271)]
count = 1
for user, race in badRaces:
    startTime = time.time()
    print(f"{user} - {race}")
    count += 1
    info = dl.getInfo(user, race)
#     addRace(user, info["text"], info["typedText"], race, False)
    sleepTime = max(startTime + 2.32 - time.time(), 0)
    if sleepTime == 0:
        print(f"weird sleep time - {user} {race}")
    else:
        time.sleep(sleepTime)
# maxRace = {"nothisisjohn": 15225, "poem": 168160, "professorxwing": 7171}
# users = ["nothisisjohn", "poem", "professorxwing"]
# endTime = time.time() + 60 * 60
# count = 1
# while time.time() < endTime:
#     startTime = time.time()
#     user = users[count % len(users)]
#     race = random.randrange(maxRace[user] - 5000, maxRace[user])
#     if count % 10 == 0:
#         print(f"{count} {int((endTime - time.time()) / 60)} m")
#     count += 1
#     info = dl.getInfo(user, race)
#     addRace(user, info["text"], info["typedText"], race)
#     sleepTime = max(startTime + 2.32 - time.time(), 0)
#     if sleepTime == 0:
#         print(f"weird sleep time - {user} {race}")
#     else:
#         time.sleep(sleepTime)
wr.con.close()
