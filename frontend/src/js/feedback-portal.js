// feedback-portal.js - Enhanced JavaScript functions for Institutional Feedback Portal

class FeedbackPortal {
    constructor() {
        this.init();
    }

    // Initialize the portal
    init() {
        this.initializeDarkMode();
        this.initializeMobileMenu();
        this.initializeAuthentication();
        this.initializeEventListeners();
        this.initializeNotificationContainer();
        this.initializePageSpecificFunctions();
        this.highlightActiveNavLink();
        console.log('Feedback Portal initialized');
    }

    // Reinitialize components after dynamic content load
    reinitializeComponents() {
        this.initializeMobileMenu();
        this.initializeAuthentication();
        this.initializePageSpecificFunctions();
        this.highlightActiveNavLink();
    }

    // Initialize functions specific to current page
    initializePageSpecificFunctions() {
        const currentPath = window.location.pathname;
        
        // Check if we're on a department feedback page (in public/departments/)
        if (currentPath.includes('/public/departments/')) {
            this.initializeDepartmentPage();
        }
        
        // Check if we're on home page
        if (currentPath.includes('home.html')) {
            this.initializeHomePage();
        }
    }

    // Initialize home page functions
    initializeHomePage() {
        console.log('Home page initialized');
        
        // Reset any stored feedback data when coming back to home
        sessionStorage.removeItem('feedbackUserInfo');
        sessionStorage.removeItem('selectedOffice');
        
        // Initialize office selection dropdown
        this.initializeOfficeSelection();
    }

    // Initialize office selection
    initializeOfficeSelection() {
        const officeSection = document.getElementById('office-section');
        if (officeSection) {
            console.log('Office selection initialized');
        }
    }

    // Initialize department page
    initializeDepartmentPage() {
        console.log('Department page initialized');
        
        // Check if user info exists, if not redirect back to home
        const userInfo = this.getUserInfo();
        if (!userInfo) {
            this.showNotification('Please select an office first', 'error');
            setTimeout(() => {
                const isDept = window.location.pathname.includes('/public/departments/');
                window.location.href = isDept ? '../../src/components/pages/home.html' : 'home.html';
            }, 2000);
            return;
        }
        
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const office = urlParams.get('office');
        
        // Display user info
        this.displayUserInfo(userInfo);
        
        // Set up form submission handler
        this.setupDepartmentFormSubmission();
    }

    // ===== DARK MODE FUNCTIONALITY =====
    initializeDarkMode() {
        const savedMode = localStorage.getItem('darkMode');
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        
        if (savedMode === 'enabled' || (!savedMode && systemPrefersDark)) {
            this.enableDarkMode();
        } else {
            this.disableDarkMode();
        }

        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            if (!localStorage.getItem('darkMode')) {
                if (e.matches) this.enableDarkMode();
                else this.disableDarkMode();
            }
        });
    }

    toggleDarkMode() {
        if (document.documentElement.classList.contains('dark')) {
            this.disableDarkMode();
        } else {
            this.enableDarkMode();
        }
    }

    enableDarkMode() {
        document.documentElement.classList.add('dark');
        this.updateDarkModeIcons(true);
        localStorage.setItem('darkMode', 'enabled');
    }

    disableDarkMode() {
        document.documentElement.classList.remove('dark');
        this.updateDarkModeIcons(false);
        localStorage.setItem('darkMode', 'disabled');
    }

    updateDarkModeIcons(isDark) {
        const darkIcons = document.querySelectorAll('.dark-mode-icon, #dark-icon, #dark-icon-mobile');
        darkIcons.forEach(icon => {
            if (isDark) {
                icon.classList.remove('fa-moon');
                icon.classList.add('fa-sun');
            } else {
                icon.classList.remove('fa-sun');
                icon.classList.add('fa-moon');
            }
        });
    }

    // ===== MOBILE MENU =====
    initializeMobileMenu() {
        this.mobileMenu = document.getElementById('mobileMenu');
        this.hamburgerBtn = document.getElementById('hamburgerBtn');
        
        if (this.hamburgerBtn) {
            this.hamburgerBtn.removeEventListener('click', this.toggleMobileMenuHandler);
            this.toggleMobileMenuHandler = () => this.toggleMobileMenu();
            this.hamburgerBtn.addEventListener('click', this.toggleMobileMenuHandler);
        }
    }

    toggleMobileMenu() {
        if (!this.mobileMenu) return;
        
        const isHidden = this.mobileMenu.classList.contains('translate-x-full');
        
        if (isHidden) {
            this.mobileMenu.classList.remove('translate-x-full', 'hidden');
            this.mobileMenu.classList.add('slide-in-right');
            
            if (this.hamburgerBtn) {
                this.hamburgerBtn.setAttribute('aria-expanded', 'true');
                const spans = this.hamburgerBtn.children;
                if (spans[0]) spans[0].classList.add('transform', 'rotate-45', 'translate-y-2');
                if (spans[1]) spans[1].classList.add('opacity-0');
                if (spans[2]) spans[2].classList.add('transform', '-rotate-45', '-translate-y-2');
            }
        } else {
            this.mobileMenu.classList.add('translate-x-full');
            this.mobileMenu.classList.remove('slide-in-right');
            
            if (this.hamburgerBtn) {
                this.hamburgerBtn.setAttribute('aria-expanded', 'false');
                const spans = this.hamburgerBtn.children;
                if (spans[0]) spans[0].classList.remove('transform', 'rotate-45', 'translate-y-2');
                if (spans[1]) spans[1].classList.remove('opacity-0');
                if (spans[2]) spans[2].classList.remove('transform', '-rotate-45', '-translate-y-2');
            }
            
            setTimeout(() => {
                this.mobileMenu.classList.add('hidden');
            }, 300);
        }
    }

    closeMobileMenu() {
        if (this.mobileMenu && !this.mobileMenu.classList.contains('translate-x-full')) {
            this.toggleMobileMenu();
        }
    }

    // ===== AUTHENTICATION =====
    initializeAuthentication() {
        this.updateNavigationBasedOnAuth();
        this.setupLogoutHandlers();
    }

    isUserLoggedIn() {
        return localStorage.getItem('token') !== null;
    }

    getUserRole() {
        return localStorage.getItem('userRole');
    }

    updateNavigationBasedOnAuth() {
        const isLoggedIn = this.isUserLoggedIn();
        const userRole = this.getUserRole();
        
        const loginElements = document.querySelectorAll('[data-auth="guest"]');
        const logoutElements = document.querySelectorAll('[data-auth="user"]');
        const adminElements = document.querySelectorAll('[data-auth="admin"]');

        if (isLoggedIn) {
            loginElements.forEach(el => el.style.setProperty('display', 'none', 'important'));
            logoutElements.forEach(el => {
                if (el.tagName === 'A' && el.classList.contains('flex')) {
                    el.style.display = 'flex';
                } else {
                    el.style.display = ''; // Fallback to CSS default
                }
            });
            if (userRole === 'admin') {
                adminElements.forEach(el => {
                    if (el.tagName === 'A' && el.classList.contains('flex')) {
                        el.style.display = 'flex';
                    } else {
                        el.style.display = '';
                    }
                });
            } else {
                adminElements.forEach(el => el.style.setProperty('display', 'none', 'important'));
            }
        } else {
            loginElements.forEach(el => {
                if (el.tagName === 'A' && el.classList.contains('flex')) {
                    el.style.display = 'flex';
                } else {
                    el.style.display = '';
                }
            });
            logoutElements.forEach(el => el.style.setProperty('display', 'none', 'important'));
            adminElements.forEach(el => el.style.setProperty('display', 'none', 'important'));
        }
    }

    setupLogoutHandlers() {
        document.querySelectorAll('[data-action="logout"]').forEach(btn => {
            btn.removeEventListener('click', this.logoutHandler);
            this.logoutHandler = (e) => {
                e.preventDefault();
                this.logout();
            };
            btn.addEventListener('click', this.logoutHandler);
        });
    }

    logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('userRole');
        localStorage.removeItem('userEmail');
        this.updateNavigationBasedOnAuth();
        const isDept = window.location.pathname.includes('/public/departments/');
        window.location.href = isDept ? '../../src/components/pages/home.html' : 'home.html';
    }

    // ===== NOTIFICATION SYSTEM =====
    initializeNotificationContainer() {
        if (!document.getElementById('notification-container')) {
            const container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'fixed inset-0 z-50 flex items-center justify-center pointer-events-none';
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'success', duration = 5000) {
        const container = document.getElementById('notification-container');
        if (!container) return null;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type} pointer-events-auto`;
        notification.style.pointerEvents = 'auto'; // Explicitly set to override container

        let icon = '';
        if (type === 'success') icon = '<i class="fas fa-check-circle notification-icon"></i>';
        else if (type === 'error') icon = '<i class="fas fa-exclamation-circle notification-icon"></i>';
        else if (type === 'warning') icon = '<i class="fas fa-exclamation-triangle notification-icon"></i>';
        else icon = '<i class="fas fa-info-circle notification-icon"></i>';

        notification.innerHTML = `
            ${icon}
            <div class="notification-content">${message}</div>
            <div class="notification-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </div>
        `;

        container.appendChild(notification);
        setTimeout(() => notification.classList.add('show'), 10);

        if (duration > 0) {
            setTimeout(() => {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 300);
            }, duration);
        }
        return notification;
    }

    // ===== DEPARTMENT PAGE FUNCTIONS =====
    getUserInfo() {
        const userInfo = sessionStorage.getItem('feedbackUserInfo');
        return userInfo ? JSON.parse(userInfo) : null;
    }

    displayUserInfo(userInfo) {
        if (!userInfo) return;
        
        const displayDiv = document.getElementById('user-info-display');
        if (!displayDiv) return;
        
        displayDiv.classList.remove('hidden');
        
        let infoHtml = '<div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">';
        infoHtml += '<div><span class="font-semibold">Feedback for:</span> ' + (userInfo.name || 'Anonymous User') + '</div>';
        if (userInfo.category) {
            infoHtml += '<div><span class="font-semibold">Category:</span> ' + userInfo.category + '</div>';
        }
        if (userInfo.email && !userInfo.anonymous) {
            infoHtml += '<div><span class="font-semibold">Email:</span> ' + userInfo.email + '</div>';
        }
        infoHtml += '</div>';
        
        displayDiv.innerHTML = infoHtml;
    }

    setupDepartmentFormSubmission() {
        const forms = document.querySelectorAll('.department-feedback-form');
        forms.forEach(form => {
            form.removeEventListener('submit', this.departmentFormSubmitHandler);
            this.departmentFormSubmitHandler = (e) => this.handleDepartmentFormSubmit(e);
            form.addEventListener('submit', this.departmentFormSubmitHandler);
        });
    }

    async handleDepartmentFormSubmit(e) {
        e.preventDefault();
        const form = e.target;
        
        const formValues = {};
        form.querySelectorAll('input, textarea, select').forEach(input => {
            if (input.type === 'radio') {
                if (input.checked) formValues[input.name] = input.value;
            } else if (input.type === 'checkbox') {
                formValues[input.name] = input.checked;
            } else if (input.type !== 'submit') {
                formValues[input.name] = input.value;
            }
        });

        const userInfo = this.getUserInfo();
        const urlParams = new URLSearchParams(window.location.search);
        const office = urlParams.get('office') || 'unknown';

        const finalData = {
            name: userInfo?.anonymous ? null : (userInfo?.name || null),
            email: userInfo?.anonymous ? null : (userInfo?.email || null),
            category: userInfo?.category || '',
            office: office,
            anonymous: userInfo?.anonymous ? "true" : "false",
            rating: formValues.rating || '',
            message: formValues.comment || '',
            ...formValues,
            timestamp: new Date().toISOString()
        };

        try {
            const loadingNotification = this.showNotification('Submitting your feedback...', 'info', 0);
            
            const res = await fetch("http://localhost:8000/api/submit-feedback", {
                method: "POST",
                headers: { "Content-Type": "application/json", "Accept": "application/json" },
                body: JSON.stringify(finalData)
            });

            loadingNotification?.remove();

            if (res.ok) {
                const result = await res.json();
                const trackingId = result.tracking_id || 'N/A';
                
                // Show persistent success notification with copy button
                this.showNotification(`
                    <div class="flex flex-col gap-3 pointer-events-auto">
                        <div class="flex items-center">
                            <i class="fas fa-check-circle mr-2 text-xl"></i>
                            <span class="font-bold">Feedback Submitted!</span>
                        </div>
                        <p class="text-sm opacity-90">Your Reference Number is:</p>
                        <div class="flex items-center bg-white/20 p-2 rounded border border-white/30 gap-2">
                            <code class="text-lg font-mono flex-1 text-white">${trackingId}</code>
                            <button onclick="window.feedbackPortal.copyToClipboard('${trackingId}')" 
                                    class="bg-white text-green-600 px-3 py-1.5 rounded text-xs font-bold hover:bg-green-50 transition-colors shadow-sm">
                                <i class="fas fa-copy mr-1"></i> COPY
                            </button>
                        </div>
                        <p class="text-xs italic opacity-80">Please save this number to track your feedback later.</p>
                        <div class="flex gap-2 mt-2">
                            <button onclick="const isDept = window.location.pathname.includes('/public/departments/'); window.location.href = isDept ? '../../src/components/pages/home.html' : 'home.html';"
                                    class="flex-1 bg-green-700 hover:bg-green-800 text-white py-2.5 rounded text-sm font-bold transition-all border border-green-400 shadow-md">
                                <i class="fas fa-home mr-2"></i> Return Home
                            </button>
                            <button onclick="this.closest('.notification').remove()" 
                                    class="bg-white/10 hover:bg-white/20 text-white px-4 py-2.5 rounded text-sm font-medium transition-all border border-white/30">
                                Close
                            </button>
                        </div>
                    </div>
                `, 'success', 0); // 0 duration means it stays until clicked/dismissed
                
                form.reset();
                
                // Clear session storage after successful submission
                sessionStorage.removeItem('feedbackUserInfo');
                sessionStorage.removeItem('selectedOffice');
            } else {
                let errorMessage = 'Failed to submit feedback';
                try {
                    const error = await res.json();
                    errorMessage = error.detail || error.message || errorMessage;
                } catch {}
                this.showNotification(`❌ ${errorMessage}`, 'error');
            }
        } catch (err) {
            console.error(err);
            this.showNotification('⚠️ Could not connect to server. Please check your connection.', 'error');
        }
    }

    goBack() {
        const isDept = window.location.pathname.includes('/public/departments/');
        window.location.href = isDept ? '../../src/components/pages/home.html' : 'home.html';
    }

    // ===== HOME PAGE FUNCTIONS =====
    startFeedbackProcess() {
        document.querySelectorAll('section').forEach(sec => sec.classList.add('hidden'));
        const officeSection = document.getElementById('office-section');
        if (officeSection) {
            officeSection.classList.remove('hidden');
            this.scrollToElement(officeSection, 80);
        }
    }

    showUserInfoForm() {
        const office = window.selectedOfficeValue;
        if (!office) {
            this.showNotification('Please select an office first', 'error');
            return;
        }
        
        document.getElementById('office-section')?.classList.add('hidden');
        const userInfoSection = document.getElementById('user-info-section');
        if (userInfoSection) {
            userInfoSection.classList.remove('hidden');
            this.scrollToElement(userInfoSection, 80);
        }
    }

    goBackToOfficeSelection() {
        const officeSection = document.getElementById('office-section');
        if (officeSection) {
            officeSection.classList.remove('hidden');
            this.scrollToElement(officeSection, 80);
        }
        document.getElementById('user-info-section')?.classList.add('hidden');
    }

    scrollToElement(element, offset = 20) {
        if (element) {
            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;
            window.scrollTo({ top: offsetPosition, behavior: 'smooth' });
        }
    }

    // Handle user info form submission and redirect to department
    handleUserInfoSubmit(e) {
        e.preventDefault();
        
        const anonymous = document.getElementById('anonymous')?.checked;
        const name = document.getElementById('name')?.value.trim();
        const email = document.getElementById('email')?.value.trim();
        const category = document.getElementById('category')?.value;
        const office = window.selectedOfficeValue;

        if (!office) {
            this.showNotification('Please select an office first', 'error');
            return;
        }
        
        if (!anonymous && (!name || !email || !category)) {
            this.showNotification('Please fill in all required fields or check "Submit Anonymously"', 'error');
            return;
        }

        const userInfo = {
            name: anonymous ? null : name,
            email: anonymous ? null : email,
            category: anonymous ? 'Anonymous' : category,
            office: office,
            anonymous: anonymous ? true : false
        };

        // Store user info in sessionStorage
        sessionStorage.setItem('feedbackUserInfo', JSON.stringify(userInfo));
        sessionStorage.setItem('selectedOffice', office);

        // Get the office file mapping (pointing to public/departments/)
        const officeFiles = {
            'admin': 'admin-feedback.html',
            'library': 'library-feedback.html',
            'finance': 'finance-feedback.html',
            'admissions': 'admissions-feedback.html',
            'ict': 'ict-feedback.html',
            'security': 'security-feedback.html',
            'catering': 'catering-feedback.html',
            'registry': 'registry-feedback.html',
            'health': 'health-feedback.html',
            'games': 'games-feedback.html',
            'hostel': 'hostel-feedback.html',
            'dean': 'dean-feedback.html'
        };

        // Redirect to department page in public/departments/
        const departmentFile = officeFiles[office];
        if (departmentFile) {
            const isPages = window.location.pathname.includes('/src/components/pages/');
            const relPath = isPages ? `../../../public/departments/${departmentFile}?office=${office}` : `public/departments/${departmentFile}?office=${office}`;
            window.location.href = relPath;
        } else {
            this.showNotification('Department page not found', 'error');
        }
    }

    // ===== EVENT LISTENERS =====
    initializeEventListeners() {
        // User info form submission
        const userInfoForm = document.getElementById('user-info-form');
        if (userInfoForm) {
            userInfoForm.removeEventListener('submit', this.userInfoSubmitHandler);
            this.userInfoSubmitHandler = (e) => this.handleUserInfoSubmit(e);
            userInfoForm.addEventListener('submit', this.userInfoSubmitHandler);
        }

        // Anonymous checkbox toggle
        const anonymousCheckbox = document.getElementById('anonymous');
        if (anonymousCheckbox) {
            anonymousCheckbox.removeEventListener('change', this.anonymousToggleHandler);
            this.anonymousToggleHandler = function() {
                const isAnonymous = this.checked;
                ['name', 'email', 'category'].forEach(id => {
                    const input = document.getElementById(id);
                    if (input) {
                        input.disabled = isAnonymous;
                        if (isAnonymous) input.value = '';
                    }
                });
            };
            anonymousCheckbox.addEventListener('change', this.anonymousToggleHandler);
        }
    }

    // ===== UI ENHANCEMENTS =====
    highlightActiveNavLink() {
        const currentPath = window.location.pathname;
        const currentFile = currentPath.split('/').pop() || 'index.html';
        
        // Handle index.html or root path
        const isHome = currentFile === 'home.html' || currentFile === 'index.html' || currentFile === '';
        
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            const linkHref = link.getAttribute('href');
            if (!linkHref) return;
            
            const linkFile = linkHref.split('/').pop();
            
            // Remove active class first
            link.classList.remove('active');
            
            // Check for match
            if (isHome && (linkFile === 'home.html' || linkFile === 'index.html')) {
                link.classList.add('active');
            } else if (linkFile === currentFile && currentFile !== '') {
                link.classList.add('active');
            }
        });
    }

    // ===== UTILITY =====
    debounce(func, wait) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), wait);
        };
    }

    // Copy text to clipboard with fallback
    copyToClipboard(text) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text).then(() => {
                this.showNotification('Reference Number copied to clipboard!', 'info');
            }).catch(err => {
                this.fallbackCopyToClipboard(text);
            });
        } else {
            this.fallbackCopyToClipboard(text);
        }
    }

    fallbackCopyToClipboard(text) {
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";
        textArea.style.left = "-999999px";
        textArea.style.top = "-999999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            document.execCommand('copy');
            this.showNotification('Reference Number copied to clipboard!', 'info');
        } catch (err) {
            console.error('Fallback copy failed', err);
            this.showNotification('Could not copy automatically. Please select the text manually.', 'warning');
        }
        document.body.removeChild(textArea);
    }
}

// Initialize the portal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.feedbackPortal = new FeedbackPortal();
});

// Legacy global functions for onclick attributes
function toggleMobileMenu() { window.feedbackPortal?.toggleMobileMenu(); }
function toggleDarkMode() { window.feedbackPortal?.toggleDarkMode(); }
function startFeedbackProcess() { window.feedbackPortal?.startFeedbackProcess(); }
function showUserInfoForm() { window.feedbackPortal?.showUserInfoForm(); }
function goBackToOfficeSelection() { window.feedbackPortal?.goBackToOfficeSelection(); }
function logout() { window.feedbackPortal?.logout(); }
function goBack() { window.feedbackPortal?.goBack(); }

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FeedbackPortal;
}