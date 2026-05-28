$ErrorActionPreference = "Stop"

Write-Host "CenitForge smoke check" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan

$RequiredFiles = @(
    "templates\{{cookiecutter.project_slug}}\tools\enforcement_verifier.py",
    "templates\{{cookiecutter.project_slug}}\sanitization\gateway.py",
    "templates\{{cookiecutter.project_slug}}\tests\shadow\shadow_safety_contract.py",
    "templates\{{cookiecutter.project_slug}}\ci\blast_radius_gate.py",
    "templates\{{cookiecutter.project_slug}}\tools\semantic_drift_detector.py"
)

$Errors = 0

foreach ($File in $RequiredFiles) {
    if (Test-Path $File) {
        Write-Host "OK  $File" -ForegroundColor Green
    } else {
        Write-Host "MISSING  $File" -ForegroundColor Red
        $Errors++
    }
}

Write-Host ""
Write-Host "Python syntax checks" -ForegroundColor Cyan

foreach ($File in $RequiredFiles) {
    if (Test-Path $File) {
        python -m py_compile $File
        if ($LASTEXITCODE -eq 0) {
            Write-Host "OK syntax  $File" -ForegroundColor Green
        } else {
            Write-Host "FAIL syntax  $File" -ForegroundColor Red
            $Errors++
        }
    }
}

Write-Host ""
Write-Host "Minimal sanitization smoke test" -ForegroundColor Cyan

$Gateway = "templates\{{cookiecutter.project_slug}}\sanitization\gateway.py"

if (Test-Path $Gateway) {
    $TempPayload = Join-Path $env:TEMP "cenitforge_payload_test.txt"
    "User email: test@example.com`nAPI key: STRIPE_TEST_KEY_REDACTED_EXAMPLE" | Set-Content -Path $TempPayload -Encoding UTF8

    python $Gateway --file $TempPayload --destination smoke-test

    if ($LASTEXITCODE -ne 0) {
        Write-Host "OK sanitizer blocked sensitive payload" -ForegroundColor Green
    } else {
        Write-Host "WARN sanitizer allowed payload; review policy expectations" -ForegroundColor Yellow
    }

    Remove-Item $TempPayload -Force
}

Write-Host ""
if ($Errors -eq 0) {
    Write-Host "Smoke check completed" -ForegroundColor Green
    exit 0
} else {
    Write-Host "Smoke check failed with $Errors error(s)" -ForegroundColor Red
    exit 1
}
