"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file FileUtility.py
@author Brian Lach
@date April 18, 2015

"""

from panda3d.core import VirtualFileSystem, Filename
vfs = VirtualFileSystem.getGlobalPtr()

def handleFileList(models, fileList):
	for fileName in fileList:
		if fileName.get_filename().get_fullpath().endswith(('.bam', 'egg', '.pz')):
			if not fileName.get_filename().get_fullpath() in models:
				models.append(fileName.get_filename().get_fullpath())
		else:
			handleFileList(models, vfs.scanDirectory(Filename(fileName.get_filename().get_fullpath())))

def findAllModelFilesInVFS(phase_array):
	models = []
	for phase in phase_array:
		fileList = vfs.scanDirectory(Filename(phase))
		handleFileList(models, fileList)
	return models
