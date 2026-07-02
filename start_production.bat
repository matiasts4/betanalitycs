@echo off
title BetAnalytics - Iniciar Produccion
echo ==========================================================
echo   Iniciando BetAnalytics en Modo Produccion (Build)
echo ==========================================================
echo.

echo [1] Iniciando Backend Flask (Motor de IA)...
start "BetAnalytics - Backend API" cmd /k "cd /d %~dp0archive\pl-predictor && python -m src.api"

echo.
echo [2] Iniciando Servidor Frontend de Produccion (Vite Preview)...
start "BetAnalytics - Frontend Production" cmd /k "cd /d %~dp0pl-web && npm run start"

echo.
echo ==========================================================
echo Ambos servicios se estan ejecutando en ventanas independientes:
echo - Frontend (Produccion): http://localhost:8080
echo - Backend API: http://localhost:5000
echo ==========================================================
echo.
pause
