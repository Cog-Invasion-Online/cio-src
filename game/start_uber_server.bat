@echo off

title CIO UberDog Server

set BASE_CHANNEL=1000000
set MAX_CHANNELS=999999
set STATE_SERVER=4002
set ASTRON_IP=127.0.0.1:7031
set EVENT_LOGGER_IP=127.0.0.1:7030
set ACCOUNT_LIMIT=2
set ACC_LIMIT_PER_COMP=2
set HOLIDAY=0

echo Starting Cog Invasion Uber Server...
echo -----------------------------------
echo BASE CHANNEL: %BASE_CHANNEL%
echo MAX_CHANNELS: %MAX_CHANNELS%
echo STATE_SERVER: %STATE_SERVER%
echo ASTRON_IP: %ASTRON_IP%
echo EVENT_LOGGER: %EVENT_LOGGER_IP%
echo -----------------------------------

..\cio-panda3d\built_x64\python\ppython.exe -B -m src.coginvasion.uber.UberStart --base-channel %BASE_CHANNEL% ^
                     --max-channels %MAX_CHANNELS% --stateserver %STATE_SERVER% ^
                     --astron-ip %ASTRON_IP% --eventlogger-ip %EVENT_LOGGER_IP% --acc-limit %ACCOUNT_LIMIT% --acc-limit-per-comp %ACC_LIMIT_PER_COMP% --holiday %HOLIDAY%
pause
