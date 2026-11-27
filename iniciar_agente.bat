@echo off
chcp 65001 > nul
title Agente LegalTech CLM - Servidor
cls
echo ======================================================================
echo    AGENTE LEGALTECH - CONTRACT LIFECYCLE MANAGEMENT (CLM)
echo ======================================================================
echo.
echo [1/2] Iniciando el navegador en http://localhost:5005 ...
start "" "http://localhost:5005"
echo.
echo [2/2] Levantando el servidor Flask del Agente CLM...
echo Presiona Ctrl+C para detener el servidor en cualquier momento.
echo.

"C:\Users\josen\AppData\Local\Python\pythoncore-3.14-64\python.exe" app.py

pause
