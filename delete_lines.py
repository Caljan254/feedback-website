import os

home_path = r'c:\Users\User\Downloads\seku-feedback-mng-sytem\frontend\src\components\pages\home.html'

with open(home_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# The index is 0-based, so line 280 is index 279, and line 378 is index 377.
# We want to remove lines 280 to 378 inclusive.
new_lines = lines[:279] + lines[378:]

with open(home_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
