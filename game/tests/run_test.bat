@ECHO OFF
REM COG INVASION ONLINE
REM Copyright (c) CIO Team. All rights reserved.
REM @file run_test.bat
REM @author Maverick Liberty
REM @date June 15, 2018
REM @desc Use this program to run a standalone test
REM program without having to manually open another command prompt.

TITLE Cog Invasion Online - Standalone Program Test
COLOR 03
ECHO Please verify that your test program is importing test_base before importing
ECHO from Cog Invasion's src or it will not run.
ECHO.

SET panda=%~dp0..\..\cio-panda3d\built_x64\python\ppython.exe
SET tests=%CD%

CD %tests%/../
SETLOCAL EnableDelayedExpansion

GOTO QUERY_TEST

:QUERY_TEST
	SET /p programName="Enter test program name: "
	GOTO RUN_PROGRAM

:RUN_PROGRAM
	IF EXIST %tests%\%programName% (
		ECHO Attempting to start %programName%...
		CALL "%panda%" "%tests%\%programName%"
		
		REM We have to delay this code from being parsed or the 'testAgain' variable won't get a value.
		SET /p testAgain="Would you like to run %programName% again? [Y/N] "
		
		IF /i "!testAgain!" EQU "y" (
			ECHO Running again...
			GOTO RUN_PROGRAM
		)ELSE (
			ECHO.
			GOTO QUERY_TEST
		)
	) ELSE (
		ECHO The program specified could not be found. Please add the file extension and/or verify the file exists.
		GOTO QUERY_TEST
	)

:END
PAUSE
