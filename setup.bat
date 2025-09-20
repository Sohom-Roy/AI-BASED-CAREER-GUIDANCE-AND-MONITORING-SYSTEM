@echo off
echo AI-Enhanced Career Guidance System Setup
echo ======================================

echo.
echo Setting up Backend...
cd backend
echo Installing Python dependencies...
pip install -r requirements.txt
echo Downloading spaCy model...
python -m spacy download en_core_web_sm
cd ..

echo.
echo Setting up Frontend...
cd frontend
echo Installing Node.js dependencies...
npm install
cd ..

echo.
echo Setup complete!
echo.
echo To start the application:
echo 1. Start MQTT broker: mosquitto -v
echo 2. Start backend: cd backend && python app.py
echo 3. Start frontend: cd frontend && npm start
echo.
echo Backend will run on http://localhost:5000
echo Frontend will run on http://localhost:3000
echo.
pause
