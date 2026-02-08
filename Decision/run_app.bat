@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Running Financial Agent...
python main.py

echo.
pause
