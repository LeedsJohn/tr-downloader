"""
John Leeds
Downloader.py
7/25/2022

Contains a class to download TypeRacer races.
"""
import requests
from bs4 import BeautifulSoup


class Downloader:
    def download(self, username, raceIndex):
        """
        Download a Type Racer race
        Returns a list [raceText, typingLog]

        username (str): the username of the player
        raceIndex (int): the index of the race to download
        """
        url = f"https://data.typeracer.com/pit/result?id=|tr:{username}|{raceIndex}"
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        raceText = soup.find(class_="fullTextStr").text
        typingLog = self.findTypingLog(soup)
        return [raceText, typingLog]

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
