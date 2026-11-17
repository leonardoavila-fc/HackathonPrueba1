# Envoltorio Windows: localiza un Python minimo y ejecuta setup.py.
# Si no hay Python utilizable, descarga uv (version fija) dentro de esta carpeta y uv provee Python.
$ErrorActionPreference = 'Stop'
$Aqui = Split-Path -Parent $MyInvocation.MyCommand.Path
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$Stack = Get-Content "$Aqui\stack.json" -Raw | ConvertFrom-Json
$VenvPy = Join-Path $Aqui '..\.venv\Scripts\python.exe'
foreach ($c in $VenvPy, 'python', 'py') {
  $p = Get-Command $c -ErrorAction SilentlyContinue
  # ignora el alias de Microsoft Store (WindowsApps) que no es un Python real
  if ($p -and $p.Source -notlike '*WindowsApps*') {
    & $p.Source -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>$null
    if ($LASTEXITCODE -eq 0) { & $p.Source "$Aqui\setup.py" @args; exit $LASTEXITCODE }
  }
}
Write-Host "No encontre Python 3.8+. Descargo uv $($Stack.uv) dentro de esta carpeta para obtenerlo..."
$Boot = "$Aqui\.bootstrap"; New-Item -ItemType Directory -Force $Boot | Out-Null
Invoke-WebRequest "https://astral.sh/uv/$($Stack.uv)/install.ps1" -OutFile "$Boot\install.ps1" -UseBasicParsing
$env:UV_UNMANAGED_INSTALL = "$Boot\uv"; $env:UV_NO_MODIFY_PATH = '1'
& powershell -NoProfile -ExecutionPolicy Bypass -File "$Boot\install.ps1"
$env:HACKATHON_BOOTSTRAP_UV = "$Boot\uv\uv.exe"
$env:UV_PYTHON_INSTALL_DIR = "$Boot\python"; $env:UV_CACHE_DIR = "$Boot\cache"; $env:UV_NO_CONFIG = '1'
& "$Boot\uv\uv.exe" run --no-project --managed-python --python $Stack.python python "$Aqui\setup.py" @args
exit $LASTEXITCODE
