// Load shared navbar and footer across all pages
(function() {
    // Load navbar
    fetch('/shared/navbar.html')
        .then(response => response.text())
        .then(html => {
            const navPlaceholder = document.getElementById('navbar-placeholder');
            if (navPlaceholder) {
                navPlaceholder.outerHTML = html;
                // Set active link based on current page
                setActiveNavLink();
                // Initialize mobile menu toggle
                initMobileMenu();
            }
        })
        .catch(err => console.error('Failed to load navbar:', err));

    // Load footer
    fetch('/shared/footer.html')
        .then(response => response.text())
        .then(html => {
            const footerPlaceholder = document.getElementById('footer-placeholder');
            if (footerPlaceholder) {
                footerPlaceholder.outerHTML = html;
            }
        })
        .catch(err => console.error('Failed to load footer:', err));

    function setActiveNavLink() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-links a');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            // Remove active class from all
            link.classList.remove('active');
            link.removeAttribute('aria-current');
            
            // Check if this link matches current page
            if (href === currentPath || 
                (currentPath === '/' && href === '/') ||
                (currentPath.includes(href) && href !== '/' && href !== '/#contact')) {
                link.classList.add('active');
                link.setAttribute('aria-current', 'page');
            }
        });
    }

    function initMobileMenu() {
        // Mobile menu toggle
        const menuBtn = document.querySelector('.menu-btn');
        const navbar = document.querySelector('.navbar');
        
        if (menuBtn && navbar) {
            menuBtn.addEventListener('click', function(e) {
                e.stopPropagation();
                navbar.classList.toggle('open');
                const expanded = this.getAttribute('aria-expanded') === 'true';
                this.setAttribute('aria-expanded', !expanded);
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                const navLinks = document.querySelector('.nav-links');
                if (navbar.classList.contains('open') && 
                    navLinks && 
                    !navLinks.contains(e.target) && 
                    !menuBtn.contains(e.target)) {
                    navbar.classList.remove('open');
                    menuBtn.setAttribute('aria-expanded', 'false');
                }
            });
            
            // Close menu when clicking a link
            const navLinks = document.querySelectorAll('.nav-links a');
            navLinks.forEach(link => {
                link.addEventListener('click', () => {
                    navbar.classList.remove('open');
                    menuBtn.setAttribute('aria-expanded', 'false');
                });
            });
        }

        // Support button navigation
        const supportBtn = document.querySelector('.nav-support');
        if (supportBtn) {
            supportBtn.addEventListener('click', () => {
                window.location.href = '/#support';
            });
        }
    }
})();
