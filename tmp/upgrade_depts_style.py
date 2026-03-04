import os
import re

def upgrade_all_depts():
    dept_dir = r'c:\Caleb.Homepage\seku-feedback-mng-sytem\frontend\public\departments'
    generic_file = os.path.join(dept_dir, 'generic-feedback.html')
    
    with open(generic_file, 'r', encoding='utf-8') as f:
        generic_template = f.read()

    files = [f for f in os.listdir(dept_dir) if f.endswith('.html') and f != 'generic-feedback.html']
    
    # We want to preserve the SPECIALIZED QUESTIONS but use the PREMIUM STYLE
    # Specialized departments:
    specialized = ['ict-feedback.html', 'admissions-feedback.html', 'finance-feedback.html']
    
    restored_count = 0
    
    for file_name in files:
        full_path = os.path.join(dept_dir, file_name)
        
        # If it's NOT in the specialized list, we apply the FULL generic template
        if file_name not in specialized:
            # Extract current title
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            title_match = re.search(r'<h3 id="department-title"[^>]*>(.*?)</h3>', content, re.IGNORECASE)
            title = title_match.group(1) if title_match else "Department Feedback"
            
            # Replace title in generic template
            new_content = re.sub(r'(<h3 id="department-title"[^>]*>)(.*?</h3>)', rf'\1{title}</h3>', generic_template, 1, re.IGNORECASE)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            restored_count += 1
            
    print(f"✅ Successfully upgraded {restored_count} departments to the new Premium Style.")
    print(f"ℹ️ Preserved Specialized Questions for: {', '.join(specialized)}")

if __name__ == "__main__":
    upgrade_all_depts()
