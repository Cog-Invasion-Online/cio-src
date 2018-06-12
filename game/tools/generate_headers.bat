@echo off
cd ..
echo Starting header generator...
..\cio-panda3d\built_x64\python\ppython.exe -B tools/header_generator.py
PAUSE
