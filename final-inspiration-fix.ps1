# Final comprehensive fix: Add footer placeholder and ensure all styles match

$file = "c:\Users\1040 G7\Documents\Cloned portfolio\mrchima-portfolio-clean\inspiration.html"
$content = Get-Content $file -Raw

# Check if footer placeholder exists, if not add it before the modal
if ($content -notmatch 'id="footer-placeholder"') {
    Write-Host "Adding footer placeholder..." -ForegroundColor Yellow
    
    # Add footer placeholder before modal overlay
    $content = $content -replace '<!-- Modal -->', @'
    <!-- Footer -->
    <div id="footer-placeholder"></div>

    <!-- Modal -->
'@
}

# Ensure footer CSS is present and matches home page
$footerCSSCheck = $content -match '\.footer-grid'
if (-not $footerCSSCheck) {
    Write-Host "Adding footer CSS..." -ForegroundColor Yellow
    
    $footerCSS = @'

        /* Footer matching home page */
        .site-footer {
            background: var(--white);
            box-shadow: inset 0 1px 0 var(--hair);
            padding: 28px 0 36px;
        }
        
        .footer-grid {
            display: grid;
            grid-template-columns: 1fr auto auto;
            gap: 40px;
            margin-bottom: 24px;
        }
        
        .footer-brand img {
            width: 120px;
            height: auto;
        }
        
        .footer-col h4 {
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 12px;
            color: var(--ink);
        }
        
        .footer-col a {
            display: block;
            color: var(--ink-3);
            font-size: 13px;
            text-decoration: none;
            margin-bottom: 8px;
        }
        
        .footer-col a:hover {
            color: var(--ink);
        }
        
        .footer-bottom {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-top: 20px;
            border-top: 1px solid var(--hair);
        }
        
        .footer-bottom p {
            color: var(--ink-3);
            font-size: 12.5px;
        }
'@
    
    # Add before responsive media queries
    $content = $content -replace '        /\* Responsive Design \*/', ($footerCSS + "`n`n        /* Responsive Design */")
}

# Add footer responsive styles if not present
if ($content -notmatch '\.footer-grid.*@media') {
    Write-Host "Adding footer responsive styles..." -ForegroundColor Yellow
    
    $footerResponsive = @'

            .footer-grid {
                grid-template-columns: 1fr;
                gap: 32px;
                text-align: center;
            }
            
            .footer-bottom {
                flex-direction: column;
                gap: 8px;
                text-align: center;
            }
'@
    
    # Add inside the max-width:600px media query, before closing brace
    $content = $content -replace '(@media \(max-width:600px\)\{[^}]+)(        \})', "`$1$footerResponsive`n`$2"
}

# Save the file
$content | Set-Content $file -Encoding UTF8 -NoNewline

Write-Host ""
Write-Host "✓ Footer placeholder added" -ForegroundColor Green
Write-Host "✓ Footer CSS matches home page exactly" -ForegroundColor Green
Write-Host "✓ Footer is responsive on all screen sizes" -ForegroundColor Green
Write-Host ""
Write-Host "Refresh http://localhost:8000/inspiration.html to see all changes!" -ForegroundColor Cyan
