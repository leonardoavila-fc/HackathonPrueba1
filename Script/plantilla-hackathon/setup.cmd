@echo off
rem Lanzador (doble clic): el instalador real vive en .hackathon\
chcp 65001 >nul
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0.hackathon\setup.ps1" %*
pause
