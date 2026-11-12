// Tree Animation - Complete reverse-engineered from React
console.log('tree-interactive.js loaded');

(function() {
  'use strict';
  
  console.log('Tree animation script starting...');
  
  const peopleData = {
    'Olamide Baddo': {
      name: 'Olamide Baddo',
      image: 'images/inspiration/olamide-baddo.jpg',
      title: 'Nigerian Rapper & YBNL Boss',
      description: 'Nigerian hip-hop artist and YBNL boss. His journey from underground to mainstream, building an empire, and staying authentic inspires my entrepreneurial drive.',
      social: 'https://instagram.com/olamide'
    },
    'Elon Musk': {
      name: 'Elon Musk',
      image: 'images/inspiration/elon-musk.jpg',
      title: 'Entrepreneur & Innovator',
      description: 'Entrepreneur and innovator behind Tesla, SpaceX, and more. His relentless pursuit of ambitious goals and ability to execute complex technical visions drives my approach to building impactful technology.',
      social: 'https://twitter.com/elonmusk'
    },
    'Steve Jobs': {
      name: 'Steve Jobs',
      image: 'images/inspiration/steve-jobs.jpg',
      title: 'Co-founder of Apple Inc.',
      description: 'Co-founder of Apple Inc. His obsession with product design, user experience, and creating technology that "just works" shapes how I think about software craftsmanship.',
      social: 'https://en.wikipedia.org/wiki/Steve_Jobs'
    }
  };

  function init() {
    console.log('Initializing tree animation...');
    document.body.classList.add('tree-ready'); // Remove hiding CSS
    setupTreeAnimation();
    setupModals();
    // setupResponsive(); // REMOVED - CSS media queries handle this
  }

  function setupTreeAnimation() {
    console.log('Setting up tree animation...');
    
    const treeLine = document.querySelector('.tree-line');
    const treeFill = document.querySelector('.tree-fill');
    const treeStage = document.querySelector('.tree-stage');
    const peopleList = document.querySelectorAll('.tree-person:not(.tree-root)');
    const rootAvatar = document.querySelector('.tree-root');
    
    console.log('Found elements:', {
      treeLine: !!treeLine,
      treeFill: !!treeFill,
      treeStage: !!treeStage,
      peopleCount: peopleList.length,
      rootAvatar: !!rootAvatar
    });
    
    if (!treeLine || !treeFill) {
      console.error('Tree SVG elements not found!');
      return;
    }
    
    // Root always visible
    if (rootAvatar) {
      rootAvatar.classList.add('is-in');
      console.log('Root avatar made visible');
    }
    
    // Get complete path
    const completePath = treeLine.getAttribute('d');
    console.log('Complete path length:', completePath ? completePath.length : 0);
    
    if (!completePath) {
      console.warn('No path data found - showing all immediately');
      peopleList.forEach(p => p.classList.add('is-in'));
      return;
    }
    
    // Animation timing (from React code)
    const peopleCount = peopleList.length;
    const BASE_DURATION = 2300;
    const EXTRA_TIME = 45 * Math.min(peopleCount, 30);
    const TOTAL_DURATION = BASE_DURATION + EXTRA_TIME + 500;
    const DELAY_MS = 450;
    
    console.log('Animation timing:', {
      peopleCount,
      BASE_DURATION,
      EXTRA_TIME,
      TOTAL_DURATION,
      DELAY_MS
    });
    
    // Parse path into segments
    const pathSegments = [];
    const regex = /M[^Z]*Z/g;
    let match;
    
    while ((match = regex.exec(completePath)) !== null) {
      pathSegments.push(match[0]);
    }
    
    console.log('Path segments found:', pathSegments.length);
    
    // Assign timing to segments (simulating React limbs)
    const limbs = pathSegments.map((path, index) => {
      const progress = index / Math.max(pathSegments.length - 1, 1);
      const start = progress * TOTAL_DURATION * 0.8;
      const dur = Math.max(260, TOTAL_DURATION * 0.15);
      
      return { path, start, dur, index };
    });
    
    // Map avatars to completion times
    const peopleArray = Array.from(peopleList);
    const seats = peopleArray.map((person, index) => {
      const limbIndex = Math.floor((index / peopleArray.length) * limbs.length);
      const limb = limbs[Math.min(limbIndex, limbs.length - 1)];
      
      return {
        element: person,
        popAt: limb.start + limb.dur - 70,
        index
      };
    }).sort((a, b) => a.popAt - b.popAt);
    
    console.log('Seats configured:', seats.length);
    
    // Start animation immediately when script runs, not when visible
    // This prevents the flash of full tree before animation
    startTreeAnimation();
    
    function startTreeAnimation() {
      console.log('Starting tree animation...');
      
      // Check prefers-reduced-motion
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
        console.log('Reduced motion detected - skipping animation');
        treeLine.setAttribute('d', completePath);
        treeFill.setAttribute('d', completePath);
        peopleList.forEach(p => p.classList.add('is-in'));
        return;
      }
      
      // IMPORTANT: Reset paths to empty IMMEDIATELY before any frames
      treeLine.setAttribute('d', '');
      treeFill.setAttribute('d', '');
      peopleList.forEach(p => p.classList.remove('is-in'));
      
      console.log('Tree paths reset to empty');
      
      const startTime = performance.now();
      let visibleAvatarIndex = 0;
      let frameCount = 0;
      
      function animateFrame(currentTime) {
        const elapsed = currentTime - startTime;
        frameCount++;
        
        // Apply delay ONLY to the rendering, not to elapsed time tracking
        const renderElapsed = Math.max(0, elapsed - DELAY_MS);
        
        if (frameCount % 30 === 0) {
          console.log(`Frame ${frameCount}: elapsed ${Math.round(renderElapsed)}ms, avatars shown: ${visibleAvatarIndex}`);
        }
        
        // Build path from limbs that have started
        let currentPath = '';
        let activeLimbCount = 0;
        
        for (const limb of limbs) {
          const limbProgress = Math.max(0, Math.min((renderElapsed - limb.start) / limb.dur, 1));
          
          if (limbProgress > 0) {
            currentPath += limb.path;
            activeLimbCount++;
          }
        }
        
        // Update SVG
        treeLine.setAttribute('d', currentPath);
        treeFill.setAttribute('d', currentPath);
        
        // Show avatars at popAt time
        while (visibleAvatarIndex < seats.length && seats[visibleAvatarIndex].popAt <= renderElapsed) {
          seats[visibleAvatarIndex].element.classList.add('is-in');
          visibleAvatarIndex++;
        }
        
        // Continue or finish
        if (renderElapsed < TOTAL_DURATION) {
          requestAnimationFrame(animateFrame);
        } else {
          console.log('Animation complete!', {
            totalFrames: frameCount,
            finalElapsed: Math.round(elapsed),
            limbsDrawn: activeLimbCount,
            avatarsShown: visibleAvatarIndex
          });
          finishAnimation();
        }
      }
      
      requestAnimationFrame(animateFrame);
    }
    
    function finishAnimation() {
      treeLine.setAttribute('d', completePath);
      treeFill.setAttribute('d', completePath);
      peopleList.forEach(p => p.classList.add('is-in'));
      console.log('Animation finished - all elements visible');
    }
  }

  function setupModals() {
    const buttons = document.querySelectorAll('.tree-person button');
    console.log('Setting up modals for', buttons.length, 'buttons');
    
    buttons.forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        const name = this.querySelector('.tree-name')?.textContent.trim();
        if (name && peopleData[name]) {
          openModal(peopleData[name]);
        }
      });
    });
  }

  function openModal(person) {
    const overlay = document.createElement('div');
    overlay.className = 'cm-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'cm-modal';
    
    modal.innerHTML = `
      <div class="cm-hero">
        <img src="${person.image}" alt="${person.name}">
        <button type="button" class="cm-close" aria-label="Close">
          <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 6 6 18"></path>
            <path d="m6 6 12 12"></path>
          </svg>
        </button>
      </div>
      <div class="cm-body">
        <h2>${person.name}</h2>
        <p style="color: var(--ink-3); font-size: 13px; margin-bottom: 12px;">${person.title}</p>
        <p style="color: var(--ink-2); font-size: 15px; line-height: 1.6;">${person.description}</p>
        ${person.social ? `<a href="${person.social}" target="_blank" rel="noopener noreferrer" class="text-link" style="margin-top: 16px; display: inline-flex;">Visit profile →</a>` : ''}
      </div>
    `;
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
    document.body.style.overflow = 'hidden';
    
    requestAnimationFrame(() => {
      overlay.style.opacity = '1';
      modal.style.transform = 'translateY(0) scale(1)';
    });
    
    const closeBtn = modal.querySelector('.cm-close');
    closeBtn.addEventListener('click', () => closeModal(overlay));
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeModal(overlay);
    });
    
    const escHandler = (e) => {
      if (e.key === 'Escape') {
        closeModal(overlay);
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);
  }

  function closeModal(overlay) {
    const modal = overlay.querySelector('.cm-modal');
    overlay.style.opacity = '0';
    modal.style.transform = 'translateY(20px) scale(0.95)';
    setTimeout(() => {
      overlay.remove();
      document.body.style.overflow = '';
    }, 250);
  }

  // Critical CSS for modals only (flash prevention is now inline in HTML)
  const style = document.createElement('style');
  style.textContent = `
    .cm-overlay {
      opacity: 0;
      transition: opacity 0.3s ease-out;
    }
    
    .cm-modal {
      transform: translateY(20px) scale(0.95);
      transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.3s;
    }
    
    .cm-modal h2 {
      font-size: 20px;
      font-weight: 600;
      margin-bottom: 4px;
    }
  `;
  
  if (document.head.firstChild) {
    document.head.insertBefore(style, document.head.firstChild);
  } else {
    document.head.appendChild(style);
  }
  
  // No need to add tree-pre-js - it's handled by tree-ready class in init()

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
    console.log('Waiting for DOMContentLoaded...');
  } else {
    console.log('DOM already loaded, initializing now');
    init();
  }
})();
