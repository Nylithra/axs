@echo off
rem TON kurulumu (Windows): `ton` komutunu her klasorde calisir hale getirir.
rem Cift tiklayarak ya da komut isteminden calistirabilirsin.
setlocal

set "TON_KOK=%~dp0"
if "%TON_KOK:~-1%"=="\" set "TON_KOK=%TON_KOK:~0,-1%"

echo.
echo   TON kuruluyor
echo   Klasor: %TON_KOK%
echo.

set "TON_PY="
where py >nul 2>nul
if not errorlevel 1 set "TON_PY=py -3"

if not defined TON_PY (
  where python >nul 2>nul
  if not errorlevel 1 set "TON_PY=python"
)

if not defined TON_PY (
  echo   [HATA] Python 3 bulunamadi.
  echo.
  echo   Once Python kur:  winget install Python.Python.3.12
  echo   ya da https://www.python.org/downloads/ adresinden indir.
  echo   Kurulumda "Add python.exe to PATH" kutusunu isaretlemeyi unutma.
  echo.
  pause
  exit /b 1
)

%TON_PY% -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)"
if errorlevel 1 (
  echo   [HATA] Python 3.8 ya da ustu gerekli.
  echo.
  pause
  exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "$k = $env:TON_KOK; $p = [Environment]::GetEnvironmentVariable('PATH','User'); if ($null -eq $p) { $p = '' }; if (($p -split ';') -notcontains $k) { [Environment]::SetEnvironmentVariable('PATH', ($p.TrimEnd(';') + ';' + $k).TrimStart(';'), 'User'); Write-Host '  PATH guncellendi.' } else { Write-Host '  PATH zaten ayarliydi.' }"

if errorlevel 1 (
  echo.
  echo   [UYARI] PATH otomatik ayarlanamadi. Elle eklemek icin:
  echo   Windows tusu -^> "ortam degiskenleri duzenle" ara -^> Path -^> Yeni
  echo   -^> %TON_KOK%
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
echo     ton -s
echo     ton main.ton
echo.
pause
