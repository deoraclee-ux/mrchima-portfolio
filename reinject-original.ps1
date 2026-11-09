# Remove old modal and inject original design
Write-Host "Injecting original modal design..." -ForegroundColor Cyan

# Read current HTML
$html = Get-Content "index.html" -Raw -Encoding UTF8

# Remove old modal
$pattern = '(?s)<!-- ADD THIS TO YOUR index\.html BEFORE CLOSING.*?</script>\s*</body>'
if ($html -match $pattern) {
    Write-Host "Removing old modal..." -ForegroundColor Yellow
    $html = $html -replace $pattern, '</body>'
} else {
    $pattern2 = '(?s)<!-- Checkout Modal.*?</script>\s*</body>'
    if ($html -match $pattern2) {
        Write-Host "Removing old modal..." -ForegroundColor Yellow
        $html = $html -replace $pattern2, '</body>'
    }
}

# Read new modal
$newModal = Get-Content "checkout-modal-original.html" -Raw -Encoding UTF8

# Inject
$html = $html -replace '</body>', "$newModal`n</body>"

# Save
$html | Set-Content "index.html" -NoNewline -Encoding UTF8

Write-Host ""
Write-Host "SUCCESS! Original modal design injected!" -ForegroundColor Green
Write-Host ""
Write-Host "Changes:" -ForegroundColor Cyan
Write-Host "  - Original simple design (no labels)" -ForegroundColor White
Write-Host "  - Blue button (#007ACC)" -ForegroundColor White
Write-Host "  - Fixed price: N15,000" -ForegroundColor White
Write-Host "  - Paystack key loads from backend (secure)" -ForegroundColor White
Write-Host ""
Write-Host "Add your Paystack keys to backend/.env" -ForegroundColor Yellow
