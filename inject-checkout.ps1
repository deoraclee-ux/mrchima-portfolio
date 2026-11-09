# Inject Checkout Modal into index.html
Write-Host "Injecting checkout modal..." -ForegroundColor Cyan

# Read the checkout modal content
$checkoutModal = Get-Content "checkout-modal.html" -Raw -Encoding UTF8

# Read the current HTML
$html = Get-Content "index.html" -Raw -Encoding UTF8

# Check if already injected
if ($html -match "checkout-modal") {
    Write-Host "Checkout modal already injected!" -ForegroundColor Yellow
    exit 0
}

# Inject before </body>
$html = $html -replace '</body>', "$checkoutModal`n</body>"

# Save
$html | Set-Content "index.html" -NoNewline -Encoding UTF8

Write-Host "Checkout modal injected successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Update your Paystack public key in index.html:" -ForegroundColor Yellow
Write-Host "Search for: const PAYSTACK_PUBLIC_KEY = 'pk_test_YOUR_PUBLIC_KEY_HERE';" -ForegroundColor Yellow
Write-Host "Replace with your actual key from Paystack dashboard" -ForegroundColor Yellow
