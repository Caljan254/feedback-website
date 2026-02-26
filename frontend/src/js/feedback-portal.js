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
        this.hidePublicNavLinks();
        this.startTimestampUpdater();
        console.log('Feedback Portal initialized');
    }

    // Reinitialize components after dynamic content load
    reinitializeComponents() {
        this.initializeMobileMenu();
        this.initializeAuthentication();
        this.initializePageSpecificFunctions();
        this.highlightActiveNavLink();
        this.hidePublicNavLinks();
        this.updateAllTimestamps();
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
        
        // Update page title and heading
        if (office) {
            const officeName = this.getOfficeName(office);
            document.title = `${officeName} Feedback - University Feedback Portal`;
            const titleEl = document.getElementById('department-title');
            if (titleEl) titleEl.textContent = `${officeName} Feedback`;
            
            this.injectQuestions(office);
        }
    }

    // Inject department-specific questions
    injectQuestions(officeId) {
        const questionsContainer = document.getElementById('dynamic-questions');
        if (!questionsContainer) return;

        const questions = this.getDepartmentQuestions(officeId);
        let html = '';

        questions.forEach((qObj, index) => {
            const name = `q_${index}`;
            const question = typeof qObj === 'string' ? qObj : qObj.q;
            const options = typeof qObj === 'string' ? ["Yes", "No"] : (qObj.options || ["Yes", "No"]);
            
            html += `
                <div class="space-y-3">
                    <p class="text-gray-700 dark:text-gray-300 font-medium">${question}</p>
                    <div class="flex items-center space-x-6">
                        ${options.map(opt => `
                            <label class="flex items-center cursor-pointer">
                                <input type="radio" name="${name}" value="${opt}" required class="mr-2 form-radio text-green-600"> 
                                <span class="text-gray-700 dark:text-gray-300">${opt}</span>
                            </label>
                        `).join('')}
                    </div>
                </div>
            `;
        });

        questionsContainer.innerHTML = html;
    }

    // Get questions based on office category
    getDepartmentQuestions(officeId) {
        // Category mapping
        const categories = {
            'management': ['vc-office', 'dvc-academic', 'dvc-admin', 'registrar-academic', 'registrar-admin', 'council-office', 'legal-services', 'corp-comm'],
            'academic': ['admissions', 'academic-registry', 'exams-office', 'timetabling', 'research-postgrad', 'quality-assurance', 'industrial-attachment', 'elearning'],
            'schools': ['ssc-dean', 'dept-math', 'dept-ict', 'dept-physical', 'dept-biological', 'set-dean', 'dept-civil', 'dept-elec', 'dept-mech', 'sbe-dean', 'dept-admin', 'dept-accounting', 'dept-economics', 'seh-dean', 'dept-edu', 'dept-social', 'dept-humanities', 'sanr-dean', 'dept-env', 'dept-agri'],
            'student-affairs': ['dean-students', 'student-affairs', 'counselling', 'chaplaincy', 'career-guidance', 'games', 'student-clubs'],
            'finance-hr': ['finance', 'fees-office', 'accounts-office', 'procurement', 'internal-audit', 'hr-office', 'staff-welfare', 'training-dev'],
            'support': ['library', 'ict-services', 'health-unit', 'hostel', 'catering', 'estate', 'transport', 'security', 'grounds'],
            'research-outreach': ['research-dir', 'innovation-office', 'community-outreach']
        };

        const questionSets = {
            'management': [
                { q: "Was the office environment professional?", options: ["Yes", "No"] },
                { q: "Did you receive timely assistance?", options: ["Yes", "No"] }
            ],
            'academic': [
                { q: "Were the academic guidelines clearly explained?", options: ["Yes", "No"] },
                { q: "Is the service delivery efficient?", options: ["Good", "Poor"] }
            ],
            'schools': [
                { q: "Is the academic support adequate?", options: ["Yes", "No"] },
                { q: "Were your departmental inquiries handled well?", options: ["Good", "Poor"] }
            ],
            'student-affairs': [
                { q: "Are the welfare services meeting your needs?", options: ["Yes", "No"] },
                { q: "Did you feel supported by the office?", options: ["Yes", "No"] }
            ],
            'finance-hr': [
                { q: "Was the transaction processed accurately?", options: ["Yes", "No"] },
                { q: "Was the staff helpful with your request?", options: ["Yes", "No"] }
            ],
            'support': [
                { q: "Are the facilities/services well-maintained?", options: ["Yes", "No"] },
                { q: "In your opinion, is the service reliable?", options: ["Yes", "No"] }
            ],
            'research-outreach': [
                { q: "Did you receive relevant information/support?", options: ["Yes", "No"] },
                { q: "Was the engagement productive?", options: ["Yes", "No"] }
            ]
        };

        // Specific overrides for legacy feel
        if (officeId === 'library') {
            return [
                { q: "Were the resources sufficient?", options: ["Yes", "No"] },
                { q: "How was the librarian's assistance?", options: ["Good", "Poor"] }
            ];
        }

        for (const [cat, ids] of Object.entries(categories)) {
            if (ids.includes(officeId)) return questionSets[cat];
        }

        return [
            { q: "Was the staff helpful?", options: ["Yes", "No"] },
            { q: "Was your issue resolved efficiently?", options: ["Yes", "No"] }
        ]; // Default
    }

    // Get human-readable office name
    getOfficeName(officeId) {
        const offices = {
            'vc-office': "Vice Chancellor's Office",
            'dvc-academic': "DVC (Academic, Research & Student Affairs)",
            'dvc-admin': "DVC (Administration, Finance & Planning)",
            'registrar-academic': "Registrar (Academic Affairs)",
            'registrar-admin': "Registrar (Administration & Human Resource)",
            'council-office': "University Council Office",
            'legal-services': "Legal Services Office",
            'corp-comm': "Corporate Communications / PR",
            'admissions': "Admissions Office",
            'academic-registry': "Academic Registry",
            'exams-office': "Examinations Office",
            'timetabling': "Timetabling Office",
            'research-postgrad': "Research, Innovation & Postgraduate Studies",
            'quality-assurance': "Quality Assurance Office",
            'industrial-attachment': "Industrial Attachment & Career Services",
            'elearning': "e-Learning / ODL Office",
            'ssc-dean': "Dean, School of Science and Computing",
            'dept-math': "Department of Mathematics",
            'dept-ict': "Department of Computing & IT",
            'dept-physical': "Department of Physical Sciences",
            'dept-biological': "Department of Biological Sciences",
            'set-dean': "Dean, School of Engineering",
            'dept-civil': "Department of Civil Engineering",
            'dept-elec': "Department of Electrical & Electronic Engineering",
            'dept-mech': "Department of Mechanical Engineering",
            'sbe-dean': "Dean, School of Business",
            'dept-admin': "Department of Business Administration",
            'dept-accounting': "Department of Accounting & Finance",
            'dept-economics': "Department of Economics",
            'seh-dean': "Dean, School of Education",
            'dept-edu': "Department of Educational Studies",
            'dept-social': "Department of Social Sciences",
            'dept-humanities': "Department of Humanities",
            'sanr-dean': "Dean, School of Agriculture",
            'dept-env': "Department of Environmental Science",
            'dept-agri': "Department of Agricultural Sciences",
            'dean-students': "Dean of Students Office",
            'student-affairs': "Student Affairs Office",
            'counselling': "Counselling Services",
            'chaplaincy': "Chaplaincy / Spiritual Services",
            'career-guidance': "Career Guidance Office",
            'games': "Games and Sports Office",
            'student-clubs': "Student Clubs & Associations Office",
            'finance': "Finance Department",
            'fees-office': "Fees Office",
            'accounts-office': "Accounts Office",
            'procurement': "Procurement Office",
            'internal-audit': "Internal Audit Office",
            'hr-office': "Human Resource Office",
            'staff-welfare': "Staff Welfare Office",
            'training-dev': "Training & Development Office",
            'library': "Library Services",
            'ict-services': "ICT Services",
            'health-unit': "Health Unit / Clinic",
            'hostel': "Accommodation / Hostel Office",
            'catering': "Catering Services",
            'estate': "Estate / Maintenance Department",
            'transport': "Transport Office",
            'security': "Security Department",
            'grounds': "Grounds & Cleaning Services",
            'research-dir': "Research Directorate",
            'innovation-office': "Innovation & Tech Transfer Office",
            'community-outreach': "Community Outreach & Extension"
        };
        return offices[officeId] || officeId.charAt(0).toUpperCase() + officeId.slice(1).replace(/-/g, ' ');
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
                
                // Save to history
                this.saveTrackingIdToHistory(trackingId, office);
                
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
        const isPages = window.location.pathname.includes('/src/components/pages/');
        const relPath = isPages ? `../../../public/departments/generic-feedback.html?office=${office}` : `public/departments/generic-feedback.html?office=${office}`;
        window.location.href = relPath;
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

    // Save tracking ID to localStorage history
    saveTrackingIdToHistory(id, office) {
        try {
            let history = JSON.parse(localStorage.getItem('feedback_history') || '[]');
            // Remove if already exists (to move to top)
            history = history.filter(item => item.id !== id);
            // Add to top
            history.unshift({
                id: id,
                office: office,
                officeName: this.getOfficeName(office),
                date: new Date().toISOString()
            });
            // Keep only last 10
            history = history.slice(0, 10);
            localStorage.setItem('feedback_history', JSON.stringify(history));
        } catch (e) {
            console.error('Failed to save tracking history:', e);
        }
    }

    // Get tracking history
    getTrackingHistory() {
        try {
            return JSON.parse(localStorage.getItem('feedback_history') || '[]');
        } catch (e) {
            return [];
        }
    }

    // Hide public navigation links in admin panel
    hidePublicNavLinks() {
        const currentPath = window.location.pathname;
        const isAdminPage = currentPath.includes('/admin.html') || currentPath.includes('/admin-panel/');
        const isAdmin = this.getUserRole() === 'admin';

        if (isAdminPage || isAdmin) {
            const publicLinks = document.querySelectorAll('[data-nav="public"]');
            publicLinks.forEach(link => {
                link.style.setProperty('display', 'none', 'important');
            });

            // Update welcome text for admin panel
            const welcomeText = document.getElementById('header-welcome-text');
            if (welcomeText) {
                welcomeText.innerText = 'Welcome to admin panel, university feedback system';
            }
        }
    }

    // ===== REAL-TIME TIMESTAMPS =====
    
    formatRelativeTime(timestamp) {
        if (!timestamp) return 'Unknown';
        try {
            const date = new Date(timestamp);
            const now = new Date();
            const diffMs = now - date;
            const diffSecs = Math.floor(diffMs / 1000);
            const diffMins = Math.floor(diffSecs / 60);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);

            if (diffSecs < 60) return 'Just now';
            if (diffMins < 60) return `${diffMins} min${diffMins === 1 ? '' : 's'} ago`;
            if (diffHours < 24) return `${diffHours} hr${diffHours === 1 ? '' : 's'} ago`;
            if (diffDays < 7) return `${diffDays} day${diffDays === 1 ? '' : 's'} ago`;

            return date.toLocaleDateString(undefined, { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric' 
            });
        } catch (e) {
            return 'Invalid date';
        }
    }

    updateAllTimestamps() {
        const timeElements = document.querySelectorAll('[data-timestamp]');
        timeElements.forEach(el => {
            const timestamp = el.getAttribute('data-timestamp');
            if (timestamp) {
                el.innerText = this.formatRelativeTime(timestamp);
                // Optional: add title with full date
                if (!el.getAttribute('title')) {
                    el.setAttribute('title', new Date(timestamp).toLocaleString());
                }
            }
        });
    }

    startTimestampUpdater() {
        // Update immediately
        this.updateAllTimestamps();
        
        // Clear existing interval if any
        if (this.timeUpdateInterval) {
            clearInterval(this.timeUpdateInterval);
        }
        
        // Update every 60 seconds
        this.timeUpdateInterval = setInterval(() => {
            this.updateAllTimestamps();
        }, 60000);
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