@echo off
rem ===========================================================
rem  Axs dili kurucusu  -  tek dosya, kaynak kodu indirmeden
rem
rem  Kullanim: bu dosyaya cift tikla ya da komut isteminden calistir
rem ===========================================================
setlocal
title Axs kurulumu
rem kutu cizim karakterleri duzgun gorunsun
chcp 65001 >nul 2>&1

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; iex ((Get-Content -LiteralPath '%~f0' -Encoding UTF8 | Where-Object { $_ -like ':::*' } | ForEach-Object { $_.Substring(3) }) -join [Environment]::NewLine)"

if errorlevel 1 (
  echo.
  echo   Kurulum tamamlanamadi.
  echo.
  pause
  exit /b 1
)

echo.
pause
exit /b 0

:::# ---------------------------------------------------------------
::: try { [Console]::OutputEncoding = [Text.Encoding]::UTF8 } catch { }
::: $depo   = if ($env:AXS_DEPO) { $env:AXS_DEPO } else { 'Nylithra/ton-language' }
::: $dallar = if ($env:AXS_DAL) { @($env:AXS_DAL) } else { @('claude/ton-language-core-qyppl7','main','master') }
::: $hedef  = if ($env:AXS_KONUM) { $env:AXS_KONUM } else { Join-Path $env:LOCALAPPDATA 'Axs' }
::: $parcalar = @('axslang','axsweb','kutuphaneler','axs','axs.cmd')
:::
::: Write-Host ''
::: Write-Host '   █████╗ ██╗  ██╗███████╗' -ForegroundColor Cyan
::: Write-Host '  ██╔══██╗╚██╗██╔╝██╔════╝' -ForegroundColor Cyan
::: Write-Host '  ███████║ ╚███╔╝ ███████╗' -ForegroundColor Cyan
::: Write-Host '  ██╔══██║ ██╔██╗ ╚════██║' -ForegroundColor Cyan
::: Write-Host '  ██║  ██║██╔╝ ██╗███████║' -ForegroundColor Cyan
::: Write-Host '  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝' -ForegroundColor Cyan
::: Write-Host ''
::: Write-Host "  Kurulum yeri: $hedef"
::: Write-Host ''
:::
::: # --- 1. Python ---
::: Write-Host '  [1/4] Python araniyor...'
::: $py = $null
::: foreach ($aday in @(@('py','-3'), @('python'), @('python3'))) {
:::   $komut = $aday[0]
:::   if (Get-Command $komut -ErrorAction SilentlyContinue) {
:::     $ek = if ($aday.Count -gt 1) { $aday[1..($aday.Count-1)] } else { @() }
:::     try {
:::       $s = & $komut @ek '-c' 'import sys; print("%d.%d" % sys.version_info[:2])' 2>$null
:::       if ($s -match '^(\d+)\.(\d+)$') {
:::         if ([int]$Matches[1] -gt 3 -or ([int]$Matches[1] -eq 3 -and [int]$Matches[2] -ge 8)) {
:::           $py = $aday; Write-Host "        bulundu: $komut $ek (Python $s)" -ForegroundColor Green; break
:::         }
:::       }
:::     } catch { }
:::   }
::: }
::: if (-not $py) {
:::   Write-Host ''
:::   Write-Host '  Python 3.8 ya da ustu bulunamadi.' -ForegroundColor Red
:::   Write-Host ''
:::   Write-Host '  Kurmak icin:  winget install Python.Python.3.12'
:::   Write-Host '  ya da:        https://www.python.org/downloads/'
:::   Write-Host '  (kurulumda "Add python.exe to PATH" kutusunu isaretle)'
:::   exit 1
::: }
:::
::: # --- 2. Indir ---
::: Write-Host '  [2/4] Axs indiriliyor...'
::: $gecici = Join-Path $env:TEMP ('axs-kur-' + [guid]::NewGuid().ToString('N'))
::: New-Item -ItemType Directory -Path $gecici -Force | Out-Null
::: $zip = Join-Path $gecici 'axs.zip'
::: $indi = $false
::: foreach ($dal in $dallar) {
:::   $adres = "https://codeload.github.com/$depo/zip/refs/heads/$dal"
:::   try {
:::     $eski = $ProgressPreference; $ProgressPreference = 'SilentlyContinue'
:::     Invoke-WebRequest -Uri $adres -OutFile $zip -UseBasicParsing
:::     $ProgressPreference = $eski
:::     $indi = $true
:::     Write-Host "        kaynak: $dal dali" -ForegroundColor Green
:::     break
:::   } catch { }
::: }
::: if (-not $indi) {
:::   Write-Host '  Indirilemedi. Internet baglantini kontrol et.' -ForegroundColor Red
:::   Remove-Item $gecici -Recurse -Force -ErrorAction SilentlyContinue
:::   exit 1
::: }
:::
::: # --- 3. Sadece calisma zamanini ac ---
::: Write-Host '  [3/4] Kuruluyor...'
::: Add-Type -AssemblyName System.IO.Compression.FileSystem
::: $ac = Join-Path $gecici 'ac'
::: [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $ac)
::: $kaynak = Get-ChildItem -LiteralPath $ac -Directory | Select-Object -First 1
::: if (-not $kaynak) { Write-Host '  Arsiv acilamadi.' -ForegroundColor Red; exit 1 }
:::
::: if (Test-Path $hedef) {
:::   foreach ($p in $parcalar) {
:::     $y = Join-Path $hedef $p
:::     if (Test-Path $y) { Remove-Item $y -Recurse -Force -ErrorAction SilentlyContinue }
:::   }
::: } else {
:::   New-Item -ItemType Directory -Path $hedef -Force | Out-Null
::: }
::: $sayac = 0
::: foreach ($p in $parcalar) {
:::   $kay = Join-Path $kaynak.FullName $p
:::   if (Test-Path $kay) {
:::     Copy-Item -LiteralPath $kay -Destination $hedef -Recurse -Force
:::     $sayac++
:::   }
::: }
::: Remove-Item $gecici -Recurse -Force -ErrorAction SilentlyContinue
::: if ($sayac -lt $parcalar.Count) { Write-Host '  Dosyalar eksik kopyalandi.' -ForegroundColor Red; exit 1 }
::: Write-Host "        $sayac parca kuruldu" -ForegroundColor Green
:::
::: # --- 4. PATH ---
::: Write-Host '  [4/4] PATH ayarlaniyor...'
::: $yol = [Environment]::GetEnvironmentVariable('PATH','User')
::: if ($null -eq $yol) { $yol = '' }
::: if (($yol -split ';') -notcontains $hedef) {
:::   [Environment]::SetEnvironmentVariable('PATH', ($yol.TrimEnd(';') + ';' + $hedef).TrimStart(';'), 'User')
:::   Write-Host '        PATH guncellendi' -ForegroundColor Green
::: } else {
:::   Write-Host '        PATH zaten ayarliydi' -ForegroundColor Green
::: }
:::
::: # --- dogrulama ---
::: $env:PATH = $env:PATH + ';' + $hedef
::: Write-Host ''
::: try {
:::   $cikti = & (Join-Path $hedef 'axs.cmd') '-s' 2>&1 | Out-String
:::   Write-Host $cikti.Trim() -ForegroundColor Cyan
::: } catch {
:::   Write-Host '  Dogrulama yapilamadi ama dosyalar yerinde.' -ForegroundColor Yellow
::: }
::: Write-Host ''
::: Write-Host '  Kurulum tamam.' -ForegroundColor Green
::: Write-Host ''
::: Write-Host '  ONEMLI: Yeni bir komut istemi ac, sonra dene:' -ForegroundColor Yellow
::: Write-Host ''
::: Write-Host '    axs -e "print: merhaba"'
::: Write-Host '    axs install jubbio'
::: Write-Host '    axs yeni ilkproje'
::: Write-Host ''
