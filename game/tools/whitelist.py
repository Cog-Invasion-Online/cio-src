""" Whitelist Tools for keeping ciwhitelist clean
makes adding and removing words seamless. """

import os, sys

words = []
whitelist = '../phase_3/etc/ciwhitelist.dat'

def loadWhitelist():
    print "Loading whitelist, this may take awhile..."
    try:
        f = open(whitelist, 'r')
        for line in f:
            if line:
                line = line.replace('\r', '')
                line = line.replace('\n', '')
                line = line.split()[0]
                words.append(str(line))
        f.close()
    except:
        print "Could not locate ciwhitelist.dat. Make sure to place this in the tools folder."
        sys.exit()
                
def handleCommand(command):
    cutStr = command.split()
    cmd = cutStr[0]
    if len(cutStr) == 2 and cutStr[1]:
        word = str(cutStr[1].split()[0]).lower()
    if cmd == '/add':
        if word and not word in words:
            words.append(word)
            words.sort()
            print "Added word to whitelist."
        elif not word:
            print "Cannot add an empty string!"
        elif word in words:
            print "Word already in whitelist!"
    elif cmd == '/remove':
        if word and cutStr[1] in words:
            words.remove(word)
            words.sort()
            print "Removed word from whitelist."
        elif not word:
            print "You must enter a string to remove."
        elif not word in words:
            print "That word isn't in the whitelist!"
    elif cmd == '/check':
        if word and word in words:
            print "%s is whitelisted." % word
        elif word and not word in words:
            print "%s is not whitelisted." % word
        elif not word:
            print "Cannot check an empty string."
    elif cmd == '/build':
        print "Building the whitelist... This may take awhile"
        words.sort()
        os.remove(whitelist)
        new_whitelist = open(whitelist, 'w')
        for word in words:
            new_whitelist.write(str(word) + '\n')
        new_whitelist.close()
        print "New whitelist was successfully built!"
    printCommands()

def printCommands():
    print "--Commands--"
    print "-/add [word] (adds a word to the whitelist)"
    print "-/remove [word] (removes a word from the whitelist)"
    print "-/check [word] (checks if a word exists in the whitelist)"
    print "-/build (build the new whitelist)"
    command = raw_input("Enter a command: ")
    handleCommand(command)
    
print "DecodedLogic's Whitelist Tools [v1.0]"
loadWhitelist()
printCommands()