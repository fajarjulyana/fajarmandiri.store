
#!/usr/bin/env python3
"""
Script to fix all wedding templates:
1. Fix photo gallery display
2. Add universal animations
3. Add autoplay music
4. Add universal script reference
"""

import os
import re

def fix_template_file(file_path):
    """Fix individual template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"Processing {file_path}...")
        
        # Fix photo gallery display - Replace complex prewedding_photos handling
        gallery_pattern = r'{% if invitation\.prewedding_photos %}.*?{% for photo_json in invitation\.prewedding_photos\.split.*?{% set photo = photo_json \| from_json %}.*?photo\.filename.*?{% endfor %}.*?{% endif %}'
        
        gallery_replacement = '''{% if prewedding_photos %}
        <section class="gallery-section fade-in">
            <h2 class="section-title animate-slideInUp">Galeri Foto</h2>
            <div class="gallery-grid">
                {% for photo in prewedding_photos %}
                    <div class="gallery-item animate-zoomIn" onclick="openLightbox('{{ url_for('static', filename='prewedding_photos/' + photo) }}')">
                        <img src="{{ url_for('static', filename='prewedding_photos/' + photo) }}" alt="Prewedding Photo" loading="lazy">
                        <div class="gallery-overlay">
                            <i class="fas fa-expand"></i>
                        </div>
                    </div>
                {% endfor %}
            </div>
        </section>
        {% endif %}'''
        
        content = re.sub(gallery_pattern, gallery_replacement, content, flags=re.DOTALL)
        
        # Add universal script before closing body tag if not exists
        if 'wedding-animations.js' not in content:
            script_tag = '''    
    <!-- Universal Wedding Features Script -->
    <script src="{{ url_for('static', filename='js/wedding-animations.js') }}"></script>
</body>'''
            content = content.replace('</body>', script_tag)
        
        # Ensure background music has default fallback
        music_pattern = r'(<!-- Background Music -->.*?{% if invitation\.background_music %}.*?</audio>.*?{% endif %})'
        
        music_replacement = '''<!-- Background Music -->
    {% if invitation.background_music %}
    <audio id="backgroundMusic" loop>
        <source src="{{ url_for('static', filename='music/' + invitation.background_music) }}" type="audio/mpeg">
    </audio>
    {% else %}
    <audio id="backgroundMusic" loop>
        <source src="{{ url_for('static', filename='music/default_wedding.mp3') }}" type="audio/mpeg">
    </audio>
    {% endif %}
    
    <button id="musicToggle" class="music-toggle animate-bounce">
        <i class="fas fa-music"></i>
    </button>'''
        
        content = re.sub(music_pattern, music_replacement, content, flags=re.DOTALL)
        
        # Add animation classes to sections if not exists
        content = content.replace('<section class="hero-section"', '<section class="hero-section fade-in"')
        content = content.replace('<section class="story-section"', '<section class="story-section fade-in"')
        content = content.replace('<section class="event-section"', '<section class="event-section fade-in"')
        content = content.replace('<section class="rsvp-section"', '<section class="rsvp-section fade-in"')
        content = content.replace('<section class="gift-section"', '<section class="gift-section fade-in"')
        
        # Write back the fixed content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"✓ Fixed {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing {file_path}: {str(e)}")
        return False

def main():
    """Main function to fix all templates"""
    template_dir = 'templates/wedding_templates'
    
    if not os.path.exists(template_dir):
        print(f"Template directory not found: {template_dir}")
        return
    
    # Get all HTML template files
    template_files = [f for f in os.listdir(template_dir) if f.endswith('.html')]
    
    if not template_files:
        print("No template files found!")
        return
    
    print(f"Found {len(template_files)} template files to fix...")
    
    success_count = 0
    
    for template_file in template_files:
        file_path = os.path.join(template_dir, template_file)
        if fix_template_file(file_path):
            success_count += 1
    
    print(f"\n🎉 Successfully fixed {success_count}/{len(template_files)} template files!")
    
    # Also fix the main wedding invitation view template
    main_template = 'templates/wedding_invitation_view.html'
    if os.path.exists(main_template):
        if fix_template_file(main_template):
            print(f"✓ Also fixed main template: {main_template}")

if __name__ == "__main__":
    main()
