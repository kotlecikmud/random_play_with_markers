@echo off

REM Chceck pyton version
python --version

REM Install/upgarde pip
python.exe -m pip install --upgrade pip

echo Check dependencies

REM Install required libraries
pip install -r requirements.txt

pause

REM Run python script
python main.py

pause