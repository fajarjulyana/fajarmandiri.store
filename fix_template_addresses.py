
#!/usr/bin/env python3
"""
Script untuk memperbaiki masalah tampilan alamat lokasi pada semua template wedding
Masalah: Template tidak menampilkan alamat baik untuk single event maupun multi event
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Backup file original"""
    timestamp = str(int(datetime.now().timestamp()))
    backup_path = f"{file_path}.backup.address_fix.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def add_address_display_styles(content):
    """Add CSS styles untuk tampilan alamat yang konsisten"""
    
    styles = """
/* Address Display Styles */
.venue-info {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.venue-name {
    font-size: 1.2rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 0.5rem;
}

.venue-address {
    color: #4a5568;
    margin-bottom: 1rem;
    line-height: 1.6;
}

.venue-link {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #4285f4, #34a853);
    color: white !important;
    text-decoration: none;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
    margin-top: 0.5rem;
}

.venue-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
    color: white !important;
    text-decoration: none;
}

.venue-link i {
    margin-right: 0.5rem;
}

.event-details {
    background: rgba(255, 255, 255, 0.9);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1.5rem 0;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.event-title {
    font-size: 1.4rem;
    font-weight: 700;
    color: #2d3748;
    margin-bottom: 1rem;
    text-align: center;
}

.event-datetime {
    text-align: center;
    margin-bottom: 1rem;
}

.event-date {
    font-size: 1.1rem;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 0.25rem;
}

.event-time {
    color: #4a5568;
    font-size: 1rem;
}
"""
    
    # Find closing </style> tag and add styles before it
    if '</style>' in content:
        content = content.replace('</style>', f'\n{styles}\n</style>')
    else:
        # If no style tag exists, add it in head
        head_pattern = r'</head>'
        if re.search(head_pattern, content):
            content = re.sub(head_pattern, f'<style>{styles}</style>\n</head>', content)
    
    return content

def fix_single_venue_display(content):
    """Fix single venue display for templates that use legacy venue fields"""
    
    # Pattern untuk mengganti tampilan venue lama dengan yang baru
    old_venue_patterns = [
        r'<p[^>]*>\s*\{\{\s*invitation\.venue_address[^}]*\}\}\s*</p>',
        r'<div[^>]*>\s*\{\{\s*invitation\.venue_address[^}]*\}\}\s*</div>',
        r'\{\{\s*invitation\.venue_address[^}]*\}\}(?!\s*["\'])',
    ]
    
    new_venue_display = '''<div class="venue-info">
    {% if invitation.venue_name %}
        <div class="venue-name">{{ invitation.venue_name }}</div>
    {% endif %}
    
    {% if invitation.venue_address %}
        {% if invitation.venue_address.startswith('http') %}
            <a href="{{ invitation.venue_address }}" target="_blank" class="venue-link">
                <i class="fas fa-map-marker-alt"></i>Lihat Lokasi di Maps
            </a>
        {% else %}
            <div class="venue-address">{{ invitation.venue_address }}</div>
            <a href="https://maps.google.com/?q={{ invitation.venue_address }}" target="_blank" class="venue-link">
                <i class="fas fa-map-marked-alt"></i>Lihat Lokasi
            </a>
        {% endif %}
    {% endif %}
</div>'''
    
    for pattern in old_venue_patterns:
        content = re.sub(pattern, new_venue_display, content, flags=re.IGNORECASE | re.DOTALL)
    
    return content

def add_multi_venue_display(content):
    """Add comprehensive multi-venue display support"""
    
    # Check if multi-venue section already exists
    if 'akad_venue_address' in content and 'resepsi_venue_address' in content:
        return content
    
    # Find wedding details section and add multi-venue support
    wedding_section_pattern = r'(<section[^>]*class="[^"]*wedding[^"]*"[^>]*>.*?</section>)'
    
    multi_venue_section = '''
    <!-- Multi-Venue Wedding Events -->
    <section id="wedding-events" class="section wedding-events-section">
        <div class="container">
            <div class="section-header text-center">
                <h2 class="section-title">Acara Pernikahan</h2>
                <p class="section-subtitle">Bergabunglah dengan kami merayakan hari bahagia</p>
            </div>
            
            <div class="row justify-content-center">
                <!-- Akad Nikah -->
                {% if invitation.akad_venue_address or invitation.akad_venue_name or invitation.akad_date %}
                <div class="col-md-6 col-lg-5 mb-4">
                    <div class="event-details">
                        <div class="event-title">
                            <i class="fas fa-mosque me-2"></i>Akad Nikah
                        </div>
                        
                        {% if invitation.akad_date or invitation.akad_time %}
                        <div class="event-datetime">
                            {% if invitation.akad_date %}
                                <div class="event-date">
                                    {{ invitation.akad_date.strftime('%A, %d %B %Y') if invitation.akad_date else '' }}
                                </div>
                            {% endif %}
                            {% if invitation.akad_time %}
                                <div class="event-time">{{ invitation.akad_time }} WIB</div>
                            {% endif %}
                        </div>
                        {% endif %}
                        
                        <div class="venue-info">
                            {% if invitation.akad_venue_name %}
                                <div class="venue-name">{{ invitation.akad_venue_name }}</div>
                            {% endif %}
                            
                            {% if invitation.akad_venue_address %}
                                {% if invitation.akad_venue_address.startswith('http') %}
                                    <a href="{{ invitation.akad_venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marker-alt"></i>Lihat Lokasi Akad
                                    </a>
                                {% else %}
                                    <div class="venue-address">{{ invitation.akad_venue_address }}</div>
                                    <a href="https://maps.google.com/?q={{ invitation.akad_venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marked-alt"></i>Lihat Lokasi Akad
                                    </a>
                                {% endif %}
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                <!-- Resepsi -->
                {% if invitation.resepsi_venue_address or invitation.resepsi_venue_name or invitation.resepsi_date %}
                <div class="col-md-6 col-lg-5 mb-4">
                    <div class="event-details">
                        <div class="event-title">
                            <i class="fas fa-utensils me-2"></i>Resepsi
                        </div>
                        
                        {% if invitation.resepsi_date or invitation.resepsi_time %}
                        <div class="event-datetime">
                            {% if invitation.resepsi_date %}
                                <div class="event-date">
                                    {{ invitation.resepsi_date.strftime('%A, %d %B %Y') if invitation.resepsi_date else '' }}
                                </div>
                            {% endif %}
                            {% if invitation.resepsi_time %}
                                <div class="event-time">{{ invitation.resepsi_time }} WIB</div>
                            {% endif %}
                        </div>
                        {% endif %}
                        
                        <div class="venue-info">
                            {% if invitation.resepsi_venue_name %}
                                <div class="venue-name">{{ invitation.resepsi_venue_name }}</div>
                            {% endif %}
                            
                            {% if invitation.resepsi_venue_address %}
                                {% if invitation.resepsi_venue_address.startswith('http') %}
                                    <a href="{{ invitation.resepsi_venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marker-alt"></i>Lihat Lokasi Resepsi
                                    </a>
                                {% else %}
                                    <div class="venue-address">{{ invitation.resepsi_venue_address }}</div>
                                    <a href="https://maps.google.com/?q={{ invitation.resepsi_venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marked-alt"></i>Lihat Lokasi Resepsi
                                    </a>
                                {% endif %}
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
            
            <!-- Family Events (Optional) -->
            {% if invitation.bride_event_venue_address or invitation.groom_event_venue_address %}
            <div class="row justify-content-center mt-4">
                <div class="col-12">
                    <h4 class="text-center mb-4">Acara Keluarga</h4>
                </div>
                
                <!-- Bride Family Event -->
                {% if invitation.bride_event_venue_address or invitation.bride_event_venue_name %}
                <div class="col-md-6 col-lg-5 mb-4">
                    <div class="event-details">
                        <div class="event-title">
                            <i class="fas fa-female me-2"></i>Keluarga Mempelai Wanita
                        </div>
                        
                        {% if invitation.bride_event_date or invitation.bride_event_time %}
                        <div class="event-datetime">
                            {% if invitation.bride_event_date %}
                                <div class="event-date">
                                    {{ invitation.bride_event_date.strftime('%A, %d %B %Y') if invitation.bride_event_date else '' }}
                                </div>
                            {% endif %}
                            {% if invitation.bride_event_time %}
                                <div class="event-time">{{ invitation.bride_event_time }} WIB</div>
                            {% endif %}
                        </div>
                        {% endif %}
                        
                        <div class="venue-info">
                            {% if invitation.bride_event_venue_name %}
                                <div class="venue-name">{{ invitation.bride_event_venue_name }}</div>
                            {% endif %}
                            
                            {% if invitation.bride_event_venue_address %}
                                {% if invitation.bride_event_venue_address.startswith('http') %}
                                    <a href="{{ invitation.bride_event_venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marker-alt"></i>Lihat Lokasi
                                    </a>
                                {% else %}
                                    <div class="venue-address">{{ invitation.bride_event_venue_address }}</div>
                                    <a href="https://maps.google.com/?q={{ invitation.bride_event_venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marked-alt"></i>Lihat Lokasi
                                    </a>
                                {% endif %}
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endif %}
                
                <!-- Groom Family Event -->
                {% if invitation.groom_event_venue_address or invitation.groom_event_venue_name %}
                <div class="col-md-6 col-lg-5 mb-4">
                    <div class="event-details">
                        <div class="event-title">
                            <i class="fas fa-male me-2"></i>Keluarga Mempelai Pria
                        </div>
                        
                        {% if invitation.groom_event_date or invitation.groom_event_time %}
                        <div class="event-datetime">
                            {% if invitation.groom_event_date %}
                                <div class="event-date">
                                    {{ invitation.groom_event_date.strftime('%A, %d %B %Y') if invitation.groom_event_date else '' }}
                                </div>
                            {% endif %}
                            {% if invitation.groom_event_time %}
                                <div class="event-time">{{ invitation.groom_event_time }} WIB</div>
                            {% endif %}
                        </div>
                        {% endif %}
                        
                        <div class="venue-info">
                            {% if invitation.groom_event_venue_name %}
                                <div class="venue-name">{{ invitation.groom_event_venue_name }}</div>
                            {% endif %}
                            
                            {% if invitation.groom_event_venue_address %}
                                {% if invitation.groom_event_venue_address.startswith('http') %}
                                    <a href="{{ invitation.groom_event_venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marker-alt"></i>Lihat Lokasi
                                    </a>
                                {% else %}
                                    <div class="venue-address">{{ invitation.groom_event_venue_address }}</div>
                                    <a href="https://maps.google.com/?q={{ invitation.groom_event_venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marked-alt"></i>Lihat Lokasi
                                    </a>
                                {% endif %}
                            {% endif %}
                        </div>
                    </div>
                </div>
                {% endif %}
            </div>
            {% endif %}
            
            <!-- Fallback for Single Event -->
            {% if not (invitation.akad_venue_address or invitation.resepsi_venue_address) and (invitation.venue_address or invitation.venue_name) %}
            <div class="row justify-content-center">
                <div class="col-md-8 col-lg-6">
                    <div class="event-details">
                        <div class="event-title">
                            <i class="fas fa-heart me-2"></i>Acara Pernikahan
                        </div>
                        
                        {% if invitation.wedding_date or invitation.wedding_time %}
                        <div class="event-datetime">
                            {% if invitation.wedding_date %}
                                <div class="event-date">
                                    {{ invitation.wedding_date.strftime('%A, %d %B %Y') if invitation.wedding_date else '' }}
                                </div>
                            {% endif %}
                            {% if invitation.wedding_time %}
                                <div class="event-time">{{ invitation.wedding_time }} WIB</div>
                            {% endif %}
                        </div>
                        {% endif %}
                        
                        <div class="venue-info">
                            {% if invitation.venue_name %}
                                <div class="venue-name">{{ invitation.venue_name }}</div>
                            {% endif %}
                            
                            {% if invitation.venue_address %}
                                {% if invitation.venue_address.startswith('http') %}
                                    <a href="{{ invitation.venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marker-alt"></i>Lihat Lokasi di Maps
                                    </a>
                                {% else %}
                                    <div class="venue-address">{{ invitation.venue_address }}</div>
                                    <a href="https://maps.google.com/?q={{ invitation.venue_address }}" target="_blank" class="venue-link">
                                        <i class="fas fa-map-marked-alt"></i>Lihat Lokasi
                                    </a>
                                {% endif %}
                            {% endif %}
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}
        </div>
    </section>
    '''
    
    # Find a good place to insert the multi-venue section
    # Look for existing wedding/events section or before RSVP section
    insertion_patterns = [
        r'(<section[^>]*class="[^"]*rsvp[^"]*"[^>]*>)',
        r'(<section[^>]*class="[^"]*gallery[^"]*"[^>]*>)',
        r'(<section[^>]*class="[^"]*gift[^"]*"[^>]*>)',
        r'(<div[^>]*class="[^"]*rsvp[^"]*"[^>]*>)',
    ]
    
    for pattern in insertion_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            content = re.sub(pattern, f'{multi_venue_section}\n\\1', content, flags=re.IGNORECASE)
            return content
    
    # If no suitable insertion point found, add before </body>
    body_pattern = r'</body>'
    if re.search(body_pattern, content):
        content = re.sub(body_pattern, f'{multi_venue_section}\n</body>', content)
    
    return content

def process_template(file_path):
    """Process a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup original
        backup_file(file_path)
        
        # Add address display styles
        content = add_address_display_styles(content)
        
        # Fix single venue display
        content = fix_single_venue_display(content)
        
        # Add multi-venue display support
        content = add_multi_venue_display(content)
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully updated: {os.path.basename(file_path)}")
        return True
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Fixing address display issues in all wedding templates...")
    print("=" * 60)
    
    templates_dir = 'templates/wedding_templates'
    
    if not os.path.exists(templates_dir):
        print(f"❌ Directory not found: {templates_dir}")
        return False
    
    # Get all HTML template files
    template_files = []
    for file in os.listdir(templates_dir):
        if file.endswith('.html') and not file.endswith('.backup'):
            template_files.append(os.path.join(templates_dir, file))
    
    if not template_files:
        print("❌ No template files found!")
        return False
    
    print(f"📋 Found {len(template_files)} template files to process:")
    for file_path in template_files:
        print(f"   - {os.path.basename(file_path)}")
    
    print("\n🚀 Starting template processing...")
    
    success_count = 0
    
    for file_path in template_files:
        print(f"\nProcessing: {os.path.basename(file_path)}")
        
        if process_template(file_path):
            success_count += 1
    
    print("\n" + "=" * 60)
    print("✨ Processing completed!")
    print(f"✅ Successfully updated: {success_count}/{len(template_files)} templates")
    
    if success_count > 0:
        print(f"\n📁 Backup files saved with suffix .backup.address_fix.[timestamp]")
        print("\n📝 Fixes applied:")
        print("   🔹 Added comprehensive address display styles")
        print("   🔹 Fixed single venue address display")
        print("   🔹 Added multi-venue support with separate events")
        print("   🔹 Support for Google Maps links (http/https)")
        print("   🔹 Fallback display for legacy single events")
        print("   🔹 Optional family events display")
        print("\n💡 Features:")
        print("   • Single Event: Shows venue name + address + map link")
        print("   • Multi Event: Shows Akad + Resepsi separately")
        print("   • Family Events: Optional bride/groom family events")
        print("   • Smart Links: Direct links or Google Maps search")
        print("   • Responsive Design: Works on all screen sizes")
    
    return True

if __name__ == "__main__":
    main()
