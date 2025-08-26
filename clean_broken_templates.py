
#!/usr/bin/env python3
import sqlite3
import os

def clean_broken_templates():
    """Hapus template yang rusak dari database"""
    
    # Template yang akan dihapus (yang error)
    broken_templates = [
        'classic_romance.html',
        'elegant_golden.html', 
        'garden_fresh.html',
        'luxury_modern.html',
        'MandiriTheme_classic.html',
        'MandiriTheme_modern.html',
        'MandiriTheme_Style.html',
        'MandiriTheme_Style_1.html',
        'MandiriTheme_Style_2.html', 
        'MandiriTheme_Style_3.html',
        'minimal_blush.html',
        'ocean_waves.html',
        'royal_burgundy.html',
        'vintage_charm.html'
    ]
    
    try:
        conn = sqlite3.connect('fajarmandiri.db')
        conn.row_factory = sqlite3.Row
        
        # Hapus template dari database berdasarkan template_file
        for template_file in broken_templates:
            result = conn.execute('DELETE FROM wedding_templates WHERE template_file = ?', (template_file,))
            if result.rowcount > 0:
                print(f"✓ Deleted {template_file} from database")
            else:
                print(f"- {template_file} not found in database")
        
        conn.commit()
        
        # Tampilkan template yang tersisa
        remaining = conn.execute('SELECT * FROM wedding_templates ORDER BY name').fetchall()
        print(f"\n{len(remaining)} template tersisa:")
        for template in remaining:
            print(f"  - {template['name']} ({template['template_file']})")
        
        conn.close()
        print("\nDatabase berhasil dibersihkan!")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    clean_broken_templates()
