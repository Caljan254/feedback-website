import os

departments_data = [
    {"name": "Academic Registry", "file": "academic-registry-feedback.html", "type": "admin"},
    {"name": "Accounts Office", "file": "accounts-office-feedback.html", "type": "admin"},
    {"name": "Admissions Office", "file": "admissions-feedback.html", "type": "admin"},
    {"name": "Career Guidance", "file": "career-guidance-feedback.html", "type": "support"},
    {"name": "Catering Services", "file": "catering-feedback.html", "type": "support", "special": "catering"},
    {"name": "Chaplaincy", "file": "chaplaincy-feedback.html", "type": "support"},
    {"name": "Community Outreach", "file": "community-outreach-feedback.html", "type": "admin"},
    {"name": "Corporate Communication", "file": "corp-comm-feedback.html", "type": "admin"},
    {"name": "Council Office", "file": "council-office-feedback.html", "type": "admin"},
    {"name": "Counselling", "file": "counselling-feedback.html", "type": "support"},
    {"name": "Dean of Students", "file": "dean-students-feedback.html", "type": "support"},
    {"name": "DP Accounting", "file": "dept-accounting-feedback.html", "type": "academic"},
    {"name": "DP Admin", "file": "dept-admin-feedback.html", "type": "academic"},
    {"name": "DP Agriculture", "file": "dept-agri-feedback.html", "type": "academic", "special": "agriculture"},
    {"name": "DP Biological Sciences", "file": "dept-biological-feedback.html", "type": "academic", "special": "science"},
    {"name": "DP Civil Engineering", "file": "dept-civil-feedback.html", "type": "academic", "special": "engineering"},
    {"name": "DP Economics", "file": "dept-economics-feedback.html", "type": "academic"},
    {"name": "DP Education", "file": "dept-edu-feedback.html", "type": "academic"},
    {"name": "DP Electrical Eng", "file": "dept-elec-feedback.html", "type": "academic", "special": "engineering"},
    {"name": "DP Environmental", "file": "dept-env-feedback.html", "type": "academic"},
    {"name": "DP Humanities", "file": "dept-humanities-feedback.html", "type": "academic"},
    {"name": "DP ICT", "file": "dept-ict-feedback.html", "type": "academic", "special": "tech"},
    {"name": "DP Mathematics", "file": "dept-math-feedback.html", "type": "academic"},
    {"name": "DP Mechanical Eng", "file": "dept-mech-feedback.html", "type": "academic", "special": "engineering"},
    {"name": "DP Physical Sciences", "file": "dept-physical-feedback.html", "type": "academic", "special": "science"},
    {"name": "DP Social Sciences", "file": "dept-social-feedback.html", "type": "academic"},
    {"name": "DVC Academic", "file": "dvc-academic-feedback.html", "type": "admin"},
    {"name": "DVC Admin", "file": "dvc-admin-feedback.html", "type": "admin"},
    {"name": "E-Learning", "file": "elearning-feedback.html", "type": "academic", "special": "tech"},
    {"name": "Estate Office", "file": "estate-feedback.html", "type": "support"},
    {"name": "Exams Office", "file": "exams-office-feedback.html", "type": "academic"},
    {"name": "Fees Office", "file": "fees-office-feedback.html", "type": "admin"},
    {"name": "Finance Department", "file": "finance-feedback.html", "type": "admin"},
    {"name": "Games & Sports", "file": "games-feedback.html", "type": "support", "special": "sports"},
    {"name": "Grounds & Estates", "file": "grounds-feedback.html", "type": "support"},
    {"name": "Health Services", "file": "health-feedback.html", "type": "support", "special": "health"},
    {"name": "Health Unit", "file": "health-unit-feedback.html", "type": "support", "special": "health"},
    {"name": "Hostels", "file": "hostel-feedback.html", "type": "support", "special": "hostel"},
    {"name": "Human Resources", "file": "hr-office-feedback.html", "type": "admin"},
    {"name": "ICT Office", "file": "ict-feedback.html", "type": "admin", "special": "tech"},
    {"name": "ICT Services", "file": "ict-services-feedback.html", "type": "admin", "special": "tech"},
    {"name": "Industrial Attachment", "file": "industrial-attachment-feedback.html", "type": "academic"},
    {"name": "Innovation Office", "file": "innovation-office-feedback.html", "type": "admin"},
    {"name": "Internal Audit", "file": "internal-audit-feedback.html", "type": "admin"},
    {"name": "Legal Services", "file": "legal-services-feedback.html", "type": "admin"},
    {"name": "Library", "file": "library-feedback.html", "type": "support", "special": "library"},
    {"name": "Procurement", "file": "procurement-feedback.html", "type": "admin"},
    {"name": "Quality Assurance", "file": "quality-assurance-feedback.html", "type": "admin"},
    {"name": "Registrar Academic", "file": "registrar-academic-feedback.html", "type": "admin"},
    {"name": "Registrar Admin", "file": "registrar-admin-feedback.html", "type": "admin"},
    {"name": "Registry", "file": "registry-feedback.html", "type": "admin"},
    {"name": "Research Directorate", "file": "research-dir-feedback.html", "type": "academic"},
    {"name": "Postgraduate Research", "file": "research-postgrad-feedback.html", "type": "academic"},
    {"name": "SANR Dean", "file": "sanr-dean-feedback.html", "type": "academic"},
    {"name": "SBE Dean", "file": "sbe-dean-feedback.html", "type": "academic"},
    {"name": "Security Services", "file": "security-feedback.html", "type": "support", "special": "security"},
    {"name": "SEH Dean", "file": "seh-dean-feedback.html", "type": "academic"},
    {"name": "SET Dean", "file": "set-dean-feedback.html", "type": "academic"},
    {"name": "SSC Dean", "file": "ssc-dean-feedback.html", "type": "academic"},
    {"name": "Staff Welfare", "file": "staff-welfare-feedback.html", "type": "admin"},
    {"name": "Student Affairs", "file": "student-affairs-feedback.html", "type": "support"},
    {"name": "Student Clubs", "file": "student-clubs-feedback.html", "type": "support"},
    {"name": "Timetabling", "file": "timetabling-feedback.html", "type": "academic"},
    {"name": "Training & Dev", "file": "training-dev-feedback.html", "type": "admin"},
    {"name": "Transport", "file": "transport-feedback.html", "type": "support", "special": "transport"},
    {"name": "VC Office", "file": "vc-office-feedback.html", "type": "admin"}
]

def generate_html(name, filepath, dept_type, special=None):
    # Template parts
    header = f'''<!DOCTYPE html>
<html lang="en" class="scroll-smooth">

<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>{name.upper()} FEEDBACK - SEKU Feedback</title>
    <link rel="icon" type="image/x-icon" href="../../favicon.ico">
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free/css/all.min.css" />
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <style>
        .notification {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(0.95);
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            z-index: 9999;
            max-width: 90%;
            width: auto;
            min-width: 280px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            opacity: 0;
            transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
        }}

        .notification.show {{
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
        }}

        .notification.success {{
            background-color: #10B981;
            color: white;
        }}

        .notification.error {{
            background-color: #EF4444;
            color: white;
        }}

        .notification.warning {{
            background-color: #F59E0B;
            color: white;
        }}

        .notification.info {{
            background-color: #3B82F6;
            color: white;
        }}

        .notification-icon {{
            margin-right: 0.75rem;
            font-size: 1.1rem;
        }}

        .notification-content {{
            flex-grow: 1;
            font-size: 0.95rem;
        }}

        .notification-close {{
            margin-left: 0.75rem;
            cursor: pointer;
            opacity: 0.8;
        }}

        .notification-close:hover {{
            opacity: 1;
        }}

        .form-input:focus {{
            border-color: #10B981;
            box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
        }}

        body {{
            display: flex;
            flex-direction: column;
            min-height: 100vh;
        }}

        .content-wrapper {{
            flex: 1 0 auto;
        }}

        footer {{
            flex-shrink: 0;
        }}
    </style>
</head>

<body class="bg-gray-100 dark:bg-gray-900 text-gray-800 dark:text-gray-100">
    <div id="header-placeholder"></div>
    <div class="content-wrapper max-w-4xl mx-auto px-4 py-8">
        <div id="notification-container"
            class="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"></div>
        <div class="mb-6">
            <button onclick="goBack()" class="flex items-center text-blue-600 hover:text-blue-700 transition-colors">
                <i class="fas fa-arrow-left mr-2"></i> ← Back to Office Selection
            </button>
        </div>
        <div id="user-info-display"
            class="hidden bg-blue-50 dark:bg-blue-900 p-4 rounded-lg mb-6 text-gray-800 dark:text-gray-200"></div>
        <section
            class="bg-blue-50/50 dark:bg-gray-800 p-8 rounded-2xl shadow-lg border border-blue-100 dark:border-gray-700">
            <h3 id="department-title" class="text-3xl font-bold text-blue-900 dark:text-blue-300 mb-8 uppercase">{name.upper()} FEEDBACK</h3>

            <form class="department-feedback-form space-y-8"
                x-data="{{ compliments: '', complaints: '', suggestions: '' }}">'''

    # Define specialized sets
    q1_opts = ['General Inquiry', 'Seeking Assistance', 'Reporting an Issue', 'Follow-up on Previous Case', 'Appointment', 'Official Application']
    if special == "catering":
        q1_opts = ['Meals/Dining service', 'Catering booking/Events', 'Cafeteria hygiene/Menu', 'Staff assistance', 'Payment/Invoicing', 'General feedback']
    elif special == "security":
        q1_opts = ['Crime/Incident reporting', 'Seeking assistance/Directions', 'Clearance/Pass request', 'Reporting lost & found', 'Gate/Security checkpoint', 'General patrol inquiry']
    elif special == "transport":
        q1_opts = ['University shuttle service', 'Trip/Transport booking', 'Driver/Staff behavior', 'Vehicle maintenance/Condition', 'Routes/Timetable inquiry', 'General transport assistance']
    elif special == "health":
        q1_opts = ['Medical consultation', 'Prescription/Pharmacy', 'Laboratory testing', 'Emergency assistance', 'Medical records/Referral', 'Health checkup']
    elif special == "library":
        q1_opts = ['Book borrowing/Returning', 'E-resources/Digital library access', 'Quiet study area/Seating', 'Reference/Research assistance', 'Reprography/Fine payment', 'Library orientation']
    elif special == "tech":
        q1_opts = ['Wi-Fi/Network connectivity', 'Email/Portal access issue', 'Hardware/Software support', 'E-Learning platform assistance', 'General IT inquiry', 'Smart card/ID issue']
    elif special == "sports":
        q1_opts = ['Gym/Sports facility access', 'Equipment booking/Use', 'Team training/Registration', 'Coaching/Coordination', 'Sports event inquiry', 'General facility feedback']
    elif special == "science":
        q1_opts = ['Course registration/Advising', 'Laboratory practical session', 'Equipment/Apparatus request', 'Research/Project supervision', 'Consultation with lecturer', 'Exam/Result inquiry']
    elif special == "agriculture":
        q1_opts = ['Field practical/Farm session', 'Crop/Livestock research', 'Advisory/Extension service', 'Laboratory/Lab equipment use', 'Project supervision', 'General consultation']
    elif special == "engineering":
        q1_opts = ['Workshop/Lab session', 'Technical project work', 'Equipment/Tools request', 'Lecturer/Workshop technician consult', 'Industrial attachment follow-up', 'Design/Drawing studio access']
    elif dept_type == "academic":
        q1_opts = ['Class session/Lectures', 'Assignment/Coursework query', 'Exam/Result inquiry', 'Academic advising/Mentorship', 'Departmental clearance', 'Project/Thesis supervision']
    elif special == "hostel":
        q1_opts = ['Room allocation/Application', 'Room repairs/Maintenance', 'Cleanliness/Common room hygiene', 'Security/Night safety', 'Hostel warden consultation', 'Entry/Exit clearance']

    q_content = f'''
                <!-- Question 1 -->
                <div class="dynamic-question-block space-y-4" data-question-id="3"
                    x-data="{{ otherPurpose: false, otherText: '' }}">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">1. What was the primary purpose of your visit to {name}? (Select one)</p>
                    <div class="space-y-3 pl-2">
                        <template
                            x-for="opt in {str(q1_opts)}">
                            <label class="flex items-center cursor-pointer group">
                                <input type="radio" name="dq_3" :value="opt" required @change="otherPurpose = false"
                                    class="w-5 h-5 text-blue-600 focus:ring-blue-500 border-gray-300">
                                <span
                                    class="ml-3 text-gray-700 dark:text-gray-300 group-hover:text-blue-600 transition-colors"
                                    x-text="opt"></span>
                            </label>
                        </template>
                        <label class="flex items-center cursor-pointer group">
                            <input type="radio" name="dq_3" :value="otherText" required @change="otherPurpose = true"
                                class="w-5 h-5 text-blue-600 focus:ring-blue-500 border-gray-300">
                            <span
                                class="ml-3 text-gray-700 dark:text-gray-300 group-hover:text-blue-600 transition-colors">Other:</span>
                            <input type="text" x-model="otherText" x-show="otherPurpose" x-bind:required="otherPurpose"
                                class="ml-2 border-b-2 border-gray-300 bg-transparent outline-none focus:border-blue-500 px-2 py-0.5 text-sm transition-all"
                                placeholder="Specify here..." x-effect="if(otherPurpose) $nextTick(() => $el.focus())">
                        </label>
                    </div>
                </div>'''

    if dept_type == "academic":
        quality_label = f"How would you rate the quality of instruction and academic support in {name}?"
        quality_desc = "(Consider lectures, tutorials, course materials, and staff helpfulness)"
        grid_items = [
            {"id": "7", "text": "Responsiveness to academic inquiries"},
            {"id": "9", "text": "Availability of study materials/resources"},
            {"id": "11", "text": "Staff-student relationship & guidance"}
        ]
        if special in ["science", "engineering", "agriculture", "tech"]:
            grid_items = [
                {"id": "7", "text": "Laboratory/Workshop facilities & equipment"},
                {"id": "9", "text": "Practical demonstrations & tech support"},
                {"id": "11", "text": "Classroom environment & resources"}
            ]
        
        q_content += f'''
                <!-- Question 2 -->
                <div class="dynamic-question-block space-y-4" data-question-id="5">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">2. {quality_label} <span
                            class="text-sm font-normal text-gray-500 block mt-1">{quality_desc}</span></p>
                    <div class="space-y-3 pl-2">
                        <template
                            x-for="opt in ['Excellent - Very comprehensive and helpful', 'Good - Well-structured and clear', 'Average - Adequate but could be better', 'Poor - Lacks depth or clarity', 'Very Poor - Inadequate']">
                            <label class="flex items-center cursor-pointer group">
                                <input type="radio" :name="'dq_5'" :value="opt" required
                                    class="w-5 h-5 text-blue-600 focus:ring-blue-500 border-gray-300">
                                <span
                                    class="ml-3 text-gray-700 dark:text-gray-300 group-hover:text-blue-600 transition-colors"
                                    x-text="opt"></span>
                            </label>
                        </template>
                    </div>
                </div>

                <!-- Question 3 Grid -->
                <div class="space-y-4">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">3. How would you rate the following departmental areas?</p>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead>
                                <tr class="bg-blue-50 dark:bg-gray-700/50">
                                    <th class="px-4 py-3 text-sm font-bold text-gray-700 dark:text-gray-300">Aspect</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">Excellent</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">Good</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">Fair</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">Poor</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">N/A</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">'''
        for item in grid_items:
            q_content += f'''
                                <tr class="dynamic-question-block" data-question-id="{item['id']}">
                                    <td class="px-4 py-4 text-sm text-gray-700 dark:text-gray-300">{item['text']}</td>
                                    <template x-for="val in ['Excellent', 'Good', 'Fair', 'Poor', 'Not Applicable']">
                                        <td class="px-2 py-4 text-center">
                                            <input type="radio" name="dq_{item['id']}" :value="val" required class="w-4 h-4 text-blue-600">
                                        </td>
                                    </template>
                                </tr>'''
        q_content += f'''
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Question 4 -->
                <div class="dynamic-question-block space-y-4" data-question-id="15">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">4. Rate your experience with departmental communication (notices, emails, timetables):</p>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pl-2">
                        <template x-for="opt in ['Very Effective', 'Effective', 'Neutral', 'Ineffective', 'Needs Urgent Improvement']">
                            <label class="flex items-center cursor-pointer group">
                                <input type="radio" :name="'dq_15'" :value="opt" required
                                    class="w-5 h-5 text-blue-600 border-gray-300">
                                <span class="ml-3 text-gray-700 dark:text-gray-300 group-hover:text-blue-600 transition-all font-medium" x-text="opt"></span>
                            </label>
                        </template>
                    </div>
                </div>

                <!-- Question 5 -->
                <div class="dynamic-question-block space-y-4" data-question-id="17">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">5. How satisfied are you with the professionalism and approachability of the staff?</p>
                    <div class="space-y-3 pl-2">
                        <template
                            x-for="opt in ['Highly Satisfied - Professional and helpful', 'Satisfied - Met expectations', 'Neutral - Average experience', 'Dissatisfied - Unprofessional behavior', 'Did not interact with staff']">
                            <label class="flex items-center cursor-pointer group">
                                <input type="radio" :name="'dq_17'" :value="opt" required
                                    class="w-5 h-5 text-blue-600 border-gray-300">
                                <span class="ml-3 text-gray-700 dark:text-gray-300 group-hover:text-blue-600 transition-colors" x-text="opt"></span>
                            </label>
                        </template>
                    </div>
                </div>'''
    else: # support or admin
        quality_label = f"How would you rate the efficiency and quality of service at {name}?"
        quality_desc = "(Consider waiting time, clarity of procedures, and staff professionalism)"
        grid_items = [
            {"id": "7", "text": "Waiting time for service"},
            {"id": "9", "text": "Clarity of information/guidance"},
            {"id": "11", "text": "Problem-solving effectiveness"}
        ]
        if special == "catering":
            grid_items = [
                {"id": "7", "text": "Food quality & taste"},
                {"id": "9", "text": "Hygiene & cleanliness"},
                {"id": "11", "text": "Menu variety & pricing"}
            ]
        elif special == "security":
            grid_items = [
                {"id": "7", "text": "Response to security concerns"},
                {"id": "9", "text": "Visibility & presence of guards"},
                {"id": "11", "text": "Night lighting & safety measures"}
            ]
        elif special == "health":
            grid_items = [
                {"id": "7", "text": "Consultation quality"},
                {"id": "9", "text": "Medicine availability"},
                {"id": "11", "text": "Emergency response speed"}
            ]
        elif special == "hostel":
            grid_items = [
                {"id": "7", "text": "Room/Maintenance repairs"},
                {"id": "9", "text": "Cleanliness of common areas"},
                {"id": "11", "text": "Security within the hostel"}
            ]

        q_content += f'''
                <!-- Question 2 -->
                <div class="dynamic-question-block space-y-4" data-question-id="5">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">2. {quality_label} <span
                            class="text-sm font-normal text-gray-500 block mt-1">{quality_desc}</span></p>
                    <div class="space-y-3 pl-2">
                        <template
                            x-for="opt in ['Excellent - Very efficient and helpful', 'Good - Helpful and clear', 'Average - Acceptable speed/quality', 'Poor - Slow and inefficient', 'Very Poor - Unacceptable']">
                            <label class="flex items-center cursor-pointer group">
                                <input type="radio" :name="'dq_5'" :value="opt" required
                                    class="w-5 h-5 text-blue-600 focus:ring-blue-500 border-gray-300">
                                <span
                                    class="ml-3 text-gray-700 dark:text-gray-300 group-hover:text-blue-600 transition-colors"
                                    x-text="opt"></span>
                            </label>
                        </template>
                    </div>
                </div>

                <!-- Question 3 Grid -->
                <div class="space-y-4">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">3. Rate the following service aspects:</p>
                    <div class="overflow-x-auto">
                        <table class="w-full text-left border-collapse">
                            <thead>
                                <tr class="bg-blue-50 dark:bg-gray-700/50">
                                    <th class="px-4 py-3 text-sm font-bold text-gray-700 dark:text-gray-300">Aspect</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">Excellent</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">Good</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">Fair</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">Poor</th>
                                    <th class="px-2 py-3 text-sm font-bold text-center text-gray-700 dark:text-gray-300">N/A</th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">'''
        for item in grid_items:
            q_content += f'''
                                <tr class="dynamic-question-block" data-question-id="{item['id']}">
                                    <td class="px-4 py-4 text-sm text-gray-700 dark:text-gray-300">{item['text']}</td>
                                    <template x-for="val in ['Excellent', 'Good', 'Fair', 'Poor', 'Not Applicable']">
                                        <td class="px-2 py-4 text-center">
                                            <input type="radio" name="dq_{item['id']}" :value="val" required class="w-4 h-4 text-blue-600">
                                        </td>
                                    </template>
                                </tr>'''
        q_content += f'''
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Question 4 -->
                <div class="dynamic-question-block space-y-4" data-question-id="15">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">4. How satisfied were you with the professionalism of the staff member you interacted with?</p>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 pl-2">
                        <template x-for="opt in ['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied', 'Very Dissatisfied']">
                            <label class="flex items-center cursor-pointer group">
                                <input type="radio" :name="'dq_15'" :value="opt" required
                                    class="w-5 h-5 text-blue-600 border-gray-300">
                                <span class="ml-3 text-gray-700 dark:text-gray-300 group-hover:text-blue-600 transition-all font-medium" x-text="opt"></span>
                            </label>
                        </template>
                    </div>
                </div>

                <!-- Question 5 -->
                <div class="dynamic-question-block space-y-4" data-question-id="17">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg">5. How easy was it to access the service or office today?</p>
                    <div class="space-y-3 pl-2">
                        <template
                            x-for="opt in ['Very Easy - Convenient location/access', 'Easy - Standard access', 'Moderate - Some difficulty', 'Difficult - Hard to find or access', 'Very Difficult - Inaccessible']">
                            <label class="flex items-center cursor-pointer group">
                                <input type="radio" :name="'dq_17'" :value="opt" required
                                    class="w-5 h-5 text-blue-600 border-gray-300">
                                <span class="ml-3 text-gray-700 dark:text-gray-300 group-hover:text-blue-600 transition-colors" x-text="opt"></span>
                            </label>
                        </template>
                    </div>
                </div>'''

    footer = f'''
                <!-- Question 9: Overall Rating -->
                <div class="dynamic-question-block space-y-4" data-question-id="23">
                    <p class="text-gray-800 dark:text-gray-200 font-semibold text-lg font-bold border-t pt-6">9.
                        Overall, how would you rate your experience with {name} Feedback today? *</p>
                    <div class="flex flex-wrap items-center gap-6 pl-2" x-data="{{ currentRating: '' }}">
                        <label class="flex items-center cursor-pointer group py-2 px-4 bg-white dark:bg-gray-700 rounded-xl border-2 border-transparent hover:border-blue-500 transition-all shadow-sm">
                            <input type="radio" name="dq_23" value="Excellent" required @change="currentRating = 'Excellent'" class="w-5 h-5 text-blue-600 border-gray-300">
                            <span class="ml-3 text-gray-700 dark:text-gray-300 font-bold">Excellent</span>
                        </label>
                        <label class="flex items-center cursor-pointer group py-2 px-4 bg-white dark:bg-gray-700 rounded-xl border-2 border-transparent hover:border-blue-500 transition-all shadow-sm">
                            <input type="radio" name="dq_23" value="Good" required @change="currentRating = 'Good'" class="w-5 h-5 text-blue-600 border-gray-300">
                            <span class="ml-3 text-gray-700 dark:text-gray-300 font-bold">Good</span>
                        </label>
                        <label class="flex items-center cursor-pointer group py-2 px-4 bg-white dark:bg-gray-700 rounded-xl border-2 border-transparent hover:border-blue-500 transition-all shadow-sm">
                            <input type="radio" name="dq_23" value="Average" required @change="currentRating = 'Average'" class="w-5 h-5 text-blue-600 border-gray-300">
                            <span class="ml-3 text-gray-700 dark:text-gray-300 font-bold">Average</span>
                        </label>
                        <label class="flex items-center cursor-pointer group py-2 px-4 bg-white dark:bg-gray-700 rounded-xl border-2 border-transparent hover:border-blue-500 transition-all shadow-sm">
                            <input type="radio" name="dq_23" value="Poor" required @change="currentRating = 'Poor'" class="w-5 h-5 text-blue-600 border-gray-300">
                            <span class="ml-3 text-gray-700 dark:text-gray-300 font-bold">Poor</span>
                        </label>
                        
                        <!-- Map to core rating for admin dashboard fallback -->
                        <input type="hidden" name="q_4" :value="currentRating">
                        <input type="hidden" name="rating" :value="currentRating">
                    </div>
                </div>

                <!-- Question 10: Compliments & Complaints -->
                <div
                    class="space-y-6 bg-blue-50/50 dark:bg-gray-700/30 p-6 rounded-2xl border border-blue-100 dark:border-gray-600">
                    <p class="text-gray-800 dark:text-gray-200 font-bold text-xl mb-4">10. Please share your specific
                        Complaints and/or Compliments to help us improve. <span
                            class="text-sm font-normal text-red-500 block mt-1 italic">(All fields are mandatory) *</span>
                    </p>

                    <div class="space-y-3">
                        <label class="text-blue-700 dark:text-blue-300 font-semibold block underline">Compliments (What
                            went well? Was there a staff member or facility that stood out?) *</label>
                        <textarea x-model="compliments" rows="3" required
                            class="w-full rounded-xl border-2 border-white dark:border-gray-600 bg-white dark:bg-gray-800 p-4 shadow-sm outline-none focus:border-blue-500 transition-all"
                            placeholder="Share your positive feedback..."></textarea>
                    </div>

                    <div class="space-y-3">
                        <label class="text-red-700 dark:text-red-300 font-semibold block underline">Complaints (What
                            went wrong or needs improvement?) *</label>
                        <textarea x-model="complaints" rows="3" required
                            class="w-full rounded-xl border-2 border-white dark:border-gray-600 bg-white dark:bg-gray-800 p-4 shadow-sm outline-none focus:border-red-500 transition-all"
                            placeholder="Tell us what needs attention..."></textarea>
                    </div>
                </div>

                <!-- Question 11: General Comments -->
                <div class="space-y-4">
                    <label class="text-gray-800 dark:text-gray-200 font-semibold text-lg block">11. Do you have any
                        general comments, suggestions, or specific areas where we need to improve? *</label>
                    <textarea x-model="suggestions" rows="4" required
                        class="w-full rounded-xl border-2 border-blue-100 focus:border-blue-500 dark:bg-gray-700 dark:text-white dark:border-gray-600 p-4 shadow-sm outline-none transition-all"
                        placeholder="Additional comments or suggestions..."></textarea>
                </div>

                <!-- Final Message Accumulator -->
                <input type="hidden" name="comment"
                    x-effect="$el.value = `COMPLIMENTS: ${{compliments || 'N/A'}}\\n\\nCOMPLAINTS: ${{complaints || 'N/A'}}\\n\\nSUGGESTIONS: ${{suggestions || 'N/A'}}`">

                <div class="pt-6">
                    <button type="submit"
                        class="bg-blue-600 text-white px-8 py-4 rounded-xl shadow-lg hover:bg-blue-700 w-full transition-all duration-300 text-xl font-bold tracking-wide transform hover:-translate-y-1 active:scale-95 flex items-center justify-center gap-3">
                        <i class="fas fa-paper-plane text-sm"></i> Submit Feedback
                    </button>
                    <p class="text-center text-xs text-gray-400 mt-4 italic">Your feedback is confidential and used to
                        improve university services.</p>
                </div>
            </form>
        </section>
    </div>
    <div id="footer-placeholder"></div>
    <script src="../../src/js/load-components.js"></script>
    <script src="../../src/js/feedback-portal.js"></script>
</body>

</html>'''

    full_html = header + q_content + footer
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_html)

# Run the generation
output_dir = r"c:\Caleb.Homepage\seku-feedback-mng-sytem\frontend\public\departments"
os.makedirs(output_dir, exist_ok=True)

for dept in departments_data:
    target_path = os.path.join(output_dir, dept["file"])
    # We want to overwrite all to the new specialized questions
    print(f"Updating {dept['name']}...")
    generate_html(dept["name"], target_path, dept["type"], dept.get("special"))
