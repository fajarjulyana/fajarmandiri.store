
#!/usr/bin/env python3
"""
Script untuk menambahkan tombol "Lihat Alamat" pada semua template wedding
yang belum memiliki fitur tersebut
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Backup file original"""
    timestamp = str(int(datetime.now().timestamp()))
    backup_path = f"{file_path}.backup.view_address.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def add_address_button_styles(content):
    """Add CSS styles for address buttons"""
    
    styles = """
/* Address Button Styles */
.address-container {
    margin: 1rem 0;
    text-align: center;
}

.address-text {
    margin-bottom: 1rem;
    color: #666;
    line-height: 1.6;
}

.direct-maps-link {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #4285f4, #34a853);
    color: white;
    text-decoration: none;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
}

.direct-maps-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
    color: white;
    text-decoration: none;
}

.maps-btn {
    display: inline-block;
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #4285f4, #34a853);
    color: white;
    text-decoration: none;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
    margin-top: 0.5rem;
}

.maps-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
    color: white;
    text-decoration: none;
}

.venue-address-section {
    background: rgba(255, 255, 255, 0.95);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.venue-address-section h3 {
    margin-bottom: 1rem;
    color: #333;
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

def update_address_displays(content):
    """Update all address displays to include view buttons"""
    
    # Pattern untuk venue_address
    venue_patterns = [
        r'<p[^>]*>\s*\{\{\s*invitation\.venue_address[^}]*\}\}\s*</p>',
        r'<div[^>]*>\s*\{\{\s*invitation\.venue_address[^}]*\}\}\s*</div>',
        r'\{\{\s*invitation\.venue_address[^}]*\}\}(?!</a>)(?!</div>)',
    ]
    
    venue_replacement = '''<div class="venue-address-section">
    {% if invitation.venue_address %}
        {% if invitation.venue_address.startswith('http') %}
            <a href="{{ invitation.venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi di Maps
            </a>
        {% else %}
            <p class="address-text">{{ invitation.venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi
            </a>
        {% endif %}
    {% endif %}
</div>'''
    
    for pattern in venue_patterns:
        content = re.sub(pattern, venue_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Pattern untuk akad_venue_address
    akad_patterns = [
        r'<p[^>]*>\s*\{\{\s*invitation\.akad_venue_address[^}]*\}\}\s*</p>',
        r'<div[^>]*>\s*\{\{\s*invitation\.akad_venue_address[^}]*\}\}\s*</div>',
        r'\{\{\s*invitation\.akad_venue_address[^}]*\}\}(?!</a>)(?!</div>)',
    ]
    
    akad_replacement = '''<div class="venue-address-section">
    {% if invitation.akad_venue_address %}
        {% if invitation.akad_venue_address.startswith('http') %}
            <a href="{{ invitation.akad_venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi Akad
            </a>
        {% else %}
            <p class="address-text">{{ invitation.akad_venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.akad_venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi Akad
            </a>
        {% endif %}
    {% endif %}
</div>'''
    
    for pattern in akad_patterns:
        content = re.sub(pattern, akad_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Pattern untuk resepsi_venue_address
    resepsi_patterns = [
        r'<p[^>]*>\s*\{\{\s*invitation\.resepsi_venue_address[^}]*\}\}\s*</p>',
        r'<div[^>]*>\s*\{\{\s*invitation\.resepsi_venue_address[^}]*\}\}\s*</div>',
        r'\{\{\s*invitation\.resepsi_venue_address[^}]*\}\}(?!</a>)(?!</div>)',
    ]
    
    resepsi_replacement = '''<div class="venue-address-section">
    {% if invitation.resepsi_venue_address %}
        {% if invitation.resepsi_venue_address.startswith('http') %}
            <a href="{{ invitation.resepsi_venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi Resepsi
            </a>
        {% else %}
            <p class="address-text">{{ invitation.resepsi_venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.resepsi_venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi Resepsi
            </a>
        {% endif %}
    {% endif %}
</div>'''
    
    for pattern in resepsi_patterns:
        content = re.sub(pattern, resepsi_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Pattern untuk bride_event_venue_address
    bride_patterns = [
        r'<p[^>]*>\s*\{\{\s*invitation\.bride_event_venue_address[^}]*\}\}\s*</p>',
        r'<div[^>]*>\s*\{\{\s*invitation\.bride_event_venue_address[^}]*\}\}\s*</div>',
        r'\{\{\s*invitation\.bride_event_venue_address[^}]*\}\}(?!</a>)(?!</div>)',
    ]
    
    bride_replacement = '''<div class="venue-address-section">
    {% if invitation.bride_event_venue_address %}
        {% if invitation.bride_event_venue_address.startswith('http') %}
            <a href="{{ invitation.bride_event_venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi Acara Keluarga Mempelai Wanita
            </a>
        {% else %}
            <p class="address-text">{{ invitation.bride_event_venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.bride_event_venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi Acara Keluarga Mempelai Wanita
            </a>
        {% endif %}
    {% endif %}
</div>'''
    
    for pattern in bride_patterns:
        content = re.sub(pattern, bride_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Pattern untuk groom_event_venue_address
    groom_patterns = [
        r'<p[^>]*>\s*\{\{\s*invitation\.groom_event_venue_address[^}]*\}\}\s*</p>',
        r'<div[^>]*>\s*\{\{\s*invitation\.groom_event_venue_address[^}]*\}\}\s*</div>',
        r'\{\{\s*invitation\.groom_event_venue_address[^}]*\}\}(?!</a>)(?!</div>)',
    ]
    
    groom_replacement = '''<div class="venue-address-section">
    {% if invitation.groom_event_venue_address %}
        {% if invitation.groom_event_venue_address.startswith('http') %}
            <a href="{{ invitation.groom_event_venue_address }}" target="_blank" class="direct-maps-link">
                <i class="fas fa-map-marker-alt me-2"></i>Lihat Lokasi Acara Keluarga Mempelai Pria
            </a>
        {% else %}
            <p class="address-text">{{ invitation.groom_event_venue_address }}</p>
            <a href="https://maps.google.com/?q={{ invitation.groom_event_venue_address }}" target="_blank" class="maps-btn">
                <i class="fas fa-map-marked-alt me-2"></i>Lihat Lokasi Acara Keluarga Mempelai Pria
            </a>
        {% endif %}
    {% endif %}
</div>'''
    
    for pattern in groom_patterns:
        content = re.sub(pattern, groom_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    return content

def check_if_already_has_address_button(content):
    """Check if template already has address button functionality"""
    button_indicators = [
        'direct-maps-link',
        'maps-btn',
        'Lihat Lokasi',
        'venue-address-section'
    ]
    
    for indicator in button_indicators:
        if indicator in content:
            return True
    return False

def process_template(file_path):
    """Process a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if already has address buttons
        if check_if_already_has_address_button(content):
            print(f"⚠️  Skipped (already has address buttons): {os.path.basename(file_path)}")
            return False
        
        # Backup original
        backup_file(file_path)
        
        # Add styles
        content = add_address_button_styles(content)
        
        # Update address displays
        content = update_address_displays(content)
        
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
    print("🚀 Adding view address buttons to all wedding templates...")
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
    skip_count = 0
    
    for file_path in template_files:
        print(f"\nProcessing: {os.path.basename(file_path)}")
        
        result = process_template(file_path)
        if result is True:
            success_count += 1
        elif result is False:
            skip_count += 1
    
    print("\n" + "=" * 60)
    print("✨ Processing completed!")
    print(f"✅ Successfully updated: {success_count}/{len(template_files)} templates")
    print(f"⚠️  Skipped (already has buttons): {skip_count} templates")
    
    if success_count > 0:
        print(f"\n📁 Backup files saved with suffix .backup.view_address.[timestamp]")
        print("\n📝 Features added:")
        print("   🔹 CSS styles for address buttons")
        print("   🔹 Smart link detection (http/https)")
        print("   🔹 Google Maps integration")
        print("   🔹 Responsive button design")
        print("   🔹 Support for all venue types (venue, akad, resepsi, bride_event, groom_event)")
        print("\n💡 How it works:")
        print("   • If address starts with 'http': Direct clickable link")
        print("   • If regular address: Shows address + Google Maps search button")
        print("   • Automatically styles all venue address fields")
    
    return True

if __name__ == "__main__":
    main()
