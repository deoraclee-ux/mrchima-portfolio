// iOS Progress Bar and Toast Notification System

// Enhance submitHireForm to use iOS progress
const originalSubmitHireForm = window.submitHireForm;
window.submitHireForm = async function(event) {
  event.preventDefault();
  const submitBtn = document.getElementById('submit-btn');
  const successMessage = document.getElementById('success-message');
  const errorMessage = document.getElementById('error-message');
  
  // Hide previous messages
  successMessage.classList.remove('show');
  errorMessage.classList.remove('show');
  
  // Validation
  if (!window.selectedProjectType) {
    showError('Please select a project type');
    return;
  }
  const description = document.getElementById('project-description').value.trim();
  if (!description) {
    showError('Please describe your project');
    return;
  }
  const name = document.getElementById('contact-name').value.trim();
  const email = document.getElementById('contact-email').value.trim();
  if (!name) {
    showError('Please enter your name');
    return;
  }
  if (!email || !isValidEmail(email)) {
    showError('Please enter a valid email address');
    return;
  }
  const selectedMethods = Array.from(document.querySelectorAll('.hf-chip.selected'))
    .map(chip => chip.dataset.method);
  if (selectedMethods.length === 0) {
    showError('Please select at least one contact method');
    return;
  }
  const phone = document.getElementById('contact-phone').value.trim();
  if ((selectedMethods.includes('whatsapp') || selectedMethods.includes('phone')) && !phone) {
    showError('Phone number is required when selecting WhatsApp or Phone call');
    return;
  }
  
  const formData = {
    projectType: sanitizeInput(window.selectedProjectType),
    description: sanitizeInput(description),
    name: sanitizeInput(name),
    email: sanitizeInput(email),
    phone: sanitizeInput(phone),
    sameWhatsapp: document.getElementById('same-whatsapp').checked,
    contactMethods: selectedMethods,
    timestamp: new Date().toISOString()
  };
  
  // Show iOS progress bar
  showProgressBar();
  submitBtn.disabled = true;
  
  // Set a longer timeout for the fetch (30 seconds)
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000);
  
  try {
    const response = await fetch(window.EMAIL_ENDPOINT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify(formData),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    const result = await response.json();
    
    if (response.ok) {
      completeProgressBar();
      setTimeout(() => {
        hideProgressBar();
        showToast('Message sent successfully', 'success');
        
        // Reset form
        document.getElementById('hire-form').reset();
        window.selectedProjectType = null;
        document.querySelectorAll('.hf-option').forEach(el => el.classList.remove('selected'));
        document.querySelectorAll('.hf-chip').forEach(el => {
          el.classList.remove('selected');
          const methodName = el.dataset.method === 'whatsapp' ? 'WhatsApp' : 
                             el.dataset.method === 'email' ? 'Email' : 'Phone call';
          el.innerHTML = methodName;
        });
        const whatsappBtn = document.querySelector('[data-method="whatsapp"]');
        if (whatsappBtn) {
          whatsappBtn.classList.add('selected');
          whatsappBtn.innerHTML = 'WhatsApp';
        }
        if (window.updateCharCount) window.updateCharCount();
      }, 500);
    } else {
      throw new Error(result.message || result.detail || 'Failed to send request');
    }
  } catch (error) {
    console.error('Submission error:', error);
    hideProgressBar();
    showToast('Failed to send. Please try again', 'error');
  } finally {
    submitBtn.disabled = false;
  }
};

// iOS Progress Bar Functions
function showProgressBar() {
  let progressBar = document.getElementById('ios-progress-bar');
  if (!progressBar) {
    progressBar = document.createElement('div');
    progressBar.id = 'ios-progress-bar';
    progressBar.innerHTML = '<div class="ios-progress-fill"></div>';
    document.body.appendChild(progressBar);
  }
  progressBar.classList.add('show');
  const fill = progressBar.querySelector('.ios-progress-fill');
  fill.style.width = '0%';
  setTimeout(() => {
    fill.style.width = '90%';
  }, 10);
}

function completeProgressBar() {
  const progressBar = document.getElementById('ios-progress-bar');
  if (progressBar) {
    const fill = progressBar.querySelector('.ios-progress-fill');
    fill.style.width = '100%';
  }
}

function hideProgressBar() {
  const progressBar = document.getElementById('ios-progress-bar');
  if (progressBar) {
    setTimeout(() => {
      progressBar.classList.remove('show');
      const fill = progressBar.querySelector('.ios-progress-fill');
      fill.style.width = '0%';
    }, 300);
  }
}

// iOS Toast Notification
function showToast(message, type = 'success') {
  let toast = document.getElementById('ios-toast');
  if (!toast) {
    toast = document.createElement('div');
    toast.id = 'ios-toast';
    toast.innerHTML = `
      <svg class="toast-icon" width="20" height="20" viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M7 10L9 12L13 8M19 10C19 14.9706 14.9706 19 10 19C5.02944 19 1 14.9706 1 10C1 5.02944 5.02944 1 10 1C14.9706 1 19 5.02944 19 10Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <span class="toast-message"></span>
    `;
    document.body.appendChild(toast);
  }
  
  toast.className = 'ios-toast ' + type;
  toast.querySelector('.toast-message').textContent = message;
  
  setTimeout(() => toast.classList.add('show'), 10);
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}
