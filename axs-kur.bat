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
:::
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
::: # ---------------------------------------------------------------
::: # yardimcilar
::: # ---------------------------------------------------------------
::: function ZipGecerli($yol) {
:::   try {
:::     if (-not (Test-Path -LiteralPath $yol)) { return $false }
:::     if ((Get-Item -LiteralPath $yol).Length -lt 10240) { return $false }
:::     $fs = [IO.File]::OpenRead($yol)
:::     $b = New-Object byte[] 2
:::     $n = $fs.Read($b, 0, 2)
:::     $fs.Close()
:::     return ($n -eq 2 -and $b[0] -eq 80 -and $b[1] -eq 75)
:::   } catch { return $false }
::: }
:::
::: function PyDene($exe, $ek) {
:::   # Calisir bir Python 3.8+ ise @(surum, tam_yol) dondurur, degilse $null
:::   try {
:::     $kod = 'import sys; sys.stdout.write("%d.%d|%s" % (sys.version_info[0], sys.version_info[1], sys.executable))'
:::     $s = & $exe @ek '-c' $kod 2>$null
:::     if ($s -is [array]) { $s = ($s -join '') }
:::     if ("$s" -match '^(\d+)\.(\d+)\|(.+)$') {
:::       $buyuk = [int]$Matches[1]; $kucuk = [int]$Matches[2]
:::       if ($buyuk -gt 3 -or ($buyuk -eq 3 -and $kucuk -ge 8)) {
:::         return @(("$buyuk." + "$kucuk"), $Matches[3])
:::       }
:::     }
:::   } catch { }
:::   return $null
::: }
:::
::: # ---------------------------------------------------------------
::: # 1. Ag hazirligi  (TLS 1.2 olmadan GitHub'a baglanilamaz)
::: # ---------------------------------------------------------------
::: Write-Host '  [1/5] Baglanti hazirlaniyor...'
::: foreach ($p in @(12288, 3072)) {
:::   try { [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor $p } catch { }
::: }
::: Write-Host ("        TLS: " + [Net.ServicePointManager]::SecurityProtocol) -ForegroundColor DarkGray
::: try {
:::   $vekil = [Net.WebRequest]::GetSystemWebProxy()
:::   $vekil.Credentials = [Net.CredentialCache]::DefaultCredentials
:::   [Net.WebRequest]::DefaultWebProxy = $vekil
::: } catch { }
:::
::: # ---------------------------------------------------------------
::: # 2. Indir  (3 yontem x 2 adres; hata olursa sebebini yazar)
::: # ---------------------------------------------------------------
::: Write-Host '  [2/5] Axs indiriliyor...'
::: $gecici = Join-Path $env:TEMP ('axs-kur-' + [guid]::NewGuid().ToString('N'))
::: New-Item -ItemType Directory -Path $gecici -Force | Out-Null
::: $zip = Join-Path $gecici 'axs.zip'
:::
::: $adresler = @()
::: foreach ($dal in $dallar) {
:::   $adresler += "https://codeload.github.com/$depo/zip/refs/heads/$dal"
:::   $adresler += "https://github.com/$depo/archive/refs/heads/$dal.zip"
::: }
:::
::: $ProgressPreference = 'SilentlyContinue'
::: $hatalar = @()
::: $indi = $false
::: $kaynak_adres = ''
::: $sunucu_cevapladi = $false
::: $ilk_adres = $true
::: foreach ($a in $adresler) {
:::   foreach ($yontem in @('Invoke-WebRequest','WebClient','curl.exe')) {
:::     if ($indi) { break }
:::     Remove-Item -LiteralPath $zip -Force -ErrorAction SilentlyContinue
:::     try {
:::       if ($yontem -eq 'Invoke-WebRequest') {
:::         Invoke-WebRequest -Uri $a -OutFile $zip -UseBasicParsing -TimeoutSec 60 -Headers @{ 'User-Agent' = 'axs-kur' }
:::       } elseif ($yontem -eq 'WebClient') {
:::         $wc = New-Object Net.WebClient
:::         $wc.Headers.Add('User-Agent', 'axs-kur')
:::         try { $wc.Proxy = [Net.WebRequest]::DefaultWebProxy } catch { }
:::         $wc.DownloadFile($a, $zip)
:::         $wc.Dispose()
:::       } else {
:::         if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) { continue }
:::         & curl.exe -L -f -sS --connect-timeout 20 --max-time 300 -A 'axs-kur' -o $zip $a 2>&1 | Out-Null
:::         if ($LASTEXITCODE -ne 0) { throw ('curl.exe hata kodu ' + $LASTEXITCODE) }
:::       }
:::       $sunucu_cevapladi = $true
:::       if (ZipGecerli $zip) {
:::         $indi = $true
:::         $kaynak_adres = $a
:::       } else {
:::         $hatalar += ($yontem + ' : gecerli bir zip gelmedi -> ' + $a)
:::       }
:::     } catch {
:::       # sunucudan bir HTTP cevabi geldiyse (404/403 vb.) adres yanlis demektir,
:::       # gelmediyse baglanti/TLS sorunu var; obur adresleri denemek bos yere bekletir
:::       try { if ($_.Exception.Response) { $sunucu_cevapladi = $true } } catch { }
:::       $hatalar += ($yontem + ' : ' + $_.Exception.Message + ' -> ' + $a)
:::     }
:::   }
:::   if ($indi) { break }
:::   if ($ilk_adres -and -not $sunucu_cevapladi) { break }
:::   $ilk_adres = $false
::: }
:::
::: if (-not $indi) {
:::   Write-Host ''
:::   Write-Host '  Indirilemedi. Denenen yollar ve hatalari:' -ForegroundColor Red
:::   foreach ($h in @($hatalar | Select-Object -Unique | Select-Object -First 8)) {
:::     Write-Host ('    - ' + $h) -ForegroundColor DarkYellow
:::   }
:::   if (-not $sunucu_cevapladi) {
:::     Write-Host ''
:::     Write-Host '  Sunucudan hic cevap gelmedi: bu bir baglanti / TLS sorunu.' -ForegroundColor Red
:::   }
:::   Write-Host ''
:::   Write-Host '  Sik sebepler:' -ForegroundColor Yellow
:::   Write-Host '    - Kurum agi / guvenlik duvari github.com adresini engelliyor'
:::   Write-Host '    - Antivirus indirmeyi durduruyor'
:::   Write-Host '    - Eski Windows: TLS 1.2 kapali'
:::   Write-Host ''
:::   Write-Host '  Elle kurmak icin su zipi indir, ac, icindeki klasorun icerigini'
:::   Write-Host ('  ' + $hedef + ' icine kopyala:') -ForegroundColor Cyan
:::   Write-Host ('    ' + $adresler[0])
:::   Remove-Item $gecici -Recurse -Force -ErrorAction SilentlyContinue
:::   exit 1
::: }
::: Write-Host ('        kaynak: ' + $kaynak_adres) -ForegroundColor Green
:::
::: # ---------------------------------------------------------------
::: # 3. Sadece calisma zamanini ac
::: # ---------------------------------------------------------------
::: Write-Host '  [3/5] Kuruluyor...'
::: $ac = Join-Path $gecici 'ac'
::: try {
:::   Add-Type -AssemblyName System.IO.Compression.FileSystem
:::   [System.IO.Compression.ZipFile]::ExtractToDirectory($zip, $ac)
::: } catch {
:::   Write-Host ('  Arsiv acilamadi: ' + $_.Exception.Message) -ForegroundColor Red
:::   Remove-Item $gecici -Recurse -Force -ErrorAction SilentlyContinue
:::   exit 1
::: }
::: $kaynak = Get-ChildItem -LiteralPath $ac -Directory | Select-Object -First 1
::: if (-not $kaynak) {
:::   Write-Host '  Arsiv bos gorunuyor.' -ForegroundColor Red
:::   Remove-Item $gecici -Recurse -Force -ErrorAction SilentlyContinue
:::   exit 1
::: }
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
::: if ($sayac -lt $parcalar.Count) {
:::   Write-Host ('  Dosyalar eksik kopyalandi (' + $sayac + '/' + $parcalar.Count + ').') -ForegroundColor Red
:::   exit 1
::: }
::: Write-Host ("        $sayac parca kuruldu") -ForegroundColor Green
:::
::: # ---------------------------------------------------------------
::: # 4. PATH
::: # ---------------------------------------------------------------
::: Write-Host '  [4/5] PATH ayarlaniyor...'
::: try {
:::   $yol = [Environment]::GetEnvironmentVariable('PATH','User')
:::   if ($null -eq $yol) { $yol = '' }
:::   if (($yol -split ';') -notcontains $hedef) {
:::     [Environment]::SetEnvironmentVariable('PATH', ($yol.TrimEnd(';') + ';' + $hedef).TrimStart(';'), 'User')
:::     Write-Host '        PATH guncellendi' -ForegroundColor Green
:::   } else {
:::     Write-Host '        PATH zaten ayarliydi' -ForegroundColor Green
:::   }
::: } catch {
:::   Write-Host ('        PATH ayarlanamadi: ' + $_.Exception.Message) -ForegroundColor Yellow
:::   Write-Host ('        Elle ekle:  ' + $hedef) -ForegroundColor Yellow
::: }
:::
::: # ---------------------------------------------------------------
::: # 5. Python  (kurulumu ENGELLEMEZ; sadece calistirmak icin gerekir)
::: # ---------------------------------------------------------------
::: Write-Host '  [5/5] Python araniyor...'
::: $adaylar = @()
::: foreach ($k in @('py','python','python3')) {
:::   foreach ($x in @(Get-Command $k -CommandType Application -ErrorAction SilentlyContinue)) {
:::     if (-not $x -or -not $x.Source) { continue }
:::     # Microsoft Store kisayolu: calistirinca Store'u acar, Python degildir
:::     if ($x.Source -like '*\WindowsApps\*') {
:::       try { if ((Get-Item -LiteralPath $x.Source).Length -lt 100000) { continue } } catch { continue }
:::     }
:::     if ($k -eq 'py') { $adaylar += ,@($x.Source, @('-3')) }
:::     $adaylar += ,@($x.Source, @())
:::   }
::: }
::: # PATH'te olmayan ama diskte duran kurulumlar
::: $desenler = @()
::: if ($env:LOCALAPPDATA) { $desenler += (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python3*\python.exe') }
::: $desenler += 'C:\Program Files\Python3*\python.exe'
::: $desenler += 'C:\Program Files (x86)\Python3*\python.exe'
::: $desenler += 'C:\Python3*\python.exe'
::: $desenler += 'C:\Windows\py.exe'
::: foreach ($d in $desenler) {
:::   foreach ($f in @(Get-ChildItem -Path $d -ErrorAction SilentlyContinue)) {
:::     $adaylar += ,@($f.FullName, @())
:::   }
::: }
:::
::: $py = $null
::: foreach ($a in $adaylar) {
:::   $r = PyDene $a[0] $a[1]
:::   if ($r) { $py = $r; break }
::: }
:::
::: if ($py) {
:::   Write-Host ('        bulundu: Python ' + $py[0]) -ForegroundColor Green
:::   Write-Host ('        ' + $py[1]) -ForegroundColor DarkGray
:::   # axs.cmd PATH'te python bulamazsa bu dosyadan okur
:::   try { Set-Content -LiteralPath (Join-Path $hedef 'python.txt') -Value $py[1] -Encoding Oem } catch { }
::: } else {
:::   Write-Host '        Python 3.8+ bulunamadi' -ForegroundColor Yellow
::: }
:::
::: # ---------------------------------------------------------------
::: # dogrulama
::: # ---------------------------------------------------------------
::: $env:PATH = $env:PATH + ';' + $hedef
::: Write-Host ''
::: if ($py) {
:::   try {
:::     $cikti = & $py[1] (Join-Path $hedef 'axs') '-s' 2>&1 | Out-String
:::     Write-Host $cikti.Trim() -ForegroundColor Cyan
:::   } catch {
:::     Write-Host ('  Dogrulama yapilamadi: ' + $_.Exception.Message) -ForegroundColor Yellow
:::   }
:::   Write-Host ''
:::   Write-Host '  Kurulum tamam.' -ForegroundColor Green
:::   Write-Host ''
:::   Write-Host '  ONEMLI: Yeni bir komut istemi ac, sonra dene:' -ForegroundColor Yellow
:::   Write-Host ''
:::   Write-Host '    axs -e "print: merhaba"'
:::   Write-Host '    axs install jubbio'
:::   Write-Host '    axs yeni ilkproje'
:::   Write-Host ''
::: } else {
:::   Write-Host '  Axs dosyalari kuruldu, ama calismak icin Python 3.8+ gerekiyor.' -ForegroundColor Yellow
:::   Write-Host ''
:::   Write-Host '  Kurmak icin:  winget install Python.Python.3.12'
:::   Write-Host '  ya da:        https://www.python.org/downloads/'
:::   Write-Host '  (kurulumda "Add python.exe to PATH" kutusunu isaretle)'
:::   Write-Host ''
:::   Write-Host '  Python kurduktan sonra bu dosyayi bir kez daha calistir.' -ForegroundColor Yellow
:::   Write-Host ''
::: }
