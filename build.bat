REM using pyinstaller to build the executable for VepleyAI_acquire.py
echo off
cls
echo Building EFLIS.exe...
REM using pyinstaller wit - copy folder data to dist and --noconsole  --icon=data/icon.ico --name=EFLIS 
pyinstaller ui.py --onefile --icon=data/icon.ico --name=EFLIS 
REM copy the data folder to the dist folder
xcopy /E /I /Y data dist\EFLIS\data
echo Done!

