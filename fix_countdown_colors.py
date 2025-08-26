
#!/usr/bin/env python3
"""
Script untuk memperbaiki warna countdown dan tombol BUKA UNDANGAN
agar sesuai dengan tema pada templates wedding
"""

import os
import re
import time
from datetime import datetime

# Definisi tema dan warna yang sesuai untuk setiap template
THEME_COLORS = {
    'MandiriTheme_Style': {
        'primary': '#D4AF37',
        'secondary': '#2C3E50', 
        'text_light': '#FFFFFF',
        'text_dark': '#2C3E50',
        'bg_overlay': 'rgba(212, 175, 55, 0.1)'
    },
    'MandiriTheme_Style_1': {
        'primary': '#D4AF37',
        'secondary': '#2C3E50',
        'text_light': '#FFFFFF', 
        'text_dark': '#2C3E50',
        'bg_overlay': 'rgba(212, 175, 55, 0.1)'
    },
    'MandiriTheme_Style_2': {
        'primary': '#8B4513',
        'secondary': '#654321',
        'text_light': '#FFFFFF',
        'text_dark': '#8B4513', 
        'bg_overlay': 'rgba(139, 69, 19, 0.1)'
    },
    'MandiriTheme_Style_3': {
        'primary': '#D4AF37',
        'secondary': '#2C3E50',
        'text_light': '#FFFFFF',
        'text_dark': '#2C3E50',
        'bg_overlay': 'rgba(212, 175, 55, 0.1)'
    },
    'MandiriTheme_classic': {
        'primary': '#059669',
        'secondary': '#047857',
        'text_light': '#FFFFFF',
        'text_dark': '#047857',
        'bg_overlay': 'rgba(5, 150, 105, 0.1)'
    },
    'MandiriTheme_elegant': {
        'primary': '#A855F7',
        'secondary': '#7C3AED',
        'text_light': '#FFFFFF',
        'text_dark': '#7C3AED',
        'bg_overlay': 'rgba(168, 85, 247, 0.1)'
    },
    'MandiriTheme_modern': {
        'primary': '#3B82F6',
        'secondary': '#1E40AF',
        'text_light': '#FFFFFF',
        'text_dark': '#1E40AF',
        'bg_overlay': 'rgba(59, 130, 246, 0.1)'
    },
    'classic_romance': {
        'primary': '#DC2626',
        'secondary': '#B91C1C',
        'text_light': '#FFFFFF',
        'text_dark': '#B91C1C',
        'bg_overlay': 'rgba(220, 38, 38, 0.1)'
    },
    'elegant_cream': {
        'primary': '#8B5CF6',
        'secondary': '#7C3AED',
        'text_light': '#FFFFFF',
        'text_dark': '#7C3AED',
        'bg_overlay': 'rgba(139, 92, 246, 0.1)'
    },
    'elegant_golden': {
        'primary': '#F59E0B',
        'secondary': '#D97706',
        'text_light': '#FFFFFF',
        'text_dark': '#D97706',
        'bg_overlay': 'rgba(245, 158, 11, 0.1)'
    },
    'garden_fresh': {
        'primary': '#22C55E',
        'secondary': '#16A34A',
        'text_light': '#FFFFFF',
        'text_dark': '#16A34A',
        'bg_overlay': 'rgba(34, 197, 94, 0.1)'
    },
    'garden_romance': {
        'primary': '#10B981',
        'secondary': '#059669',
        'text_light': '#FFFFFF',
        'text_dark': '#059669',
        'bg_overlay': 'rgba(16, 185, 129, 0.1)'
    },
    'luxury_modern': {
        'primary': '#1F2937',
        'secondary': '#111827',
        'text_light': '#FFFFFF',
        'text_dark': '#1F2937',
        'bg_overlay': 'rgba(31, 41, 55, 0.1)'
    },
    'minimal_blush': {
        'primary': '#F472B6',
        'secondary': '#EC4899',
        'text_light': '#FFFFFF',
        'text_dark': '#EC4899',
        'bg_overlay': 'rgba(244, 114, 182, 0.1)'
    },
    'modern_minimalist': {
        'primary': '#6B7280',
        'secondary': '#4B5563',
        'text_light': '#FFFFFF',
        'text_dark': '#4B5563',
        'bg_overlay': 'rgba(107, 114, 128, 0.1)'
    },
    'ocean_waves': {
        'primary': '#0891B2',
        'secondary': '#0E7490',
        'text_light': '#FFFFFF',
        'text_dark': '#0E7490',
        'bg_overlay': 'rgba(8, 145, 178, 0.1)'
    },
    'royal_burgundy': {
        'primary': '#BE185D',
        'secondary': '#9D174D',
        'text_light': '#FFFFFF',
        'text_dark': '#9D174D',
        'bg_overlay': 'rgba(190, 24, 93, 0.1)'
    },
    'vintage_charm': {
        'primary': '#A3A3A3',
        'secondary': '#737373',
        'text_light': '#FFFFFF',
        'text_dark': '#737373',
        'bg_overlay': 'rgba(163, 163, 163, 0.1)'
    }
}

def backup_file(file_path):
    """Membuat backup file sebelum dimodifikasi"""
    timestamp = str(int(time.time()))
    backup_path = f"{file_path}.backup.countdown.{timestamp}"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as original:
            content = original.read()
        
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(content)
        
        print(f"Backup dibuat: {backup_path}")
        return True
    except Exception as e:
        print(f"Error membuat backup: {e}")
        return False

def fix_countdown_colors(content, theme_name):
    """Memperbaiki warna countdown sesuai tema"""
    colors = THEME_COLORS.get(theme_name, THEME_COLORS['MandiriTheme_Style'])
    
    # Fix countdown section background
    countdown_bg_pattern = r'\.countdown-section\s*{[^}]*background:[^;]*;'
    countdown_bg_replacement = f".countdown-section {{background: {colors['bg_overlay']};"
    content = re.sub(countdown_bg_pattern, countdown_bg_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix countdown number color untuk kontras yang baik
    countdown_number_pattern = r'\.countdown-number\s*{[^}]*color:[^;]*;'
    countdown_number_replacement = f".countdown-number {{color: {colors['text_dark']};"
    content = re.sub(countdown_number_pattern, countdown_number_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix countdown label color
    countdown_label_pattern = r'\.countdown-label\s*{[^}]*color:[^;]*;'
    countdown_label_replacement = f".countdown-label {{color: {colors['secondary']};"
    content = re.sub(countdown_label_pattern, countdown_label_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix countdown item background untuk readability
    countdown_item_pattern = r'\.countdown-item\s*{[^}]*background:[^;]*;'
    countdown_item_replacement = f".countdown-item {{background: rgba(255,255,255,0.9);"
    content = re.sub(countdown_item_pattern, countdown_item_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix tombol BUKA UNDANGAN - background sesuai tema
    btn_pattern = r'\.open-invitation-btn\s*{[^}]*background:[^;]*;'
    btn_replacement = f".open-invitation-btn {{background: {colors['primary']};"
    content = re.sub(btn_pattern, btn_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix tombol BUKA UNDANGAN - text color untuk kontras
    btn_color_pattern = r'(\.open-invitation-btn\s*{[^}]*color:)[^;]*;'
    btn_color_replacement = f"\\1 {colors['text_light']};"
    content = re.sub(btn_color_pattern, btn_color_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Fix hover state tombol
    btn_hover_pattern = r'\.open-invitation-btn:hover\s*{[^}]*background:[^;]*;'
    btn_hover_replacement = f".open-invitation-btn:hover {{background: {colors['secondary']};"
    content = re.sub(btn_hover_pattern, btn_hover_replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    return content

def process_template(file_path):
    """Memproses satu template file"""
    try:
        # Baca file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Dapatkan nama tema dari nama file
        theme_name = os.path.basename(file_path).replace('.html', '')
        
        print(f"=== Memproses {theme_name} ===")
        
        # Cek apakah tema ada dalam definisi warna
        if theme_name not in THEME_COLORS:
            print(f"⚠️  Tema {theme_name} tidak ditemukan dalam definisi warna, menggunakan default")
            theme_name = 'MandiriTheme_Style'
        
        colors = THEME_COLORS[theme_name]
        print(f"Primary: {colors['primary']}")
        print(f"Secondary: {colors['secondary']}")
        print(f"Text Dark: {colors['text_dark']}")
        
        # Backup file
        if not backup_file(file_path):
            print(f"❌ Gagal membuat backup untuk {theme_name}")
            return False
        
        # Fix warna countdown dan tombol
        updated_content = fix_countdown_colors(content, theme_name)
        
        # Tulis kembali file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        print(f"✓ Template {theme_name} berhasil diupdate!")
        return True
        
    except Exception as e:
        print(f"❌ Error memproses {file_path}: {e}")
        return False

def main():
    """Fungsi utama"""
    print("🎨 Wedding Template Countdown Color Fixer")
    print("Memperbaiki warna countdown dan tombol pada semua template")
    print("=" * 60)
    
    templates_dir = "templates/wedding_templates"
    
    if not os.path.exists(templates_dir):
        print(f"❌ Directory {templates_dir} tidak ditemukan!")
        return
    
    # Cari semua file HTML template
    template_files = []
    for file in os.listdir(templates_dir):
        if file.endswith('.html') and not file.endswith('.backup'):
            template_files.append(os.path.join(templates_dir, file))
    
    if not template_files:
        print(f"❌ Tidak ada file template ditemukan di {templates_dir}")
        return
    
    print(f"📁 Ditemukan {len(template_files)} template(s)")
    print()
    
    success_count = 0
    
    for template_file in sorted(template_files):
        if process_template(template_file):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"🎉 Selesai! {success_count}/{len(template_files)} template berhasil diupdate")
    print()
    print("✅ Perubahan yang diterapkan:")
    print("  - Countdown background dengan opacity tema")
    print("  - Countdown number dengan warna tema gelap")
    print("  - Countdown label dengan warna secondary")
    print("  - Countdown item background putih semi-transparan")
    print("  - Tombol 'BUKA UNDANGAN' dengan warna tema")
    print("  - Text tombol dengan kontras yang baik")
    print("  - Hover state tombol dengan warna secondary")
    print()
    print("💡 Tip: Refresh browser untuk melihat perubahan")

if __name__ == "__main__":
    main()
