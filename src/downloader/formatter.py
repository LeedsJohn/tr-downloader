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
        typingLog = self.group(typingLog, text)
#         typingLog = self.splitDoubles(typingLog)
        typingLog = self.cropEnd(text[-1], typingLog)
#         typingLog = self.separate(typingLog)
        typingLog = self.addTypos(text, typingLog)
        return typingLog

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
                groupings += newEntry
                for c in newEntry:
                    if c[2]:
                        curWord.append(c[0])
                    else:
                        if c[0] in curWord:
                            curWord.reverse()
                            curWord.remove(c[0])
                            curWord.reverse()
                if "".join(curWord) == goalWord:
                    goalWord = words.pop(0)
                    curWord = []
            ms = item
        
        return groupings

#         groupings = []
#         prev = ""
#         for item in typingLog:
#             if not item.isnumeric():
#                 group = self.getCharacter(prev, item)
#                 if group[0] != "*#*":
#                     groupings.append(group)
#                 else:
#                     # highlight + replace - delete last character of previous word
#                     group[0] = groupings[-1][0][-1]
#                     groupings.append(group[:3])
#                     groupings.append(group[3:])
#                     print(group)
#                     print(groupings[-10:])
#                     print("---")
#             prev = item
#         return groupings

    def getCharacters(self, ms, entry, curWord):
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
        while i < length:
            if entry[i] == "+":
                res.append([entry[i + 1], ms.pop(), 1])
                i += 2
            elif entry[i] == "-":
                res.append([entry[i + 1], ms.pop(), 0])
                i += 2
            elif entry[i] == "$":
                replacedChar = curWord[getIndex(entry, i - 1)]
                end.append([entry[i + 1], ms.pop(), 1])
                res.append([replacedChar, ms.pop(), 0])
                i += 2
            else:
                i += 1
        res += end
        return res
#         ms = int(ms)
#         typed = re.search("^\d{1,2}\+", char)
#         replace = re.search("^\d{1,2}\$", char)
#         if typed:
#             return [char[typed.span()[1]:], ms, 1]
#         if replace:
#             if ms % 2 == 0:
#                 msDel, msAdd = ms // 2, ms // 2
#             else:
#                 msDel, msAdd = (ms // 2 + 1), ms // 2
#             return ["*#*", msDel, 0, char[replace.span()[1]:], msAdd, 1]
#         else:
#             return ["".join(re.split("\d{1,2}\-", char)), ms, 0]

    def splitDoubles(self, log):
        """
        Splits character sequences that are mashed together.
        Ex: 3+b,124,!!!4+ 5+t!!!,84,3,47,1+h
        https://data.typeracer.com/pit/result?id=|tr:hi_i_am_epic|1138
        Triple split: https://data.typeracer.com/pit/result?id=|tr:nothisisjohn|14785
        (when I type "tearing")
        """
        newLog = []
        for c in log:
            if re.search(".\d[+-]", c[0]):
                chars = c[0][0] # create list of typed characters in the log
                # first character is always typed
                for i, char in enumerate(c[0][1:-1], start = 1):
                    # look add characters that come after a + or -
                    # But not if it is the second character in a row that is
                    # + or - (because that indicates a typed + or -)
                    if char in "+-" and c[0][i - 1] not in "+-":
                        chars += c[0][i + 1]
                newLog.append([chars, c[1], c[2]])
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

    def separate(self, typingLog):
        """
        Separates entries that are combined
        ex: [['es', 77, 1], ...]
                     VVV
            [['e', 77, 1], ['s', 0, 1]]
        """
        newLog = []
        for e in typingLog:
            if len(e[0]) == 1:
                newLog.append(e)
            else:
                extraChars = e[0][1:]
                typed = e[2]
                e[0] = e[0][:1]
                newLog.append(e)
                for c in extraChars:
                    newLog.append([c, 0, typed])
        return newLog

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
