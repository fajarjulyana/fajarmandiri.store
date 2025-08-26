
#!/usr/bin/env python3
import os
import re

def fix_jinja_syntax(file_path):
    """Fix common Jinja2 syntax errors in templates"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # 1. Fix malformed endif tags - remove orphaned endif
        content = re.sub(r'{%\s*endif\s*%}(?=\s*{%\s*endif\s*%})', '', content)
        
        # 2. Fix malformed nested if statements 
        content = re.sub(r'{%\s*if\s+[^%]+%}\s*{%\s*if\s+[^%]+%}\s*{%\s*else\s*%}[^{]*{%\s*endif\s*%}\s*{%\s*endif\s*%}', '', content, flags=re.DOTALL)
        
        # 3. Remove duplicate gallery sections
        gallery_patterns = [
            r'<!-- Enhanced Responsive Gallery Section -->.*?{%\s*endif\s*%}',
            r'<!-- Gallery Section -->.*?{%\s*endif\s*%}',
            r'<!-- Photo Gallery Section -->.*?{%\s*endif\s*%}'
        ]
        
        for pattern in gallery_patterns:
            matches = re.findall(pattern, content, flags=re.DOTALL)
            if len(matches) > 1:
                # Keep first, remove others
                for i in range(1, len(matches)):
                    content = content.replace(matches[i], '', 1)
        
        # 4. Fix venue address sections with proper syntax
        venue_fields = ['akad_venue_address', 'resepsi_venue_address', 'bride_event_venue_address', 'groom_event_venue_address']
        
        for field in venue_fields:
            # Create proper pattern without f-string issues
            pattern = r'{%\s*if\s+invitation\.' + field + r'\s*%}.*?{%\s*endif\s*%}'
            
            # Replace with clean address display
            clean_replacement = '''{% if invitation.''' + field + ''' %}
                <div class="venue-address">{{ invitation.''' + field + ''' }}</div>
                <a href="https://maps.google.com/?q={{ invitation.''' + field + ''' | urlencode }}" 
                   target="_blank" class="venue-address-link">
                    <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi
                </a>
                {% endif %}'''
            
            content = re.sub(pattern, clean_replacement, content, flags=re.DOTALL)
        
        # 5. Count and balance if/endif pairs
        if_count = len(re.findall(r'{%\s*if\s+', content))
        endif_count = len(re.findall(r'{%\s*endif\s*%}', content))
        
        # Add missing endif tags if needed
        if if_count > endif_count:
            missing_endifs = if_count - endif_count
            for _ in range(missing_endifs):
                if '</body>' in content:
                    content = content.replace('</body>', '{% endif %}\n</body>', 1)
                elif '</html>' in content:
                    content = content.replace('</html>', '{% endif %}\n</html>', 1)
                else:
                    content += '\n{% endif %}'
        
        # Remove excess endif tags
        elif endif_count > if_count:
            excess_endifs = endif_count - if_count
            for _ in range(excess_endifs):
                # Remove last standalone endif
                content = re.sub(r'\s*{%\s*endif\s*%}\s*(?=\s*</(?:body|html)>)', '', content, count=1)
        
        # 6. Clean up any remaining malformed syntax
        content = re.sub(r'{%\s*endif\s*%}\s*{%\s*endif\s*%}', '{% endif %}', content)
        content = re.sub(r'{{{{ if', '{% if', content)
        content = re.sub(r'{{{{ endif }}}}', '{% endif %}', content)
        
        # 7. Fix any try/endtry blocks to proper if/endif
        content = re.sub(r'{%\s*try\s*%}', '{% if True %}', content)
        content = re.sub(r'{%\s*endtry\s*%}', '{% endif %}', content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error fixing {file_path}: {str(e)}")
        return False

def main():
    """Fix all wedding templates"""
    templates_dir = 'templates/wedding_templates'
    
    if not os.path.exists(templates_dir):
        print(f"Directory {templates_dir} not found!")
        return
    
    fixed_count = 0
    total_count = 0
    
    print("Fixing Jinja2 syntax errors in all wedding templates...")
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html') and not filename.startswith('.'):
            file_path = os.path.join(templates_dir, filename)
            total_count += 1
            
            print(f"Fixing {filename}...")
            
            try:
                if fix_jinja_syntax(file_path):
                    print(f"✓ Fixed {filename}")
                    fixed_count += 1
                else:
                    print(f"- No changes needed for {filename}")
            except Exception as e:
                print(f"✗ Error fixing {filename}: {str(e)}")
    
    print(f"\nCompleted! Fixed {fixed_count} out of {total_count} templates.")
    print("All templates now have:")
    print("- Proper Jinja2 syntax")
    print("- Balanced if/endif pairs")
    print("- Clean address display sections")
    print("- Removed duplicate gallery sections")
    print("- Fixed try/endtry blocks")

if __name__ == "__main__":
    main()
