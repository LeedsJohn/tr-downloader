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
import re
from codecs import decode 

class Formatter:
    def format(self, text, oldLog, newLog):
        oldLog = self.getTimings(oldLog)
        newLog = self.removeUnicode(newLog)
        newLog = self.splitTypingLog(newLog)
        log = self.addTypos(oldLog, newLog)
#         print(log)
#         print("--------------------------")
#         for c in log:
#             if c[2]:
#                 print(c[0], end = "")
#             else:
#                 print(f"\n|{c[0]}|")
#         print("--------------------------\n")
        return log
#         typingLog = self.group(typingLog, text)
#         typingLog = self.cropEnd(text[-1], typingLog)
#         typingLog = self.addTypos(text, typingLog)
#         return typingLog

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
        
        if i == len(oldLog):
            print("GOOD")
        else:
            print("BAD!")
        return oldLog

    def group(self, typingLog, text):
        """
        Splits the typing log into a list in the format
        [Character typed / deleted, ms, deleted (bool)]
        """
        def getNumActions(entry):
            # Count how many actions there are in one entry
            length = len(entry)
            num = 0
            for i, c in enumerate(entry[1:]):
                if c in "-+" and entry[i] not in "-+$":
                    num += 1
                elif c == "$" and entry[i] not in "-+$":
                    num += 2
            return num 
        def getMSPerKey(ms, entry):
            ms = int(ms)
            numActions = getNumActions(entry)
            msL = [ms // numActions] * numActions
            total = msL[0] * numActions
            i = 0
            while total < ms:
                msL[i] += 1
                i += 1
                total += 1
            return msL 
        def checkWord(curWord, goalWord):
            if len(curWord) < len(goalWord):
                return False
            i = 0
            for goal in goalWord:
                if curWord[i][0] != goal:
                    return False
                i += 1 
            return True
        def removeTypo(curWord, typo):
            for i in range(len(curWord) - 1, -1, -1):
                if curWord[i][0] == typo:
                    del curWord[i]
                    return curWord
            return curWord

        words = [w + " " for w in text.split()]
        words[-1] = words[-1][:-1]
        words.append("")
        groupings = []
        curWord = []
        goalWord = words.pop(0)
        ms = ""
        for item in typingLog:
            if not item.isnumeric():
                msPerKey = getMSPerKey(ms, item)
                newEntry = self.getCharacters(msPerKey, item, curWord)
                for c in newEntry:
                    wordIndex = c[3]
                    del c[3]
                    if c[2]:
                        if wordIndex != -1:
                            insertIndex = curWord[c[-1]][1] - 1
                            print(f"INSERTINDEX: {insertIndex} - WORDINDEX: {wordIndex}")
                            curWord.insert(wordIndex, [c[0], wordIndex])
                            groupings.insert(insertIndex, c)
                            print(f"\n{groupings[-30:]}\n")
                        else:
                            curWord.append([c[0], len(groupings)])
                            groupings.append(c)
                    else:
                        groupings.append(c) 
                        removeTypo(curWord, c[0])
                if checkWord(curWord, goalWord): 
                    curWord = curWord[len(goalWord):]
                    goalWord = words.pop(0)
            ms = item

        return groupings

    def getCharacters(self, ms, entry, curWord):
        """
        Takes the number of ms and raw character information and turns it to
        [character(s) typed, ms, typed/deleted (1/0), -1 if the char is in
        order, else the index that it should be inserted]
        NOTE: Highlighting one character and replacing it looks weird
        (ex: view-source:https://data.typeracer.com/pit/result?id=|tr:hi_i_am_epic|1140)
        "1$l"
        I am assuming this to mean delete the last character and add the letter
        after the $. This will not break if the player highlights a character
        that is not the most recently typed one, but that is so stupid that
        I am not going to account for it right now.
        This special case is indicated by the 0th index being "*#*"
        """
        print(f"{ms} - |{entry}| - {curWord}")
        def getIndex(e, i):
            index = ""
            while i >= 0 and e[i].isnumeric():
                index = e[i] + index
                i -= 1
            return int(index)
        i = 0
        res = []
        end = []
        length = len(entry)
        numDeleted = 0
        while i < length:
            if entry[i] == "+":
                wordIndex = getIndex(entry, i - 1)
                if wordIndex + 1 == len(curWord) and "--" not in entry and "+-" not in entry:
                    end.append([entry[i + 1], ms.pop(), 1, -1])
                elif wordIndex < len(curWord):
                    res.append([entry[i + 1], ms.pop(), 1, wordIndex])
                else:
                    res.append([entry[i + 1], ms.pop(), 1, -1])
                i += 2
            elif entry[i] == "-":
                res.append([entry[i + 1], ms.pop(), 0, -1])
                numDeleted += 1
                i += 2
            elif entry[i] == "$":
                replacedChar = curWord[getIndex(entry, i - 1) + numDeleted]
                end.append([entry[i + 1], ms.pop(), 1, -1])
                res.append([replacedChar, ms.pop(), 0, -1])
                i += 2
            else:
                i += 1
        res += end
        print(f"{res}\n{'-'*16}\n")
        return res

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

    def addTyposOLD(self, text, log):
        """
        Adds in the typo indicator to each entry
        1 if the character was properly typed / deleted
        0 if the character should not have been typed / deleted
        """
        text = list(text)
        typed = []
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

        for i, c in enumerate(log):
            if c[2]:
                typed.append(c[0])
                log[i].append(1 if typed == text[:len(typed)] else 0)
            else:
                log[i].append(1 if typed != text[:len(typed)] else 0)
                for character in c[0]:
                    delChar(typed, character)
        return log

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
