import os
import re
from datetime import datetime

def backup_template(template_path):
    """Backup template before modification"""
    timestamp = str(int(datetime.now().timestamp()))
    # Modified backup path to reflect the nature of the update
    backup_path = f"{template_path}.backup.direct_links.{timestamp}"

    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Backup created: {backup_path}")

# New function to handle the general venue address display
def update_venue_address_display(content):
    """Update venue address to show as direct clickable links"""

    # Pattern for replacing the general venue address display
    patterns_to_replace = [
        r'<p[^>]*>\{\{\s*invitation\.venue_address[^}]*\}\}</p>',
        r'<p[^>]*>\{\{\s*invitation\.venue_address\s+if\s+not\s+invitation\.venue_address\.startswith\([\'"]http[\'"]\)[^}]*\}\}</p>',
        r'<p[^>]*>\{\{\s*invitation\.venue_address\s*\}\}</p>',
    ]

    # Replacement HTML structure for displaying the venue address
    replacement = '''<div class="venue-address">
    {% if invitation.venue_address %}
        {% if invitation.venue_address.startswith('http') %}
            <a href="{{ invitation.venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.venue_address }}
            </a>
        {% else %}
            <p class="address-text">
                <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.venue_address }}
            </p>
            <a href="https://maps.google.com/?q={{ invitation.venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat di Maps
            </a>
        {% endif %}
    {% endif %}
</div>'''

    for pattern in patterns_to_replace:
        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE | re.DOTALL)

    return content

# New function to update existing map button logic
def update_maps_button_logic(content):
    """Update existing maps button logic to support direct links"""

    # Patterns for existing maps buttons
    maps_button_patterns = [
        r'<a[^>]*href=["\']https://maps\.google\.com/\?q=\{\{\s*invitation\.venue_address\s*\}\}["\'][^>]*>[^<]*</a>',
        r'<a[^>]*href=["\']\{\{\s*invitation\.venue_address\s*\}\}["\'][^>]*>[^<]*</a>',
    ]

    # Replacement for maps buttons to support direct links
    maps_replacement = '''{% if invitation.venue_address %}
    {% if invitation.venue_address.startswith('http') %}
        <a href="{{ invitation.venue_address }}" target="_blank" class="maps-btn">
            <i class="fas fa-map-marked-alt me-2"></i>Buka Lokasi
        </a>
    {% else %}
        <a href="https://maps.google.com/?q={{ invitation.venue_address }}" target="_blank" class="maps-btn">
            <i class="fas fa-map-marked-alt me-2"></i>Lihat di Maps
        </a>
    {% endif %}
{% endif %}'''

    for pattern in maps_button_patterns:
        content = re.sub(pattern, maps_replacement, content, flags=re.IGNORECASE | re.DOTALL)

    return content

# New function to add specific CSS for direct link styles
def add_direct_link_styles(content):
    """Add CSS styles for direct link display"""

    direct_link_css = '''
/* Direct Maps Link Styles */
.venue-address {
    margin: 15px 0;
}

.direct-maps-link {
    display: inline-block;
    color: #2563eb;
    text-decoration: none;
    font-weight: 500;
    padding: 10px 15px;
    background: rgba(37, 99, 235, 0.1);
    border-radius: 8px;
    border: 1px solid rgba(37, 99, 235, 0.2);
    transition: all 0.3s ease;
    word-break: break-all;
    max-width: 100%;
}

.direct-maps-link:hover {
    background: rgba(37, 99, 235, 0.2);
    border-color: rgba(37, 99, 235, 0.4);
    text-decoration: none;
    color: #1d4ed8;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}

.direct-maps-link i {
    color: #2563eb;
    margin-right: 8px;
}

.address-text {
    margin-bottom: 10px;
    color: #6b7280;
    font-style: italic;
}

.address-text i {
    color: #ef4444;
    margin-right: 8px;
}

/* Enhanced Maps Button */
.maps-btn {
    display: inline-block;
    background: linear-gradient(135deg, #ef4444, #dc2626);
    color: white;
    text-decoration: none;
    padding: 12px 20px;
    border-radius: 25px;
    font-weight: 600;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

.maps-btn:hover {
    background: linear-gradient(135deg, #dc2626, #b91c1c);
    color: white;
    text-decoration: none;
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

.maps-btn i {
    margin-right: 8px;
}

/* Responsive Design */
@media (max-width: 768px) {
    .direct-maps-link {
        font-size: 14px;
        padding: 8px 12px;
        word-break: break-all;
    }

    .maps-btn {
        padding: 10px 16px;
        font-size: 14px;
    }
}
'''

    # Insert CSS into the content
    if '</style>' in content:
        content = content.replace('</style>', direct_link_css + '\n</style>')
    elif '</head>' in content:
        content = content.replace('</head>', f'<style>\n{direct_link_css}\n</style>\n</head>')

    return content

# Modified function to handle venue addresses within event sections
def update_multiple_venue_sections(content):
    """Update venue sections for akad, resepsi, and family events to support direct links"""

    # Patterns and replacements for Akad venue address
    akad_patterns = [
        r'<p class="event-address">\s*\{\{\s*invitation\.akad_venue_address[^}]*\}\}\s*</p>',
        r'<p[^>]*>\s*\{\{\s*invitation\.akad_venue_address[^}]*\}\}\s*</p>',
    ]
    akad_replacement = '''<div class="event-address">
    {% if invitation.akad_venue_address %}
        {% if invitation.akad_venue_address.startswith('http') %}
            <a href="{{ invitation.akad_venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.akad_venue_address }}
            </a>
        {% else %}
            <p class="address-text">{{ invitation.akad_venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.akad_venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi
            </a>
        {% endif %}
    {% endif %}
</div>'''
    for pattern in akad_patterns:
        content = re.sub(pattern, akad_replacement, content, flags=re.IGNORECASE | re.DOTALL)

    # Patterns and replacements for Resepsi venue address
    resepsi_patterns = [
        r'<p class="event-address">\s*\{\{\s*invitation\.resepsi_venue_address[^}]*\}\}\s*</p>',
        r'<p[^>]*>\s*\{\{\s*invitation\.resepsi_venue_address[^}]*\}\}\s*</p>',
    ]
    resepsi_replacement = '''<div class="event-address">
    {% if invitation.resepsi_venue_address %}
        {% if invitation.resepsi_venue_address.startswith('http') %}
            <a href="{{ invitation.resepsi_venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.resepsi_venue_address }}
            </a>
        {% else %}
            <p class="address-text">{{ invitation.resepsi_venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.resepsi_venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi
            </a>
        {% endif %}
    {% endif %}
</div>'''
    for pattern in resepsi_patterns:
        content = re.sub(pattern, resepsi_replacement, content, flags=re.IGNORECASE | re.DOTALL)

    # Patterns and replacements for Bride event venue address
    bride_patterns = [
        r'<p class="event-address">\s*\{\{\s*invitation\.bride_event_venue_address[^}]*\}\}\s*</p>',
        r'<p[^>]*>\s*\{\{\s*invitation\.bride_event_venue_address[^}]*\}\}\s*</p>',
    ]
    bride_replacement = '''<div class="event-address">
    {% if invitation.bride_event_venue_address %}
        {% if invitation.bride_event_venue_address.startswith('http') %}
            <a href="{{ invitation.bride_event_venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.bride_event_venue_address }}
            </a>
        {% else %}
            <p class="address-text">{{ invitation.bride_event_venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.bride_event_venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi
            </a>
        {% endif %}
    {% endif %}
</div>'''
    for pattern in bride_patterns:
        content = re.sub(pattern, bride_replacement, content, flags=re.IGNORECASE | re.DOTALL)

    # Patterns and replacements for Groom event venue address
    groom_patterns = [
        r'<p class="event-address">\s*\{\{\s*invitation\.groom_event_venue_address[^}]*\}\}\s*</p>',
        r'<p[^>]*>\s*\{\{\s*invitation\.groom_event_venue_address[^}]*\}\}\s*</p>',
    ]
    groom_replacement = '''<div class="event-address">
    {% if invitation.groom_event_venue_address %}
        {% if invitation.groom_event_venue_address.startswith('http') %}
            <a href="{{ invitation.groom_event_venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.groom_event_venue_address }}
            </a>
        {% else %}
            <p class="address-text">{{ invitation.groom_event_venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.groom_event_venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi
            </a>
        {% endif %}
    {% endif %}
</div>'''
    for pattern in groom_patterns:
        content = re.sub(pattern, groom_replacement, content, flags=re.IGNORECASE | re.DOTALL)

    return content

# The original functions add_photo_display_section, add_gallery_styles, and update_navigation_menu are kept as they are not affected by the venue address update.
def add_photo_display_section(content):
    """Add photo display section if not exists"""
    photo_section = '''
    <!-- Photo Gallery Section -->
    {% if prewedding_photos %}
    <section id="gallery" class="section gallery-section">
        <div class="container">
            <div class="section-header text-center">
                <h2 class="section-title">Our Moments</h2>
                <p class="section-subtitle">Beautiful memories we want to share</p>
            </div>
            <div class="gallery-grid">
                {% for photo in prewedding_photos %}
                <div class="gallery-item" onclick="openModal('{{ url_for('static', filename='prewedding_photos/' + photo) }}')">
                    <img src="{{ url_for('static', filename='prewedding_photos/' + photo) }}" alt="Prewedding Photo">
                    <div class="gallery-overlay">
                        <i class="fas fa-expand"></i>
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
    </section>

    <!-- Photo Modal -->
    <div class="modal" id="photoModal">
        <span class="close-button" onclick="closeModal()">&times;</span>
        <div class="modal-content">
            <img id="modalImage" src="" alt="Gallery Photo">
        </div>
    </div>
    {% endif %}
'''

    # Find RSVP section and insert gallery before it
    rsvp_pattern = r'(<section[^>]*id=["\']rsvp["\'][^>]*>)'
    if re.search(rsvp_pattern, content):
        content = re.sub(rsvp_pattern, photo_section + r'\n\1', content)
    else:
        # If no RSVP section, add before closing body
        content = content.replace('</body>', photo_section + '\n</body>')

    return content

# This function is no longer directly used for venue display but is kept for completeness if other template types use it.
def add_multiple_venue_support(content):
    """Add support for multiple venues (akad, resepsi, different locations)"""

    # Replace single venue display with multiple venue support
    venue_section = '''
    <!-- Wedding Events -->
    <section id="events" class="section events-section">
        <div class="container">
            <div class="section-header text-center">
                <h2 class="section-title">Wedding Events</h2>
                <p class="section-subtitle">Join us in celebrating our special day</p>
            </div>

            <div class="events-timeline">
                <!-- Akad Nikah -->
                {% if invitation.akad_date or invitation.wedding_date %}
                <div class="event-item">
                    <div class="event-icon">
                        <i class="fas fa-ring"></i>
                    </div>
                    <div class="event-content">
                        <h3 class="event-title">Akad Nikah</h3>
                        <div class="event-details">
                            <p class="event-date">
                                <i class="fas fa-calendar-alt"></i>
                                {{ invitation.akad_date or invitation.wedding_date }}
                            </p>
                            <p class="event-time">
                                <i class="fas fa-clock"></i>
                                {{ invitation.akad_time or invitation.wedding_time or '09:00' }}
                            </p>
                            <p class="event-venue">
                                <i class="fas fa-map-marker-alt"></i>
                                <strong>{{ invitation.akad_venue_name or invitation.venue_name or 'Venue Akad' }}</strong>
                            </p>
                            <p class="event-address">
                                {{ invitation.akad_venue_address or invitation.venue_address }}
                            </p>
                        </div>
                    </div>
                </div>
                {% endif %}

                <!-- Resepsi -->
                {% if invitation.resepsi_date or invitation.wedding_date %}
                <div class="event-item">
                    <div class="event-icon">
                        <i class="fas fa-glass-cheers"></i>
                    </div>
                    <div class="event-content">
                        <h3 class="event-title">Resepsi</h3>
                        <div class="event-details">
                            <p class="event-date">
                                <i class="fas fa-calendar-alt"></i>
                                {{ invitation.resepsi_date or invitation.wedding_date }}
                            </p>
                            <p class="event-time">
                                <i class="fas fa-clock"></i>
                                {{ invitation.resepsi_time or invitation.wedding_time or '19:00' }}
                            </p>
                            <p class="event-venue">
                                <i class="fas fa-map-marker-alt"></i>
                                <strong>{{ invitation.resepsi_venue_name or invitation.venue_name or 'Venue Resepsi' }}</strong>
                            </p>
                            <p class="event-address">
                                {{ invitation.resepsi_venue_address or invitation.venue_address }}
                            </p>
                        </div>
                    </div>
                </div>
                {% endif %}

                <!-- Bride Location (if different) -->
                {% if invitation.bride_event_venue_name %}
                <div class="event-item bride-event">
                    <div class="event-icon">
                        <i class="fas fa-female"></i>
                    </div>
                    <div class="event-content">
                        <h3 class="event-title">{{ invitation.bride_name }}'s Family Event</h3>
                        <div class="event-details">
                            <p class="event-date">
                                <i class="fas fa-calendar-alt"></i>
                                {{ invitation.bride_event_date or invitation.wedding_date }}
                            </p>
                            <p class="event-time">
                                <i class="fas fa-clock"></i>
                                {{ invitation.bride_event_time or '10:00' }}
                            </p>
                            <p class="event-venue">
                                <i class="fas fa-map-marker-alt"></i>
                                <strong>{{ invitation.bride_event_venue_name }}</strong>
                            </p>
                            <p class="event-address">
                                {{ invitation.bride_event_venue_address }}
                            </p>
                        </div>
                    </div>
                </div>
                {% endif %}

                <!-- Groom Location (if different) -->
                {% if invitation.groom_event_venue_name %}
                <div class="event-item groom-event">
                    <div class="event-icon">
                        <i class="fas fa-male"></i>
                    </div>
                    <div class="event-content">
                        <h3 class="event-title">{{ invitation.groom_name }}'s Family Event</h3>
                        <div class="event-details">
                            <p class="event-date">
                                <i class="fas fa-calendar-alt"></i>
                                {{ invitation.groom_event_date or invitation.wedding_date }}
                            </p>
                            <p class="event-time">
                                <i class="fas fa-clock"></i>
                                {{ invitation.groom_event_time or '10:00' }}
                            </p>
                            <p class="event-venue">
                                <i class="fas fa-map-marker-alt"></i>
                                <strong>{{ invitation.groom_event_venue_name }}</strong>
                            </p>
                            <p class="event-address">
                                {{ invitation.groom_event_venue_address }}
                            </p>
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
        </div>
    </section>
'''

    # Replace existing venue/event sections
    patterns_to_replace = [
        r'<section[^>]*class="[^"]*venue[^"]*"[^>]*>.*?</section>',
        r'<section[^>]*id="venue"[^>]*>.*?</section>',
        r'<section[^>]*class="[^"]*event[^"]*"[^>]*>.*?</section>',
        r'<section[^>]*id="event"[^>]*>.*?</section>',
    ]

    for pattern in patterns_to_replace:
        content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)

    # Find gallery section and insert events after it, or before RSVP
    gallery_pattern = r'(</section>\s*{% endif %}\s*)'
    if 'gallery-section' in content:
        content = re.sub(gallery_pattern, r'\1' + venue_section, content, count=1)
    else:
        rsvp_pattern = r'(<section[^>]*id=["\']rsvp["\'][^>]*>)'
        if re.search(rsvp_pattern, content):
            content = re.sub(rsvp_pattern, venue_section + r'\n\1', content)
        else:
            content = content.replace('</body>', venue_section + '\n</body>')

    return content

# New function to add CSS for gallery and events (unchanged from original)
def add_gallery_styles(content):
    """Add CSS styles for gallery and events"""
    gallery_css = '''
/* Gallery Styles */
.gallery-section {
    padding: 80px 0;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
}

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-top: 50px;
}

.gallery-item {
    position: relative;
    overflow: hidden;
    border-radius: 15px;
    cursor: pointer;
    aspect-ratio: 1;
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    transition: all 0.3s ease;
}

.gallery-item:hover {
    transform: translateY(-10px);
    box-shadow: 0 20px 40px rgba(0,0,0,0.2);
}

.gallery-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.3s ease;
}

.gallery-item:hover img {
    transform: scale(1.1);
}

.gallery-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.7);
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    transition: opacity 0.3s ease;
}

.gallery-item:hover .gallery-overlay {
    opacity: 1;
}

.gallery-overlay i {
    color: white;
    font-size: 2rem;
}

/* Modal Styles */
.modal {
    display: none;
    position: fixed;
    z-index: 9999;
    left: 0;
    top: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.9);
    animation: fadeIn 0.3s ease;
}

.modal-content {
    position: relative;
    margin: auto;
    padding: 20px;
    width: 90%;
    max-width: 800px;
    top: 50%;
    transform: translateY(-50%);
}

.modal-content img {
    width: 100%;
    height: auto;
    border-radius: 10px;
}

.close-button {
    position: absolute;
    top: 20px;
    right: 35px;
    color: #fff;
    font-size: 40px;
    font-weight: bold;
    cursor: pointer;
    z-index: 10000;
}

.close-button:hover {
    opacity: 0.7;
}

/* Events Timeline Styles */
.events-section {
    padding: 80px 0;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.events-timeline {
    margin-top: 50px;
    position: relative;
}

.events-timeline::before {
    content: '';
    position: absolute;
    left: 50%;
    top: 0;
    bottom: 0;
    width: 2px;
    background: rgba(255,255,255,0.3);
    transform: translateX(-50%);
}

.event-item {
    display: flex;
    align-items: center;
    margin-bottom: 50px;
    position: relative;
}

.event-item:nth-child(odd) {
    flex-direction: row;
}

.event-item:nth-child(even) {
    flex-direction: row-reverse;
}

.event-icon {
    width: 80px;
    height: 80px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    margin: 0 30px;
    backdrop-filter: blur(10px);
    border: 2px solid rgba(255,255,255,0.3);
}

.event-content {
    flex: 1;
    max-width: 400px;
    background: rgba(255,255,255,0.1);
    padding: 30px;
    border-radius: 15px;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}

.event-title {
    font-size: 1.5rem;
    margin-bottom: 20px;
    color: #fff;
}

.event-details p {
    margin-bottom: 10px;
    display: flex;
    align-items: center;
}

.event-details i {
    margin-right: 10px;
    width: 20px;
}

.bride-event .event-icon {
    background: rgba(255, 182, 193, 0.3);
}

.groom-event .event-icon {
    background: rgba(173, 216, 230, 0.3);
}

@media (max-width: 768px) {
    .events-timeline::before {
        left: 30px;
    }

    .event-item {
        flex-direction: row !important;
        padding-left: 60px;
    }

    .event-icon {
        position: absolute;
        left: 0;
        margin: 0;
    }

    .gallery-grid {
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
    }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
'''

    # Insert CSS before closing </style> tag
    if '</style>' in content:
        content = content.replace('</style>', gallery_css + '\n</style>')
    elif '</head>' in content:
        content = content.replace('</head>', f'<style>\n{gallery_css}\n</style>\n</head>')

    return content

# New function to add gallery javascript (unchanged from original)
def add_gallery_javascript(content):
    """Add JavaScript for gallery modal functionality"""
    gallery_js = '''
<script>
// Gallery Modal Functions
function openModal(imageSrc) {
    const modal = document.getElementById('photoModal');
    const modalImage = document.getElementById('modalImage');

    modal.style.display = 'block';
    modalImage.src = imageSrc;

    // Prevent body scroll
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    const modal = document.getElementById('photoModal');
    modal.style.display = 'none';

    // Restore body scroll
    document.body.style.overflow = 'auto';
}

// Close modal when clicking outside the image
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

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});
</script>
'''

    # Insert JavaScript before closing </body> tag
    content = content.replace('</body>', gallery_js + '\n</body>')

    return content

# Function to update navigation menu (unchanged from original)
def update_navigation_menu(content):
    """Update navigation menu to include gallery link"""
    # Find navigation menu and add gallery link
    nav_patterns = [
        r'(<a[^>]*href="#venue"[^>]*>[^<]*</a>)',
        r'(<a[^>]*href="#event"[^>]*>[^<]*</a>)',
        r'(<a[^>]*href="#rsvp"[^>]*>[^<]*</a>)',
    ]

    gallery_link = '<a href="#gallery">Gallery</a>'
    events_link = '<a href="#events">Events</a>'

    for pattern in nav_patterns:
        if re.search(pattern, content):
            # This part of the original code was intended to add new links,
            # but the new functionality focuses on updating existing address displays.
            # For now, we keep it to not alter unrelated parts of the original logic.
            # The primary goal of address linking is handled by other functions.
            content = re.sub(pattern, gallery_link + '\n' + events_link + '\n' + r'\1', content, count=1)
            break

    return content

# Main processing function, now calling the new functions
def process_template_file(template_path):
    """Process a single template file"""
    print(f"Processing: {template_path}")

    try:
        # Read original content
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Create backup
        backup_template(template_path)

        # Apply modifications
        content = update_venue_address_display(content)
        content = update_maps_button_logic(content)
        content = update_multiple_venue_sections(content) # This function now handles specific event addresses
        content = add_direct_link_styles(content)       # Adds CSS for new styles

        # The following functions are from the original script and are kept to maintain existing functionality.
        # They are not directly related to the venue address linking but are part of the template processing.
        content = add_photo_display_section(content)
        content = add_gallery_styles(content)
        content = add_gallery_javascript(content)
        content = update_navigation_menu(content)

        # Write updated content
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"✅ Successfully updated: {template_path}")

    except Exception as e:
        print(f"❌ Error processing {template_path}: {str(e)}")

# Main function, unchanged except for the print statements reflecting the new purpose.
def main():
    """Main function to process all wedding templates"""
    templates_dir = 'templates/wedding_templates'

    if not os.path.exists(templates_dir):
        print(f"❌ Directory {templates_dir} tidak ditemukan!")
        return

    # Get all HTML template files (exclude backup files)
    template_files = [f for f in os.listdir(templates_dir)
                     if f.endswith('.html') and not '.backup' in f]

    if not template_files:
        print(f"❌ Tidak ada file template ditemukan di {templates_dir}")
        return

    print(f"📋 Ditemukan {len(template_files)} template untuk diproses:")
    for template_file in template_files:
        print(f"   - {template_file}")

    print("\n🚀 Memulai proses update alamat venue menjadi link langsung...")

    success_count = 0
    for template_file in template_files:
        template_path = os.path.join(templates_dir, template_file)
        try:
            process_template_file(template_path)
            success_count += 1
        except Exception as e:
            print(f"❌ Gagal memproses {template_file}: {str(e)}")

    print(f"\n✨ Proses selesai!")
    print(f"✅ Berhasil: {success_count}/{len(template_files)} template")
    print(f"📁 Backup tersimpan dengan suffix .backup.direct_links.[timestamp]")

    if success_count > 0:
        print("\n📝 Perubahan yang diterapkan:")
        print("   1. ✅ Alamat venue sekarang ditampilkan sebagai link langsung")
        print("   2. ✅ Support untuk link Google Maps (https://maps.app.goo.gl/...)")
        print("   3. ✅ Fallback ke Google Maps search untuk alamat teks biasa")
        print("   4. ✅ Styling yang diperbaiki untuk link alamat")
        print("   5. ✅ Responsive design untuk mobile devices")

        print("\n🎯 Contoh penggunaan:")
        print("   - Link langsung: https://maps.app.goo.gl/63m4DkQWedK8dHv29")
        print("   - Alamat teks: Jl. Merdeka No. 123, Jakarta")

if __name__ == "__main__":
    main()