"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file header_generator.py
@author Maverick Liberty
@date March 15, 2017

"""

from datetime import datetime
from Tkinter import *
import tkFileDialog
import os

class HeaderGenerator:

	def __init__(self):
		self.knownAuthors = ['Maverick Liberty', 'Brian Lach']
		self.fileAuthor = None
		self.fileName = None
		self.header = '%s\nCOG INVASION ONLINE\nCopyright (c) CIO Team. All rights reserved.\n\n@file %s\n@author %s\n@date %s\n\n%s'
		
		# If the date mode is 0 we are using Month Day, Year format
		# If the date mode is 1, we are using YYYY-MM-DD format
		self.dateMode = 0
		
	def gatherInformation(self):
		print 'Welcome to the Header Generator!'
		self.askAuthor()
		
	def askAuthor(self):
		# We need to know who is programming this file.
		authors = 'Known Authors:'
		for i in xrange(0, len(self.knownAuthors)):
			author = self.knownAuthors[i]
			authors += '\n%d) %s' % (i + 1, author)
			
		print authors
		
		selectedAuthor = raw_input('Enter the index of the author of the file: ')
		
		try:
			author = int(selectedAuthor)
			author -= 1
			if 0 <= author <= len(self.knownAuthors):
				self.fileAuthor = self.knownAuthors[author]
				self.askFiles()
			else:
				print ('Please enter a number between 1 and %d' % len(self.knownAuthors))
				self.askAuthor()
		except ValueError:
			print ('Please enter a number between 1 and %d' % len(self.knownAuthors))
			self.askAuthor()
	
	def askFiles(self):
		print 'Please select the files you would like to generate headers for.'
		r = Tk()
		r.withdraw()
		files = tkFileDialog.askopenfiles(mode = 'r+', title = 'Generate code headers for...')
		
		for file in files:
			with file as f:
				header = self.generateHeader(os.path.basename(file.name))
				content = f.read()
				f.seek(0, 0)
				f.write(header.rstrip('\r\n') + '\n\n' + content)
			file.close()
		
		print 'Done!'
		
	def generateHeader(self, fileName):
		print 'Generating header... Please wait...'
		_, fileExt = fileName.split('.')
		blockCmtStartChars = '"""'
		blockCmtEndChars = blockCmtStartChars
		
		if fileExt in ['java', 'h', 'cxx', 'cpp', 'hpp', 'hxx', 'cc']:
			blockCmtStartChars = '/*'
			blockCmtEndChars = '*/'
		
		header = self.header % (blockCmtStartChars, fileName, self.fileAuthor, self.getDate(), blockCmtEndChars)
		return header
		
	def getDate(self):
		now = datetime.now()
		if self.dateMode:
			month = str(now.month) if now.month > 9 else '0%d' % now.month
			day = str(now.day) if now.day > 9 else '0%d' % now.day 
			return '%d-%s-%s' % (now.year, month, day)
		else:
			months = ['January', 'February', 'March', 'April', 'May', 'June', 
				'July', 'August', 'September', 'October', 'November', 'December']
			month = months[now.month - 1]
			return '%s %d, %d' % (month, now.day, now.year)

gen = HeaderGenerator()
gen.gatherInformation()