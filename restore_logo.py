import base64
import os

b64_path = r'c:\Users\User\Downloads\seku-feedback-mng-sytem\tmp_logo_b64.txt'
logo_path = r'c:\Users\User\Downloads\seku-feedback-mng-sytem\frontend\public\uploads\logo.png'

with open(b64_path, 'r') as f:
    b64_content = f.read().strip()

# Some b64 files start with data:image/png;base64,
if ',' in b64_content:
    b64_content = b64_content.split(',')[1]

img_data = base64.b64decode(b64_content)

with open(logo_path, 'wb') as f:
    f.write(img_data)

print(f"Restored logo to {logo_path}")
