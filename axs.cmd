@echo off
rem Axs dilinin Windows calistiricisi.  Kullanim:  axs main.axs
setlocal

set "AXS_KOK=%~dp0"
set "AXS_PY="

where py >nul 2>nul
if not errorlevel 1 set "AXS_PY=py -3"

if not defined AXS_PY (
  where python >nul 2>nul
  if not errorlevel 1 set "AXS_PY=python"
)

if not defined AXS_PY (
  where python3 >nul 2>nul
  if not errorlevel 1 set "AXS_PY=python3"
)

if not defined AXS_PY (
  echo Python 3 bulunamadi.
  echo.
  echo Kurmak icin:  winget install Python.Python.3.12
  echo ya da:        https://www.python.org/downloads/
  echo Kurulum sirasinda "Add python.exe to PATH" secenegini isaretle.
  exit /b 1
)

%AXS_PY% "%AXS_KOK%axs" %*
