# Permanent Encoding Fix Script
# This replaces all problematic characters with HTML entities

Write-Host "Starting permanent encoding fix..." -ForegroundColor Green

# Define replacements (character -> HTML entity)
$replacements = @{
    '₦' = '&#8358;'  # Naira symbol
    '©' = '&#169;'    # Copyright symbol
    '✓' = '&#x2713;'  # Checkmark
    'Â©' = '&#169;'   # Corrupted copyright
}

# Files to fix (only the main active files)
$files = @(
    'index.html',
    'source-code.html',
    'hire.html',
    'shop.html',
    'classes.html',
    'projects.html',
    'shared/footer.html',
    'shared/navbar.html'
)

foreach ($file in $files) {
    if (Test-Path $file) {
        Write-Host "Fixing $file..." -ForegroundColor Yellow
        
        # Read file as UTF-8
        $content = Get-Content $file -Raw -Encoding UTF8
        
        # Replace each problematic character
        foreach ($char in $replacements.Keys) {
            $entity = $replacements[$char]
            if ($content -match [regex]::Escape($char)) {
                $count = ([regex]::Matches($content, [regex]::Escape($char))).Count
                $content = $content -replace [regex]::Escape($char), $entity
                Write-Host "  Replaced $count instances of '$char' with '$entity'" -ForegroundColor Cyan
            }
        }
        
        # Save with UTF-8 BOM for maximum compatibility
        $utf8Bom = New-Object System.Text.UTF8Encoding $true
        [System.IO.File]::WriteAllText((Resolve-Path $file).Path, $content, $utf8Bom)
        
        Write-Host "  ✓ Saved with UTF-8 BOM" -ForegroundColor Green
    }
}

Write-Host "`nEncoding fix complete!" -ForegroundColor Green
Write-Host "All naira symbols (₦), copyright (©), and checkmarks (✓) have been replaced with HTML entities." -ForegroundColor Green
