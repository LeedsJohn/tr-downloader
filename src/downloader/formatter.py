"""
John Leeds
formatter.py
7/25/2022

Contains class formatter. Converts a race text and typing log into something more usable.
Format of typing log:
    [[char(s) typed, ms, typed / deleted, typo], ...]
    Index 2 will be 1 if the character was typed, 0 if deleted
    Index 3 will be 1 if the stroke was correct, 0 if it was a typo
"""
from codecs import decode 

class Formatter:
    def format(self, oldLog, newLog):
        oldLog = self.getTimings(oldLog)
        newLog = self.removeUnicode(newLog)
        newLog = self.splitTypingLog(newLog)
        log = self.addTypos(oldLog, newLog)
        return log

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
        splitLog = typingLog.split(",")
        i = 1
        while i < len(splitLog):
            if not splitLog[i]:
                # empty list indicates comma
                splitLog[i - 1] += ","
                del splitLog[i]
            elif not splitLog[i - 1].isnumeric() and not splitLog[i].isnumeric():
                # two non numbers means it was split down the middle
                splitLog[i - 1] += f",{splitLog[i]}"
                del splitLog[i]
            elif splitLog[i].isnumeric() and splitLog[i - 1].isnumeric():
                # two integers in a row indicates a character count mark
                del splitLog[i - 1:i + 1]
            else:
                i += 1
        return splitLog
    
    def getTimings(self, oldLog):
        log = []
        num = ""
        # TODO is there a better way to handle special cases? (nums, apostrophes)
        for i, c in enumerate(oldLog):
            if len(log) >= 2 and log[-2][0] == "\\" and log[-1][0] == "b":
                del log[-2:]
                log.append([c])
                num = ""
            elif c == '"': # " is escaped with a \
                log[-1] == '"'
                num = ""
            elif not c.isnumeric():
                if num:
                    log[-1].append(int(num))
                log.append([c])
                num = ""
            else:
                num += c 
        log[-1].append(int(num))
        return log

    def addTypos(self, oldLog, newLog):
        cumOldLog = [oldLog[0][1]]
        for _, t in oldLog[1:]:
            cumOldLog.append(cumOldLog[-1] + t)
        splitNewLog = []
        for entry in newLog:
            added = False
            cur = ""
            for c in entry:
                cur += c
                if len(cur) >= 2 and cur[-2] == "+":
                    splitNewLog.append(cur)
                    cur = ""
            if cur:
                splitNewLog.append(cur)
        newSum = 0
        oldLogIndex = 0
        typo = False
        i = 0
        for c in splitNewLog:
            if c.isnumeric():
                newSum += int(c)
                continue
            if newSum == cumOldLog[i]:
                oldLog[i].append(0 if typo else 1)
                typo = False
                i += 1
                if i == len(cumOldLog): # prevent errors from extra characters in old log
                    break
            elif newSum > cumOldLog[i]:
                while newSum > cumOldLog[i]:
                    oldLog[i].append(0)
                    i += 1
                typo = False
            else:
                typo = True
        
        return oldLog

    def printRace(self, pattern):
        def delChar(text, char):
            for i in range(len(text) - 1, -1, -1):
                if char in text[i]:
                    if len(text[i]) != 1:
                        index = text[i].rfind(char)
                        if index == 0:
                            text[i] = text[i][1:]
                        elif index == len(text[i]) - 1:
                            text[i] = text[i][:-1]
                        else:
                            text[i] = text[i][:i] + text[i][i + 1:]
                    else: 
                        del text[i]
                    return
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
