@echo off
cd ..
echo Starting header generator...
..\Panda3D-CI\python\ppython.exe -B tools/header_generator.py
PAUSE
