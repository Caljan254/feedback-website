import filecmp
import os

dist_logo = r'frontend\dist\uploads\logo.png'
public_favicon = r'frontend\public\uploads\favicon.ico'

if os.path.exists(dist_logo):
    same = filecmp.cmp(dist_logo, public_favicon)
    print(f"Dist logo same as favicon? {same}")
    print(f"Dist logo size: {os.path.getsize(dist_logo)}")
else:
    print("Dist logo missing")
