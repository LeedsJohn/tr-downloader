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
    word = ["", 0, False]
    countingWord = False
    for i, entry in enumerate(log[1:], start = 1):
        typo = False if entry[2] else True 
        cp = log[i - 1][0] + entry[0]
        if word[0] and entry[0] != " ":
            word[0] += entry[0]
            word[1] += entry[1]
            if not entry[2]:
                word[2] = True
        writer.updateChars(uid, entry[0], num, entry[1], typo)
        writer.updateChar_pairs(uid, cp, num, entry[1], typo)
        if entry[0] == " " or i + 1 == len(log):
            writer.updateWords(uid, word[0], num, word[1], word[2])
            word = [" ", entry[1], typo]

    writer.cur.execute("commit")
    writer.con.close()
    reader.con.close()

wr = Writer()
# wr.addUser("poem", "azerty")
# wr.addUser("nothisisjohn", "dvorak")
# wr.addUser("professorxwing", "colemak")
dl = Downloader()
    

badRaces = [["poem", 163523]]
count = 1
for user, race in badRaces:
    startTime = time.time()
    print(f"{user} - {race}", end=" | ")
    count += 1
    info = dl.getInfo(user, race)
    errors = 0
    for c in info["typedText"]:
        if not c[2]:
            errors += 1
    print(f"Errors: {errors}")
    addRace(user, info["text"], info["typedText"], race, False)
    sleepTime = max(startTime + 2.32 - time.time(), 0)
    if sleepTime == 0:
        print(f"weird sleep time - {user} {race}")
    else:
        time.sleep(sleepTime)

# maxRace = {"nothisisjohn": 15225, "poem": 168160, "professorxwing": 7171}
# users = ["nothisisjohn", "poem", "professorxwing"]
# endTime = time.time() + 0.51 * 60
# count = 1
# while time.time() < endTime:
#     startTime = time.time()
#     user = users[count % len(users)]
#     race = random.randrange(maxRace[user] - 5000, maxRace[user])
#     if count % 1 == 0:
#         print(f"{count} {int((endTime - time.time()) / 60)} m {user} {race}", end = " | ")
#     count += 1
#     info = dl.getInfo(user, race)
#     errors = 0
#     for c in info["typedText"]:
#         if not c[2]:
#             errors += 1
#     print(f"Errors: {errors}")
#     addRace(user, info["text"], info["typedText"], race)
#     sleepTime = max(startTime + 2.35 - time.time(), 0)
#     if sleepTime == 0:
#         print(f"weird sleep time - {user} {race}")
#     else:
#         time.sleep(sleepTime)
wr.con.close()
