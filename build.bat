REM using pyinstaller to build the executable for VepleyAI_acquire.py
cls
echo off
echo Building EFLIS.exe...
REM using pyinstaller with flag: --onefile
pyinstaller ui.py --onefile --noconsole --icon=icon.ico --name=EFLIS 

