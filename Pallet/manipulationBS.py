'''---------------------------------------
|  Functions to manipulate block scripts  |
----------------------------------------'''

import re

def baseofBlock(blockscript):
    blockscript = re.sub('{[^}]*}', '{}', blockscript)
    readingEntry = {'start': None}
    entryDepth = 0
    deviation = 0
    for loopi, char in enumerate(blockscript):
        if char == '[':
            if entryDepth == 0:
                readingEntry['start'] = loopi + 1
            entryDepth += 1
        elif char == ']':
            if entryDepth == 1:
                blockscript = blockscript[:readingEntry['start'] - deviation] + blockscript[loopi - deviation:]
                deviation += loopi - readingEntry['start']
            entryDepth -= 1
    return blockscript
def getEntryfromBlockscript(blockscript, index):
    readingEntry = {'start': None}
    entryDepth = 0
    numberofEntry = 0
    for loopi, char in enumerate(blockscript):
        if char == '[':
            if entryDepth == 0:
                readingEntry['start'] = loopi + 1
            entryDepth += 1
        elif char == ']':
            if entryDepth == 1:
                if numberofEntry == index:
                    return blockscript[readingEntry['start']:loopi]
                numberofEntry += 1
            entryDepth -= 1

    print('[ERROR] we cannot get entry from blockscript.')
    return None
