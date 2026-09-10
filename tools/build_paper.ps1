$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$jobs = @(
    @{ Folder = 'paper/en'; Engine = '-pdf'; File = 'main.tex' },
    @{ Folder = 'paper/en'; Engine = '-pdf'; File = 'supplementary.tex' },
    @{ Folder = 'paper/zh'; Engine = '-xelatex'; File = 'main.tex' }
)
foreach ($job in $jobs) {
    Push-Location (Join-Path $repoRoot $job.Folder)
    try {
        & latexmk $job.Engine -interaction=nonstopmode -halt-on-error $job.File
        if ($LASTEXITCODE -ne 0) { throw "Compilation failed: $($job.Folder)/$($job.File)" }
    } finally { Pop-Location }
}
