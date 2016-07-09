@echo off

echo Writing md5 sums of game files to file_info.txt...
echo.

set FILES_FILE=tools\\files.txt

tools\cio-file-hash-writer.exe

echo Done!

pause
