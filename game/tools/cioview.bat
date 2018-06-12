
REM COG INVASION ONLINE
REM Copyright (c) CIO Team. All rights reserved.
REM @file cioview.bat
REM @author Maverick Liberty
REM @date February 25, 2018
REM @desc Drag files onto this batch file to run tool_cioview.py 
REM 	with the models you have selected.

@ECHO OFF
set path=%~dp0/../../cio-panda3d/built_x64/python/ppython.exe
CALL "%path%" "%~dp0/tool_cioview.py" %*
PAUSE
