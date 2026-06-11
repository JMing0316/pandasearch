# PandaSearch Init Script
# Calls POST /api/v1/init to create indexes and sync data
# Usage: .\init-search.ps1

$ErrorActionPreference = "Stop"

$API_URL = "http://localhost:8000/api/v1/init"

Write-Host "[PandaSearch] Calling init endpoint..." -ForegroundColor Cyan
Write-Host "  URL: $API_URL" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri $API_URL -Method POST -ContentType "application/json"

    Write-Host ""
    Write-Host "[OK] Init succeeded!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Yellow
    $response | ConvertTo-Json -Depth 10 | Write-Host
}
catch {
    Write-Host ""
    Write-Host "[ERROR] Init failed!" -ForegroundColor Red
    Write-Host ""

    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP Status: $statusCode" -ForegroundColor Red

        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $reader.BaseStream.Position = 0
        $reader.DiscardBufferedData()
        $errorBody = $reader.ReadToEnd()
        Write-Host "Details: $errorBody" -ForegroundColor Red
    }
    else {
        Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host ""
        Write-Host "[HINT] Common causes:" -ForegroundColor Yellow
        Write-Host "  1. Backend not running - check 'docker compose up'" -ForegroundColor Gray
        Write-Host "  2. Port not mapped - verify backend exposes 8000" -ForegroundColor Gray
        Write-Host "  3. Wrong table name - check configs/minimal.yaml" -ForegroundColor Gray
    }

    exit 1
}

Write-Host ""
Write-Host "[DONE] Visit http://localhost:3000 to use search." -ForegroundColor Green
