
#!/usr/bin/env python3
import os
import re

def clean_template_file(file_path):
    """Clean and fix a wedding template file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # 1. Remove duplicate gallery sections
    # Remove any existing gallery sections to start clean
    gallery_patterns = [
        r'<!-- Enhanced Responsive Gallery Section -->.*?{% endif %}',
        r'<!-- Enhanced Gallery Section.*?{% endif %}',
        r'<!-- Gallery Section -->.*?{% endif %}',
        r'<!-- Photo Gallery Section -->.*?{% endif %}',
        r'<section[^>]*gallery-section[^>]*>.*?</section>.*?{% endif %}',
        r'{% if prewedding_photos.*?{% endif %}(?=\s*{% if prewedding_photos)',  # Remove duplicate if blocks
    ]
    
    for pattern in gallery_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # 2. Remove duplicate modal sections
    modal_patterns = [
        r'<!-- Photo Modal -->.*?</div>\s*</div>(?=.*<!-- Photo Modal -->)',
        r'<div class="modal" id="photoModal"[^>]*>.*?</div>\s*</div>(?=.*<div class="modal" id="photoModal")',
    ]
    
    for pattern in modal_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
    
    # 3. Fix venue address display patterns
    venue_address_patterns = [
        r'{% if invitation\.venue_address %}\s*{% if invitation\.venue_address\.startswith\(\'http\'\) %}.*?{% endif %}\s*{% endif %}',
        r'{% if invitation\.venue_address %}\s*{% if invitation\.venue_address\.startswith\(\'http\'\) %}.*?{% else %}.*?{% endif %}\s*{% endif %}',
    ]
    
    venue_address_replacement = '''{% if invitation.venue_address %}
                                <div class="venue-address">
                                    <a href="https://maps.google.com/?q={{ invitation.venue_address | urlencode }}" 
                                       target="_blank" class="venue-address-link">
                                        <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.venue_address }}
                                    </a>
                                </div>
                            {% endif %}'''
    
    for pattern in venue_address_patterns:
        content = re.sub(pattern, venue_address_replacement, content, flags=re.DOTALL | re.IGNORECASE)
    
    # 4. Add clean gallery section before RSVP if not exists
    if 'prewedding_photos' not in content:
        gallery_section = '''
    <!-- Photo Gallery Section -->
    {% if prewedding_photos and prewedding_photos|length > 0 %}
    <section class="gallery-section fade-in">
        <div class="container">
            <div class="section-header text-center">
                <h2 class="section-title">Galeri Foto</h2>
                <p class="section-subtitle">Momen indah menuju hari bahagia</p>
            </div>
            
            <div class="gallery-grid">
                {% for photo in prewedding_photos %}
                <div class="gallery-item" onclick="openModal('{{ url_for('static', filename='prewedding_photos/' + photo) }}')">
                    <img src="{{ url_for('static', filename='prewedding_photos/' + photo) }}" 
                         alt="Galeri Foto {{ loop.index }}" 
                         loading="lazy">
                    <div class="gallery-overlay">
                        <i class="fas fa-search-plus"></i>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>
    
    <!-- Photo Modal -->
    <div class="modal" id="photoModal" style="display: none;">
        <span class="close-button" onclick="closeModal()">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="Gallery Photo">
        </div>
    </div>
    {% endif %}
'''
        
        # Find insertion point before RSVP
        rsvp_pattern = r'<!-- RSVP|<section[^>]*rsvp|<!-- Footer|<footer'
        match = re.search(rsvp_pattern, content, re.IGNORECASE)
        if match:
            insertion_point = match.start()
            content = content[:insertion_point] + gallery_section + '\n\n' + content[insertion_point:]
    
    # 5. Ensure modal JavaScript exists
    if 'function openModal' not in content:
        js_script = '''
<script>
function openModal(imageSrc) {
    document.getElementById('photoModal').style.display = 'flex';
    document.getElementById('modalImage').src = imageSrc;
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('photoModal').style.display = 'none';
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside image
document.getElementById('photoModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});
</script>'''
        
        # Add before closing body tag
        body_pattern = r'</body>'
        if re.search(body_pattern, content):
            content = re.sub(body_pattern, js_script + '\n</body>', content)
    
    # 6. Ensure gallery CSS exists
    if '.gallery-grid' not in content:
        css_styles = '''
<style>
/* Gallery Styles */
.gallery-section {
    padding: 60px 0;
    background: #f8f9fa;
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 40px;
}

.gallery-item {
    position: relative;
    aspect-ratio: 1;
    overflow: hidden;
    border-radius: 15px;
    cursor: pointer;
    transition: transform 0.3s ease;
}

.gallery-item:hover {
    transform: scale(1.05);
}

.gallery-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.gallery-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
    color: white;
    font-size: 24px;
}

.gallery-item:hover .gallery-overlay {
    opacity: 1;
}

/* Modal Styles */
.modal {
    position: fixed;
    z-index: 9999;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.9);
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-content {
    max-width: 90%;
    max-height: 90%;
}

.modal-content img {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
}

.close-button {
    position: absolute;
    top: 20px;
    right: 40px;
    color: white;
    font-size: 40px;
    font-weight: bold;
    cursor: pointer;
    z-index: 10000;
}

@media (max-width: 768px) {
    .gallery-grid {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        gap: 15px;
    }
    
    .close-button {
        right: 20px;
        font-size: 30px;
    }
}
</style>'''
        
        # Add to head section
        head_pattern = r'</head>'
        if re.search(head_pattern, content):
            content = re.sub(head_pattern, css_styles + '\n</head>', content)
    
    # Check if content changed
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Fix all wedding templates"""
    templates_dir = 'templates/wedding_templates'
    
    if not os.path.exists(templates_dir):
        print(f"Directory {templates_dir} not found!")
        return
    
    fixed_count = 0
    total_count = 0
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html') and not filename.startswith('.'):
            file_path = os.path.join(templates_dir, filename)
            total_count += 1
            
            print(f"Fixing {filename}...")
            
            try:
                if clean_template_file(file_path):
                    print(f"✓ Fixed {filename}")
                    fixed_count += 1
                else:
                    print(f"- No changes needed for {filename}")
            except Exception as e:
                print(f"✗ Error fixing {filename}: {str(e)}")
    
    print(f"\nCompleted! Fixed {fixed_count} out of {total_count} templates.")
    print("All templates now have:")
    print("- Clean gallery sections without duplicates")
    print("- Working photo modal")
    print("- Proper venue address display")
    print("- Responsive design")

if __name__ == "__main__":
    main()
