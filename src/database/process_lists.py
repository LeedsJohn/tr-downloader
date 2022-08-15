"""
John Leeds
process_lists.py
8/10/2022

Script to handle changing text between a list and text
"""
# how much data to store
MAX_WORD = 50
MAX_CP = 100
MAX_CHAR = 500
# ----------------------
I_SPL = chr(8592) # inner split - leftward arrow
O_SPL = chr(8593) # outer split - upward arrow

        
def toString(l):
    log = [[str(c) for c in e] for e in l]
    log = [I_SPL.join(e) for e in log]
    log = O_SPL.join(log)
    return log

def toList(s):
    if not s:
        return []
    def toInt(c):
        if c.isnumeric():
            return int(c)
        return c
    log = s.split(O_SPL)
    log = [e.split(I_SPL) for e in log]
    log = [[toInt(c) for i, c in enumerate(e) if i <= 3] for e in log]
    if not log[0][0]:
        return []
    return log

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
            add[i] += sub[i]
        return add

    lengthMap = {"word": MAX_WORD, "char_pair": MAX_CP, "char": MAX_CHAR}
    length = lengthMap[dataType]
    log = toList(log)
    added = [newEntry[1], 0, 1, 0]
    if newEntry[2] == "-":
        added = [0, newEntry[1], 0, 1]
    removed = [0, 0, 0, 0]
    if len(log) == length:
        if log[-1][0] <= newEntry[0]:
            # if the log is max length and there is an older entry than the new
            deleted = log.pop()
            if deleted[2] == "+":
                removed = [-deleted[1], 0, -1, 0]
            else:
                removed = [0, -deleted[1], 0, -1]
        else:
            # log is full of more recent entries
            added = [0, 0, 0, 0]
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
    races = toList(races)
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
        return toString([[num, num]])
    if numInRaces(races, num):
        return races
    races = toList(races)
    if not races:
        return toString([[num, num]])
    if num > races[-1][1]:
        if num == races[-1][1] + 1:
            races[-1][1] += 1
        else:
            races.append([num, num])
        return toString(races)
    if num < races[0][0]:
        if num == races[0][0] - 1:
            races[0][0] -= 1
        else:
            races.insert(0, [num, num])
        return toString(races)
    
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
            return toString(races)
        if races[m][1] < num:
            l = m + 1
        else:
            r = m - 1
