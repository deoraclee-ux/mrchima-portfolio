# Remove old modal and inject improved version
Write-Host "Removing old checkout modal and injecting improved version..." -ForegroundColor Cyan

# Read the current HTML
$html = Get-Content "index.html" -Raw -Encoding UTF8

# Find and remove old modal (from comment to script end)
$pattern = '(?s)<!-- ADD THIS TO YOUR index\.html BEFORE CLOSING.*?</script>\s*</body>'
if ($html -match $pattern) {
    Write-Host "Found old modal, removing..." -ForegroundColor Yellow
    $html = $html -replace $pattern, '</body>'
    Write-Host "Old modal removed!" -ForegroundColor Green
} else {
    Write-Host "No old modal found, checking alternative..." -ForegroundColor Yellow
    
    # Try alternative pattern
    $pattern2 = '(?s)<!-- Checkout Modal HTML -->.*?</script>\s*</body>'
    if ($html -match $pattern2) {
        Write-Host "Found old modal, removing..." -ForegroundColor Yellow
        $html = $html -replace $pattern2, '</body>'
        Write-Host "Old modal removed!" -ForegroundColor Green
    }
}

# Read the new checkout modal content
$checkoutModal = Get-Content "checkout-modal.html" -Raw -Encoding UTF8

# Inject before closing body tag
$html = $html -replace '</body>', "$checkoutModal`n</body>"

# Save
$html | Set-Content "index.html" -NoNewline -Encoding UTF8

Write-Host ""
Write-Host "SUCCESS! Improved checkout modal injected!" -ForegroundColor Green
Write-Host ""
Write-Host "Changes made:" -ForegroundColor Cyan
Write-Host "  - Better user-friendly placeholders" -ForegroundColor White
Write-Host "  - Smooth animations and focus effects" -ForegroundColor White
Write-Host "  - Pay button shows exact amount only" -ForegroundColor White
Write-Host "  - Fixed backend URL to localhost:8000" -ForegroundColor White
Write-Host "  - Added field labels for clarity" -ForegroundColor White
Write-Host "  - Better notice styling" -ForegroundColor White
Write-Host ""
Write-Host "IMPORTANT: Update Paystack public key in index.html" -ForegroundColor Yellow
Write-Host "Search for: PAYSTACK_PUBLIC_KEY" -ForegroundColor Yellow
