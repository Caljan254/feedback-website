
import os
import re

template_path = r'c:\Caleb.Homepage\seku-feedback-mng-sytem\frontend\public\departments\generic-feedback.html'
departments_dir = r'c:\Caleb.Homepage\seku-feedback-mng-sytem\frontend\public\departments'

with open(template_path, 'r', encoding='utf-8') as f:
    template_content = f.read()

# Files to skip
skip_files = ['ict-feedback.html', 'admissions-feedback.html', 'finance-feedback.html', 'generic-feedback.html']

def clean_title(title):
    title = re.sub(r'<[^>]+>', '', title).strip()
    title = title.replace('Feedback System', '').strip()
    # If the title is too generic, return None to trigger filename-based title
    if title.lower() in ['', 'feedback form', 'feedback']:
        return None
    return title

for filename in os.listdir(departments_dir):
    if filename.endswith('.html') and filename not in skip_files:
        filepath = os.path.join(departments_dir, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Try splitting by filename first for better accuracy
            filename_title = filename.replace('-feedback.html', '').replace('-', ' ').title()
            # Special case for "Ict" -> "ICT"
            filename_title = filename_title.replace('Ict', 'ICT').replace('Dvc', 'DVC').replace('Vc ', 'VC ').replace('Hr ', 'HR ')
            
            title = filename_title + " Feedback"

            # Create new content from template
            new_content = re.sub(
                r'(<h3[^>]*id="department-title"[^>]*>).*?(</h3>)',
                f'\\1{title}\\2',
                template_content,
                flags=re.DOTALL
            )
            
            # Update meta title too
            new_content = re.sub(
                r'<title>.*?</title>',
                f'<title>{title} - SEKU Feedback</title>',
                new_content
            )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Updated {filename} with title: {title}")
        except Exception as e:
            print(f"Error updating {filename}: {e}")

print("Batch update complete.")
