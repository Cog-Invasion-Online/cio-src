@echo off
title Astron Server
cd astron
astrond --loglevel info config/astrond.yml
pause
