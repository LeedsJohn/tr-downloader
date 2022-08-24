"""
John Leeds
process_lists.py
8/10/2022

Script to handle changing text between a list and text
"""
# how much data to store
MAX_WORD = 1000
MAX_CP = 2500
MAX_CHAR = 10000
# ----------------------
I_SPL = chr(8592) # inner split - leftward arrow
O_SPL = chr(8593) # outer split - upward arrow
W_SPL = chr(8595) # word split - downward arrow

def toString(l, raceNums = False):
    if not l:
        return ""
    if raceNums:
        log = [[str(c) for c in e] for e in l]
        log = [I_SPL.join(e) for e in log]
        return O_SPL.join(log)

    for i in range(len(l)):
        l[i][1] = [str(e) for e in l[i][1]]
    log = [[str(e[0]), W_SPL.join(e[1]), e[2]] for e in l] # split words
    log = [I_SPL.join(e) for e in log]
    return O_SPL.join(log)

def toList(s, raceNums = False):
    if not s:
        return []
    if raceNums:
        log = s.split(O_SPL)
        log = [e.split(I_SPL) for e in log]
        return [[int(n) for n in e] for e in log]
    log = s.split(O_SPL)
    log = [e.split(I_SPL) for e in log]
    log = [[e[0], e[1].split(W_SPL), e[2]] for e in log]
    return [[int(e[0]), [int(n) for n in e[1]], e[2]] for e in log]

def splitTimes(nums):
    nums = [str(n) for n in nums]
    return O_SPL.join(nums)

def listTimes(times):
    nums = times.split(O_SPL)
    return [int(n) for n in nums]

def sumTimes(t1, t2):
    if not t1 or t1 == "0":
        return t2
    if not t2 or t2 == "0":
        return t1
    t1, t2 = listTimes(t1), listTimes(t2)
    for i in range(len(t2)):
        t1[i] += t2[i]
    return splitTimes(t1)

def addToLog(log, dataType, newEntry):
    """
    Inserts an entry into the log
    log: string copy of the log
    dataType: "word", "char_pair", or "char"
    newEntry: to be inserted in the form
        [race index, ms, "+" for added or "-" for typo]

    returns [newLog, typed deleted (ms), typo deleted (ms),
             difference in number of typed chars, typo dif] 
    """
    def combine(add, sub):
        for i in range(4):
            if i < 2:
                a = len(add[i])
                b = len(sub[i])
                if a < b:
                    add[i] += [0] * (b - a)
                elif b < a:
                    sub[i] += [0] * (a - b)
                for j in range(len(add[i])):
                    add[i][j] += sub[i][j]
            else:
                add[i] += sub[i]
        add[0] = splitTimes(add[0])
        add[1] = splitTimes(add[1])
        return add
    lengthMap = {"word": MAX_WORD, "char_pair": MAX_CP, "char": MAX_CHAR}
    length = lengthMap[dataType]
    log = toList(log)
    added = [newEntry[1], [], 1, 0]
    if newEntry[2] == "-":
        added = [[], newEntry[1], 0, 1]
    removed = [[], [], 0, 0]
    if len(log) == length:
        if log[-1][0] <= newEntry[0]:
            # if the log is max length and there is an older entry than the new
            deleted = log.pop()
            if deleted[2] == "+":
                removed = [[-n for n in deleted[1]], [], -1, 0]
            else:
                removed = [[], [-n for n in deleted[1]], 0, -1]
        else:
            # log is full of more recent entries
            added = [[], [], 0, 0]
            return [toString(log)] + combine(added, removed)
    # handle edge cases to avoid index out of bounds
    if log[-1][0] > newEntry[0]:
        log.append(newEntry)
        return [toString(log)] + combine(added, removed)
    if log[0][0] <= newEntry[0]:
        log.insert(0, newEntry)
        return [toString(log)] + combine(added, removed)
    # binary search to insert in sorted order
    l, r = 0, len(log) - 1
    while l <= r:
        m = (l + r) // 2
        if log[m + 1][0] <= newEntry[0] < log[m][0]:
            log.insert(m + 1, newEntry)
            return [toString(log)] + combine(added, removed)
        if newEntry[0] < log[m][0]:
            l = m + 1
        else:
            r = m - 1
     
    return [toString(log)] + combine(added, removed)

def numInRaces(races, num):
    races = toList(races, True)
    if not races or num < races[0][0] or num > races[-1][1]:
        return False
    l, r = 0, len(races) - 1
    while l <= r:
        m = (l + r) // 2
        if races[m][0] <= num <= races[m][1]:
            return True
        if races[m][1] < num:
            l = m + 1
        else:
            r = m - 1
    return False

def addToRaces(races, num):
    if not races:
        return toString([[num, num]], True)
    if numInRaces(races, num):
        return races
    races = toList(races, True)
    if not races:
        return toString([[num, num]], True)
    if num > races[-1][1]:
        if num == races[-1][1] + 1:
            races[-1][1] += 1
        else:
            races.append([num, num])
        return toString(races, True)
    if num < races[0][0]:
        if num == races[0][0] - 1:
            races[0][0] -= 1
        else:
            races.insert(0, [num, num])
        return toString(races, True)
    
    l, r = 0, len(races) - 1
    while l <= r:
        m = (l + r) // 2
        if races[m][1] < num < races[m + 1][0]:
            if races[m][1] + 1 == races[m + 1][0] - 1: # merge entries
                races[m][1] = races[m + 1][1]
                del races[m + 1]
            elif num > races[m][1] + 1 and num < races[m + 1][0] - 1: # new entry
                races.insert(m + 1, [num, num])
            elif num == races[m][1] + 1:
                races[m][1] += 1
            else:
                races[m + 1][0] -= 1
            return toString(races, True)
        if races[m][1] < num:
            l = m + 1
        else:
            r = m - 1
