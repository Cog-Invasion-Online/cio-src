@echo off

title CIO AI Server

set /p BASE_CHANNEL=Base channel(start at 403, go one number higher with each new district): 
set MAX_CHANNELS=999999
set STATE_SERVER=4002
set ASTRON_IP=127.0.0.1:7031
set EVENT_LOGGER_IP=127.0.0.1:7030

echo Starting Cog Invasion AI Server...
echo -----------------------------------
echo BASE CHANNEL: %BASE_CHANNEL%
echo MAX_CHANNELS: %MAX_CHANNELS%
echo STATE_SERVER: %STATE_SERVER%
echo ASTRON_IP: %ASTRON_IP%
echo EVENT_LOGGER: %EVENT_LOGGER_IP%
echo -----------------------------------

..\Panda3D-CI\python\ppython.exe -B -m lib.coginvasion.ai.AIStart --base-channel %BASE_CHANNEL% ^
                     --max-channels %MAX_CHANNELS% --stateserver %STATE_SERVER% ^
                     --astron-ip %ASTRON_IP% --eventlogger-ip %EVENT_LOGGER_IP%
pause
