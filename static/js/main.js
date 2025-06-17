/**
 * Gaming Center Hub - Main JavaScript File
 * Handles client-side interactions, form validation, and UI enhancements
 */

(function() {
    'use strict';

    // Global variables
    let currentUser = null;
    let notifications = [];
    let activeModals = [];

    // Initialize when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });

    /**
     * Main application initialization
     */
    function initializeApp() {
        console.log('Gaming Center Hub - Initializing...');

        // Core functionality
        initializeNavigation();
        initializeAlerts();
        initializeForms();
        initializeTooltips();
        initializeAnimations();

        // Page-specific functionality
        const currentPage = getCurrentPage();
        initializePageSpecific(currentPage);



        // Enhanced user experience
        initializeKeyboardShortcuts();
        initializeProgressIndicators();
        initializeAutoSave();

        console.log('Gaming Center Hub - Initialized successfully');
    }

    /**
     * Get current page identifier
     */
    function getCurrentPage() {
        const path = window.location.pathname;
        const body = document.body;

        if (path === '/' || path === '/index') return 'home';
        if (path.includes('/login')) return 'login';
        if (path.includes('/register')) return 'register';
        if (path.includes('/dashboard')) return 'dashboard';
        if (path.includes('/available_slots')) return 'available-slots';
        if (path.includes('/book_slot')) return 'booking';
        if (path.includes('/payment')) return 'payment';
        if (path.includes('/booking_confirmation')) return 'confirmation';
        if (path.includes('/console_details')) return 'console-details';
        if (path.includes('/add_console')) return 'add-console';
        if (path.includes('/add_slot')) return 'add-slot';
        if (path.includes('/user_dashboard')) return 'user-dashboard';

        return 'general';
    }

    /**
     * Initialize navigation enhancements
     */
    function initializeNavigation() {
        const navbar = document.querySelector('.navbar');
        const navToggler = document.querySelector('.navbar-toggler');

        if (!navbar) return;

        // Add scroll effect to navbar
        let lastScrollTop = 0;
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;

            if (scrollTop > lastScrollTop && scrollTop > 100) {
                // Scrolling down
                navbar.style.transform = 'translateY(-100%)';
            } else {
                // Scrolling up
                navbar.style.transform = 'translateY(0)';
            }

            // Add background blur when scrolled
            if (scrollTop > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }

            lastScrollTop = scrollTop;
        });

        // Mobile menu enhancements
        if (navToggler) {
            navToggler.addEventListener('click', function() {
                const navCollapse = document.querySelector('.navbar-collapse');
                if (navCollapse) {
                    navCollapse.classList.toggle('show');
                }
            });
        }

        // Active page highlighting
        highlightActivePage();
    }

    /**
     * Highlight active navigation item
     */
    function highlightActivePage() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');

        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (href && currentPath.includes(href) && href !== '/') {
                link.classList.add('active');
            }
        });
    }

    /**
     * Initialize alert system enhancements
     */
    function initializeAlerts() {
        const alerts = document.querySelectorAll('.alert');

        alerts.forEach(alert => {
            // Auto-dismiss alerts after 5 seconds
            if (alert.classList.contains('alert-success')) {
                setTimeout(() => {
                    dismissAlert(alert);
                }, 5000);
            }

            // Enhanced alert animations
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-20px)';

            setTimeout(() => {
                alert.style.transition = 'all 0.3s ease';
                alert.style.opacity = '1';
                alert.style.transform = 'translateY(0)';
            }, 100);
        });
    }

    /**
     * Dismiss alert with animation
     */
    function dismissAlert(alert) {
        alert.style.transition = 'all 0.3s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-20px)';

        setTimeout(() => {
            if (alert.parentNode) {
                alert.parentNode.removeChild(alert);
            }
        }, 300);
    }

    /**
     * Show custom notification
     */
    function showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show notification`;
        notification.innerHTML = `
            <i class="fas ${getIconForType(type)} me-2"></i>
            ${message}
            <button type="button" class="btn-close" onclick="dismissAlert(this.parentElement)"></button>
        `;

        notification.style.position = 'fixed';
        notification.style.top = '100px';
        notification.style.right = '20px';
        notification.style.zIndex = '9999';
        notification.style.minWidth = '300px';
        notification.style.maxWidth = '400px';

        document.body.appendChild(notification);

        // Auto-dismiss
        setTimeout(() => {
            dismissAlert(notification);
        }, duration);

        notifications.push(notification);
    }

    /**
     * Get icon for notification type
     */



    // Add initializeWalkinBooking to initializeApp
    function initializePageSpecific(page) {
        // ... existing code ...
    }

    // ... existing code ...

    // Call initializeApp when DOM is loaded
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });
    function getIconForType(type) {
        const icons = {
            'success': 'fa-check-circle',
            'danger': 'fa-exclamation-triangle',
            'warning': 'fa-exclamation-circle',
            'info': 'fa-info-circle'
        };
        return icons[type] || icons.info;
    }

    /**
     * Initialize form enhancements
     */
    function initializeForms() {
        const forms = document.querySelectorAll('form');

        forms.forEach(form => {
            enhanceForm(form);
        });

        // Initialize specific form types
        initializePasswordFields();
        initializePhoneFields();
        initializeDateFields();
        initializeFileFields();
    }

    /**
     * Enhance individual form
     */
    function enhanceForm(form) {
        // Add loading state on submit
        form.addEventListener('submit', function(e) {
            const submitButton = form.querySelector('button[type="submit"]');
            if (submitButton && !submitButton.disabled) {
                showFormLoading(submitButton);
            }
        });

        // Real-time validation
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                validateField(input);
            });

            input.addEventListener('input', function() {
                clearFieldError(input);
            });
        });

        // Enhanced form validation
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                showNotification('Please correct the errors in the form', 'danger');
            }
        });
    }

    /**
     * Show form loading state
     */
    function showFormLoading(button) {
        const originalText = button.innerHTML;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';

        // Store original text for restoration
        button.dataset.originalText = originalText;
    }

    /**
     * Hide form loading state
     */
    function hideFormLoading(button) {
        button.disabled = false;
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
        }
    }

    /**
     * Validate individual field
     */
    function validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        let isValid = true;
        let errorMessage = '';

        // Required field validation
        if (field.hasAttribute('required') && !value) {
            isValid = false;
            errorMessage = 'This field is required';
        }

        // Type-specific validation
        if (value && isValid) {
            switch (type) {
                case 'email':
                    if (!isValidEmail(value)) {
                        isValid = false;
                        errorMessage = 'Please enter a valid email address';
                    }
                    break;
                case 'tel':
                    if (!isValidPhone(value)) {
                        isValid = false;
                        errorMessage = 'Please enter a valid 10-digit phone number';
                    }
                    break;
                case 'password':
                    if (value.length < 6) {
                        isValid = false;
                        errorMessage = 'Password must be at least 6 characters long';
                    }
                    break;
                case 'number':
                    const min = field.getAttribute('min');
                    const max = field.getAttribute('max');
                    const numValue = parseFloat(value);

                    if (isNaN(numValue)) {
                        isValid = false;
                        errorMessage = 'Please enter a valid number';
                    } else if (min && numValue < parseFloat(min)) {
                        isValid = false;
                        errorMessage = `Value must be at least ${min}`;
                    } else if (max && numValue > parseFloat(max)) {
                        isValid = false;
                        errorMessage = `Value must be no more than ${max}`;
                    }
                    break;
            }
        }

        // Custom pattern validation
        const pattern = field.getAttribute('pattern');
        if (value && pattern && isValid) {
            const regex = new RegExp(pattern);
            if (!regex.test(value)) {
                isValid = false;
                errorMessage = 'Please enter a valid format';
            }
        }

        // Show/hide validation state
        if (isValid) {
            showFieldSuccess(field);
        } else {
            showFieldError(field, errorMessage);
        }

        return isValid;
    }

    /**
     * Show field success state
     */
    function showFieldSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');

        const feedback = field.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.style.display = 'none';
        }
    }

    /**
     * Show field error state
     */
    function showFieldError(field, message) {
        field.classList.remove('is-valid');
        field.classList.add('is-invalid');

        let feedback = field.parentElement.querySelector('.invalid-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            field.parentElement.appendChild(feedback);
        }

        feedback.textContent = message;
        feedback.style.display = 'block';
    }

    /**
     * Clear field error state
     */
    function clearFieldError(field) {
        field.classList.remove('is-invalid');

        const feedback = field.parentElement.querySelector('.invalid-feedback');
        if (feedback) {
            feedback.style.display = 'none';
        }
    }

    /**
     * Validate entire form
     */
    function validateForm(form) {
        const fields = form.querySelectorAll('input[required], select[required], textarea[required]');
        let isValid = true;

        fields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Email validation
     */
    function isValidEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    /**
     * Phone validation (10 digits)
     */
    function isValidPhone(phone) {
        const regex = /^[0-9]{10}$/;
        return regex.test(phone.replace(/\D/g, ''));
    }

    /**
     * Initialize password field enhancements
     */
    function initializePasswordFields() {
        const passwordToggles = document.querySelectorAll('.password-toggle');

        passwordToggles.forEach(toggle => {
            toggle.addEventListener('click', function(e) {
                e.preventDefault();
                const input = this.parentElement.querySelector('input[type="password"], input[type="text"]');
                const icon = this.querySelector('i');

                if (input.type === 'password') {
                    input.type = 'text';
                    icon.classList.remove('fa-eye');
                    icon.classList.add('fa-eye-slash');
                } else {
                    input.type = 'password';
                    icon.classList.remove('fa-eye-slash');
                    icon.classList.add('fa-eye');
                }
            });
        });

        // Password strength indicator
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(input => {
            if (input.name === 'password' || input.id === 'password') {
                addPasswordStrengthIndicator(input);
            }
        });
    }

    /**
     * Add password strength indicator
     */
    function addPasswordStrengthIndicator(input) {
        const container = document.createElement('div');
        container.className = 'password-strength mt-2';
        container.innerHTML = `
            <div class="strength-meter">
                <div class="strength-bar"></div>
            </div>
            <small class="strength-text text-muted">Enter a password</small>
        `;

        input.parentElement.appendChild(container);

        input.addEventListener('input', function() {
            const strength = calculatePasswordStrength(this.value);
            updatePasswordStrengthIndicator(container, strength);
        });
    }

    /**
     * Calculate password strength
     */
    function calculatePasswordStrength(password) {
        let score = 0;

        if (password.length >= 6) score += 1;
        if (password.length >= 8) score += 1;
        if (/[a-z]/.test(password)) score += 1;
        if (/[A-Z]/.test(password)) score += 1;
        if (/[0-9]/.test(password)) score += 1;
        if (/[^A-Za-z0-9]/.test(password)) score += 1;

        return Math.min(score, 4);
    }

    /**
     * Update password strength indicator
     */
    function updatePasswordStrengthIndicator(container, strength) {
        const bar = container.querySelector('.strength-bar');
        const text = container.querySelector('.strength-text');

        const levels = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong'];
        const colors = ['#f56565', '#ed8936', '#ecc94b', '#48bb78', '#38a169'];

        bar.style.width = `${(strength / 4) * 100}%`;
        bar.style.backgroundColor = colors[strength] || colors[0];
        text.textContent = levels[strength] || levels[0];
        text.style.color = colors[strength] || colors[0];
    }

    /**
     * Initialize phone field enhancements
     */
    function initializePhoneFields() {
        const phoneInputs = document.querySelectorAll('input[type="tel"]');

        phoneInputs.forEach(input => {
            input.addEventListener('input', function() {
                // Auto-format phone number
                let value = this.value.replace(/\D/g, '');
                if (value.length > 10) value = value.slice(0, 10);
                this.value = value;

                // Visual feedback
                if (value.length === 10) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else if (value.length > 0) {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                } else {
                    this.classList.remove('is-valid', 'is-invalid');
                }
            });
        });
    }

    /**
     * Initialize date field enhancements
     */
    function initializeDateFields() {
        const dateInputs = document.querySelectorAll('input[type="date"]');

        dateInputs.forEach(input => {
            // Set minimum date to today for future dates
            if (!input.hasAttribute('min')) {
                const today = new Date().toISOString().split('T')[0];
                input.min = today;
            }

            input.addEventListener('change', function() {
                validateDateField(this);
            });
        });
    }

    /**
     * Validate date field
     */
    function validateDateField(input) {
        const selectedDate = new Date(input.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        if (selectedDate < today) {
            showFieldError(input, 'Cannot select a past date');
            return false;
        }

        showFieldSuccess(input);
        return true;
    }

    /**
     * Initialize file field enhancements
     */
    function initializeFileFields() {
        const fileInputs = document.querySelectorAll('input[type="file"]');

        fileInputs.forEach(input => {
            input.addEventListener('change', function() {
                const fileName = this.files[0]?.name || 'No file selected';
                const label = this.parentElement.querySelector('label') ||
                             this.nextElementSibling;

                if (label) {
                    label.textContent = fileName;
                }
            });
        });
    }

    /**
     * Initialize tooltips
     */
    function initializeTooltips() {
        // Initialize Bootstrap tooltips
        const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        if (tooltipTriggerList.length > 0) {
            [].slice.call(tooltipTriggerList).map(function(tooltipTriggerEl) {
                return new bootstrap.Tooltip(tooltipTriggerEl);
            });
        }

        // Add helpful tooltips to common elements
        addHelpfulTooltips();
    }

    /**
     * Add helpful tooltips
     */
    function addHelpfulTooltips() {
        // Add tooltip to booking IDs
        const bookingIds = document.querySelectorAll('code');
        bookingIds.forEach(code => {
            if (code.textContent.includes('GC')) {
                code.setAttribute('data-bs-toggle', 'tooltip');
                code.setAttribute('data-bs-placement', 'top');
                code.setAttribute('title', 'Click to copy booking ID');
                code.style.cursor = 'pointer';

                code.addEventListener('click', function() {
                    copyToClipboard(this.textContent);
                    showNotification('Booking ID copied to clipboard!', 'success', 2000);
                });
            }
        });

        // Add tooltip to phone numbers
        const phoneLinks = document.querySelectorAll('a[href^="tel:"]');
        phoneLinks.forEach(link => {
            link.setAttribute('data-bs-toggle', 'tooltip');
            link.setAttribute('data-bs-placement', 'top');
            link.setAttribute('title', 'Click to call');
        });
    }

    /**
     * Copy text to clipboard
     */
    function copyToClipboard(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text);
        } else {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
        }
    }

    /**
     * Initialize animations
     */
    function initializeAnimations() {
        // Intersection Observer for scroll animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        // Observe elements for animation
        const animatedElements = document.querySelectorAll('.card, .stat-card, .feature-card, .console-card, .slot-card');
        animatedElements.forEach(el => {
            el.classList.add('animate-on-scroll');
            observer.observe(el);
        });

        // Add CSS for animations
        addAnimationStyles();
    }

    /**
     * Add animation styles
     */
    function addAnimationStyles() {
        const style = document.createElement('style');
        style.textContent = `
            .animate-on-scroll {
                opacity: 0;
                transform: translateY(30px);
                transition: all 0.6s ease-out;
            }

            .animate-on-scroll.animate-in {
                opacity: 1;
                transform: translateY(0);
            }

            .card:hover, .stat-card:hover, .console-card:hover, .slot-card:hover {
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }

            .btn {
                transition: all 0.2s ease;
            }

            .btn:hover {
                transform: translateY(-1px);
            }

            .btn:active {
                transform: translateY(0);
            }

            .navbar {
                transition: transform 0.3s ease;
            }

            .navbar.scrolled {
                background-color: rgba(45, 55, 72, 0.98) !important;
                backdrop-filter: blur(10px);
            }

            .form-control:focus {
                transform: scale(1.02);
                transition: all 0.2s ease;
            }

            .password-strength .strength-meter {
                height: 4px;
                background-color: #e2e8f0;
                border-radius: 2px;
                overflow: hidden;
            }

            .password-strength .strength-bar {
                height: 100%;
                width: 0%;
                transition: all 0.3s ease;
                border-radius: 2px;
            }

            .notification {
                animation: slideInRight 0.3s ease-out;
            }

            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }

    /**
     * Initialize page-specific functionality
     */
    function initializePageSpecific(page) {
        switch (page) {
            case 'home':
                initializeHomePage();
                break;
            case 'available-slots':
                initializeAvailableSlotsPage();
                break;
            case 'booking':
                initializeBookingPage();
                break;
            case 'payment':
                initializePaymentPage();
                break;
            case 'confirmation':
                initializeConfirmationPage();
                break;
            case 'dashboard':
                initializeDashboardPage();
                break;
            case 'console-details':
                initializeConsoleDetailsPage();
                break;
            case 'add-console':
                initializeAddConsolePage();
                break;
            case 'add-slot':
                initializeAddSlotPage();
                break;
            case 'user-dashboard':
                initializeUserDashboardPage();
                break;
            default:
                console.log(`No specific initialization for page: ${page}`);
        }
    }

    /**
     * Initialize homepage functionality
     */
    function initializeHomePage() {
        // Smooth scroll for anchor links
        const anchorLinks = document.querySelectorAll('a[href^="#"]');
        anchorLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });

        // Counter animation for stats
        animateCounters();
    }

    /**
     * Animate number counters
     */
    function animateCounters() {
        const counters = document.querySelectorAll('.stat-number');

        counters.forEach(counter => {
            const target = parseInt(counter.textContent.replace(/\D/g, ''));
            if (target > 0) {
                animateCounter(counter, target);
            }
        });
    }

    /**
     * Animate individual counter
     */
    function animateCounter(element, target) {
        let current = 0;
        const increment = target / 100;
        const prefix = element.textContent.match(/^\D*/)[0];
        const suffix = element.textContent.match(/\D*$/)[0];

        const timer = setInterval(() => {
            current += increment;
            if (current >= target) {
                element.textContent = prefix + target + suffix;
                clearInterval(timer);
            } else {
                element.textContent = prefix + Math.floor(current) + suffix;
            }
        }, 20);
    }

    /**
     * Initialize available slots page
     */
    function initializeAvailableSlotsPage() {
        // Auto-submit form on filter change (debounced)
        const filterInputs = document.querySelectorAll('.filters-form select, .filters-form input');
        let debounceTimer;

        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                clearTimeout(debounceTimer);
                debounceTimer = setTimeout(() => {
                    if (this.form) {
                        this.form.submit();
                    }
                }, 500);
            });
        });

        // Enhanced sorting
        initializeSorting();

        // Infinite scroll or pagination enhancement
        initializePagination();
    }

    /**
     * Initialize sorting functionality
     */
    function initializeSorting() {
        const sortSelect = document.getElementById('sort-slots');
        if (!sortSelect) return;

        sortSelect.addEventListener('change', function() {
            const sortBy = this.value;
            const slotsContainer = document.getElementById('slots-grid');
            if (!slotsContainer) return;

            const slots = Array.from(slotsContainer.children);

            slots.sort((a, b) => {
                switch(sortBy) {
                    case 'date':
                        const dateA = new Date(a.dataset.date || '');
                        const dateB = new Date(b.dataset.date || '');
                        return dateA - dateB;
                    case 'price':
                        const priceA = parseFloat(a.dataset.price || '0');
                        const priceB = parseFloat(b.dataset.price || '0');
                        return priceA - priceB;
                    case 'console':
                        const consoleA = a.dataset.console || '';
                        const consoleB = b.dataset.console || '';
                        return consoleA.localeCompare(consoleB);
                    default:
                        return 0;
                }
            });

            // Re-append sorted elements with animation
            slots.forEach((slot, index) => {
                setTimeout(() => {
                    slotsContainer.appendChild(slot);
                    slot.style.animation = 'fadeIn 0.3s ease-out';
                }, index * 50);
            });
        });
    }

    /**
     * Initialize pagination enhancements
     */
    function initializePagination() {
        // Add "Load More" functionality if needed
        const loadMoreBtn = document.getElementById('load-more');
        if (loadMoreBtn) {
            loadMoreBtn.addEventListener('click', function() {
                // Implementation would depend on backend pagination
                showNotification('Loading more slots...', 'info');
            });
        }
    }

    /**
     * Initialize booking page
     */
    function initializeBookingPage() {
        // Real-time form validation
        const bookingForm = document.getElementById('booking-form');
        if (bookingForm) {
            enhanceBookingForm(bookingForm);
        }

        // Sticky slot details on scroll
        initializeStickyElements();
    }

    /**
     * Enhance booking form
     */
    function enhanceBookingForm(form) {
        // Agreement checkboxes validation
        const agreementCheckboxes = form.querySelectorAll('input[type="checkbox"][required]');
        const submitButton = form.querySelector('button[type="submit"]');

        function checkAgreements() {
            const allChecked = Array.from(agreementCheckboxes).every(checkbox => checkbox.checked);
            if (submitButton) {
                submitButton.disabled = !allChecked;
            }
        }

        agreementCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', checkAgreements);
        });

        // Initial check
        checkAgreements();

        // Auto-save form data
        initializeAutoSaveForForm(form);
    }

    /**
     * Initialize sticky elements
     */
    function initializeStickyElements() {
        const stickyElements = document.querySelectorAll('[style*="sticky"]');

        stickyElements.forEach(element => {
            // Add intersection observer to handle sticky state
            const observer = new IntersectionObserver(
                ([entry]) => {
                    if (entry.intersectionRatio < 1) {
                        element.classList.add('stuck');
                    } else {
                        element.classList.remove('stuck');
                    }
                },
                { threshold: [1] }
            );

            observer.observe(element);
        });
    }

    /**
     * Initialize payment page
     */
    function initializePaymentPage() {
        // Payment method selection enhancement
        const paymentMethods = document.querySelectorAll('input[name="payment_method"]');

        paymentMethods.forEach(method => {
            method.addEventListener('change', function() {
                // Update UI based on selected payment method
                updatePaymentMethodUI(this.value);
            });
        });

        // Security indicators
        addSecurityIndicators();

        // Payment form validation
        const paymentForm = document.getElementById('payment-form');
        if (paymentForm) {
            enhancePaymentForm(paymentForm);
        }
    }

    /**
     * Update payment method UI
     */
    function updatePaymentMethodUI(method) {
        const methodOptions = document.querySelectorAll('.method-option');

        methodOptions.forEach(option => {
            option.classList.remove('active');
        });

        const selectedOption = document.querySelector(`input[value="${method}"]`).closest('.method-option');
        if (selectedOption) {
            selectedOption.classList.add('active');
        }
    }

    /**
     * Add security indicators
     */
    function addSecurityIndicators() {
        // Add SSL indicator
        if (location.protocol === 'https:') {
            const securityIndicator = document.createElement('div');
            securityIndicator.className = 'security-indicator';
            securityIndicator.innerHTML = `
                <i class="fas fa-lock text-success"></i>
                <small class="text-success">Secure SSL Connection</small>
            `;

            const paymentForm = document.querySelector('.payment-form-card');
            if (paymentForm) {
                paymentForm.insertBefore(securityIndicator, paymentForm.firstChild);
            }
        }
    }

    /**
     * Enhance payment form
     */
    function enhancePaymentForm(form) {
        form.addEventListener('submit', function(e) {
            // Add loading overlay
            showPaymentProcessing();

            // Simulate processing delay for demo
            setTimeout(() => {
                hidePaymentProcessing();
            }, 3000);
        });
    }

    /**
     * Show payment processing overlay
     */
    function showPaymentProcessing() {
        const overlay = document.createElement('div');
        overlay.id = 'payment-processing';
        overlay.className = 'payment-processing-overlay';
        overlay.innerHTML = `
            <div class="processing-content">
                <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;"></div>
                <h4 class="mt-3">Processing Payment...</h4>
                <p class="text-muted">Please do not close this window</p>
            </div>
        `;

        overlay.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(255, 255, 255, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            backdrop-filter: blur(5px);
        `;

        document.body.appendChild(overlay);
    }

    /**
     * Hide payment processing overlay
     */
    function hidePaymentProcessing() {
        const overlay = document.getElementById('payment-processing');
        if (overlay) {
            overlay.remove();
        }
    }

    /**
     * Initialize confirmation page
     */
    function initializeConfirmationPage() {
        // Auto-scroll to ticket
        setTimeout(() => {
            const ticket = document.querySelector('.booking-ticket');
            if (ticket) {
                ticket.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 1000);

        // Enhanced sharing functionality
        initializeSharing();

        // Print optimization
        initializePrintMode();
    }

    /**
     * Initialize sharing functionality
     */
    function initializeSharing() {
        // Add share buttons if Web Share API is supported
        if (navigator.share) {
            addNativeShareButton();
        }

        // Add copy link functionality
        addCopyLinkButton();
    }

    /**
     * Add native share button
     */
    function addNativeShareButton() {
        const shareButton = document.createElement('button');
        shareButton.className = 'btn btn-outline-primary btn-lg';
        shareButton.innerHTML = '<i class="fas fa-share me-2"></i>Share';

        shareButton.addEventListener('click', function() {
            const bookingId = document.querySelector('.id-value')?.textContent || 'N/A';
            navigator.share({
                title: 'Gaming Slot Booking Confirmation',
                text: `My gaming slot booking (${bookingId}) has been confirmed!`,
                url: window.location.href
            });
        });

        const actionsContainer = document.querySelector('.confirmation-actions');
        if (actionsContainer) {
            actionsContainer.appendChild(shareButton);
        }
    }

    /**
     * Add copy link button
     */
    function addCopyLinkButton() {
        const copyButton = document.createElement('button');
        copyButton.className = 'btn btn-outline-secondary btn-lg';
        copyButton.innerHTML = '<i class="fas fa-link me-2"></i>Copy Link';

        copyButton.addEventListener('click', function() {
            copyToClipboard(window.location.href);
            showNotification('Booking link copied to clipboard!', 'success');
        });

        const actionsContainer = document.querySelector('.confirmation-actions');
        if (actionsContainer) {
            actionsContainer.appendChild(copyButton);
        }
    }

    /**
     * Initialize print mode
     */
    function initializePrintMode() {
        // Optimize for printing
        window.addEventListener('beforeprint', function() {
            document.body.classList.add('printing');

            // Hide unnecessary elements
            const elementsToHide = [
                '.navbar',
                '.confirmation-actions',
                '.next-steps',
                '.support-section'
            ];

            elementsToHide.forEach(selector => {
                const elements = document.querySelectorAll(selector);
                elements.forEach(el => el.style.display = 'none');
            });
        });

        window.addEventListener('afterprint', function() {
            document.body.classList.remove('printing');

            // Restore hidden elements
            const hiddenElements = document.querySelectorAll('[style*="display: none"]');
            hiddenElements.forEach(el => el.style.display = '');
        });
    }

    /**
     * Initialize dashboard page
     */
    function initializeDashboardPage() {
        // Real-time updates for stats
        initializeRealTimeUpdates();

        // Enhanced console management
        initializeConsoleManagement();

        // Dashboard widgets
        initializeDashboardWidgets();
    }

    /**
     * Initialize real-time updates
     */
    function initializeRealTimeUpdates() {
        // Poll for updates every 30 seconds
        setInterval(() => {
            updateDashboardStats();
        }, 30000);
    }

    /**
     * Update dashboard stats
     */
    function updateDashboardStats() {
        // This would typically fetch fresh data from the server
        // For now, we'll just add a visual indicator that stats are fresh
        const statCards = document.querySelectorAll('.stat-card');
        statCards.forEach(card => {
            card.classList.add('updated');
            setTimeout(() => {
                card.classList.remove('updated');
            }, 1000);
        });
    }

    /**
     * Initialize console management
     */
    function initializeConsoleManagement() {
        // Bulk operations
        initializeBulkOperations();

        // Quick actions
        initializeQuickActions();
    }

    /**
     * Initialize bulk operations
     */
    function initializeBulkOperations() {
        // Add bulk selection checkboxes
        const consoleCards = document.querySelectorAll('.console-card');

        if (consoleCards.length > 3) {
            addBulkSelectionUI();
        }
    }

    /**
     * Add bulk selection UI
     */
    function addBulkSelectionUI() {
        const bulkActions = document.createElement('div');
        bulkActions.className = 'bulk-actions mb-3';
        bulkActions.innerHTML = `
            <div class="d-flex align-items-center gap-3">
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="selectAll">
                    <label class="form-check-label" for="selectAll">Select All</label>
                </div>
                <button class="btn btn-sm btn-outline-warning" disabled>Bulk Maintenance</button>
                <button class="btn btn-sm btn-outline-success" disabled>Bulk Activate</button>
            </div>
        `;

        const consolesSection = document.querySelector('.consoles-section');
        if (consolesSection) {
            consolesSection.insertBefore(bulkActions, consolesSection.firstChild);
        }
    }

    /**
     * Initialize quick actions
     */
    function initializeQuickActions() {
        // Add keyboard shortcuts for quick actions
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey || e.metaKey) {
                switch(e.key) {
                    case 'n':
                        e.preventDefault();
                        const addConsoleBtn = document.querySelector('a[href*="add_console"]');
                        if (addConsoleBtn) addConsoleBtn.click();
                        break;
                    case 'r':
                        e.preventDefault();
                        location.reload();
                        break;
                }
            }
        });
    }

    /**
     * Initialize dashboard widgets
     */
    function initializeDashboardWidgets() {
        // Add expandable/collapsible widgets
        const widgets = document.querySelectorAll('.stat-card, .metric-card');

        widgets.forEach(widget => {
            addWidgetControls(widget);
        });
    }

    /**
     * Add widget controls
     */
    function addWidgetControls(widget) {
        const header = widget.querySelector('.card-header');
        if (!header) return;

        const controls = document.createElement('div');
        controls.className = 'widget-controls';
        controls.innerHTML = `
            <button class="btn btn-sm btn-outline-secondary" onclick="refreshWidget(this)">
                <i class="fas fa-sync-alt"></i>
            </button>
        `;

        header.appendChild(controls);
    }

    /**
     * Initialize keyboard shortcuts
     */
    function initializeKeyboardShortcuts() {
        const shortcuts = {
            'ctrl+h': () => window.location.href = '/',
            'ctrl+d': () => {
                const dashboardLink = document.querySelector('a[href*="dashboard"]');
                if (dashboardLink) dashboardLink.click();
            },
            'ctrl+s': () => {
                const slotsLink = document.querySelector('a[href*="available_slots"]');
                if (slotsLink) slotsLink.click();
            },
            'escape': () => {
                // Close any open modals or dropdowns
                const dropdowns = document.querySelectorAll('.dropdown-menu.show');
                dropdowns.forEach(dropdown => dropdown.classList.remove('show'));
            }
        };

        document.addEventListener('keydown', function(e) {
            const key = `${e.ctrlKey ? 'ctrl+' : ''}${e.shiftKey ? 'shift+' : ''}${e.key.toLowerCase()}`;

            if (shortcuts[key]) {
                e.preventDefault();
                shortcuts[key]();
            }
        });
    }

    /**
     * Initialize progress indicators
     */
    function initializeProgressIndicators() {
        // Page loading progress
        let loadingProgress = 0;
        const progressBar = createProgressBar();

        const checkProgress = setInterval(() => {
            loadingProgress += Math.random() * 30;
            updateProgressBar(progressBar, Math.min(loadingProgress, 90));

            if (document.readyState === 'complete') {
                updateProgressBar(progressBar, 100);
                setTimeout(() => {
                    hideProgressBar(progressBar);
                }, 500);
                clearInterval(checkProgress);
            }
        }, 100);
    }

    /**
     * Create progress bar
     */
    function createProgressBar() {
        const progressBar = document.createElement('div');
        progressBar.className = 'page-loading-progress';
        progressBar.innerHTML = '<div class="progress-fill"></div>';

        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 3px;
            background: rgba(102, 126, 234, 0.1);
            z-index: 10001;
        `;

        const fill = progressBar.querySelector('.progress-fill');
        fill.style.cssText = `
            height: 100%;
            background: linear-gradient(90deg, #667eea, #764ba2);
            width: 0%;
            transition: width 0.3s ease;
        `;

        document.body.appendChild(progressBar);
        return progressBar;
    }

    /**
     * Update progress bar
     */
    function updateProgressBar(progressBar, percentage) {
        const fill = progressBar.querySelector('.progress-fill');
        fill.style.width = `${percentage}%`;
    }

    /**
     * Hide progress bar
     */
    function hideProgressBar(progressBar) {
        progressBar.style.opacity = '0';
        setTimeout(() => {
            if (progressBar.parentNode) {
                progressBar.parentNode.removeChild(progressBar);
            }
        }, 300);
    }

    /**
     * Initialize auto-save functionality
     */
    function initializeAutoSave() {
        const forms = document.querySelectorAll('form[data-autosave]');

        forms.forEach(form => {
            initializeAutoSaveForForm(form);
        });
    }

    /**
     * Initialize auto-save for specific form
     */
    function initializeAutoSaveForForm(form) {
        const formId = form.id || `form_${Date.now()}`;
        const storageKey = `autosave_${formId}`;

        // Load saved data
        loadAutoSavedData(form, storageKey);

        // Save data on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', debounce(() => {
                saveFormData(form, storageKey);
            }, 1000));
        });

        // Clear saved data on successful submit
        form.addEventListener('submit', () => {
            clearAutoSavedData(storageKey);
        });
    }

    /**
     * Debounce function
     */
    function debounce(func, wait) {
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

    /**
     * Save form data to localStorage
     */
    function saveFormData(form, storageKey) {
        const formData = new FormData(form);
        const data = {};

        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }

        try {
            localStorage.setItem(storageKey, JSON.stringify(data));
        } catch (e) {
            console.warn('Failed to save form data:', e);
        }
    }

    /**
     * Load auto-saved data
     */
    function loadAutoSavedData(form, storageKey) {
        try {
            const savedData = localStorage.getItem(storageKey);
            if (savedData) {
                const data = JSON.parse(savedData);

                Object.keys(data).forEach(key => {
                    const input = form.querySelector(`[name="${key}"]`);
                    if (input && !input.readOnly) {
                        if (input.type === 'checkbox') {
                            input.checked = data[key] === 'on';
                        } else {
                            input.value = data[key];
                        }
                    }
                });

                showNotification('Form data restored from previous session', 'info', 3000);
            }
        } catch (e) {
            console.warn('Failed to load saved form data:', e);
        }
    }

    /**
     * Clear auto-saved data
     */
    function clearAutoSavedData(storageKey) {
        try {
            localStorage.removeItem(storageKey);
        } catch (e) {
            console.warn('Failed to clear saved form data:', e);
        }
    }

    /**
     * Initialize console details page
     */
    function initializeConsoleDetailsPage() {
        // Slot filtering
        initializeSlotFiltering();

        // Slot management
        initializeSlotManagement();
    }

    /**
     * Initialize slot filtering
     */
    function initializeSlotFiltering() {
        const filterButtons = document.querySelectorAll('input[name="slot-filter"]');
        const slotCards = document.querySelectorAll('.slot-card');

        filterButtons.forEach(button => {
            button.addEventListener('change', function() {
                const filter = this.id;

                slotCards.forEach(card => {
                    let shouldShow = false;

                    switch(filter) {
                        case 'all-slots':
                            shouldShow = true;
                            break;
                        case 'available-slots':
                            shouldShow = card.classList.contains('available-slot');
                            break;
                        case 'booked-slots':
                            shouldShow = card.classList.contains('booked-slot');
                            break;
                    }

                    if (shouldShow) {
                        card.style.display = 'block';
                        card.style.animation = 'fadeIn 0.3s ease-out';
                    } else {
                        card.style.display = 'none';
                    }
                });

                // Update filter count
                updateFilterCount(filter, slotCards);
            });
        });
    }

    /**
     * Update filter count
     */
    function updateFilterCount(filter, slotCards) {
        const visibleCards = Array.from(slotCards).filter(card =>
            card.style.display !== 'none'
        );

        const countElement = document.querySelector('.filter-count');
        if (countElement) {
            countElement.textContent = `${visibleCards.length} slot${visibleCards.length !== 1 ? 's' : ''}`;
        }
    }

    /**
     * Initialize slot management
     */
    function initializeSlotManagement() {
        // Add confirmation dialogs for destructive actions
        const deleteButtons = document.querySelectorAll('[onclick*="deleteSlot"]');
        const cancelButtons = document.querySelectorAll('[onclick*="cancelBooking"]');

        deleteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('Are you sure you want to delete this slot? This action cannot be undone.')) {
                    // Proceed with deletion
                    showNotification('Slot deletion functionality will be implemented soon.', 'info');
                }
            });
        });

        cancelButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                if (confirm('Are you sure you want to cancel this booking? This may affect the customer.')) {
                    // Proceed with cancellation
                    showNotification('Booking cancellation functionality will be implemented soon.', 'info');
                }
            });
        });
    }

    /**
     * Initialize add console page
     */
    function initializeAddConsolePage() {
        // Auto-pricing suggestions
        initializeAutoPricing();

        // Console type enhancements
        initializeConsoleTypeEnhancements();
    }

    /**
     * Initialize auto-pricing
     */
    function initializeAutoPricing() {
        const consoleTypeSelect = document.getElementById('console_type');
        const hourlyRateInput = document.getElementById('hourly_rate');

        if (!consoleTypeSelect || !hourlyRateInput) return;

        const pricingSuggestions = {
            'PS5': 250,
            'PS4': 150,
            'Xbox Series X': 230,
            'Xbox Series S': 180,
            'Xbox One': 130,
            'Nintendo Switch': 160,
            'Gaming PC': 200,
            'VR Setup': 300,
            'Arcade Machine': 100
        };

        consoleTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            if (pricingSuggestions[selectedType]) {
                hourlyRateInput.value = pricingSuggestions[selectedType];
                hourlyRateInput.focus();

                // Show suggestion notification
                showNotification(
                    `Suggested rate for ${selectedType}: ₹${pricingSuggestions[selectedType]}/hour`,
                    'info',
                    3000
                );
            }
        });
    }

    /**
     * Initialize console type enhancements
     */
    function initializeConsoleTypeEnhancements() {
        const consoleTypeSelect = document.getElementById('console_type');

        if (!consoleTypeSelect) return;

        consoleTypeSelect.addEventListener('change', function() {
            const selectedType = this.value;
            updateConsoleTypeFeatures(selectedType);
        });
    }

    /**
     * Update console type features
     */
    function updateConsoleTypeFeatures(consoleType) {
        const featureCheckboxes = document.querySelectorAll('.feature-checkboxes input[type="checkbox"]');

        // Auto-select relevant features based on console type
        const featureMap = {
            'PS5': ['4k_support', 'online_multiplayer', 'premium_games'],
            'Xbox Series X': ['4k_support', 'online_multiplayer', 'premium_games'],
            'Gaming PC': ['4k_support', 'online_multiplayer', 'premium_games'],
            'VR Setup': ['premium_games', 'wireless_controllers'],
            'Nintendo Switch': ['wireless_controllers']
        };

        // Reset all checkboxes
        featureCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        // Check relevant features
        if (featureMap[consoleType]) {
            featureMap[consoleType].forEach(featureId => {
                const checkbox = document.getElementById(featureId);
                if (checkbox) {
                    checkbox.checked = true;
                }
            });
        }
    }

    /**
     * Initialize add slot page
     */
    function initializeAddSlotPage() {
        // Real-time calculation
        initializeSlotCalculation();

        // Time validation
        initializeTimeValidation();

        // Quick time presets
        initializeTimePresets();
    }

    /**
     * Initialize slot calculation
     */
    function initializeSlotCalculation() {
        const dateInput = document.getElementById('date');
        const startTimeInput = document.getElementById('start_time');
        const endTimeInput = document.getElementById('end_time');
        const calculationDisplay = document.getElementById('calculation-display');

        if (!dateInput || !startTimeInput || !endTimeInput) return;

        const hourlyRate = parseFloat(document.querySelector('[data-hourly-rate]')?.dataset.hourlyRate || '0');

        function calculateSlot() {
            const startTime = startTimeInput.value;
            const endTime = endTimeInput.value;

            if (startTime && endTime) {
                const start = new Date(`2000-01-01T${startTime}`);
                const end = new Date(`2000-01-01T${endTime}`);

                if (end > start) {
                    const durationMs = end - start;
                    const durationHours = durationMs / (1000 * 60 * 60);
                    const totalAmount = durationHours * hourlyRate;

                    updateCalculationDisplay(durationHours, totalAmount);
                    return true;
                } else {
                    hideCalculationDisplay();
                    return false;
                }
            } else {
                hideCalculationDisplay();
                return false;
            }
        }

        function updateCalculationDisplay(duration, amount) {
            if (calculationDisplay) {
                const durationDisplay = document.getElementById('duration-display');
                const totalAmountDisplay = document.getElementById('total-amount-display');

                if (durationDisplay) {
                    durationDisplay.textContent = `${duration} hour${duration !== 1 ? 's' : ''}`;
                }

                if (totalAmountDisplay) {
                    totalAmountDisplay.textContent = `₹${Math.round(amount)}`;
                }

                calculationDisplay.style.display = 'block';
            }
        }

        function hideCalculationDisplay() {
            if (calculationDisplay) {
                calculationDisplay.style.display = 'none';
            }
        }

        startTimeInput.addEventListener('change', calculateSlot);
        endTimeInput.addEventListener('change', calculateSlot);
    }

    /**
     * Initialize time validation
     */
    function initializeTimeValidation() {
        const dateInput = document.getElementById('date');
        const startTimeInput = document.getElementById('start_time');
        const endTimeInput = document.getElementById('end_time');

        if (dateInput) {
            const today = new Date().toISOString().split('T')[0];
            dateInput.min = today;
            if (!dateInput.value) {
                dateInput.value = today;
            }
        }

        if (startTimeInput && endTimeInput) {
            endTimeInput.addEventListener('change', function() {
                validateTimeRange(startTimeInput, endTimeInput);
            });
        }
    }

    /**
     * Validate time range
     */
    function validateTimeRange(startInput, endInput) {
        const startTime = startInput.value;
        const endTime = endInput.value;

        if (startTime && endTime) {
            const start = new Date(`2000-01-01T${startTime}`);
            const end = new Date(`2000-01-01T${endTime}`);

            if (end <= start) {
                showFieldError(endInput, 'End time must be after start time');
                return false;
            } else {
                showFieldSuccess(endInput);
                return true;
            }
        }

        return true;
    }

    /**
     * Initialize time presets
     */
    function initializeTimePresets() {
        const presetButtons = document.querySelectorAll('[onclick*="setTimePreset"]');

        presetButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const onclick = this.getAttribute('onclick');
                const match = onclick.match(/setTimePreset\('(.+?)', '(.+?)'\)/);

                if (match) {
                    const startTime = match[1];
                    const endTime = match[2];
                    setTimePreset(startTime, endTime);
                }
            });
        });
    }

    /**
     * Set time preset
     */
    function setTimePreset(startTime, endTime) {
        const startTimeInput = document.getElementById('start_time');
        const endTimeInput = document.getElementById('end_time');

        if (startTimeInput && endTimeInput) {
            startTimeInput.value = startTime;
            endTimeInput.value = endTime;

            // Trigger change events
            startTimeInput.dispatchEvent(new Event('change'));
            endTimeInput.dispatchEvent(new Event('change'));

            showNotification(`Time set to ${startTime} - ${endTime}`, 'success', 2000);
        }
    }

    /**
     * Initialize user dashboard page
     */
    function initializeUserDashboardPage() {
        // Rating system
        initializeRatingSystem();

        // Booking management
        initializeBookingManagement();

        // Settings auto-save
        initializeSettingsAutoSave();
    }

    /**
     * Initialize rating system
     */
    function initializeRatingSystem() {
        const ratingContainers = document.querySelectorAll('.rating-stars');

        ratingContainers.forEach(container => {
            const stars = container.querySelectorAll('.fa-star');

            stars.forEach((star, index) => {
                star.addEventListener('click', function() {
                    const rating = index + 1;
                    const bookingId = container.dataset.booking;

                    // Update visual state
                    stars.forEach((s, i) => {
                        if (i < rating) {
                            s.classList.add('rated');
                            s.classList.remove('hover');
                        } else {
                            s.classList.remove('rated', 'hover');
                        }
                    });

                    // Save rating
                    saveRating(bookingId, rating);
                    showNotification(`Thank you for rating this experience ${rating} star${rating > 1 ? 's' : ''}!`, 'success');
                });

                star.addEventListener('mouseenter', function() {
                    const rating = index + 1;
                    stars.forEach((s, i) => {
                        if (i < rating) {
                            s.classList.add('hover');
                        } else {
                            s.classList.remove('hover');
                        }
                    });
                });
            });

            container.addEventListener('mouseleave', function() {
                stars.forEach(s => s.classList.remove('hover'));
            });
        });
    }

    /**
     * Save rating
     */
    function saveRating(bookingId, rating) {
        // This would typically send the rating to the server
        localStorage.setItem(`rating_${bookingId}`, rating);
    }

    /**
     * Initialize booking management
     */
    function initializeBookingManagement() {
        // Add quick action buttons
        const bookingCards = document.querySelectorAll('.booking-card');

        bookingCards.forEach(card => {
            enhanceBookingCard(card);
        });
    }

    /**
     * Enhance booking card
     */
    function enhanceBookingCard(card) {
        // Add quick call action
        const phoneNumber = card.querySelector('[href^="tel:"]')?.getAttribute('href')?.replace('tel:', '');
        if (phoneNumber) {
            addQuickCallButton(card, phoneNumber);
        }

        // Add directions action
        const address = card.querySelector('.detail-row:has(.fa-store)')?.textContent?.trim();
        if (address) {
            addDirectionsButton(card, address);
        }
    }

    /**
     * Add quick call button
     */
    function addQuickCallButton(card, phoneNumber) {
        const footer = card.querySelector('.booking-footer');
        if (!footer) return;

        const callButton = document.createElement('button');
        callButton.className = 'btn btn-outline-success btn-sm';
        callButton.innerHTML = '<i class="fas fa-phone me-1"></i>Call';
        callButton.onclick = () => window.open(`tel:${phoneNumber}`);

        footer.appendChild(callButton);
    }

    /**
     * Add directions button
     */
    function addDirectionsButton(card, address) {
        const footer = card.querySelector('.booking-footer');
        if (!footer) return;

        const directionsButton = document.createElement('button');
        directionsButton.className = 'btn btn-outline-info btn-sm';
        directionsButton.innerHTML = '<i class="fas fa-directions me-1"></i>Directions';
        directionsButton.onclick = () => {
            const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(address)}`;
            window.open(mapsUrl, '_blank');
        };

        footer.appendChild(directionsButton);
    }

    /**
     * Initialize settings auto-save
     */
    function initializeSettingsAutoSave() {
        const settingsInputs = document.querySelectorAll('.settings-section input, .settings-section select');

        settingsInputs.forEach(input => {
            input.addEventListener('change', function() {
                saveUserSetting(this.id, this.type === 'checkbox' ? this.checked : this.value);
                showNotification('Settings saved', 'success', 1000);
            });
        });

        // Load saved settings
        loadUserSettings();
    }

    /**
     * Save user setting
     */
    function saveUserSetting(key, value) {
        try {
            const settings = JSON.parse(localStorage.getItem('userSettings') || '{}');
            settings[key] = value;
            localStorage.setItem('userSettings', JSON.stringify(settings));
        } catch (e) {
            console.warn('Failed to save user setting:', e);
        }
    }

    /**
     * Load user settings
     */
    function loadUserSettings() {
        try {
            const settings = JSON.parse(localStorage.getItem('userSettings') || '{}');

            Object.keys(settings).forEach(key => {
                const input = document.getElementById(key);
                if (input) {
                    if (input.type === 'checkbox') {
                        input.checked = settings[key];
                    } else {
                        input.value = settings[key];
                    }
                }
            });
        } catch (e) {
            console.warn('Failed to load user settings:', e);
        }
    }

    // Global functions for inline event handlers
    window.refreshWidget = function(button) {
        const widget = button.closest('.card');
        widget.style.opacity = '0.5';

        setTimeout(() => {
            widget.style.opacity = '1';
            showNotification('Widget refreshed', 'success', 1000);
        }, 1000);
    };

    window.setTimePreset = setTimePreset;

    // Utility functions
    window.showNotification = showNotification;
    window.copyToClipboard = copyToClipboard;

    console.log('Gaming Center Hub - All functionality loaded');

    // Simple Booking Flow
    document.addEventListener('DOMContentLoaded', function() {
        const bookingFlow = {
            currentStep: 1,
            selectedDate: null,
            selectedTime: null,
            selectedConsole: null,
            
            init() {
                this.setupEventListeners();
                this.showStep(1);
            },

            setupEventListeners() {
                // Date selection
                document.querySelectorAll('.date-item').forEach(item => {
                    item.addEventListener('click', (e) => {
                        this.selectDate(e.target.dataset.date);
                    });
                });

                // Time slot selection
                document.querySelectorAll('.time-slot').forEach(slot => {
                    slot.addEventListener('click', (e) => {
                        if (!e.target.classList.contains('booked')) {
                            this.selectTimeSlot(e.target);
                        }
                    });
                });

                // Console selection
                document.querySelectorAll('.console-card').forEach(card => {
                    card.addEventListener('click', () => {
                        this.selectConsole(card);
                    });
                });

                // Navigation
                document.querySelectorAll('.nav-btn').forEach(btn => {
                    btn.addEventListener('click', (e) => {
                        const action = e.target.dataset.action;
                        if (action === 'next') this.nextStep();
                        if (action === 'prev') this.prevStep();
                    });
                });

                // Form submission
                const form = document.getElementById('booking-form');
                if (form) {
                    form.addEventListener('submit', (e) => {
                        e.preventDefault();
                        this.submitBooking();
                    });
                }
            },

            selectDate(date) {
                this.selectedDate = date;
                console.log("Selected date:", date);  // Debug print
                document.querySelectorAll('.date-item').forEach(item => {
                    item.classList.toggle('selected', item.dataset.date === date);
                });
                this.updateTimeSlots();
            },

            selectTimeSlot(slot) {
                this.selectedTime = slot.dataset.time;
                document.querySelectorAll('.time-slot').forEach(s => {
                    s.classList.remove('selected');
                });
                slot.classList.add('selected');
            },

            selectConsole(card) {
                this.selectedConsole = card.dataset.consoleId;
                document.querySelectorAll('.console-card').forEach(c => {
                    c.classList.remove('selected');
                });
                card.classList.add('selected');
            },

            showStep(step) {
                document.querySelectorAll('.booking-step').forEach(s => {
                    s.style.display = parseInt(s.dataset.step) === step ? 'block' : 'none';
                });
                this.currentStep = step;
                this.updateNavigation();
                this.updateSummary();
            },

            nextStep() {
                if (this.validateCurrentStep()) {
                    this.showStep(this.currentStep + 1);
                }
            },

            prevStep() {
                this.showStep(this.currentStep - 1);
            },

            validateCurrentStep() {
                switch(this.currentStep) {
                    case 1:
                        if (!this.selectedDate || !this.selectedTime) {
                            this.showToast('Please select a date and time');
                            return false;
                        }
                        break;
                    case 2:
                        if (!this.selectedConsole) {
                            this.showToast('Please select a console');
                            return false;
                        }
                        break;
                }
                return true;
            },

            updateTimeSlots() {
                const container = document.querySelector('.time-slots');
                container.innerHTML = '<div class="loading"></div>';
                console.log("Selected date:", this.selectedDate);  // Debug print

                fetch(`/api/available-slots?date=${this.selectedDate}&console_id=${typeof CONSOLE_ID !== 'undefined' ? CONSOLE_ID : ''}`)
                    .then(response => response.json())
                    .then(slots => {
                        console.log("API response:", slots);  // Debug print
                        container.innerHTML = slots.map(slot => `
                            <div class="time-slot ${slot.isBooked ? 'booked' : ''}" 
                                 data-time="${slot.time}"
                                 ${slot.isBooked ? 'disabled' : ''}>
                                ${slot.time}
                            </div>
                        `).join('');
                        // Attach click event to each time-slot
                        container.querySelectorAll('.time-slot').forEach(slotEl => {
                            if (!slotEl.classList.contains('booked')) {
                                slotEl.addEventListener('click', () => {
                                    window.bookingFlow.selectTimeSlot(slotEl);
                                });
                            }
                        });
                    })
                    .catch(() => {
                        this.showToast('Error loading time slots');
                    });
            },

            updateNavigation() {
                const prevBtn = document.querySelector('[data-action="prev"]');
                const nextBtn = document.querySelector('[data-action="next"]');
                
                prevBtn.style.display = this.currentStep === 1 ? 'none' : 'block';
                nextBtn.style.display = this.currentStep === 3 ? 'none' : 'block';
            },

            updateSummary() {
                if (this.currentStep === 3) {
                    // Update booking summary
                    document.getElementById('summary-date').textContent = this.selectedDate;
                    document.getElementById('summary-time').textContent = this.selectedTime;
                    
                    const selectedConsole = document.querySelector('.console-card.selected');
                    if (selectedConsole) {
                        document.getElementById('summary-console').textContent = 
                            `${selectedConsole.querySelector('h3').textContent} (${selectedConsole.querySelector('p').textContent})`;
                    }
                }
            },

            submitBooking() {
                const form = document.getElementById('booking-form');
                const formData = new FormData(form);
                // Add selected items to form data
                formData.append('date', this.selectedDate);
                formData.append('time', this.selectedTime);
                formData.append('console_id', typeof CONSOLE_ID !== 'undefined' ? CONSOLE_ID : this.selectedConsole);

                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="loading"></span> Processing...';

                // Submit booking
                fetch('/api/book-slot', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = `/payment/${data.booking_id}`;
                    } else {
                        this.showToast(data.message || 'Booking failed');
                    }
                })
                .catch(() => {
                    this.showToast('Error processing booking');
                })
                .finally(() => {
                    submitBtn.disabled = false;
                    submitBtn.textContent = 'Confirm Booking';
                });
            },

            showToast(message) {
                const toast = document.createElement('div');
                toast.className = 'toast';
                toast.textContent = message;
                document.body.appendChild(toast);
                
                setTimeout(() => {
                    toast.remove();
                }, 3000);
            }
        };
        window.bookingFlow = bookingFlow;
        bookingFlow.init();
    });
})();