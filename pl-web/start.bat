@echo off
echo ===================================================
echo Iniciando PL Predictor (Motor Neuronal + UI Premium)
echo ===================================================

echo.
echo [1] Iniciando Backend Flask (Redes Neuronales)...
start "PL Predictor - Backend API" cmd /c "cd /d c:\Users\PC\DataScience\archive\pl-predictor && python -m src.api"

echo.
echo [2] Iniciando Frontend Vite (Panel de Control)...
start "PL Predictor - Frontend UI" cmd /c "cd /d c:\Users\PC\DataScience\pl-web && npm run dev"

echo.
echo Todos los servicios se estan ejecutando en ventanas independientes.
echo - Frontend disponible en: http://localhost:8080
echo - Backend de IA disponible en: http://localhost:5000/api/stats
echo.
pause
