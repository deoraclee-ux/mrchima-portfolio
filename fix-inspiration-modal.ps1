# Script to add modal HTML and fix JavaScript in inspiration.html

$filePath = "c:\Users\1040 G7\Documents\Cloned portfolio\mrchima-portfolio-clean\inspiration.html"
$content = Get-Content $filePath -Raw

# Modal HTML to insert before </body>
$modalHTML = @'

    <!-- Modal -->
    <div class="co-overlay" id="modalOverlay">
        <div class="co-modal">
            <div class="co-head">
                <div class="tree-sheet-who">
                    <div class="tree-face" id="modalFace">
                        AC
                    </div>
                    <h3 id="modalName">Person Name</h3>
                </div>
                <button class="co-close" onclick="closeModal()" aria-label="Close">
                    <svg fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                        <path d="M6 18L18 6M6 6l12 12"/>
                    </svg>
                </button>
            </div>
            <div class="co-body tree-sheet-body">
                <section id="aboutSection">
                    <h4>About</h4>
                    <p id="modalAbout">About text will appear here.</p>
                </section>
                <section id="whySection" style="display:none;">
                    <h4>Why they inspire me</h4>
                    <p id="modalWhy">Why text will appear here.</p>
                </section>
                <p class="tree-credit" id="creditSection" style="display:none;"></p>
            </div>
        </div>
    </div>

'@

# New complete JavaScript to replace existing
$newJS = @'
    <!-- Load shared components -->
    <script src="/shared/components.js"></script>
    <!-- Load inspiration people data -->
    <script src="/data/inspiration-people.js"></script>
    <script>
        // Modal functions
        function openModal() {
            document.getElementById('modalOverlay').classList.add('active');
            document.body.style.overflow = 'hidden';
        }
        
        function closeModal() {
            document.getElementById('modalOverlay').classList.remove('active');
            document.body.style.overflow = '';
        }
        
        // Close modal when clicking outside
        document.getElementById('modalOverlay').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // Update modal with person data when clicked
        function showPersonModal(personId) {
            const person = inspirationPeople.find(p => p.id === personId);
            if (!person) return;
            
            document.getElementById('modalName').textContent = person.name;
            document.getElementById('modalAbout').textContent = person.about;
            
            // Update face image or initials
            const modalFace = document.getElementById('modalFace');
            if (person.image) {
                modalFace.innerHTML = `<img src="${person.image}" alt="${person.name}">`;
            } else {
                // Show initials if no image
                const initials = person.name.split(' ').map(n => n[0]).join('');
                modalFace.textContent = initials;
            }
            
            // Update "About" heading - "About" for mentors, "About me" for root
            const aboutHeading = document.querySelector('#aboutSection h4');
            if (aboutHeading) {
                aboutHeading.textContent = person.isMe ? 'About me' : 'About';
            }
            
            // Update why section
            const whySection = document.getElementById('whySection');
            const modalWhy = document.getElementById('modalWhy');
            if (person.why) {
                whySection.style.display = 'block';
                modalWhy.textContent = person.why;
            } else {
                // Hide why section if person doesn't have it (for root person)
                whySection.style.display = 'none';
            }
            
            // Add image credit
            const creditSection = document.getElementById('creditSection');
            if (person.imageCredit) {
                creditSection.style.display = 'block';
                creditSection.textContent = person.imageCredit;
            } else {
                creditSection.style.display = 'none';
            }
            
            openModal();
        }
        
        // Expose function globally for onclick handlers
        window.showPersonModal = showPersonModal;
    </script>
</body>
</html>
'@

# First, remove old JS section if present
if ($content -match '<!-- Load shared components -->[\s\S]*?<\/html>?') {
    $content = $content -replace '<!-- Load shared components -->[\s\S]*?<\/html>?', ''
}

# Insert modal HTML and new JS before </body>
$content = $content -replace '</body>[\s\S]*', ($modalHTML + $newJS)

# Save the file
$content | Set-Content $filePath -Encoding UTF8 -NoNewline

Write-Host "Modal HTML and JavaScript added successfully!" -ForegroundColor Green
