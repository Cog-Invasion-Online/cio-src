# Filename: FileWordReplacer.py
# Created by:  blach (21Apr15)

BASE_PATH = raw_input("Base path (where all the folders to look in are): ")
FOLDER_NAMES = raw_input("Folders to look in (separate with semicolon): ")
FILE_WORD = raw_input("Word to replace: ")

FOLDER_NAME_LIST = []
for folderName in FOLDER_NAMES.split(';'):
	FOLDER_NAME_LIST.append(BASE_PATH + "/" + folderName)

print FOLDER_NAME_LIST

print "Starting..."

import glob, fileinput

def look_through_here(folder_name):
	print "Looking in folder " + folder_name
	full_path = folder_name + "/*.py"
	print full_path
	fileList = glob.glob(folder_name + "/*.py")
	print fileList
	for fileName in fileList:
		print "Currently looking in " + fileName
		lineNum = 0
		for line in fileinput.input(fileName, inplace = True):
			lineNum += 1
			if FILE_WORD in line:
				text = fileName + ': Line %d: ' % lineNum + line + '\n'
				file2write2.write(text)
				file2write2.flush()

file2write2 = open('found_words.txt', 'w')

for folderName in FOLDER_NAME_LIST:
	look_through_here(folderName)

file2write2.close()

print "Finished."
