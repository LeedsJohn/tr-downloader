"""
John Leeds
format_lists.py
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
    log = s.split(O_SPL)
    log = [e.split(I_SPL) for e in log]
    log = [[int(e[0]), int(e[1]), e[2]] for e in log]
    return log

def addToLog(log, dataType, newEntry):
    """
    Inserts an entry into the log
    log: string copy of the log
    dataType: "word", "char_pair", or "char"
    newEntry: to be inserted in the form
        [race index, ms, "+" for added or "-" for typo]

    returns [newLog, typo (bool), ms of deleted character]
    """
    length = {"word": MAX_WORD, "char_pair": MAX_CP, "char": MAX_CHAR}
    log = toList(log)
    if len(log) == length:
        if log[-1][0] <= newEntry[0]:
            # if the log is max length and there is an older entry than the new
            deleted = log.pop()
            old = [False, deleted[1]]
            if deleted[2] == "-":
                old[0] = True
            if log[-1][0] > newEntry[0]:
                # handle adding to end to avoid index out of bounds
                log.append(newEntry)
                return [toString(log), old[0], old[1]]
        else:
            # log is full of more recent entries
            return [toString(log), False, -1]

    # binary search to insert in sorted order
    l, r = 0, length - 1
    while l <= r:
        m = (l + r) // 2
        if log[m + 1][0] <= newEntry[0] < log[m][0]:
            log.insert(m, newEntry)
            return [toString(log), old[0], old[1]]
        if log[m][0] > newEntry[0]:
            l = m + 1
        else:
            r = m - 1
    
    return [toString(log), False, 0]
