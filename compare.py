import filecmp
logo = r'frontend\public\uploads\logo.png'
favicon = r'frontend\public\uploads\favicon.ico'
same = filecmp.cmp(logo, favicon)
print(f"Same? {same}")
