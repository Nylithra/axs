@echo off
rem TON dilinin Windows calistiricisi.  Kullanim:  ton main.ton
setlocal

set "TON_KOK=%~dp0"
set "TON_PY="

where py >nul 2>nul
if not errorlevel 1 set "TON_PY=py -3"

if not defined TON_PY (
  where python >nul 2>nul
  if not errorlevel 1 set "TON_PY=python"
)

if not defined TON_PY (
  where python3 >nul 2>nul
  if not errorlevel 1 set "TON_PY=python3"
)

if not defined TON_PY (
  echo Python 3 bulunamadi.
  echo.
  echo Kurmak icin:  winget install Python.Python.3.12
  echo ya da:        https://www.python.org/downloads/
  echo Kurulum sirasinda "Add python.exe to PATH" secenegini isaretle.
  exit /b 1
)

%TON_PY% "%TON_KOK%ton" %*
