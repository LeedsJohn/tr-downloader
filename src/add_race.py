"""
John Leeds
add_race.py
8/8/2022

Function to download a race and add it to the database
"""
from downloader.downloader import Downloader
from database.db_writer import Writer
from database.db_reader import Reader

# def addRace(username, num):
#     dl = Downloader()
#     writer = Writer()
#     reader = Reader()
#     info = dl.getInfo(username, num)
#     uid = reader.getUserID(username)
#     print(uid)
#     writer.addRace(uid, num, info["textID"], info["date"],
#             info["registeredSpeed"], info["unlagSpeed"], info["adjustSpeed"],
#             info["accuracy"], info["typedText"])
#     writer.con.close()
#     reader.con.close()

def addRace(username, text, log, num):
    writer = Writer()
    reader = Reader()
    uid = reader.getUserID(username)
    addChars(uid, text, log, num, writer, reader)

def addChars(uid, text, log, num, wr, re):
    i = 2 
    cur = ""
    # ignore first character
    for e in log:
        if e[2]:
            cur += e[0]
        else:
            cur = removeTypo(cur, e[0])
        del log[0]
        if cur == text[0]:
            break

    time = 0
    typo = False
    for e in log:
        print(e)
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

dl = Downloader()
info = dl.getInfo("nothisisjohn", 15181)
text = "Scissors cuts paper. Paper covers rock. Rock crushes lizard. Lizard poisons Spock. Spock smashes scissors. Scissors decapitates lizard. Lizard eats paper. Paper disproves Spock. Spock vaporizes rock. And as it always has, rock crushes scissors."
addRace("nothisisjohn", text, info["typedText"], 15181)
