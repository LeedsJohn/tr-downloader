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
    
    def download(self, username, startIndex, endIndex):
        raceLogs = self.openRaceLogs(username)
        raceNum = startIndex
        missingCount = 0
        while raceNum <= endIndex:
            print(f"{'-'*16}\n{raceNum}")
            if str(raceNum) in raceLogs:
                raceNum += 1
                continue
            info = self.getInfo(username, raceNum)
            if info == "Missing":
                missingCount += 1
                raceNum += 1
                if missingCount == 10:
                    # end if 10 consecutive missing races
                    break
            else:
                missingCount = 0

            print(f"Text: {info['text'][:min(100, len(info['text']))]}")
            print(f"Speed: {info['unlagSpeed']}, Accuracy: {info['accuracy']}")
            print(f"{info['date']}")
            raceLogs[raceNum] = info
            if raceNum % 25 == 0:
                self.saveRaceLogs(username, raceLogs)
            raceNum += 1
            time.sleep(2.01)
        self.saveRaceLogs(username, raceLogs)


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
        raceText = soup.find(class_="fullTextStr").text
        raceText = raceText.replace("  ", " ")
        typingLog = self.findTypingLog(soup)
        typingLog = self.formatter.format(raceText, typingLog)
        date = self.findDate(soup)
        textID = self.findTextID(soup)
        time = self.findTime(typingLog)
        accuracy = self.findAccuracy(soup)
        registeredSpeed = self.findRegisteredSpeed(soup)
        unlagSpeed, adjustSpeed = self.findSpeeds(time, len(raceText),
                typingLog[0][1])
        return {"textID": textID, "date": date, "accuracy": accuracy, 
                "registeredSpeed": registeredSpeed, "unlagSpeed": unlagSpeed,
                "adjustSpeed": adjustSpeed, "time": time, "text": raceText,
                "typedText": typingLog}

    def findTypingLog(self, soup):
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
        print(date)
        time = date[4].split(":")
        print(time)
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
