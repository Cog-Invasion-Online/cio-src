"""
COG INVASION ONLINE
Copyright (c) CIO Team. All rights reserved.

@file tool_cioview.py
@author Maverick Liberty
@date February 25, 2018
@desc This script acts like a light-weight replacement to pview.exe, but just for CIO.
	This script loads models that are dragged and dropped onto tool_cioview.bat.
	Please note that this script relies on absolute paths. 
"""

from panda3d.core import loadPrcFile, loadPrcFileData, ConfigVariableString
from direct.showbase.ShowBase import ShowBase
import os
import sys

def correctDrivePrefix(str):
  return "/c/" + str[str.index("C:\\")+3:len(str)]

# We need to change the drive's prefix to what panda can use.
# This changes C:\ to /c/
res_path = correctDrivePrefix(os.path.dirname(os.path.realpath(__file__)))
res_path = res_path[:-6]

loadPrcFile('../../config/config_client.prc')
loadPrcFileData('', 'load-display pandagl')
loadPrcFileData('', ('model-path {0}/resources'.format(res_path)))

base = ShowBase()

# Let's load in all the models dragged and dropped to the batch file.
for i in range(1, len(sys.argv)):
    arg = sys.argv[i]
    path = correctDrivePrefix(arg)
    mdl = loader.loadModel(path)
    mdl.reparentTo(render)
	
#base.startDirect()
base.run()
