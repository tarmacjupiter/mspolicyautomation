@echo off
REM A batch script to run the python scripting MS Policy Automation Software
call .\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated
echo Python path: %VIRTUAL_ENV%
where python
python --version

echo Installing required packages...
pip install python-dotenv
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install python-dotenv
    pause
    exit /b 1
)

echo Running Python script...
python main_control.py
if errorlevel 1 (
    echo Python script failed to run
    pause
    exit /b 1
)
echo Script completed successfully
pause