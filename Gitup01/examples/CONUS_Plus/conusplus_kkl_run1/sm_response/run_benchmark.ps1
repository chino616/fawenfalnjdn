param(
    [Parameter(Mandatory=$true)][string]$OutputDir,
    [string]$Python = "python",
    [ValidateSet("all","predictions","validate","report")][string]$Stage = "all"
)
$ErrorActionPreference = "Stop"
$runner = Join-Path (Split-Path -Parent $PSScriptRoot) "run_benchmark.py"
& $Python -B $runner --method sm --output-dir $OutputDir --stage $Stage
if ($LASTEXITCODE -ne 0) { throw "The benchmark did not complete successfully." }
