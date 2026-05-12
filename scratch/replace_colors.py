import os
import re

directory = r"c:\Users\benza\EPR MEDECIN\src"

def replace_colors_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace specific dark hex colors with #0050b3 (Dark Blue)
    new_content = re.sub(r'#(141414|434343|000000|333333|222222|111111|000|111|222|333)\b', '#0050b3', content, flags=re.IGNORECASE)
    
    # Replace "black" with "#0050b3" if it's in a CSS rule (very naive approach, but safe enough if we only match color: black)
    new_content = re.sub(r':\s*black\b', ': #0050b3', new_content, flags=re.IGNORECASE)

    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated colors in {filepath}")

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith(('.py', '.qss')):
            replace_colors_in_file(os.path.join(root, file))

print("Done replacing dark colors with vivid dark blue (#0050b3).")
