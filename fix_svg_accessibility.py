#!/usr/bin/env python3
"""
Fix SVG accessibility by adding aria-hidden="true" to all SVG elements
that don't already have accessibility attributes.
"""

import re
import sys

def fix_svg_accessibility(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to match SVG tags without aria-hidden or aria-label
    # Match: <svg className="..." fill="none" viewBox="0 0 24 24" stroke="currentColor">
    # That don't already have aria-hidden or aria-label

    def replace_svg(match):
        svg_tag = match.group(0)
        # Check if already has aria-hidden or aria-label
        if 'aria-hidden' in svg_tag or 'aria-label' in svg_tag:
            return svg_tag
        # Add aria-hidden="true" before the closing >
        return svg_tag.replace('stroke="currentColor">', 'stroke="currentColor" aria-hidden="true">')

    # Find all SVG opening tags
    pattern = r'<svg[^>]*className="[^"]*"[^>]*fill="none"[^>]*viewBox="0 0 24 24"[^>]*stroke="currentColor"[^>]*>'

    original_content = content
    content = re.sub(pattern, replace_svg, content)

    # Write back
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Count changes
    changes = content.count('aria-hidden="true"') - original_content.count('aria-hidden="true"')
    print(f"✅ Fixed {changes} SVG icons in {file_path}")
    return changes

if __name__ == '__main__':
    file_path = '/home/jarek/projects/MARKET_INTELLIGENCE/MI-NAVIGATOR/frontend/src/app/reports/page.tsx'
    changes = fix_svg_accessibility(file_path)
    print(f"Total changes: {changes}")
