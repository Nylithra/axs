@echo off
rem Axs dilinin Windows calistiricisi.  Kullanim:  axs main.axs
setlocal

set "AXS_KOK=%~dp0"
set "AXS_PYEXE="
set "AXS_PYARG="

rem 1) Kurulum sirasinda dogrulanmis yorumlayici (PATH'te olmasa da calisir)
if exist "%AXS_KOK%python.txt" (
  for /f "usebackq delims=" %%p in ("%AXS_KOK%python.txt") do (
    if exist "%%p" set "AXS_PYEXE=%%p"
  )
)

rem 2) PATH
if not defined AXS_PYEXE (
  where py >nul 2>nul
  if not errorlevel 1 (
    set "AXS_PYEXE=py"
    set "AXS_PYARG=-3"
  )
)

if not defined AXS_PYEXE (
  where python >nul 2>nul
  if not errorlevel 1 set "AXS_PYEXE=python"
)

if not defined AXS_PYEXE (
  where python3 >nul 2>nul
  if not errorlevel 1 set "AXS_PYEXE=python3"
)

if not defined AXS_PYEXE (
  echo Python 3 bulunamadi.
  echo.
  echo Kurmak icin:  winget install Python.Python.3.12
  echo ya da:        https://www.python.org/downloads/
  echo Kurulum sirasinda "Add python.exe to PATH" secenegini isaretle.
  exit /b 1
)

"%AXS_PYEXE%" %AXS_PYARG% "%AXS_KOK%axs" %*
