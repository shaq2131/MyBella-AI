@echo off
echo ============================================================
echo Starting MyBella Server...
echo ============================================================
echo.
echo The server will start in a new window.
echo Keep that window open while using MyBella.
echo.
echo Access MyBella at: http://127.0.0.1:5000
echo.
echo Press any key to start the server...
pause >nul

start "MyBella Server" /D "%~dp0" python mybella.py

echo.
echo Server started! A new window should have opened.
echo If you need to stop the server, close the server window or press CTRL+C in it.
echo.
pause
