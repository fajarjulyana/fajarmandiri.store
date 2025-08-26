
#!/usr/bin/env python3
"""
Script untuk mengubah semua alamat pada template wedding menjadi link yang bisa diklik langsung
Alamat akan menjadi link yang membuka Google Maps menunjukkan lokasi acara
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Backup file original"""
    timestamp = str(int(datetime.now().timestamp()))
    backup_path = f"{file_path}.backup.address_links.{timestamp}"
    shutil.copy2(file_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path

def update_address_to_clickable_links(content):
    """Ubah semua tampilan alamat menjadi link yang bisa diklik langsung"""
    
    # Pattern untuk venue_address - ubah menjadi link langsung
    venue_patterns = [
        r'<div class="venue-address">[^<]*</div>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
        r'<p class="address-text">[^<]*</p>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
        r'<div class="venue-address">\{\{\s*invitation\.venue_address\s*\}\}</div>',
        r'<p class="address-text">\{\{\s*invitation\.venue_address\s*\}\}</p>',
    ]
    
    venue_replacement = '''{% if invitation.venue_address %}
    {% if invitation.venue_address.startswith('http') %}
        <a href="{{ invitation.venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.venue_address }}
        </a>
    {% else %}
        <a href="https://maps.google.com/?q={{ invitation.venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.venue_address }}
        </a>
    {% endif %}
{% endif %}'''
    
    for pattern in venue_patterns:
        content = re.sub(pattern, venue_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Pattern untuk akad_venue_address
    akad_patterns = [
        r'<div class="venue-address">[^<]*\{\{\s*invitation\.akad_venue_address[^}]*\}\}[^<]*</div>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
        r'<p class="address-text">[^<]*\{\{\s*invitation\.akad_venue_address[^}]*\}\}[^<]*</p>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
    ]
    
    akad_replacement = '''{% if invitation.akad_venue_address %}
    {% if invitation.akad_venue_address.startswith('http') %}
        <a href="{{ invitation.akad_venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.akad_venue_address }}
        </a>
    {% else %}
        <a href="https://maps.google.com/?q={{ invitation.akad_venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.akad_venue_address }}
        </a>
    {% endif %}
{% endif %}'''
    
    for pattern in akad_patterns:
        content = re.sub(pattern, akad_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Pattern untuk resepsi_venue_address
    resepsi_patterns = [
        r'<div class="venue-address">[^<]*\{\{\s*invitation\.resepsi_venue_address[^}]*\}\}[^<]*</div>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
        r'<p class="address-text">[^<]*\{\{\s*invitation\.resepsi_venue_address[^}]*\}\}[^<]*</p>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
    ]
    
    resepsi_replacement = '''{% if invitation.resepsi_venue_address %}
    {% if invitation.resepsi_venue_address.startswith('http') %}
        <a href="{{ invitation.resepsi_venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.resepsi_venue_address }}
        </a>
    {% else %}
        <a href="https://maps.google.com/?q={{ invitation.resepsi_venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.resepsi_venue_address }}
        </a>
    {% endif %}
{% endif %}'''
    
    for pattern in resepsi_patterns:
        content = re.sub(pattern, resepsi_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Pattern untuk bride_event_venue_address
    bride_patterns = [
        r'<div class="venue-address">[^<]*\{\{\s*invitation\.bride_event_venue_address[^}]*\}\}[^<]*</div>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
        r'<p class="address-text">[^<]*\{\{\s*invitation\.bride_event_venue_address[^}]*\}\}[^<]*</p>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
    ]
    
    bride_replacement = '''{% if invitation.bride_event_venue_address %}
    {% if invitation.bride_event_venue_address.startswith('http') %}
        <a href="{{ invitation.bride_event_venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.bride_event_venue_address }}
        </a>
    {% else %}
        <a href="https://maps.google.com/?q={{ invitation.bride_event_venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.bride_event_venue_address }}
        </a>
    {% endif %}
{% endif %}'''
    
    for pattern in bride_patterns:
        content = re.sub(pattern, bride_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    # Pattern untuk groom_event_venue_address
    groom_patterns = [
        r'<div class="venue-address">[^<]*\{\{\s*invitation\.groom_event_venue_address[^}]*\}\}[^<]*</div>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
        r'<p class="address-text">[^<]*\{\{\s*invitation\.groom_event_venue_address[^}]*\}\}[^<]*</p>\s*<a href="[^"]*"[^>]*>[^<]*</a>',
    ]
    
    groom_replacement = '''{% if invitation.groom_event_venue_address %}
    {% if invitation.groom_event_venue_address.startswith('http') %}
        <a href="{{ invitation.groom_event_venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.groom_event_venue_address }}
        </a>
    {% else %}
        <a href="https://maps.google.com/?q={{ invitation.groom_event_venue_address }}" target="_blank" class="venue-address-link">
            <i class="fas fa-map-marker-alt me-2"></i>{{ invitation.groom_event_venue_address }}
        </a>
    {% endif %}
{% endif %}'''
    
    for pattern in groom_patterns:
        content = re.sub(pattern, groom_replacement, content, flags=re.IGNORECASE | re.DOTALL)
    
    return content

def add_address_link_styles(content):
    """Tambah CSS styling untuk address links"""
    
    styles = """
/* Address Link Styles */
.venue-address-link {
    display: inline-block;
    padding: 12px 20px;
    background: linear-gradient(135deg, #4285f4, #34a853);
    color: white !important;
    text-decoration: none;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    box-shadow: 0 4px 15px rgba(66, 133, 244, 0.3);
    margin: 10px 0;
    font-size: 0.95rem;
    line-height: 1.4;
    word-break: break-word;
}

.venue-address-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(66, 133, 244, 0.4);
    color: white !important;
    text-decoration: none;
    background: linear-gradient(135deg, #3367d6, #2d7d32);
}

.venue-address-link i {
    margin-right: 8px;
    font-size: 1rem;
}

/* Responsive address links */
@media (max-width: 768px) {
    .venue-address-link {
        padding: 10px 16px;
        font-size: 0.9rem;
        display: block;
        text-align: center;
        margin: 15px auto;
        max-width: 280px;
    }
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

def remove_duplicate_buttons(content):
    """Hapus tombol lihat lokasi yang duplikat"""
    
    # Remove old style buttons that are now redundant
    button_patterns = [
        r'<a[^>]*class="[^"]*maps-btn[^"]*"[^>]*>[^<]*<i[^>]*></i>[^<]*</a>',
        r'<a[^>]*class="[^"]*venue-link[^"]*"[^>]*>[^<]*<i[^>]*></i>[^<]*</a>',
        r'<button[^>]*class="[^"]*maps-btn[^"]*"[^>]*>[^<]*</button>',
    ]
    
    for pattern in button_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE | re.DOTALL)
    
    return content

def process_template(file_path):
    """Process a single template file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup original
        backup_file(file_path)
        
        # Update address displays to clickable links
        content = update_address_to_clickable_links(content)
        
        # Remove duplicate buttons
        content = remove_duplicate_buttons(content)
        
        # Add address link styles
        content = add_address_link_styles(content)
        
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
    print("🚀 Converting addresses to clickable Google Maps links...")
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
        print(f"\n📁 Backup files saved with suffix .backup.address_links.[timestamp]")
        print("\n📝 Changes applied:")
        print("   🔹 Alamat sekarang menjadi link yang bisa diklik langsung")
        print("   🔹 Link langsung ke Google Maps menunjukkan lokasi")
        print("   🔹 Support untuk link Maps langsung (https://maps.app.goo.gl/...)")
        print("   🔹 Hapus tombol duplikat 'Lihat Lokasi'")
        print("   🔹 Styling yang konsisten untuk semua link alamat")
        print("\n💡 Fitur:")
        print("   • Klik alamat = langsung buka Google Maps")
        print("   • Auto detect link Maps langsung")
        print("   • Responsive design untuk mobile")
        print("   • Icon lokasi pada setiap alamat")
        print("   • Hover effect yang smooth")
    
    return True

if __name__ == "__main__":
    main()
