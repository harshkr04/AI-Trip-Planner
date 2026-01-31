# Script to append CSS redesign to App.css
import os

# Read the redesign CSS
with open(r'c:\Users\Harsh\Desktop\travel\AI4\itinerary_redesign.css', 'r', encoding='utf-8') as f:
    redesign_css = f.read()

# Read the current App.css
with open(r'c:\Users\Harsh\Desktop\travel\AI4\frontend\src\App.css', 'r', encoding='utf-8') as f:
    app_css = f.read()

# Append the redesign CSS
updated_css = app_css + '\n\n' + redesign_css

# Write back
with open(r'c:\Users\Harsh\Desktop\travel\AI4\frontend\src\App.css', 'w', encoding='utf-8') as f:
    f.write(updated_css)

print("✅ Successfully appended CSS redesign to App.css!")
print(f"   Total lines: {len(updated_css.splitlines())}")
