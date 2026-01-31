# Script to fix ItinerarySection.jsx - remove summary cards and useMemo import
import re

# Read the file
with open(r'c:\Users\Harsh\Desktop\travel\AI4\frontend\src\components\ItinerarySection.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Remove useMemo from imports
content = content.replace(
    'import React, { useState, useMemo } from "react";',
    'import React, { useState } from "react";'
)

# Fix 2: Remove the summaryCards useMemo definition
pattern = r'  const summaryCards = useMemo\(\(\) => \{[^}]+\}, \[itinerary, days\.length\]\);'
content = re.sub(pattern, '', content, flags=re.DOTALL)

# Fix 3: Remove the header summary cards section
old_header = '''        <div className="itinerary-header-row">
          <div className="header-summary-cards">
            {summaryCards.map((card) => (
              <div key={card.label} className="header-card">
                <span className="header-icon">{card.icon}</span>
                <div>
                  <span className="header-label">{card.label}</span>
                  <strong className="header-value">{card.value}</strong>
                </div>
              </div>
            ))}
          </div>
          <div className="header-actions">
            <button className="btn-action-subtle" onClick={handleShareLink}>🔗 Share</button>
            <button className="btn-action-subtle" onClick={onDownloadPdf}>📥 PDF</button>
          </div>
        </div>'''

new_header = '''        {/* Header Actions */}
        <div className="itinerary-header-row">
          <div className="header-actions">
            <button className="btn-action-subtle" onClick={handleShareLink}>🔗 Share</button>
            <button className="btn-action-subtle" onClick={onDownloadPdf}>📥 PDF</button>
          </div>
        </div>'''

content = content.replace(old_header, new_header)

# Write back
with open(r'c:\Users\Harsh\Desktop\travel\AI4\frontend\src\components\ItinerarySection.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Successfully fixed ItinerarySection.jsx!")
print("  - Removed useMemo import")
print("  - Removed summaryCards definition")
print("  - Removed header summary cards UI")
