// Team Hierarchy Interactive Features
document.addEventListener('DOMContentLoaded', function() {
    initializeTeamHierarchy();
});

function initializeTeamHierarchy() {
    // Add click handlers to profile cards
    const profileCards = document.querySelectorAll('.profile-card');
    
    profileCards.forEach(card => {
        // Add hover effect with 3D tilt
        card.addEventListener('mousemove', handleCardTilt);
        card.addEventListener('mouseleave', resetCardTilt);
        
        // Add ripple effect on click
        card.addEventListener('click', createRipple);
    });

    // Initialize tooltips
    initializeTooltips();
    
    // Add smooth scroll animations
    observeElements();
    
    // Initialize search functionality if needed
    initializeSearch();
}

// 3D Tilt Effect on Hover
function handleCardTilt(e) {
    const card = e.currentTarget;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = (y - centerY) / 10;
    const rotateY = (centerX - x) / 10;
    
    card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-8px)`;
}

function resetCardTilt(e) {
    const card = e.currentTarget;
    card.style.transform = '';
}

// Ripple Effect
function createRipple(e) {
    const card = e.currentTarget;
    const ripple = document.createElement('span');
    const rect = card.getBoundingClientRect();
    
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    card.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Add ripple CSS dynamically
const style = document.createElement('style');
style.textContent = `
    .profile-card {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.6);
        transform: scale(0);
        animation: ripple-animation 0.6s ease-out;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

// Tooltips
function initializeTooltips() {
    const detailItems = document.querySelectorAll('.detail-item span');
    
    detailItems.forEach(item => {
        if (item.scrollWidth > item.clientWidth) {
            item.setAttribute('title', item.textContent);
        }
    });
}

// Intersection Observer for Scroll Animations
function observeElements() {
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    const sections = document.querySelectorAll('.hierarchy-section');
    sections.forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
        observer.observe(section);
    });
}

// Search Functionality (Optional Enhancement)
function initializeSearch() {
    // Check if search input exists
    const searchInput = document.querySelector('.hierarchy-search');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        const cards = document.querySelectorAll('.profile-card');
        
        cards.forEach(card => {
            const name = card.querySelector('.profile-name').textContent.toLowerCase();
            const position = card.querySelector('.profile-position').textContent.toLowerCase();
            const badge = card.querySelector('.profile-badge').textContent.toLowerCase();
            
            const matches = name.includes(searchTerm) || 
                          position.includes(searchTerm) || 
                          badge.includes(searchTerm);
            
            if (matches) {
                card.style.display = '';
                card.style.animation = 'fadeIn 0.3s ease-in-out';
            } else {
                card.style.display = 'none';
            }
        });
        
        // Update section visibility
        updateSectionVisibility();
    });
}

function updateSectionVisibility() {
    const sections = document.querySelectorAll('.hierarchy-section');
    
    sections.forEach(section => {
        const visibleCards = section.querySelectorAll('.profile-card:not([style*="display: none"])');
        if (visibleCards.length === 0) {
            section.style.display = 'none';
        } else {
            section.style.display = '';
        }
    });
}

// Status Indicator Updates (if real-time data available)
function updateOnlineStatus() {
    // This would be connected to a WebSocket or polling mechanism
    // For now, it's a placeholder for future enhancement
    const statusIndicators = document.querySelectorAll('.status-indicator');
    
    statusIndicators.forEach(indicator => {
        // Example: fetch status from API
        // updateIndicatorStatus(indicator);
    });
}

// Card Interaction Analytics (Optional)
function trackCardInteraction(employeeId, action) {
    // Send analytics data
    console.log(`Employee ${employeeId} - Action: ${action}`);
    // You can integrate with your analytics service here
}

// Add event listeners for analytics
document.querySelectorAll('.profile-card').forEach(card => {
    const employeeId = card.getAttribute('data-employee-id');
    
    card.addEventListener('click', () => {
        trackCardInteraction(employeeId, 'card_click');
    });
});

document.querySelectorAll('.action-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        const card = e.target.closest('.profile-card');
        const employeeId = card?.getAttribute('data-employee-id');
        const action = e.target.closest('.action-btn').textContent.trim();
        
        if (employeeId) {
            trackCardInteraction(employeeId, `button_${action.toLowerCase().replace(/\s+/g, '_')}`);
        }
    });
});

// Keyboard Navigation
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        // Close any open modals or reset focus
        document.activeElement.blur();
    }
});

// Print Functionality
function printHierarchy() {
    window.print();
}

// Export Functionality (Optional)
function exportHierarchy() {
    // Implement export to PDF or image
    console.log('Export hierarchy chart');
}

// Refresh Data
function refreshHierarchyData() {
    // Reload the page or fetch new data via AJAX
    location.reload();
}

// Add print styles
const printStyle = document.createElement('style');
printStyle.textContent = `
    @media print {
        .hierarchy-header::before {
            display: none;
        }
        
        .profile-card {
            break-inside: avoid;
            box-shadow: none;
            border: 1px solid #e5e7eb;
        }
        
        .action-btn {
            display: none;
        }
        
        .status-indicator {
            display: none;
        }
    }
`;
document.head.appendChild(printStyle);

// Accessibility Enhancements
function enhanceAccessibility() {
    // Add ARIA labels
    const cards = document.querySelectorAll('.profile-card');
    cards.forEach(card => {
        const name = card.querySelector('.profile-name')?.textContent;
        const position = card.querySelector('.profile-position')?.textContent;
        card.setAttribute('role', 'article');
        card.setAttribute('aria-label', `${name}, ${position}`);
    });
    
    // Add keyboard navigation
    cards.forEach((card, index) => {
        card.setAttribute('tabindex', '0');
        
        card.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const link = card.querySelector('.action-btn');
                if (link) link.click();
            }
        });
    });
}

// Initialize accessibility features
enhanceAccessibility();

// Performance: Lazy load images
function lazyLoadImages() {
    const images = document.querySelectorAll('.profile-image');
    
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                }
                imageObserver.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        if (img.dataset.src) {
            imageObserver.observe(img);
        }
    });
}

// Initialize lazy loading
lazyLoadImages();

// Console log for debugging
console.log('Team Hierarchy initialized successfully');
