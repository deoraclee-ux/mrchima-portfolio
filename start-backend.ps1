# Start Backend Server
Write-Host "Starting Mr Chima Backend Server..." -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "ERROR: backend\.env file not found!" -ForegroundColor Red
    Write-Host "Please configure your credentials in backend\.env" -ForegroundColor Yellow
    exit 1
}

# Check for product files
$missingFiles = @()
if (-not (Test-Path "backend\downloads\Oracle-Weather-App.zip")) {
    $missingFiles += "Oracle-Weather-App.zip"
}
if (-not (Test-Path "backend\downloads\mr-chima-ai-agent.zip")) {
    $missingFiles += "mr-chima-ai-agent.zip"
}

if ($missingFiles.Count -gt 0) {
    Write-Host "WARNING: Missing product files in backend\downloads\:" -ForegroundColor Yellow
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Start server
Write-Host "Server starting on http://localhost:8000" -ForegroundColor Green
Write-Host "API docs available at http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

cd backend
py -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
