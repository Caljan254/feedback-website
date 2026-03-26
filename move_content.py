import os

home_path = r'c:\Users\User\Downloads\seku-feedback-mng-sytem\frontend\src\components\pages\home.html'
submit_path = r'c:\Users\User\Downloads\seku-feedback-mng-sytem\frontend\src\components\pages\submit-feedback.html'

with open(home_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
end_idx = -1

for i, line in enumerate(lines):
    if '<!-- NEW: How It Works Section -->' in line:
        start_idx = i
    if 'Frequently Asked Questions' in line and start_idx != -1:
        # We need to find the closing </section> for FAQ
        # It's followed directly by </main>
        pass
    if '</main>' in line and start_idx != -1:
        end_idx = i
        break

if start_idx != -1 and end_idx != -1:
    extracted_lines = lines[start_idx:end_idx]
    
    # Remove from home
    new_home_lines = lines[:start_idx] + lines[end_idx:]
    with open(home_path, 'w', encoding='utf-8') as f:
        f.writelines(new_home_lines)
    print('Extracted from home.html')
    
    # Insert to submit
    with open(submit_path, 'r', encoding='utf-8') as f:
        submit_lines = f.readlines()
        
    insert_idx = -1
    for i in range(len(submit_lines)-1, -1, -1):
        if '<!-- Footer placeholder -->' in submit_lines[i]:
            # The div above this is </div> for content wrapper
            insert_idx = i - 2
            break
            
    if insert_idx != -1:
        new_submit = submit_lines[:insert_idx] + ['\n        <!-- MOVED FROM HOME -->\n'] + extracted_lines + submit_lines[insert_idx:]
        with open(submit_path, 'w', encoding='utf-8') as f:
            f.writelines(new_submit)
        print('Moved successfully')
    else:
        print('Insert point not found')
else:
    print('Could not find indices', start_idx, end_idx)
