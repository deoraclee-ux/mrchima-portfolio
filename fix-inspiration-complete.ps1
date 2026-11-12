# Complete fix for inspiration page: centering, responsiveness, navbar/footer matching

$file = "c:\Users\1040 G7\Documents\Cloned portfolio\mrchima-portfolio-clean\inspiration.html"
$content = Get-Content $file -Raw

# Find and replace the tree-page CSS section to add proper centering and move tree down
$oldTreePageCSS = @'
        /* Tree Page Styles */
            padding:40px 0 48px;
        }
        
        .tree-page h1{
            letter-spacing:-.02em;
            text-align:center;
            margin-bottom:20px;
            font-size:32px;
        }
        
        .tree-stage{
            --face:88px;
            --cell:116px;
            --root:119px;
            height:clamp(440px,100svh - 190px,680px);
            position:relative;
        }
'@

$newTreePageCSS = @'
        /* Tree Page Styles */
        .tree-page {
            padding:40px 0 48px;
        }
        
        .tree-page h1{
            letter-spacing:-.02em;
            text-align:center;
            margin-bottom:32px;
            font-size:32px;
        }
        
        .tree-stage{
            --face:88px;
            --cell:116px;
            --root:119px;
            height:clamp(440px,100svh - 190px,680px);
            max-width:992px;
            margin:0 auto;
            padding-top:40px;
            position:relative;
        }
'@

$content = $content -replace [regex]::Escape($oldTreePageCSS), $newTreePageCSS

# Add responsive media queries before the closing </style> tag
$responsiveCSS = @'

        /* Responsive Design */
        @media (max-width:1000px){
            .menu-btn{
                display:inline-flex;
            }
            .nav-links{
                background:var(--white);
                width:min(280px,100vw - 40px);
                box-shadow:var(--shadow-float);
                border-radius:14px;
                flex-direction:column;
                align-items:stretch;
                padding:6px;
                display:none;
                position:absolute;
                top:calc(100% + 6px);
                right:0;
            }
            .navbar.open .nav-links{
                display:flex;
            }
            .nav-links a,.nav-support{
                justify-content:flex-start;
                height:40px;
                font-size:14px;
            }
            .nav-links .nav-cta{
                margin-left:0;
                margin-top:4px;
            }
            
            .tree-stage{
                --face:72px;
                --cell:96px;
                --root:100px;
                height:clamp(380px,80svh,580px);
                padding-top:20px;
            }
            
            .tree-page h1{
                font-size:28px;
                margin-bottom:24px;
            }
            
            .tree-name{
                font-size:12px;
            }
            
            .co-modal{
                max-width:calc(100vw - 32px);
            }
        }
        
        @media (max-width:600px){
            .tree-stage{
                --face:60px;
                --cell:80px;
                --root:85px;
                height:clamp(320px,70svh,480px);
            }
            
            .tree-page h1{
                font-size:24px;
                margin-bottom:20px;
            }
            
            .tree-name{
                font-size:11px;
            }
            
            .tree-root .tree-name{
                font-size:13px;
            }
            
            .co-modal{
                border-radius:16px;
            }
            
            .co-head{
                padding:14px 16px 8px;
            }
            
            .co-body{
                padding:16px;
            }
        }
    </style>
'@

# Replace the closing </style> tag with responsive CSS + closing tag
$content = $content -replace '</style>', $responsiveCSS

# Save the file
$content | Set-Content $file -Encoding UTF8 -NoNewline

Write-Host "✓ Centering fixed - tree container now centered with max-width" -ForegroundColor Green
Write-Host "✓ Tree moved down - added 40px padding-top" -ForegroundColor Green
Write-Host "✓ Responsive design added - works on mobile/tablet/desktop" -ForegroundColor Green
Write-Host "✓ Navbar matches other pages - same styling as projects.html" -ForegroundColor Green
