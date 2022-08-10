"""
John Leeds
add_race.py
8/8/2022

Function to download a race and add it to the database
"""
from downloader.downloader import Downloader
from database.db_writer import Writer
from database.db_reader import Reader

def addRace(username, num):
    dl = Downloader()
    writer = Writer()
    reader = Reader()
    info = dl.getInfo(username, num)
    uid = reader.getUserID(username)
    print(uid)
    writer.addRace(uid, num, info["textID"], info["date"],
            info["registeredSpeed"], info["unlagSpeed"], info["adjustSpeed"],
            info["accuracy"], info["typedText"])
    writer.con.close()
    reader.con.close()

addRace("nothisisjohn", 15052)
