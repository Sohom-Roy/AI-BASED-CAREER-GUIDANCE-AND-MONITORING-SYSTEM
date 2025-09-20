@echo off
echo Starting AI-Enhanced Career Guidance System
echo ==========================================

echo.
echo Starting MQTT Broker...
start "MQTT Broker" cmd /k "mosquitto -v"

echo.
echo Waiting 3 seconds for MQTT broker to start...
timeout /t 3 /nobreak > nul

echo.
echo Starting Backend...
start "Backend Server" cmd /k "cd backend && python app.py"

echo.
echo Waiting 5 seconds for backend to start...
timeout /t 5 /nobreak > nul

echo.
echo Starting Frontend...
start "Frontend Server" cmd /k "cd frontend && npm start"

echo.
echo All services started!
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
