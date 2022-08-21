"""
John Leeds
Downloader.py
7/25/2022

Contains a class to download TypeRacer races.
"""
import requests
from bs4 import BeautifulSoup
import datetime
import time
import json
import downloader.formatter as fm

class Downloader:
    def __init__(self):
        self.formatter = fm.Formatter()
    
    def getInfo(self, username, raceIndex):
        """
        Download a Type Racer race
        Returns a dictionary containing with the following keys:
        date: The date in format {day of the week}, date, Month year, hh:mm:ss
        textID: The ID of the Type Racer text
        text: The text that was typed
        typedText: List in the form ["char typed", ms, add or delete, typo]
            See Formatter.py for more information
        time: The total amount of time the race took (ms)
        registeredSpeed: The speed registered to Type Racer
        accuracy: The accuracy registered to Type Racer
        unlagSpeed: The true speed of the race without latency
        adjustSpeed: The speed of the race accounting for start time

        Parameters:
            username (str): the username of the player
            raceIndex (int): the index of the race to download
        """
        url = f"https://data.typeracer.com/pit/result?id=|tr:{username}|{raceIndex}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        raceText = self.processRaceText(self.findOldLog(soup))
        newLog = self.findNewLog(soup)
        newLog = self.formatter.format(raceText, self.findOldLog(soup), newLog)
        date = self.findDate(soup)
        textID = self.findTextID(soup)
        time = self.findTime(newLog)
        accuracy = self.findAccuracy(soup)
        registeredSpeed = self.findRegisteredSpeed(soup)
        unlagSpeed, adjustSpeed = self.findSpeeds(time, len(raceText),
                newLog[0][1])

        print(newLog)
        bruh = ""
        for c in newLog:
            bruh += c[0]
        print(bruh)
        print(raceText)
        print(f"DOES RECORDED EQUAL RACETXT? {bruh == raceText}")

        return {"textID": textID, "date": date, "accuracy": accuracy, 
                "registeredSpeed": registeredSpeed, "unlagSpeed": unlagSpeed,
                "adjustSpeed": adjustSpeed, "time": time, "text": raceText,
                "typedText": newLog}

    def processRaceText(self, text):
        raceText = []
        for i, c in enumerate(text):
            if len(raceText) >= 2 and raceText[-2:] == ["\\", "b"]:
                del raceText[-2:]
                raceText.append(c)
            elif not c.isnumeric():
                raceText.append(c)

        return "".join(raceText)

    def findOldLog(self, soup):
        scripts = soup.find_all('script')
        for script in scripts:
            if "var typingLog" in script.text:
                text = script.text
                beginning = 3
                commaCount = 0
                while commaCount < 3:
                    if text[beginning] == ",":
                        commaCount += 1
                    beginning += 1
                end = text.find("|")
                return text[beginning:end]

    def findNewLog(self, soup):
        scripts = soup.find_all('script')
        for script in scripts:
            if "var typingLog" in script.text:
                text = script.text
                beginning = text.find("|") + 1
                end = text.rfind(",")
                return text[beginning:end]

    def findDate(self, soup):
        prev = ""
        date = ""
        for td in soup.find_all("td"):
            if prev == "Date":
                date = td.text.strip()
            prev = td.text
        date = date.split()
        monthToNum = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5,
                      "Jun": 6, "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10,
                      "Nov": 11, "Dec": 12}
        time = date[4].split(":")
        time = [int(t) for t in time]
        return int(datetime.datetime(int(date[3]), monthToNum[date[2]],
            int(date[1]), time[0], time[1], time[2]).timestamp())

    def findTextID(self, soup):
        for link in soup.find_all("a"):
            text = link.get('href')
            if "text_info?id=" in text:
                return int(text[13:])

    def findRegisteredSpeed(self, soup):
        for span in soup.find_all("span"):
            if " WPM" in span.text:
                return int("".join([c for c in span.text if c.isdigit()]))
    
    def findAccuracy(self, soup):
        prev = ""
        for td in soup.find_all("td"):
            if prev == "Accuracy":
                return int("".join([c for c in td.text if c.isdigit()])) / 1000
            prev = td.text

    def findTime(self, log):
        time = 0
        for e in log:
            time += e[1]
        return time

    def findSpeeds(self, time, textLen, firstCharTime):
        """
        Returns a list
        [unlagged speed, adjusted speed]
        """
        def wpm(time, length):
            return (length / 5) / (time / 60000)
        return [round(wpm(time, textLen), 2),
                round(wpm(time - firstCharTime, textLen - 1), 2)]
    
    def openRaceLogs(self, username): 
        try:
            with open(f"{username}.json", "r") as f:
                raceLog = json.load(f)
        except:
            raceLog = {}
        return raceLog

    def saveRaceLogs(self, username, raceLogs):
        with open(f"{username}.json", "w") as f:
            json.dump(raceLogs, f)
