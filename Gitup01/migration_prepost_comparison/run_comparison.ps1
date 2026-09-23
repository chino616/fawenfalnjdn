param(
    [string]$Python = "F:\Work\.codex_conda_envs\codex-py311\python.exe",
    [string]$LegacyRoot = "F:\Work\2026-07-15 CEvNSpyEFT-Local\CEvNS-pyEFT-main\CEvNS-pyEFT-main",
    [string]$RepoRoot = "F:\Work\2026-07-15 CEvNSpyEFT-Local\260820Gitup1-Flavor\git-worktree-f0\Gitup01"
)

$ErrorActionPreference = "Stop"
$Here = Split-Path -Parent $MyInvocation.MyCommand.Path
$Out = Join-Path $Here "outputs"
New-Item -ItemType Directory -Force -Path $Out | Out-Null

function Invoke-Checked {
    param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Command)
    & $Command[0] $Command[1..($Command.Count - 1)]
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $($Command -join ' ')"
    }
}

Invoke-Checked $Python (Join-Path $Here "collect_legacy_statistics.py") --source-root $LegacyRoot --out (Join-Path $Out "legacy_statistics_outputs.json")
Invoke-Checked $Python (Join-Path $Here "collect_migrated_statistics.py") --repo-root $RepoRoot --out (Join-Path $Out "migrated_statistics_outputs.json")
Invoke-Checked $Python (Join-Path $Here "compare_statistics_outputs.py") --legacy (Join-Path $Out "legacy_statistics_outputs.json") --migrated (Join-Path $Out "migrated_statistics_outputs.json") --out-dir $Out

