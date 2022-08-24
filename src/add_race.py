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

def getGlobalStats(log):
    """
    Returns [start time, num_chars, num_typo, type_time, typo_time]
    """
    num_chars, num_typo, type_time, typo_time = 0, 0, 0, 0
    if log[0][2] == 0:
        num_typo = 1
    else:
        num_chars = 1
    start_time = log[0][1]
    for e in log[1:]:
        if e[2] == 0:
            if e[0] == " ":
                print(f"TYPO!!! - {e}")
            num_typo += 1
            typo_time += e[1]
        else:
            num_chars += 1
            type_time += e[1]
    return [start_time, num_chars, num_typo, type_time, typo_time]
    
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
    
    stats = getGlobalStats(log)
    writer.incrementGlobalStats(username, stats[1], stats[2], stats[3],
            stats[4], stats[0])
    writer.addRaceNum(username, num)
    uid = reader.getUserID(username)
    word = None
    countingWord = False
    for i, entry in enumerate(log[1:], start = 1):
        typo = False if entry[2] else True 
        cp = log[i - 1][0] + entry[0]
        if word and entry[0] != " ":
            word[0] += entry[0]
            word[1].append(entry[1])
            if not entry[2]:
                word[2] = True
        writer.updateChars(uid, entry[0], num, [entry[1]], typo)
        writer.updateChar_pairs(uid, cp, num, [entry[1]], typo)
        if entry[0] == " " or i + 1 == len(log):
            if word:
                writer.updateWords(uid, word[0], num, word[1], word[2])
            word = [" ", [entry[1]], typo]

    writer.cur.execute("commit")
    writer.con.close()
    reader.con.close()

wr = Writer()
rd = Reader()
# wr.addUser("poem", "azerty")
wr.addUser("nothisisjohn", "dvorak")
# wr.addUser("professorxwing", "colemak")
# wr.addUser("flaneur", "qwerty")
wr.addUser("giftedotter", "qwerty")
dl = Downloader()
    
badRaces = None
# badRaces = [["giftedotter", n] for n in range(41838, 41888)]
count = 1
if badRaces:
    for user, race in badRaces:
        startTime = time.time()
        print(f"{user} - {race}") 
        count += 1
        info = dl.getInfo(user, race)
        errors = 0
        for c in info["typingLog"]:
            if not c[2]:
                errors += 1
        if errors >= 20:
            badString = "++++++++\n" * 8
            print(badString)
            print(f"Errors: {errors}")
        addRace(user, info["text"], info["typingLog"], race, False)
        sleepTime = max(startTime + 2.32 - time.time(), 0)
        if sleepTime == 0:
            print(f"weird sleep time - {user} {race}")
        else:
            time.sleep(sleepTime)

maxRace = {"nothisisjohn": 15327, "poem": 168160, "professorxwing": 7171, "flaneur": 39594}
users = ["nothisisjohn", "poem", "professorxwing", "flaneur"]
endTime = 0
endTime = time.time() + 30 * 60
count = 1
race = 15328
while time.time() < endTime:
    startTime = time.time()
#     user = users[count % len(users)]
#     while True:
#         race = random.randrange(maxRace[user] - 5000, maxRace[user])
#         if not rd.completedRace(user, race):
#             break
#     if count % 10 == 0:
    user = "nothisisjohn"
    race -= 1
    print(f"{count} {int((endTime - time.time()) / 60)} m {user} {race}")
    count += 1
    infoTime = time.time()
    info = dl.getInfo(user, race)
    infoTime = time.time() - infoTime
    errors = 0
    for c in info["typingLog"]:
        if not c[2]:
            errors += 1
    if errors >= 20:
        badString = "++++++++\n" * 8
        print(badString)
        print(f"{user} {race}")
        print(f"Errors: {errors}")
    addRace(user, info["text"], info["typingLog"], race)
    sleepTime = max(startTime + 2.15 - time.time(), 0)
    if sleepTime == 0:
        print(f"weird sleep time - {user} {race}")
        print(f"download time: {infoTime}")
    else:
        time.sleep(sleepTime)
wr.con.close()
rd.con.close()
