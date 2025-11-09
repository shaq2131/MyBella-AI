/**
 * MyBella - Main JavaScript Application
 * Handles core functionality, UI interactions, and utilities
 */

class MyBella {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.setupNotifications();
        this.handleAuthForms();
        this.setupMobileMenu();
    }

    setupEventListeners() {
        // Global event listeners
        document.addEventListener('DOMContentLoaded', () => {
            this.onDOMReady();
        });

        // Flash message close buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('alert-close')) {
                this.closeAlert(e.target.parentElement);
            }
        });

        // Modal close on outside click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal-overlay')) {
                this.closeModal(e.target);
            }
        });

        // Escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const openModal = document.querySelector('.modal-overlay:not(.hidden)');
                if (openModal) {
                    this.closeModal(openModal);
                }
            }
        });

        // Form validation
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('form-input')) {
                this.validateField(e.target);
            }
        });
    }

    onDOMReady() {
        // Initialize tooltips
        this.initTooltips();
        
        // Initialize animations
        this.initAnimations();
        
        // Setup auto-resize textareas
        this.setupAutoResize();
        
        // Initialize file upload previews
        this.initFileUploads();
        
        console.log('🎉 MyBella initialized successfully!');
    }

    initializeComponents() {
        // Initialize any component-specific functionality
        this.initDropdowns();
        this.initTabs();
        this.initLoadingStates();
    }

    setupNotifications() {
        // Request notification permission if supported
        if ('Notification' in window && Notification.permission === 'default') {
            Notification.requestPermission();
        }
    }

    // Alert/Flash message handling
    showAlert(message, type = 'success', duration = 5000) {
        const alertContainer = this.getOrCreateAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = `alert alert-${type}`;
        alert.innerHTML = `
            ${message}
            <button type="button" class="alert-close" onclick="myBella.closeAlert(this.parentElement)">×</button>
        `;
        
        alertContainer.appendChild(alert);
        
        // Auto-hide after duration
        if (duration > 0) {
            setTimeout(() => {
                this.closeAlert(alert);
            }, duration);
        }
        
        return alert;
    }

    closeAlert(alertElement) {
        alertElement.style.opacity = '0';
        alertElement.style.transform = 'translateX(100%)';
        
        setTimeout(() => {
            if (alertElement.parentNode) {
                alertElement.parentNode.removeChild(alertElement);
            }
        }, 300);
    }

    getOrCreateAlertContainer() {
        let container = document.querySelector('.flash-messages');
        if (!container) {
            container = document.createElement('div');
            container.className = 'flash-messages';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 1000;
                max-width: 400px;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    // Modal handling
    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.classList.remove('hidden');
            document.body.style.overflow = 'hidden';
            
            // Focus first input in modal
            const firstInput = modal.querySelector('input, textarea, select');
            if (firstInput) {
                setTimeout(() => firstInput.focus(), 100);
            }
        }
    }

    closeModal(modal) {
        if (typeof modal === 'string') {
            modal = document.getElementById(modal);
        }
        
        if (modal) {
            modal.classList.add('hidden');
            document.body.style.overflow = '';
        }
    }

    // Mobile menu functionality
    setupMobileMenu() {
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        const mobileNav = document.getElementById('mobileNav');
        
        if (mobileMenuBtn && mobileNav) {
            mobileMenuBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleMobileMenu();
            });

            // Close menu when clicking on a link
            mobileNav.addEventListener('click', (e) => {
                if (e.target.tagName === 'A') {
                    this.closeMobileMenu();
                }
            });

            // Close menu when clicking outside
            document.addEventListener('click', (e) => {
                if (!mobileMenuBtn.contains(e.target) && !mobileNav.contains(e.target)) {
                    this.closeMobileMenu();
                }
            });

            // Close menu on window resize to desktop size
            window.addEventListener('resize', () => {
                if (window.innerWidth >= 768) {
                    this.closeMobileMenu();
                }
            });
        }
    }

    toggleMobileMenu() {
        const mobileNav = document.getElementById('mobileNav');
        
        if (mobileNav) {
            const isActive = mobileNav.classList.contains('active');
            
            if (isActive) {
                this.closeMobileMenu();
            } else {
                this.openMobileMenu();
            }
        }
    }

    openMobileMenu() {
        const mobileNav = document.getElementById('mobileNav');
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        
        if (mobileNav && mobileMenuBtn) {
            mobileNav.classList.add('active');
            mobileMenuBtn.textContent = 'Close';
            mobileMenuBtn.setAttribute('aria-expanded', 'true');
            document.body.style.overflow = 'hidden';
        }
    }

    closeMobileMenu() {
        const mobileNav = document.getElementById('mobileNav');
        const mobileMenuBtn = document.getElementById('mobileMenuBtn');
        
        if (mobileNav && mobileMenuBtn) {
            mobileNav.classList.remove('active');
            mobileMenuBtn.textContent = 'Menu';
            mobileMenuBtn.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }
    }

    // Form validation
    validateField(field) {
        const value = field.value.trim();
        const fieldType = field.type;
        let isValid = true;
        let errorMessage = '';

        // Remove existing validation styles
        field.classList.remove('error', 'success');
        this.removeFieldError(field);

        // Skip validation if field is empty and not required
        if (!value && !field.required) {
            return true;
        }

        // Field-specific validation
        switch (fieldType) {
            case 'email':
                isValid = this.validateEmail(value);
                errorMessage = 'Please enter a valid email address';
                break;
            case 'password':
                if (field.name === 'password') {
                    isValid = value.length >= 8;
                    errorMessage = 'Password must be at least 8 characters';
                }
                break;
            case 'text':
                if (field.name === 'username') {
                    isValid = value.length >= 3 && /^[a-zA-Z0-9_]+$/.test(value);
                    errorMessage = 'Username must be at least 3 characters and contain only letters, numbers, and underscores';
                }
                break;
        }

        // Show validation result
        if (!isValid) {
            this.showFieldError(field, errorMessage);
        } else {
            field.classList.add('success');
        }

        return isValid;
    }

    validateEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    showFieldError(field, message) {
        field.classList.add('error');
        
        // Remove existing error message
        this.removeFieldError(field);
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-error text-sm mt-1';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }

    removeFieldError(field) {
        const existingError = field.parentNode.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }
    }

    // Authentication form handling
    handleAuthForms() {
        const loginForm = document.getElementById('loginForm');
        const registerForm = document.getElementById('registerForm');

        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                this.handleFormSubmission(e, 'Signing in...');
            });
        }

        if (registerForm) {
            registerForm.addEventListener('submit', (e) => {
                this.handleFormSubmission(e, 'Creating account...');
            });
        }
    }

    handleFormSubmission(event, loadingText) {
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        
        if (submitBtn) {
            submitBtn.disabled = true;
            const originalText = submitBtn.textContent;
            submitBtn.textContent = loadingText;
            
            // Re-enable button after 30 seconds (fallback)
            setTimeout(() => {
                submitBtn.disabled = false;
                submitBtn.textContent = originalText;
            }, 30000);
        }
    }

    // Component initializers
    initTooltips() {
        const tooltipElements = document.querySelectorAll('[data-tooltip]');
        tooltipElements.forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.dataset.tooltip);
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        let tooltip = document.getElementById('tooltip');
        if (!tooltip) {
            tooltip = document.createElement('div');
            tooltip.id = 'tooltip';
            tooltip.style.cssText = `
                position: absolute;
                background: var(--text-primary);
                color: var(--surface-color);
                padding: var(--spacing-sm);
                border-radius: var(--radius-md);
                font-size: var(--font-size-sm);
                z-index: 1000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.2s ease;
            `;
            document.body.appendChild(tooltip);
        }

        tooltip.textContent = text;
        tooltip.style.opacity = '1';

        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.bottom + 8 + 'px';
    }

    hideTooltip() {
        const tooltip = document.getElementById('tooltip');
        if (tooltip) {
            tooltip.style.opacity = '0';
        }
    }

    initAnimations() {
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

        this.autoAssignAnimations();

        const animatedElements = document.querySelectorAll('[data-animate]');
        if (!animatedElements.length) {
            return;
        }

        if (prefersReducedMotion) {
            animatedElements.forEach((element) => {
                element.classList.add('is-visible');
                element.style.opacity = '1';
                element.style.transform = 'none';
            });
            return;
        }

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.activateAnimatedElement(entry.target);
                    obs.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.15,
            rootMargin: '0px 0px -40px 0px'
        });

        animatedElements.forEach((element, index) => {
            this.prepareAnimatedElement(element, index);
            observer.observe(element);
        });
    }

    autoAssignAnimations() {
        const autoSelectors = [
            '.section-card',
            '.feature-card',
            '.stat-card',
            '.tool-card',
            '.persona-card',
            '.card',
            '.card-elevated',
            '.glass-card',
            '.timeline-item',
            '.analytics-card',
            '.overview-card',
            '.chart-card',
            '.achievement-card',
            '.voice-card',
            '.support-card',
            '.page-section',
            '.surface-card',
            '.cta-section',
            '.profile-card'
        ];

        autoSelectors.forEach((selector) => {
            document.querySelectorAll(selector).forEach((element, index) => {
                if (!element.dataset.animate && !element.classList.contains('no-auto-animate')) {
                    element.dataset.animate = 'fade-up';
                    if (!element.dataset.animateDelay) {
                        const autoDelay = Math.min(index * 45, 450);
                        element.dataset.animateDelay = autoDelay;
                    }
                }
            });
        });

        // Maintain support for legacy animate-on-scroll classes
        document.querySelectorAll('.animate-on-scroll').forEach((element, index) => {
            if (!element.dataset.animate) {
                element.dataset.animate = 'fade-up';
            }
            if (!element.dataset.animateDelay) {
                element.dataset.animateDelay = Math.min(index * 45, 450);
            }
        });
    }

    prepareAnimatedElement(element, index) {
        if (element.dataset.animatePrepared) {
            return;
        }

        const defaultDelay = Number(element.dataset.animateDelay);
        const delay = Number.isFinite(defaultDelay) ? defaultDelay : Math.min(index * 45, 450);
        const duration = Number(element.dataset.animateDuration);

        element.style.transitionDelay = `${delay}ms`;
        if (Number.isFinite(duration)) {
            element.style.transitionDuration = `${duration}ms`;
        }

        element.dataset.animatePrepared = 'true';
    }

    activateAnimatedElement(element) {
        window.requestAnimationFrame(() => {
            element.classList.add('is-visible');
        });
    }

    setupAutoResize() {
        const textareas = document.querySelectorAll('textarea[data-auto-resize]');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', () => {
                textarea.style.height = 'auto';
                textarea.style.height = textarea.scrollHeight + 'px';
            });
        });
    }

    initFileUploads() {
        const fileInputs = document.querySelectorAll('input[type="file"]');
        fileInputs.forEach(input => {
            input.addEventListener('change', (e) => {
                this.handleFileUpload(e.target);
            });
        });
    }

    handleFileUpload(input) {
        const file = input.files[0];
        if (!file) return;

        // Show preview if it's an image
        if (file.type.startsWith('image/')) {
            const preview = input.parentNode.querySelector('.file-preview') || 
                           this.createFilePreview(input);
            
            const reader = new FileReader();
            reader.onload = (e) => {
                preview.src = e.target.result;
                preview.style.display = 'block';
            };
            reader.readAsDataURL(file);
        }

        // Validate file size (10MB limit)
        const maxSize = 10 * 1024 * 1024;
        if (file.size > maxSize) {
            this.showAlert('File size must be less than 10MB', 'error');
            input.value = '';
            return;
        }
    }

    createFilePreview(input) {
        const preview = document.createElement('img');
        preview.className = 'file-preview';
        preview.style.cssText = `
            display: none;
            max-width: 150px;
            max-height: 150px;
            margin-top: var(--spacing-sm);
            border-radius: var(--radius-md);
            border: 1px solid var(--border-color);
        `;
        input.parentNode.appendChild(preview);
        return preview;
    }

    initDropdowns() {
        document.addEventListener('click', (e) => {
            // Close all dropdowns when clicking outside
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                    menu.classList.remove('show');
                });
            }
        });
    }

    initTabs() {
        const tabButtons = document.querySelectorAll('[data-tab]');
        tabButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(button.dataset.tab);
            });
        });
    }

    switchTab(tabId) {
        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });

        // Remove active class from all tab buttons
        document.querySelectorAll('[data-tab]').forEach(button => {
            button.classList.remove('active');
        });

        // Show selected tab content
        const targetTab = document.getElementById(tabId);
        if (targetTab) {
            targetTab.style.display = 'block';
        }

        // Add active class to clicked button
        document.querySelector(`[data-tab="${tabId}"]`).classList.add('active');
    }

    initLoadingStates() {
        // Handle buttons with loading states
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-loading')) {
                this.setButtonLoading(e.target, true);
            }
        });
    }

    setButtonLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.innerHTML = '<span class="loading"></span> Loading...';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || 'Submit';
        }
    }

    // Utility functions
    formatTime(date) {
        return new Intl.DateTimeFormat('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    }

    formatDate(date) {
        return new Intl.DateTimeFormat('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(new Date(date));
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function(...args) {
            if (!inThrottle) {
                func.apply(this, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // API helpers
    async apiRequest(url, options = {}) {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        };

        const finalOptions = { ...defaultOptions, ...options };

        try {
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            this.showAlert('An error occurred. Please try again.', 'error');
            throw error;
        }
    }
}

// Initialize MyBella when script loads
const myBella = new MyBella();

// Export for global access
window.myBella = myBella;