"""
John Leeds
Downloader.py
7/25/2022

Contains a class to download TypeRacer races.
"""
import requests
from bs4 import BeautifulSoup
import formatter as fm

class Downloader:
    def __init__(self):
        self.formatter = fm.Formatter()

    def download(self, username, raceIndex):
        """
        Download a Type Racer race
        Returns a dictionary containing with the following keys:
        date: The date in format {day of the week}, date, Month year, hh:mm:ss
        textID: The ID of the Type Racer text
        text: The text that was typed
        typedText: List in the form ["char typed", ms, add or delete, typo]
            See Formatter.py for more information
        raceNum: The race number of the race
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
        typingLog = self.findTypingLog(soup)
        typingLog = self.formatter.format(raceText, typingLog)
        date = self.findDate(soup)
        textID = self.findTextID(soup)
        time = "UNIMPLEMENTED"
        accuracy = self.findAccuracy(soup)
        registeredSpeed = self.findRegisteredSpeed(soup)
        unlagSpeed = "UNIMPLEMENTED"
        adjustSpeed = "UNIMPLEMENTED"
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
        for td in soup.find_all("td"):
            if prev == "Date":
                return td.text.strip()
            prev = td.text

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
