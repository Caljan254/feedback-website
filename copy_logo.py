import shutil
import os

src = r'frontend\public\uploads\ict-logo.png'
dst = r'frontend\public\uploads\logo.png'

if os.path.exists(src):
    shutil.copy2(src, dst)
    print(f"Copied {src} to {dst}")
else:
    print(f"File {src} not found")
