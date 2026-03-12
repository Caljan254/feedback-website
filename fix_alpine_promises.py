import os
import re

def fix_html_files():
    directory = r'c:\Caleb.Homepage\seku-feedback-mng-sytem\frontend\public\departments'
    pattern = r'x-effect="\$el\.value\s*=\s*\$nextTick\(\(\)\s*=>\s*document\.querySelector\(\'input\[name=q_4\]:checked\'\)\?\.value\)"'
    replacement = r'x-effect="$nextTick(() => { $el.value = document.querySelector(\'input[name=q_4]:checked\')?.value || \'\' })"'
    
    # Also handle alternate patterns just in case
   
    
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith('.html'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = re.sub(pattern, replacement, content)
            
            # Simple fallback for other naming conventions like q_5 if they exist
            # But the batch script used q_4 for rating
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Fixed: {filename}")
                count += 1
    
    print(f"Total files fixed: {count}")

if __name__ == "__main__":
    fix_html_files()
