@echo off
echo ========================================================
echo 🛡️  DisasterShield AI - Launcher
echo Tagline: Prepare Smarter. Respond Safer.
echo ========================================================
echo [1] Launch Fire TV Edition (10-Foot UI, Port 8000)
echo [2] Launch Command Center Dashboard (Streamlit, Port 8501)
echo [3] Run Automated Test Suite (Pytest)
echo ========================================================
set /p choice="Select an option [1-3] (Default: 1): "
if "%choice%"=="2" goto stream
if "%choice%"=="3" goto test
goto firetv

:firetv
echo Starting Fire TV Edition on http://localhost:8000 ...
python firetv_server.py
goto end

:stream
echo Starting Streamlit Command Center on http://localhost:8501 ...
python -m streamlit run app.py
goto end

:test
echo Running Pytest Suite...
pytest -v
pause
goto end

:end
