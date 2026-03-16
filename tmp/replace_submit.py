import os, glob

for path in glob.glob(r'c:\Users\User\Downloads\seku-feedback-mng-sytem\frontend\public\departments\*.html') + glob.glob(r'c:\Users\User\Downloads\seku-feedback-mng-sytem\frontend\src\**\*.html', recursive=True):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'Submit Feedback' in content:
            content = content.replace('Submit Feedback', 'ICT Feedback')
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("updated", path)
    except Exception as e:
        print(e)
print('Done')
