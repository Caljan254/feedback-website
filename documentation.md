# SEKU Feedback Management System
## Comprehensive Technical Documentation

---

### 1. Executive Summary
The **SEKU Feedback Management System** is a full-stack web application designed to collect, manage, and analyze feedback from students, staff, and visitors across various university departments. It bridges the gap between university stakeholders and administrators by providing an intuitive submission portal and a powerful, data-driven admin dashboard.

---

### 2. System Architecture
The application follows a decoupled client-server architecture:
*   **Frontend (Client):** Rendered purely in the browser using HTML5, TailwindCSS for styling, Alpine.js for lightweight reactive state, and Vanilla JavaScript for business logic.
*   **Backend (API Server):** A fast, asynchronous RESTful API built with Python and the FastAPI framework.
*   **Database:** A relational structure hosted on MySQL, interfaced via SQLAlchemy ORM.

---

### 3. Frontend Overview
The frontend is built to be fast, responsive, and highly dynamic without relying on heavy single-page application frameworks like React or Angular.

**Core Technologies:**
*   **HTML5 & CSS3:** Structural foundation.
*   **Tailwind CSS:** Utility-first CSS framework used for highly customized, responsive, and modern UI design (including dark mode support).
*   **Alpine.js:** Used for localized state management, DOM manipulation, and dynamic UI interactions (e.g., toggling modals, reactive form fields).
*   **Vanilla JavaScript (`feedback-portal.js`):** Handles core logic, API communication (via `fetch`), form validation, and session management.

**Key Components:**
1.  **Department-Specific Forms (`/public/departments/`):** Over 30 specialized HTML forms tailored to individual offices (e.g., Vice Chancellor, ICT Services, Academic Registry). Each form asks department-specific questions.
2.  **Global Form Handler:** `feedback-portal.js` intercepts form submissions, performs strict client-side validation (ensuring required fields, compliments, and complaints are filled), collects both static and dynamic responses, and sends a consolidated JSON payload to the backend.
3.  **Admin Dashboard (`admin.html`):** A secure, authenticated portal for administrators. Features include:
    *   Chronological feedback feed prioritizing "Top Concerns" (highlighted in red).
    *   Status tracking (Read, Unread, Replied).
    *   Modal interfaces for reading full feedback details, replying directly to users, and viewing system activity logs.
    *   Exporting feedback data to CSV.
4.  **Data Mining & Analytics Panel:** A dynamic dashboard that parses all feedback arrays in real-time to generate:
    *   **Sentiment Score:** Calculates the overall positivity based on user ratings and positive textual signals.
    *   **Resolution Efficiency:** Measures how effectively issues are being solved based on specific resolution-oriented questions.
    *   **Actionability & Anonymity Indices:** Evaluates the thoroughness of the feedback and the ratio of anonymous submissions.
    *   **Category Distribution & Top Concerns:** Aggregates and visually maps the most frequent issues and the departments receiving them.

---

### 4. Backend Overview
The backend acts as the secure data processing layer, handling validation, storage, and retrieval.

**Core Technologies:**
*   **FastAPI (Python):** Chosen for its extreme speed, asynchronous capabilities, and automatic API documentation (Swagger UI).
*   **SQLAlchemy ORM:** Used to map Python objects to MySQL database tables, preventing SQL injection and simplifying data relationships.
*   **PyMySQL:** The database driver connecting Python to the MySQL server.
*   **Pydantic:** Used for strict data validation and schema definition, ensuring the backend only accepts properly formatted data from the frontend.
*   **JWT (JSON Web Tokens):** Handles secure authentication and role-based access control.

**Core Database Entities (`models.py`):**
1.  **User:** Stores staff, students, and admin credentials, including hashed passwords and role assignments.
2.  **Feedback:** The core entity storing submission details (Name, Email, Category, Office, Message, Rating, Tracking ID, Read/Replied status).
3.  **Department:** Stores office names and allows routing feedback to specific departmental admins.
4.  **Question & QuestionResponse:** A highly dynamic system allowing custom questions per department. `QuestionResponse` saves both the user's answer and the *exact visible question text* (`question_text`) they were asked at the time of submission.
5.  **ActivityLog:** An audit trail tracking admin actions (e.g., "Replied to feedback", "Viewed analytics").

**Core API Endpoints (`routes.py`):**
*   **`POST /api/auth/login`:** Authenticates users and returns a JWT.
*   **`POST /api/submit-feedback`:** Receives the complex JSON payload, maps the office string to a Department ID, generates a unique Tracking ID (`REF-XXXX`), saves the feedback, saves the dynamic question responses, and triggers background email notifications.
*   **`GET /api/admin/feedback`:** Retrieves all feedback using eagerly loaded relationships (`selectinload`) to optimize database query performance and prevent N+1 issues.
*   **`POST /api/admin/reply`:** Allows admins to send direct email responses to users from the dashboard.

---

### 5. Data Flow Lifecycle (From User to Admin)

1.  **Interaction:** A user visits a department feedback page (e.g., Vice Chancellor's Office) and fills out ratings, text areas, and mandatory comments.
2.  **Validation:** Upon clicking "Submit", `feedback-portal.js` halts the process. It sweeps the DOM to ensure no required fields, compliments, or complaints are empty. Unanswered fields are highlighted in red.
3.  **Packaging:** The JS script extracts the values, *visibly reading the specific HTML question text* (to prevent database ID mismatches), and builds a JSON payload.
4.  **Submission:** The payload is sent via a `POST` request to the FastAPI backend.
5.  **Processing:** The backend validates the payload against Pydantic schemas, saves it to MySQL, maps it to a tracking ID, schedules an asynchronous background task to notify admins via email, and returns a success response.
6.  **Admin Review:** An authenticated admin logs into the dashboard. The frontend fetches the data from the API. The admin can read the full context (including the dynamically saved, department-specific question labels), reply to the user, and view real-time data analytics.

---

### 6. Security Features
*   **JWT Authentication:** Protects all `/api/admin/*` routes from unauthorized access.
*   **Input Validation:** Pydantic schemas immediately reject malformed or malicious data before it reaches the core logic.
*   **Client-Side Protection:** HTML5 `required` tags supplemented by rigorous JavaScript validation (`feedback-portal.js`) ensure complete, non-empty data objects are built.
*   **SQL Injection Prevention:** Pure reliance on SQLAlchemy ORM parameterized queries; raw SQL is completely avoided in API transactions.
*   **Secure Password Hashing:** User passwords are never stored in plaintext within the database.
