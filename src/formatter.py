"""
John Leeds
formatter.py
7/25/2022

Contains class formatter. Converts a race text and typing log into something more usable.
"""
import re


class Formatter:
    def format(self, text, typingLog):
        typingLog = self.splitTypingLog(typingLog)
        typingLog = self.group(typingLog)
        typingLog = self.splitDoubles(typingLog)
        self.printRace(typingLog)

    def splitTypingLog(self, typingLog):
        """
        Splits the typing log into a list of [ms, {int}+/-{char}]. There will still be extra characters.
        """
        splitLog = []
        cur = ""
        for i, c in enumerate(typingLog[:-1]):
            if c == "," and typingLog[i + 1] != ",":
                # add in comma if there's no character
                if cur[-1] in "-+" and cur[-2] not in "-+":
                    cur += ","
                splitLog.append(cur)
                cur = ""
            else:
                cur += c
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
        if not ms.isnumeric(): # TODO check this
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

    def printRace(self, pattern):
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
                    index = len(res) - res[::-1].index(character) - 1
                    del res[index]
        stringRes = "".join(res)
        print(stringRes)
        mins = totalMS / 60000
        words = len(stringRes) / 5
        print(f"words: {words}\nmins: {mins}\nWPM: {round(words / mins, 2)}")
