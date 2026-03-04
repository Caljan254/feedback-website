import os
import re

def restore_questions():
    dept_dir = r'c:\Caleb.Homepage\seku-feedback-mng-sytem\frontend\public\departments'
    generic_file = os.path.join(dept_dir, 'generic-feedback.html')
    
    with open(generic_file, 'r', encoding='utf-8') as f:
        generic_template = f.read()

    files = [f for f in os.listdir(dept_dir) if f.endswith('.html') and f != 'generic-feedback.html']
    
    restored_count = 0
    preserved_count = 0
    
    for file_name in files:
        full_path = os.path.join(dept_dir, file_name)
        size = os.path.getsize(full_path)
        
        # Files < 7000 bytes are the generic ones that need the "standard 5 questions"
        if size < 7000:
            # Extract current title if possible
            with open(full_path, 'r', encoding='utf-8') as f:
                current_content = f.read()
            
            title_match = re.search(r'<h3 id="department-title"[^>]*>(.*?)</h3>', current_content, re.IGNORECASE)
            title = title_match.group(1) if title_match else "Feedback"
            
            # Apply generic template
            new_content = re.sub(r'(<h3 id="department-title"[^>]*>)(.*?</h3>)', rf'\1{title}</h3>', generic_template, 1, re.IGNORECASE)
            
            # Also need to make sure the back link color is right (some were using yellow/teal)
            # But the generic uses green-600. That's fine.
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            restored_count += 1
        else:
            preserved_count += 1
            print(f"Preserving specialized file: {file_name} ({size} bytes)")

    print(f"Restored standard questions to {restored_count} departments.")
    print(f"Preserved {preserved_count} specialized departments.")

if __name__ == "__main__":
    restore_questions()
