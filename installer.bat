@echo off

echo Installing required modules...
py -m pip install selenium
py -m pip install requests
py -m pip install discord_webhook



echo %GREEN%Successfully installed.%RESET%
pause