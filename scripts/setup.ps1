$ErrorActionPreference = "Stop"
Write-Host "[setup] Checking Python 3.11+"
$pyVersion = py -3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
if (-not $pyVersion.StartsWith("3.11") -and -not $pyVersion.StartsWith("3.12") -and -not $pyVersion.StartsWith("3.13")) {
  throw "Python 3.11+ is required"
}

if (-not (Test-Path ".venv")) { py -3 -m venv .venv }
& .\.venv\Scripts\python -m pip install --upgrade pip
& .\.venv\Scripts\python -m pip install -r requirements.txt
& .\.venv\Scripts\python -m robot_voice.scripts.bootstrap_defaults
Write-Host "[setup] Done"
