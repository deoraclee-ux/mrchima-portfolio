# Simple HTTP server to run the reconstructed site
$port = 8080

Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  SERVING RECONSTRUCTED MRBAYO.DEV" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "Opening in browser: http://localhost:$port" -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Python HTTP server
python -m http.server $port
