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
    def format(self, text, typingLog):
        typingLog = self.removeUnicode(typingLog)
        typingLog = self.splitTypingLog(typingLog)
        typingLog = self.group(typingLog)
        typingLog = self.splitDoubles(typingLog)
        typingLog = self.cropEnd(text[-1], typingLog)
        typingLog = self.addTypos(text, typingLog)
        return typingLog
#        self.printRace(typingLog)

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
    
    def group(self, typingLog):
        """
        Splits the typing log into a list in the format
        [Character typed / deleted, ms, deleted (bool)]
        """
        groupings = []
        prev = ""
        for item in typingLog:
            if not item.isnumeric():
                group = self.getCharacter(prev, item)
                if group[0] != "*#*":
                    groupings.append(group)
                else:
                    # highlight + replace - delete last character of previous word
                    group[0] = groupings[-1][0][-1]
                    groupings.append(group[:3])
                    groupings.append(group[3:])
            prev = item
        return groupings

    def getCharacter(self, ms, char):
        """
        Takes the number of ms and raw character information and turns it to
        [character(s) typed, ms, typed/deleted (1/0)]
        NOTE: Highlighting one character and replacing it looks weird
        (ex: view-source:https://data.typeracer.com/pit/result?id=|tr:hi_i_am_epic|1140)
        "1$l"
        I am assuming this to mean delete the last character and add the letter
        after the $. This will not break if the player highlights a character
        that is not the most recently typed one, but that is so stupid that
        I am not going to account for it right now.
        This special case is indicated by the 0th index being "*#*"
        """
        if not ms.isnumeric():  # TODO check this
            ms == "0"
        ms = int(ms)
        typed = re.search("^\d{1,2}\+", char)
        replace = re.search("^\d{1,2}\$", char)
        if typed:
            return [char[typed.span()[1]:], ms, 1]
        if replace:
            if ms % 2 == 0:
                msDel, msAdd = ms // 2, ms // 2
            else:
                msDel, msAdd = (ms // 2 + 1), ms // 2
            return ["*#*", msDel, 0, char[replace.span()[1]:], msAdd, 1]
        else:
            return ["".join(re.split("\d{1,2}\-", char)), ms, 0]

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

    def addTypos(self, text, log):
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
