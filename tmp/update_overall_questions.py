import os
import re

directory = r'c:\Caleb.Homepage\seku-feedback-mng-sytem\frontend\public\departments'

def title_case(s):
    # Basic title case, handling some acronyms if needed
    return ' '.join(word.capitalize() for word in s.split())

for filename in os.listdir(directory):
    if filename.endswith('.html'):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # 1. Try to find the department name from the title
        # <h3 id="department-title" class="...">ADMISSIONS OFFICE FEEDBACK</h3>
        # or <h3 ...>ADMISSIONS OFFICE FEEDBACK</h3>
        dept_match = re.search(r'<h3[^>]*id=["\']department-title["\'][^>]*>(.*?)</h3>', content, re.IGNORECASE | re.DOTALL)
        if not dept_match:
            dept_match = re.search(r'<h3[^>]*>(.*?)</h3>', content, re.IGNORECASE | re.DOTALL)
        
        if dept_match:
            dept_name_raw = dept_match.group(1).strip()
            # Remove "FEEDBACK" from the end if present
            dept_name = re.sub(r'\s*FEEDBACK\s*$', '', dept_name_raw, flags=re.IGNORECASE).strip()
            # Title case it
            dept_name = title_case(dept_name.lower())
            
            # Special case for "Ict" -> "ICT"
            dept_name = dept_name.replace("Ict", "ICT")
            dept_name = dept_name.replace("Dvc", "DVC")
            dept_name = dept_name.replace("Vc ", "VC ")
            
            # 2. Find the "Overall" question
            # It usually looks like:
            # <p ...>NUMBER. Overall, how would you rate your experience with ... आज? *</p>
            # Or similar.
            
            new_question = f"Overall, how would you rate your experience with {dept_name} Feedback today? *"
            
            # Pattern to match the "Overall" question paragraph content
            # We look for "Overall, how would you rate your experience"
            # and potentially a leading number like "9. " or "5. "
            
            # Match the entire <p> tag content that contains the overall rating question
            pattern = r'(<p[^>]*class=["\'][^"\']*font-semibold[^"\']*["\'][^>]*>)\s*(\d+\.)?\s*Overall, how would you rate.*?\?\s*\*?\s*(</p>)'
            
            new_content = re.sub(pattern, rf'\1 \2 {new_question} \3', content, flags=re.IGNORECASE | re.DOTALL)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filename} with department name: {dept_name}")
            else:
                # Try a broader pattern if the first one failed
                pattern2 = r'(Overall, how would you rate your experience with).*?(\? \*?|今天\?)'
                new_content2 = re.sub(pattern2, rf'Overall, how would you rate your experience with {dept_name} Feedback today? *', content, flags=re.IGNORECASE)
                
                if new_content2 != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content2)
                    print(f"Updated {filename} (broad pattern) with department name: {dept_name}")
                else:
                    print(f"Could not find overall question in {filename}")
        else:
            print(f"Could not find department title in {filename}")
