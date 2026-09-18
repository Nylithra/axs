@echo off
rem Axs yerel kurulumu (Windows): `axs` komutunu her klasorde calisir hale getirir.
rem Cift tiklayarak ya da komut isteminden calistirabilirsin.
setlocal

set "AXS_KOK=%~dp0"
if "%AXS_KOK:~-1%"=="\" set "AXS_KOK=%AXS_KOK:~0,-1%"

echo.
echo   Axs kuruluyor
echo   Klasor: %AXS_KOK%
echo.

set "AXS_PY="
where py >nul 2>nul
if not errorlevel 1 set "AXS_PY=py -3"

if not defined AXS_PY (
  where python >nul 2>nul
  if not errorlevel 1 set "AXS_PY=python"
)

if not defined AXS_PY (
  echo   [HATA] Python 3 bulunamadi.
  echo.
  echo   Once Python kur:  winget install Python.Python.3.12
  echo   ya da https://www.python.org/downloads/ adresinden indir.
  echo   Kurulumda "Add python.exe to PATH" kutusunu isaretlemeyi unutma.
  echo.
  pause
  exit /b 1
)

%AXS_PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
  echo   [HATA] Python 3.8 ya da ustu gerekli.
  echo.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$k = $env:AXS_KOK; $p = [Environment]::GetEnvironmentVariable('PATH','User'); if ($null -eq $p) { $p = '' }; if (($p -split ';') -notcontains $k) { [Environment]::SetEnvironmentVariable('PATH', ($p.TrimEnd(';') + ';' + $k).TrimStart(';'), 'User'); Write-Host '  PATH guncellendi.' } else { Write-Host '  PATH zaten ayarliydi.' }"

if errorlevel 1 (
  echo.
  echo   [UYARI] PATH otomatik ayarlanamadi. Elle eklemek icin:
  echo   Windows tusu -^> "ortam degiskenleri duzenle" ara -^> Path -^> Yeni
  echo   -^> %AXS_KOK%
  echo.
  pause
  exit /b 1
)

echo.
echo   Kurulum tamam!
echo.
echo   ONEMLI: Simdi YENI bir komut istemi ac (bu pencere eskisini kullaniyor),
echo   sonra dene:
echo.
echo     axs -s
echo     axs main.axs
echo.
pause
