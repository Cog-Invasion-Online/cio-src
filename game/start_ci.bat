@echo off

title CIO Client

set ACCOUNT_NAME=orange12345
set GAME_SERVER=127.0.0.1:7032
set GAME_VERSION=1.1.0
set LOGIN_TOKEN=asdasd$asdasdASfdasdgdaAsassa4234QW34324436REGdfnjGFb
REM coginvasion.exe
..\Panda3D-CI\python\ppython.exe -B -m src.coginvasion.base.CIStartGlobal
pause
