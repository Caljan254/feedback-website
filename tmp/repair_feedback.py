import sys
import os

# Add the backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.getcwd(), 'backend'))
sys.path.append(backend_path)

from database import SessionLocal
from models import Feedback, Department

def repair():
    db = SessionLocal()
    try:
        slug_map = {
            'vc-office': "Vice Chancellor’s Office",
            'dvc-academic': "Deputy Vice Chancellor (Academic)",
            'dvc-admin': "Deputy Vice Chancellor (Administration)",
            'registrar-academic': "Registrar (Academic Affairs)",
            'registrar-admin': "Registrar (Administration & HR)",
            'council-office': "University Council Office",
            'legal-services': "Legal Services Office",
            'corp-comm': "Corporate Communications",
            'admissions': "Admissions Office",
            'academic-registry': "Academic Registry",
            'exams-office': "Examinations Office",
            'timetabling': "Timetabling Office",
            'research-postgrad': "Research Directorate",
            'quality-assurance': "Quality Assurance",
            'industrial-attachment': "Attachment & Career Services",
            'elearning': "e-Learning Office",
            'ssc-dean': "School of Science & Computing - Dean’s Office",
            'dept-math': "Mathematics Department (Chairperson)",
            'dept-ict': "Computing & IT Department",
            'dept-physical': "Physical Sciences",
            'dept-biological': "Biological Sciences",
            'set-dean': "School of Engineering - Dean’s Office",
            'dept-civil': "Civil Engineering",
            'dept-elec': "Electrical Engineering",
            'dept-mech': "Mechanical Engineering",
            'sbe-dean': "School of Business - Dean’s Office",
            'dept-admin': "Business Administration",
            'dept-accounting': "Accounting & Finance",
            'dept-economics': "Economics",
            'seh-dean': "School of Education & Social Sciences - Dean’s Office",
            'dept-edu': "Educational Studies",
            'dept-social': "Social Sciences",
            'dept-humanities': "Humanities",
            'sanr-dean': "School of Agriculture & Environment - Dean’s Office",
            'dept-env': "Environmental Science",
            'dept-agri': "Agricultural Sciences",
            'dean-students': "Dean of Students",
            'student-affairs': "Student Affairs",
            'counselling': "Counselling Services",
            'chaplaincy': "Chaplaincy",
            'career-guidance': "Attachment & Career Services",
            'games': "Games & Sports",
            'student-clubs': "Student Clubs",
            'finance': "Finance Department",
            'fees-office': "Fees Office",
            'accounts-office': "Accounts Office",
            'procurement': "Procurement Office",
            'internal-audit': "Internal Audit",
            'hr-office': "Human Resource",
            'staff-welfare': "Staff Welfare",
            'training-dev': "Training & Development",
            'library': "Library",
            'ict-services': "ICT Services",
            'health-unit': "Health Unit",
            'hostel': "Hostel / Accommodation",
            'catering': "Catering",
            'estate': "Estate / Maintenance",
            'transport': "Transport",
            'security': "Security",
            'grounds': "Grounds & Cleaning",
            'research-dir': "Research Directorate",
            'innovation-office': "Innovation Office",
            'community-outreach': "Community Outreach"
        }

        feedbacks = db.query(Feedback).filter(Feedback.department_id == None).all()
        print(f"Found {len(feedbacks)} feedback records to repair.")

        repaired_count = 0
        for f in feedbacks:
            if f.office:
                office_val = f.office.lower()
                dept_name = slug_map.get(office_val, office_val)
                dept = db.query(Department).filter(Department.name.ilike(dept_name)).first()
                if dept:
                    f.department_id = dept.id
                    repaired_count += 1
                    print(f"Repaired Feedback ID {f.id}: Assigned to '{dept.name}'")
                else:
                    print(f"Could not find department for office slug: '{f.office}' (mapped to '{dept_name}')")
        
        db.commit()
        print(f"Successfully repaired {repaired_count} records.")

    except Exception as e:
        print(f"Error during repair: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    repair()
