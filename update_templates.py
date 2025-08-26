
#!/usr/bin/env python3
import os
import re

def update_template_file(file_path):
    """Update a single template file with gallery and location buttons"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Skip if already has gallery section
    if 'prewedding_photos' in content and 'gallery-section' in content:
        print(f"Template {file_path} already has gallery - skipping")
        return False
    
    # Gallery section HTML
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
    {% endif %}'''
    
    # Event section with location buttons
    event_section = '''
    <!-- Wedding Events Section -->
    <section class="wedding-events-section fade-in">
        <div class="container">
            <div class="section-header text-center">
                <h2 class="section-title">Acara Pernikahan</h2>
                <p class="section-subtitle">Bergabunglah dengan kami merayakan hari bahagia</p>
            </div>
            
            <div class="row justify-content-center">
                <!-- Akad Nikah -->
                {% if invitation.akad_venue_address or invitation.akad_venue_name or invitation.akad_date %}
                <div class="col-md-6 col-lg-5 mb-4">
                    <div class="event-detail">
                        <div class="event-icon">
                            <i class="fas fa-mosque"></i>
                        </div>
                        <h3 class="event-title">Akad Nikah</h3>
                        {% if invitation.akad_date %}
                        <p class="event-date">
                            <i class="far fa-calendar-alt me-2"></i>
                            {{ invitation.akad_date.strftime('%A, %d %B %Y') if invitation.akad_date.__class__.__name__ == 'datetime' else invitation.akad_date }}
                        </p>
                        {% endif %}
                        {% if invitation.akad_time %}
                        <p class="event-time">
                            <i class="far fa-clock me-2"></i>
                            {{ invitation.akad_time }} WIB
                        </p>
                        {% endif %}
                        <p class="event-venue">{{ invitation.akad_venue_name or 'Tempat Akad' }}</p>
                        {% if invitation.akad_venue_address %}
                        <p class="event-address">{{ invitation.akad_venue_address }}</p>
                        <a href="https://maps.google.com/?q={{ invitation.akad_venue_address | urlencode }}" 
                           target="_blank" class="location-btn">
                            <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi
                        </a>
                        {% endif %}
                    </div>
                </div>
                {% endif %}
                
                <!-- Resepsi -->
                {% if invitation.resepsi_venue_address or invitation.resepsi_venue_name or invitation.resepsi_date %}
                <div class="col-md-6 col-lg-5 mb-4">
                    <div class="event-detail">
                        <div class="event-icon">
                            <i class="fas fa-glass-cheers"></i>
                        </div>
                        <h3 class="event-title">Resepsi</h3>
                        {% if invitation.resepsi_date %}
                        <p class="event-date">
                            <i class="far fa-calendar-alt me-2"></i>
                            {{ invitation.resepsi_date.strftime('%A, %d %B %Y') if invitation.resepsi_date.__class__.__name__ == 'datetime' else invitation.resepsi_date }}
                        </p>
                        {% endif %}
                        {% if invitation.resepsi_time %}
                        <p class="event-time">
                            <i class="far fa-clock me-2"></i>
                            {{ invitation.resepsi_time }} WIB
                        </p>
                        {% endif %}
                        <p class="event-venue">{{ invitation.resepsi_venue_name or 'Tempat Resepsi' }}</p>
                        {% if invitation.resepsi_venue_address %}
                        <p class="event-address">{{ invitation.resepsi_venue_address }}</p>
                        <a href="https://maps.google.com/?q={{ invitation.resepsi_venue_address | urlencode }}" 
                           target="_blank" class="location-btn">
                            <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi
                        </a>
                        {% endif %}
                    </div>
                </div>
                {% endif %}
                
                <!-- Single Event Fallback -->
                {% if not (invitation.akad_venue_address or invitation.resepsi_venue_address) and invitation.venue_address %}
                <div class="col-md-8 col-lg-6">
                    <div class="event-detail">
                        <div class="event-icon">
                            <i class="fas fa-heart"></i>
                        </div>
                        <h3 class="event-title">Pernikahan</h3>
                        {% if invitation.wedding_date %}
                        <p class="event-date">
                            <i class="far fa-calendar-alt me-2"></i>
                            {{ invitation.wedding_date.strftime('%A, %d %B %Y') if invitation.wedding_date.__class__.__name__ == 'datetime' else invitation.wedding_date }}
                        </p>
                        {% endif %}
                        {% if invitation.wedding_time %}
                        <p class="event-time">
                            <i class="far fa-clock me-2"></i>
                            {{ invitation.wedding_time }} WIB
                        </p>
                        {% endif %}
                        <p class="event-venue">{{ invitation.venue_name or 'Tempat Pernikahan' }}</p>
                        <p class="event-address">{{ invitation.venue_address }}</p>
                        <a href="https://maps.google.com/?q={{ invitation.venue_address | urlencode }}" 
                           target="_blank" class="location-btn">
                            <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi
                        </a>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </section>'''
    
    # CSS for gallery and events
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
        
        /* Wedding Events Styles */
        .wedding-events-section {
            padding: 60px 0;
        }
        
        .event-detail {
            background: white;
            padding: 30px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
            height: 100%;
        }
        
        .event-detail:hover {
            transform: translateY(-5px);
        }
        
        .event-icon {
            font-size: 48px;
            color: #d4af37;
            margin-bottom: 20px;
        }
        
        .event-title {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 15px;
            color: #333;
        }
        
        .event-date, .event-time {
            font-size: 16px;
            color: #666;
            margin-bottom: 10px;
        }
        
        .event-venue {
            font-size: 18px;
            font-weight: 600;
            color: #333;
            margin-bottom: 10px;
        }
        
        .event-address {
            font-size: 14px;
            color: #777;
            margin-bottom: 20px;
            line-height: 1.5;
        }
        
        .location-btn {
            display: inline-block;
            background: linear-gradient(135deg, #d4af37, #b8941f);
            color: white;
            padding: 12px 24px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        
        .location-btn:hover {
            background: linear-gradient(135deg, #b8941f, #d4af37);
            color: white;
            transform: scale(1.05);
        }
        
        /* Responsive */
        @media (max-width: 768px) {
            .gallery-grid {
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
            }
            
            .event-detail {
                padding: 20px;
            }
            
            .close-button {
                right: 20px;
                font-size: 30px;
            }
        }
    </style>'''
    
    # JavaScript for modal functionality
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
    
    # Find insertion points
    modified = False
    
    # 1. Add CSS to head section
    head_pattern = r'</head>'
    if re.search(head_pattern, content):
        content = re.sub(head_pattern, css_styles + '\n</head>', content)
        modified = True
    
    # 2. Insert gallery section before RSVP or footer
    rsvp_pattern = r'<!-- RSVP|<section[^>]*rsvp|<!-- Footer|<footer|</body>'
    match = re.search(rsvp_pattern, content, re.IGNORECASE)
    if match:
        insertion_point = match.start()
        content = content[:insertion_point] + gallery_section + '\n\n' + content[insertion_point:]
        modified = True
    
    # 3. Replace existing event sections or add new ones
    # Look for existing event sections to replace
    event_patterns = [
        r'<!-- Event Section -->.*?</section>',
        r'<!-- Wedding Events.*?</section>',
        r'<!-- Multi-Venue.*?</section>',
        r'<section[^>]*event[^>]*>.*?</section>'
    ]
    
    replaced_event = False
    for pattern in event_patterns:
        if re.search(pattern, content, re.DOTALL | re.IGNORECASE):
            content = re.sub(pattern, event_section, content, flags=re.DOTALL | re.IGNORECASE)
            replaced_event = True
            modified = True
            break
    
    # If no event section found, add it before gallery
    if not replaced_event:
        gallery_pos = content.find('<!-- Photo Gallery Section -->')
        if gallery_pos > -1:
            content = content[:gallery_pos] + event_section + '\n\n' + content[gallery_pos:]
            modified = True
    
    # 4. Add JavaScript before closing body tag
    body_pattern = r'</body>'
    if re.search(body_pattern, content):
        content = re.sub(body_pattern, js_script + '\n</body>', content)
        modified = True
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False

def main():
    """Update all wedding templates"""
    templates_dir = 'templates/wedding_templates'
    
    if not os.path.exists(templates_dir):
        print(f"Directory {templates_dir} not found!")
        return
    
    updated_count = 0
    total_count = 0
    
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html') and not filename.startswith('.'):
            file_path = os.path.join(templates_dir, filename)
            total_count += 1
            
            print(f"Processing {filename}...")
            
            try:
                if update_template_file(file_path):
                    print(f"✓ Updated {filename}")
                    updated_count += 1
                else:
                    print(f"- Skipped {filename}")
            except Exception as e:
                print(f"✗ Error updating {filename}: {str(e)}")
    
    print(f"\nCompleted! Updated {updated_count} out of {total_count} templates.")
    print("All templates now include:")
    print("- Photo gallery section with modal view")
    print("- Location buttons for each event")
    print("- Responsive design for mobile and desktop")

if __name__ == "__main__":
    main()
