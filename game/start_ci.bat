@echo off

title CIO Client

set /P ACCOUNT_NAME=Username: 
set GAME_SERVER=127.0.0.1:7032
set GAME_VERSION=1.1.0
set LOGIN_TOKEN=asdasd$asdasdASfdasdgdaAsassa4234QW34324436REGdfnjGFb
set RESOURCE_ENCRYPTION=cio-03-06-16_lsphases

cls

:main
..\..\cio-panda3d-3\built_x64\python\ppython.exe -B -m src.coginvasion.base.CIStartGlobal
pause
goto :main
