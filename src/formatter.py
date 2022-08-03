"""
John Leeds
formatter.py
7/25/2022

Contains class formatter. Converts a race text and typing log into something more usable.
"""
import re
from codecs import decode 

class Formatter:
    def format(self, text, typingLog):
        typingLog = self.removeUnicode(typingLog)
        typingLog = self.splitTypingLog(typingLog)
        typingLog = self.group(typingLog)
        typingLog = self.splitDoubles(typingLog)
        typingLog = self.cropEnd(text[-1], typingLog)
        self.printRace(typingLog)

    def removeUnicode(self, typingLog):
        """
        Unicode gets mangled sometimes - example: 
        https://data.typeracer.com/pit/result?id=|tr:poem|145006
        (\\u00eo)
        This function decodes this to utf-8
        """
        return decode(typingLog, "unicode_escape")


    def splitTypingLog(self, typingLog):
        """
        Takes string typingLog and splits it while accounting for typed / 
        deleted commas.
        """
        splitLog = []
        cur = ""
        for i, c in enumerate(typingLog[:-1]):
            if c != "," or (typingLog[i - 1] in "+-" and\
                    typingLog[i - 1] != typingLog[i - 2]):
                cur += c
            else:
                splitLog.append(cur)
                cur = ""
        splitLog.append(cur + typingLog[-1])
        return splitLog

    def group(self, typingLog):
        """
        Splits the typing log into a list in the format
        [Character typed / deleted, ms, deleted (bool)]
        """
        groupings = []
        prev = ""
        for item in typingLog:
            if not item.isnumeric():
                groupings.append(self.getCharacter(prev, item))
            prev = item
        return groupings

    def getCharacter(self, ms, char):
        """
        Takes the number of ms and raw character information and turns it to
        [character(s) typed, ms, deleted (bool)]
        """
        if not ms.isnumeric():  # TODO check this
            ms == "0"
        ms = int(ms)
        typed = re.search("^\d{1,2}\+", char)
        if typed:
            return [char[typed.span()[1]:], ms, False]
        else:
            return ["".join(re.split("\d{1,2}\-", char)), ms, True]

    def splitDoubles(self, log):
        """
        Splits character sequences that are mashed together.
        Ex: 3+b,124,!!!4+ 5+t!!!,84,3,47,1+h
        https://data.typeracer.com/pit/result?id=|tr:hi_i_am_epic|1138
        """
        newLog = []
        for c in log:
            if re.search(".\d[+-]", c[0]):
                newLog.append([c[0][0] + c[0][-1], c[1], c[2]])
            else:
                newLog.append(c)
        return newLog

    def cropEnd(self, lastChar, log):
        """
        Cuts the last letter from the typing log if there is 
        an extra character typed.
        Example: https://data.typeracer.com/pit/result?id=|tr:professorxwing|5942
        """
        i = len(log) - 1
        while i >= 0:
            if lastChar not in log[i][0]:
                log.pop()
            else:
                endIndex = log[i][0].find(lastChar)
                log[i][0] = log[i][0][:endIndex + 1]
                return log
            i -= 1

    def printRace(self, pattern):
        def delChar(text, char):
            for i in range(len(text) - 1, -1, -1):
                if char in text[i]:
                    text[i] = "".join(filter(lambda x: x != char, char))
                    if not text[i]:
                        del text[i]
                    return text

        totalMS = 0
        res = []
        for c in pattern:
            totalMS += c[1]
            if not c[2]:
                print(f"add {c}")
                res.append(c[0])
            else:
                print(f"DELETING {c}")
                for character in c[0]:
                    delChar(res, character)
        stringRes = "".join(res)
        print(stringRes)
        mins = totalMS / 60000
        words = len(stringRes) / 5
        print(f"words: {words}\nmins: {mins}\nWPM: {round(words / mins, 2)}")
