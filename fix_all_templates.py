
import os
import re

def fix_template_syntax(file_path):
    """Fix common Jinja2 syntax errors in wedding templates"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes_made = []
        
        # 1. Fix malformed endif tags
        if re.search(r'{% endif %}(?!\s*$)', content, re.MULTILINE):
            content = re.sub(r'{% endif %}(?!\s*$)', '{% endif %}\n', content)
            changes_made.append("Fixed endif spacing")
        
        # 2. Fix unclosed if statements
        if_count = len(re.findall(r'{% if ', content))
        endif_count = len(re.findall(r'{% endif %}', content))
        
        if if_count != endif_count:
            # Add missing endif tags at the end before </body> or </html>
            missing_endifs = if_count - endif_count
            if missing_endifs > 0:
                for _ in range(missing_endifs):
                    if '</body>' in content:
                        content = content.replace('</body>', '{% endif %}\n</body>')
                    elif '</html>' in content:
                        content = content.replace('</html>', '{% endif %}\n</html>')
                    else:
                        content += '\n{% endif %}'
                changes_made.append(f"Added {missing_endifs} missing endif tags")
        
        # 3. Fix malformed for loops
        content = re.sub(r'{% for ([^%]+) %}(?!\s*$)', r'{% for \1 %}\n', content)
        
        # 4. Fix malformed variable outputs
        content = re.sub(r'{{ ([^}]+) }}(?!\s)', r'{{ \1 }} ', content)
        
        # 5. Remove duplicate gallery sections (keep only one)
        gallery_sections = re.findall(r'<!-- .*?Gallery.*? -->.*?{% endif %}', content, re.DOTALL | re.IGNORECASE)
        if len(gallery_sections) > 1:
            # Keep the first gallery section, remove the rest
            for i in range(1, len(gallery_sections)):
                content = content.replace(gallery_sections[i], '', 1)
            changes_made.append(f"Removed {len(gallery_sections)-1} duplicate gallery sections")
        
        # 6. Fix venue address display
        venue_patterns = [
            (r'{{ invitation\.venue_address }}', '{{ invitation.venue_address or "Alamat akan diumumkan" }}'),
            (r'{{ invitation\.venue_name }}', '{{ invitation.venue_name or "Venue akan diumumkan" }}'),
        ]
        
        for pattern, replacement in venue_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes_made.append(f"Fixed venue display pattern: {pattern}")
        
        # 7. Ensure proper photo gallery structure
        if 'prewedding_photos' in content and not re.search(r'{% if prewedding_photos and prewedding_photos\|length > 0 %}', content):
            # Add proper gallery section if missing
            gallery_html = '''
<!-- Enhanced Photo Gallery Section -->
{% if prewedding_photos and prewedding_photos|length > 0 %}
<section class="gallery-section py-5" style="background: #f8f9fa;">
    <div class="container">
        <div class="text-center mb-5">
            <h2 class="section-title" style="color: var(--primary-color, #d4af37);">Galeri Foto</h2>
            <p class="text-muted">Momen-momen indah kami</p>
        </div>
        <div class="row g-3">
            {% for photo in prewedding_photos %}
            <div class="col-lg-4 col-md-6 col-sm-6">
                <div class="gallery-item">
                    <img src="{{ url_for('static', filename='prewedding_photos/' + photo) }}" 
                         alt="Prewedding Photo" 
                         class="img-fluid rounded shadow-sm gallery-image"
                         data-bs-toggle="modal" 
                         data-bs-target="#photoModal" 
                         data-photo="{{ url_for('static', filename='prewedding_photos/' + photo) }}"
                         style="cursor: pointer; transition: transform 0.3s;">
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</section>

<!-- Photo Modal -->
<div class="modal fade" id="photoModal" tabindex="-1">
    <div class="modal-dialog modal-lg modal-dialog-centered">
        <div class="modal-content">
            <div class="modal-body p-0">
                <button type="button" class="btn-close position-absolute top-0 end-0 m-3 z-index-1" 
                        data-bs-dismiss="modal" style="background: white; border-radius: 50%;"></button>
                <img id="modalPhoto" src="" alt="Prewedding Photo" class="w-100 rounded">
            </div>
        </div>
    </div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Gallery modal functionality
    const galleryImages = document.querySelectorAll('.gallery-image');
    const modalPhoto = document.getElementById('modalPhoto');
    
    galleryImages.forEach(img => {
        img.addEventListener('click', function() {
            const photoSrc = this.getAttribute('data-photo');
            modalPhoto.src = photoSrc;
        });
        
        // Hover effect
        img.addEventListener('mouseenter', function() {
            this.style.transform = 'scale(1.05)';
        });
        
        img.addEventListener('mouseleave', function() {
            this.style.transform = 'scale(1)';
        });
    });
});
</script>
{% endif %}
'''
            if '</section>' in content and 'gallery-section' not in content:
                # Insert before the last section
                last_section_pos = content.rfind('</section>')
                if last_section_pos > 0:
                    content = content[:last_section_pos] + gallery_html + content[last_section_pos:]
                    changes_made.append("Added proper gallery section")
        
        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ Fixed {os.path.basename(file_path)}: {', '.join(changes_made)}")
            return True
        else:
            print(f"- No changes needed for {os.path.basename(file_path)}")
            return False
            
    except Exception as e:
        print(f"✗ Error fixing {os.path.basename(file_path)}: {str(e)}")
        return False

def main():
    template_dir = 'templates/wedding_templates'
    
    if not os.path.exists(template_dir):
        print(f"Directory {template_dir} not found!")
        return
    
    print("Fixing all wedding templates...")
    
    fixed_count = 0
    total_count = 0
    
    for filename in os.listdir(template_dir):
        if filename.endswith('.html'):
            file_path = os.path.join(template_dir, filename)
            total_count += 1
            
            if fix_template_syntax(file_path):
                fixed_count += 1
    
    print(f"\nCompleted! Fixed {fixed_count} out of {total_count} templates.")

if __name__ == "__main__":
    main()
