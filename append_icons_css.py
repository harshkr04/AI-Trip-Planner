# Script to append Icons & Typography CSS to App.css
import os

# Read the CSS
with open(r'c:\Users\Harsh\Desktop\travel\AI4\icons_typography.css', 'r', encoding='utf-8') as f:
    new_css = f.read()

# Read the current App.css
with open(r'c:\Users\Harsh\Desktop\travel\AI4\frontend\src\App.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

# Append the new CSS
updated_css = app_css + '\n\n' + new_css

# Write back
with open(r'c:\Users\Harsh\Desktop\travel\AI4\frontend\src\App.css', 'w', encoding='utf-8') as f:
    f.write(updated_css)

print("✅ Successfully appended Icons & Typography CSS to App.css!")
print(f"   Total lines: {len(updated_css.splitlines())}")
