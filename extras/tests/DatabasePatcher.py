# Filename: DatabasePatcher.py
# Created by:  blach (24Nov15)

import glob
import fileinput

directory = raw_input('Directory of database files (Unix style): ')
className = raw_input('Class name: ')
field = raw_input('Field: ')
whatToPutIn = raw_input('What to put in {0}: '.format(field))

databaseFiles = glob.glob(directory + '/*.yaml')
filesPatched = 0

for fileName in databaseFiles:
    if 'info.yaml' in fileName:
        continue
    f = open(fileName, 'r')
    if not 'class: ' + className in f.read():
        f.close()
        continue
    f.close()
    print 'Patching {0}...'.format(fileName)
    for line in fileinput.input(fileName, inplace = True):
        if field in line:
            print line.replace(line, "  " + field + ': ' + whatToPutIn)
        else:
            print line,
    filesPatched += 1

print 'Successfully patched {0} database file(s).'.format(filesPatched)
