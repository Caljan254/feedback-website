// feedback-portal.js - Enhanced JavaScript functions for Institutional Feedback Portal

class FeedbackPortal {
    constructor() {
        // --- DEPLOYMENT CONNECTION URL ---
        // CONNECTED TO RENDER BACKEND
        this.apiBaseUrl = "https://seku-feedback-backend.onrender.com/api"; 

        
        window.feedbackPortal = this;
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
        this.updateLogoForOffice();
        this.adjustHeaderSpacer();
        this.initializeContentProtection();
        console.log('Feedback Portal initialized');
    }

    // Initialize content protection to prevent copying
    initializeContentProtection() {
    }

    // Update logo based on office
    updateLogoForOffice() {
        setTimeout(() => {
            const headerLogo = document.getElementById('main-header-logo');
            if (!headerLogo) return;
            headerLogo.src = '/uploads/ict-logo.png';
            headerLogo.className = 'h-10 sm:h-16 md:h-24 w-auto max-w-[180px] sm:max-w-[400px] md:max-w-2xl object-contain py-1';
        }, 300);
    }

    // Reinitialize components after dynamic content load
    reinitializeComponents() {
        this.initializeMobileMenu();
        this.initializeAuthentication();
        this.initializePageSpecificFunctions();
        this.highlightActiveNavLink();
        this.hidePublicNavLinks();
        this.updateAllTimestamps();
        this.updateLogoForOffice();
    }

    // Initialize functions specific to current page
    initializePageSpecificFunctions() {
        const currentPath = window.location.pathname;
        if (currentPath.includes('/departments/')) {
            this.initializeDepartmentPage();
        }
        
        // Check if we're on home page
        if (currentPath.includes('home.html') || currentPath === '/' || currentPath.endsWith('/')) {
            this.initializeHomePage();
        }
    }

    // Initialize home page functions
    initializeHomePage() {
        console.log('Home page initialized');
        sessionStorage.removeItem('feedbackUserInfo');
        sessionStorage.removeItem('selectedOffice');
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
        const userInfo = this.getUserInfo();
        if (!userInfo) {
            this.showNotification('Please select an office first', 'error');
            setTimeout(() => {
                window.location.href = '/src/components/pages/home.html';
            }, 2000);
            return;
        }
        
        // Get URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const office = urlParams.get('office');
        this.displayUserInfo(userInfo);
        this.setupDepartmentFormSubmission();
        if (office) {
            const officeName = this.getOfficeName(office);
            document.title = `${officeName} Feedback - University Feedback Portal`;
            const titleEl = document.getElementById('department-title');
            if (titleEl && !titleEl.textContent.trim().includes("CUSTOMER FEEDBACK")) {
                titleEl.textContent = `${officeName} Feedback`;
            }
            
            this.injectQuestions(office);
        }
    }

    // Inject department-specific questions
    async injectQuestions(officeId) {
        const questionsContainer = document.getElementById('dynamic-questions');
        if (!questionsContainer) return;

        try {
            const res = await fetch(`${this.apiBaseUrl}/questions?office=${officeId}`);
            const questions = await res.json();
            
            if (questions.length === 0) {
                questionsContainer.innerHTML = '<p class="text-gray-500 italic text-sm">No specific questions for this office.</p>';
                return;
            }

            let html = '';
            questions.forEach((qObj) => {
                const question = qObj.text;
                const options = qObj.options ? qObj.options.split(',') : ["Yes", "No"];
                
                html += `
                    <div class="space-y-3 dynamic-question-block" data-question-id="${qObj.id}">
                        <p class="text-gray-700 dark:text-gray-300 font-medium">${question}</p>
                        <div class="flex items-center space-x-6">
                            ${options.map(opt => `
                                <label class="flex items-center cursor-pointer">
                                    <input type="radio" name="dq_${qObj.id}" value="${opt}" required class="mr-2 form-radio text-green-600"> 
                                    <span class="text-gray-700 dark:text-gray-300">${opt}</span>
                                </label>
                            `).join('')}
                        </div>
                    </div>
                `;
            });

            questionsContainer.innerHTML = html;
        } catch (error) {
            console.error('Error fetching dynamic questions:', error);
            questionsContainer.innerHTML = '<p class="text-red-500">Error loading questions.</p>';
        }
    }

    // Get questions based on office category
    getDepartmentQuestions(officeId) {
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
        if (officeId === 'admissions') {
            return [
                { q: "What type of application is this feedback about?", options: ["Undergraduate", "Postgraduate", "Transfer", "International", "Scholarship"] },
                { q: "Clarity of admissions policies and procedures?", options: ["Excellent", "Good", "Poor"] },
                { q: "Ease of finding information about admissions?", options: ["Very Easy", "Easy", "Neutral", "Difficult", "Very Difficult"] },
                { q: "Responsiveness and helpfulness of Admissions Office?", options: ["Excellent", "Good", "Poor", "Did not contact"] },
                { q: "Overall admission process satisfaction?", options: ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"] }
            ];
        }

        if (officeId === 'finance' || officeId === 'fees-office' || officeId === 'accounts-office') {
            return [
                { q: "Primary purpose of your interaction today?", options: ["Fee payment", "Reimbursement", "Procurement", "Budget inquiry", "General inquiry"] },
                { q: "Clarity and ease of understanding financial procedures?", options: ["Excellent", "Good", "Poor"] },
                { q: "Efficiency and timeliness of financial transactions?", options: ["Excellent", "Good", "Poor"] },
                { q: "Helpfulness and professionalism of Finance staff?", options: ["Excellent", "Good", "Poor", "Did not interact"] },
                { q: "Transparency of financial information?", options: ["Very Satisfied", "Satisfied", "Neutral", "Dissatisfied", "Very Dissatisfied"] }
            ];
        }

        if (officeId === 'ict-services' || officeId === 'dept-ict') {
            return [
                { q: "Primary purpose of your visit today?", options: ["Academic Work", "Administrative Work", "Research", "Event/Meeting", "General Browsing"] },
                { q: "Reliability of technical infrastructure?", options: ["Excellent", "Good", "Poor"] },
                { q: "Rating of ICT Helpdesk support experience?", options: ["Excellent", "Good", "Poor", "Did not seek help"] },
                { q: "Ease of navigating ICT services?", options: ["Very Easy", "Easy", "Neutral", "Difficult", "Very Difficult"] },
                { q: "Overall ICT experience rating?", options: ["Excellent", "Good", "Poor"] }
            ];
        }

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
        ];
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
            'ict-services': "Directorate Of ICT",
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
        this.mobileMenuOverlay = document.getElementById('mobileMenuOverlay');
        this.hamburgerBtn = document.getElementById('hamburgerBtn');
        
        if (this.hamburgerBtn) {
            this.hamburgerBtn.removeEventListener('click', this.toggleMobileMenuHandler);
            this.toggleMobileMenuHandler = (e) => {
                e.preventDefault();
                this.toggleMobileMenu();
            };
            this.hamburgerBtn.addEventListener('click', this.toggleMobileMenuHandler);
        }
    }

    toggleMobileMenu() {
        if (!this.mobileMenu || !this.mobileMenuOverlay) return;
        
        const isCurrentlyVisible = this.mobileMenu.style.display !== 'none';
        
        if (!isCurrentlyVisible) {
            this.mobileMenu.style.display = 'block';
            this.mobileMenuOverlay.style.display = 'block';
            document.body.style.overflow = 'hidden';
            setTimeout(() => {
                this.mobileMenu.classList.remove('translate-x-full');
            }, 10);
            
            if (this.hamburgerBtn) this.hamburgerBtn.setAttribute('aria-expanded', 'true');
        } else {
            this.mobileMenu.classList.add('translate-x-full');
            this.mobileMenuOverlay.style.display = 'none';
            document.body.style.overflow = '';
            
            if (this.hamburgerBtn) this.hamburgerBtn.setAttribute('aria-expanded', 'false');
            setTimeout(() => {
                this.mobileMenu.style.display = 'none';
            }, 300);
        }
    }

    closeMobileMenu() {
        if (this.mobileMenu && this.mobileMenu.style.display !== 'none') {
            this.toggleMobileMenu();
        }
    }

    // New Header Spacer logic moved into FeedbackPortal
    adjustHeaderSpacer() {
        const header = document.querySelector('header');
        const spacer = document.getElementById('header-dynamic-spacer');
        if (header && spacer) {
            const height = Math.min(header.offsetHeight, 180);
            spacer.style.height = height + 'px';
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

        const showEl = (el) => {
            el.style.display = el.tagName === 'A' ? 'inline-flex' : 'flex';
        };

        if (isLoggedIn) {
            loginElements.forEach(el => el.style.display = 'none');
            logoutElements.forEach(el => showEl(el));
            if (userRole === 'admin') {
                adminElements.forEach(el => showEl(el));
            } else {
                adminElements.forEach(el => el.style.display = 'none');
            }
        } else {
            loginElements.forEach(el => showEl(el));
            logoutElements.forEach(el => el.style.display = 'none');
            adminElements.forEach(el => el.style.display = 'none');
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
            container.className = 'fixed inset-0 z-[100000] flex items-center justify-center pointer-events-none';
            document.body.appendChild(container);
        }
    }

    showNotification(message, type = 'success', duration = 5000) {
        const container = document.getElementById('notification-container');
        if (!container) return null;
        
        const notification = document.createElement('div');
        notification.className = `notification ${type} pointer-events-auto`;
        notification.style.pointerEvents = 'auto';

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
        if (userInfo.category && userInfo.category !== 'Anonymous') {
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
        // 1. Check every dynamic-question-block radio group (Validate all in form)
        const allQuestionBlocks = Array.from(document.querySelectorAll('.dynamic-question-block'));
        const visibleQuestionBlocks = allQuestionBlocks.filter(block => block.offsetParent !== null);
        
        let firstUnanswered = null;

        allQuestionBlocks.forEach(block => {
            const questionId = block.getAttribute('data-question-id');
            if (!questionId) return;
            
            const inputs = block.querySelectorAll(`input[type="radio"], input[type="checkbox"]`);
            const textarea = block.querySelector(`textarea`);
            const visibleTextInputs = block.querySelectorAll(`input[type="text"]`);
            
            let answered = true;
            
            if (inputs.length > 0) {
                const isChecked = Array.from(inputs).some(i => i.checked);
                if (!isChecked) {
                    answered = false;
                } else {
                    visibleTextInputs.forEach(ti => {
                        if (ti.offsetParent !== null && !ti.value.trim()) {
                            answered = false;
                        }
                    });
                }
            } else if (textarea) {
                if (!textarea.value.trim()) answered = false;
            }

            if (!answered) {
                if (block.offsetParent !== null) {
                    block.classList.add('ring-2', 'ring-red-500', 'p-2', 'rounded-lg');
                    if (!firstUnanswered) firstUnanswered = block;
                }
            } else {
                block.classList.remove('ring-2', 'ring-red-500', 'p-2');
            }
        });
        let firstEmptyRequired = null;
        const requiredInputs = Array.from(form.querySelectorAll('textarea[required], input[required]:not([type="radio"]):not([type="hidden"])'))
            .filter(el => el.offsetParent !== null);
        
        requiredInputs.forEach(el => {
            if (!el.value.trim()) {
                el.classList.add('ring-2', 'ring-red-500');
                if (!firstEmptyRequired) firstEmptyRequired = el;
            } else {
                el.classList.remove('ring-2', 'ring-red-500');
            }
        });
        if (firstUnanswered || firstEmptyRequired) {
             // but we keep it as a safety net for visible fields.
             if (firstUnanswered || firstEmptyRequired) {
                this.showNotification('⚠️ Please answer all questions on this page.', 'error');
                return;
             }
        }
        // ─────────────────────────────────────────────────────────────────────

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

        const dynamicResponses = [];
        allQuestionBlocks.forEach(block => {
            const questionId = block.getAttribute('data-question-id');
            if (!questionId) return;
            let visibleQuestionText = '';
            const pEl = block.querySelector('p');
            const labelEl = block.querySelector('label.font-semibold, label.block');
            const tdEl = block.querySelector('td:first-child');
            
            const targetEl = pEl || labelEl || tdEl;
            if (targetEl) {
                const clone = targetEl.cloneNode(true);
                clone.querySelectorAll('span, i, .text-xs, .text-gray-500').forEach(s => s.remove());
                visibleQuestionText = clone.textContent.trim().replace(/^\d+\.\s*/, '');
            }
            
            if (!visibleQuestionText) visibleQuestionText = `Question #${questionId}`;

            let answer = null;
            const radios = block.querySelectorAll('input[type="radio"]');
            const checks = block.querySelectorAll('input[type="checkbox"]');
            const textarea = block.querySelector('textarea');

            if (radios.length > 0) {
                const checkedRadio = block.querySelector('input[type="radio"]:checked');
                if (checkedRadio) answer = checkedRadio.value;
            } else if (checks.length > 0) {
                const checkedOnes = Array.from(checks).filter(c => c.checked).map(c => c.value);
                if (checkedOnes.length > 0) {
                    const otherInput = block.querySelector('input[type="text"]');
                    const formattedAnswers = checkedOnes.map(v => {
                        if (v === 'other' && otherInput && otherInput.value.trim()) {
                            return otherInput.value.trim();
                        }
                        return v;
                    }).filter(v => v !== 'other');
                    
                    if (formattedAnswers.length > 0) answer = formattedAnswers.join(', ');
                }
            } else if (textarea) {
                if (textarea.value.trim()) answer = textarea.value.trim();
            }

            if (answer) {
                dynamicResponses.push({
                    question_id: parseInt(questionId),
                    answer: answer,
                    question_text: visibleQuestionText
                });
            }
        });

        const userInfo = this.getUserInfo();
        const urlParams = new URLSearchParams(window.location.search);
        const office = urlParams.get('office') || 'unknown';
        const finalData = {
            ...formValues,
            name: userInfo?.anonymous ? null : (userInfo?.name || null),
            email: userInfo?.anonymous ? null : (userInfo?.email || null),
            category: userInfo?.category || '',
            office: office,
            anonymous: userInfo?.anonymous ? "true" : "false",
            rating: formValues.rating || formValues.q_4 || formValues.dq_23 || '',
            message: formValues.comment || formValues.message || '',
            dynamic_responses: dynamicResponses,
            timestamp: new Date().toISOString()
        };
        if (!finalData.rating || finalData.rating === '') {
            const ratingResponse = dynamicResponses.find(r => 
                r.question_id === 23 || 
                (r.question_text && r.question_text.toLowerCase().includes('overall'))
            );
            if (ratingResponse) finalData.rating = ratingResponse.answer;
        }

        // Clean up: Ensure q_4 and other fields are also populated if missing but rating exists
        if (finalData.rating && !finalData.q_4) finalData.q_4 = finalData.rating;


        try {
            const loadingNotification = this.showNotification('Submitting your feedback...', 'info', 0);
            await new Promise(resolve => setTimeout(resolve, 2000));
            const headers = { 
                "Content-Type": "application/json", 
                "Accept": "application/json" 
            };
            const token = localStorage.getItem('token');
            if (token) {
                headers["Authorization"] = `Bearer ${token}`;
            }

            const res = await fetch(`${this.apiBaseUrl}/submit-feedback`, {
                method: "POST",
                headers: headers,
                body: JSON.stringify(finalData)
            });

            loadingNotification?.remove();

            if (res.ok) {
                const result = await res.json();
                const trackingId = result.tracking_id || 'N/A';
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
                        <p class="text-xs italic opacity-80">This page will automatically return to home in <span id="redirect-timer">15</span> seconds.</p>
                        <div class="flex gap-2 mt-2">
                            <button onclick="window.location.href = '/src/components/pages/home.html';"
                                    class="flex-1 bg-green-700 hover:bg-green-800 text-white py-2.5 rounded text-sm font-bold transition-all border border-green-400 shadow-md">
                                <i class="fas fa-home mr-2"></i> Return Home
                            </button>
                            <button onclick="window.location.href = '/src/components/pages/home.html';" 
                                    class="bg-white/10 hover:bg-white/20 text-white px-4 py-2.5 rounded text-sm font-medium transition-all border border-white/30">
                                Close
                            </button>
                        </div>
                    </div>
                `, 'success', 0);
                
                // Set up automatic redirect timer
                let timeLeft = 15;
                const timerInterval = setInterval(() => {
                    timeLeft--;
                    const timerEl = document.getElementById('redirect-timer');
                    if (timerEl) {
                        timerEl.textContent = timeLeft;
                    }
                    if (timeLeft <= 0) {
                        clearInterval(timerInterval);
                        window.location.href = '/src/components/pages/home.html';
                    }
                }, 1000);
                this.saveTrackingIdToHistory(trackingId, office, result.created_at);
                
                form.reset();
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

        // PRE-FILL for logged in users
        const token = localStorage.getItem('token');
        if (token) {
            const nameEl = document.getElementById('name');
            const emailEl = document.getElementById('email');
            const categoryEl = document.getElementById('category');

            if (nameEl && !nameEl.value) nameEl.value = localStorage.getItem('userFullname') || '';
            if (emailEl && !emailEl.value) emailEl.value = localStorage.getItem('userEmail') || '';
            if (categoryEl && !categoryEl.value) {
                const role = localStorage.getItem('userRole');
                if (role) {
                    const formattedRole = role.charAt(0).toUpperCase() + role.slice(1).toLowerCase();
                    const options = Array.from(categoryEl.options).map(opt => opt.value);
                    if (options.includes(formattedRole)) {
                        categoryEl.value = formattedRole;
                    } else if (role.toLowerCase().includes('staff')) {
                        categoryEl.value = 'Staff';
                    } else if (role.toLowerCase().includes('student')) {
                        categoryEl.value = 'Student';
                    }
                }
            }
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
        sessionStorage.setItem('feedbackUserInfo', JSON.stringify(userInfo));
        sessionStorage.setItem('selectedOffice', office);
        const officeFiles = {
            'academic-registry': 'academic-registry-feedback.html',
            'accounts-office': 'accounts-office-feedback.html',
            'admissions': 'admissions-feedback.html',
            'career-guidance': 'career-guidance-feedback.html',
            'catering': 'catering-feedback.html',
            'chaplaincy': 'chaplaincy-feedback.html',
            'community-outreach': 'community-outreach-feedback.html',
            'corp-comm': 'corp-comm-feedback.html',
            'council-office': 'council-office-feedback.html',
            'counselling': 'counselling-feedback.html',
            'dean-students': 'dean-students-feedback.html',
            'dept-accounting': 'dept-accounting-feedback.html',
            'dept-admin': 'dept-admin-feedback.html',
            'dept-agri': 'dept-agri-feedback.html',
            'dept-biological': 'dept-biological-feedback.html',
            'dept-civil': 'dept-civil-feedback.html',
            'dept-economics': 'dept-economics-feedback.html',
            'dept-edu': 'dept-edu-feedback.html',
            'dept-elec': 'dept-elec-feedback.html',
            'dept-env': 'dept-env-feedback.html',
            'dept-humanities': 'dept-humanities-feedback.html',
            'dept-ict': 'dept-ict-feedback.html',
            'dept-math': 'dept-math-feedback.html',
            'dept-mech': 'dept-mech-feedback.html',
            'dept-physical': 'dept-physical-feedback.html',
            'dept-social': 'dept-social-feedback.html',
            'dvc-academic': 'dvc-academic-feedback.html',
            'dvc-admin': 'dvc-admin-feedback.html',
            'elearning': 'elearning-feedback.html',
            'estate': 'estate-feedback.html',
            'exams-office': 'exams-office-feedback.html',
            'fees-office': 'fees-office-feedback.html',
            'finance': 'finance-feedback.html',
            'games': 'games-feedback.html',
            'grounds': 'grounds-feedback.html',
            'health-unit': 'health-unit-feedback.html',
            'hostel': 'hostel-feedback.html',
            'hr-office': 'hr-office-feedback.html',
            'ict-services': 'ict-services-feedback.html',
            'industrial-attachment': 'industrial-attachment-feedback.html',
            'innovation-office': 'innovation-office-feedback.html',
            'internal-audit': 'internal-audit-feedback.html',
            'legal-services': 'legal-services-feedback.html',
            'library': 'library-feedback.html',
            'procurement': 'procurement-feedback.html',
            'quality-assurance': 'quality-assurance-feedback.html',
            'registrar-academic': 'registrar-academic-feedback.html',
            'registrar-admin': 'registrar-admin-feedback.html',
            'research-dir': 'research-dir-feedback.html',
            'research-postgrad': 'research-postgrad-feedback.html',
            'sanr-dean': 'sanr-dean-feedback.html',
            'sbe-dean': 'sbe-dean-feedback.html',
            'security': 'security-feedback.html',
            'seh-dean': 'seh-dean-feedback.html',
            'set-dean': 'set-dean-feedback.html',
            'ssc-dean': 'ssc-dean-feedback.html',
            'staff-welfare': 'staff-welfare-feedback.html',
            'student-affairs': 'student-affairs-feedback.html',
            'student-clubs': 'student-clubs-feedback.html',
            'timetabling': 'timetabling-feedback.html',
            'training-dev': 'training-dev-feedback.html',
            'transport': 'transport-feedback.html',
            'vc-office': 'vc-office-feedback.html'
};
        const fileName = officeFiles[office] || 'generic-feedback.html';
        window.location.href = `/departments/${fileName}?office=${office}`;
    }

    // ===== EVENT LISTENERS =====
    initializeEventListeners() {
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
                    input.style.cursor = isAnonymous ? 'not-allowed' : 'auto';
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
        
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (!href) return;
            let normalizedPath = currentPath;
            if (currentPath === '/' || currentPath === '/index.html') {
                normalizedPath = '/src/components/pages/home.html';
            }
            
            // Normalize href (ensure it starts with / for comparison if it's relative)
            let normalizedHref = href;
            if (!href.startsWith('/') && !href.startsWith('http')) {
                normalizedHref = '/' + href;
            }
            
            link.classList.remove('active');
            const currentFile = normalizedPath.split('/').pop();
            const hrefFile = normalizedHref.split('/').pop();
            
            if (normalizedPath === normalizedHref || (currentFile === hrefFile && currentFile !== '')) {
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
    saveTrackingIdToHistory(id, office, timestamp = null) {
        try {
            let history = JSON.parse(localStorage.getItem('feedback_history') || '[]');
            history = history.filter(item => item.id !== id);
            history.unshift({
                id: id,
                office: office,
                officeName: this.getOfficeName(office),
                date: timestamp || new Date().toISOString()
            });
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

    // Remove a single tracking ID from history
    removeFromTrackingHistory(id) {
        try {
            let history = JSON.parse(localStorage.getItem('feedback_history') || '[]');
            history = history.filter(item => item.id !== id);
            localStorage.setItem('feedback_history', JSON.stringify(history));
            return history;
        } catch (e) {
            console.error('Failed to remove from tracking history:', e);
            return [];
        }
    }

    // Clear all tracking history
    clearTrackingHistory() {
        localStorage.removeItem('feedback_history');
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
            const welcomeText = document.getElementById('header-welcome-text');
            if (welcomeText) {
                welcomeText.innerText = 'Welcome to admin panel, Customer Feedback System';
            }
        }
    }

    // ===== REAL-TIME TIMESTAMPS =====
    
    formatRelativeTime(timestamp) {
        if (!timestamp) return 'Unknown';
        try {
            const date = new Date(timestamp);
            return date.toLocaleString('en-KE', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: true
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
                if (!el.getAttribute('title')) {
                    el.setAttribute('title', new Date(timestamp).toLocaleString());
                }
            }
        });
    }

    startTimestampUpdater() {
        this.updateAllTimestamps();
        if (this.timeUpdateInterval) {
            clearInterval(this.timeUpdateInterval);
        }
        
        // Update every 30 seconds
        this.timeUpdateInterval = setInterval(() => {
            this.updateAllTimestamps();
        }, 30000);
    }
}

// Initialize the portal when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new FeedbackPortal();
});
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

// Start the portal
document.addEventListener('DOMContentLoaded', () => {
    if (!window.feedbackPortal) {
        window.feedbackPortal = new FeedbackPortal();
    }
});

// Immediately instantiate for scripts that need it before DOMContentLoaded
if (typeof window !== 'undefined' && !window.feedbackPortal) {
    window.feedbackPortal = new FeedbackPortal();
}