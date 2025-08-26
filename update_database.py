
#!/usr/bin/env python3
import sqlite3
import os

def update_database():
    """Update database untuk menghapus template yang rusak dan menjaga yang baik"""
    
    # Template yang akan dihapus (yang masih error)
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
    
    # Template yang berfungsi dengan baik
    working_templates = [
        'MandiriTheme_elegant.html',
        'elegant_cream.html',
        'garden_romance.html',
        'modern_minimalist.html'
    ]
    
    try:
        conn = sqlite3.connect('fajarmandiri.db')
        conn.row_factory = sqlite3.Row
        
        print("Membersihkan database dari template yang rusak...")
        
        # 1. Hapus template yang rusak dari database
        for template_file in broken_templates:
            result = conn.execute('DELETE FROM wedding_templates WHERE template_file = ?', (template_file,))
            if result.rowcount > 0:
                print(f"✓ Deleted {template_file} from database")
        
        # 2. Update template yang berfungsi dengan informasi lengkap
        template_updates = {
            'MandiriTheme_elegant.html': {
                'name': 'Mandiri Theme Elegant',
                'description': 'Template elegan dengan desain modern dan responsif',
                'category': 'elegant',
                'color_scheme': 'gold',
                'animations': 'fade-in,slide-up',
                'ornaments': 'floral,border',
                'is_premium': 0,
                'price': 0
            },
            'elegant_cream.html': {
                'name': 'Elegant Cream',
                'description': 'Template dengan nuansa cream dan emas yang elegan',
                'category': 'elegant',
                'color_scheme': 'cream',
                'animations': 'fade-in,zoom-in',
                'ornaments': 'classic,border',
                'is_premium': 0,
                'price': 0
            },
            'garden_romance.html': {
                'name': 'Garden Romance',
                'description': 'Template romantis dengan tema taman dan bunga',
                'category': 'romantic',
                'color_scheme': 'green',
                'animations': 'slide-up,fade-in',
                'ornaments': 'floral,nature',
                'is_premium': 0,
                'price': 0
            },
            'modern_minimalist.html': {
                'name': 'Modern Minimalist',
                'description': 'Template minimalis modern dengan desain bersih',
                'category': 'modern',
                'color_scheme': 'blue',
                'animations': 'slide-in,fade',
                'ornaments': 'minimal,geometric',
                'is_premium': 0,
                'price': 0
            }
        }
        
        # 3. Update atau insert template yang berfungsi
        for template_file, details in template_updates.items():
            # Cek apakah template sudah ada
            existing = conn.execute('SELECT id FROM wedding_templates WHERE template_file = ?', (template_file,)).fetchone()
            
            if existing:
                # Update template yang sudah ada
                conn.execute('''
                    UPDATE wedding_templates 
                    SET name = ?, description = ?, category = ?, color_scheme = ?, 
                        animations = ?, ornaments = ?, is_premium = ?, price = ?
                    WHERE template_file = ?
                ''', (details['name'], details['description'], details['category'], 
                     details['color_scheme'], details['animations'], details['ornaments'],
                     details['is_premium'], details['price'], template_file))
                print(f"✓ Updated {template_file}")
            else:
                # Insert template baru
                conn.execute('''
                    INSERT INTO wedding_templates 
                    (name, description, category, template_file, color_scheme, animations, 
                     ornaments, is_premium, price, preview_image)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (details['name'], details['description'], details['category'], template_file,
                     details['color_scheme'], details['animations'], details['ornaments'],
                     details['is_premium'], details['price'], ''))
                print(f"✓ Inserted {template_file}")
        
        # 4. Update undangan yang menggunakan template yang dihapus ke template default
        default_template_id = conn.execute(
            'SELECT id FROM wedding_templates WHERE template_file = ? LIMIT 1', 
            ('MandiriTheme_elegant.html',)
        ).fetchone()
        
        if default_template_id:
            # Update undangan yang menggunakan template yang dihapus
            for template_file in broken_templates:
                broken_template = conn.execute(
                    'SELECT id FROM wedding_templates WHERE template_file = ?', 
                    (template_file,)
                ).fetchone()
                
                if broken_template:
                    updated_invitations = conn.execute('''
                        UPDATE wedding_invitations 
                        SET template_id = ? 
                        WHERE template_id = ?
                    ''', (default_template_id['id'], broken_template['id']))
                    
                    if updated_invitations.rowcount > 0:
                        print(f"✓ Updated {updated_invitations.rowcount} invitations using {template_file}")
        
        conn.commit()
        
        # 5. Tampilkan template yang tersisa
        remaining = conn.execute('SELECT * FROM wedding_templates ORDER BY name').fetchall()
        print(f"\n{len(remaining)} template tersisa di database:")
        for template in remaining:
            print(f"  - {template['name']} ({template['template_file']}) - {template['category']}")
        
        # 6. Tampilkan statistik undangan
        total_invitations = conn.execute('SELECT COUNT(*) FROM wedding_invitations').fetchone()[0]
        print(f"\nTotal undangan dalam database: {total_invitations}")
        
        # 7. Bersihkan file template yang rusak dari folder
        template_dir = 'templates/wedding_templates'
        if os.path.exists(template_dir):
            for template_file in broken_templates:
                file_path = os.path.join(template_dir, template_file)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    print(f"✓ Removed file {template_file}")
        
        conn.close()
        print("\n✅ Database berhasil diperbarui!")
        print("✅ File template yang rusak telah dihapus!")
        print("✅ Template yang berfungsi telah diperbarui!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    update_database()
