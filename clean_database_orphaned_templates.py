
#!/usr/bin/env python3
import sqlite3
import os

def clean_orphaned_templates():
    """Hapus template dari database yang file-nya sudah tidak ada"""
    
    template_dir = 'templates/wedding_templates'
    
    # Dapatkan daftar file template yang benar-benar ada
    existing_files = []
    if os.path.exists(template_dir):
        existing_files = [f for f in os.listdir(template_dir) if f.endswith('.html')]
    
    print(f"File template yang ada di {template_dir}:")
    for file in existing_files:
        print(f"  ✓ {file}")
    
    try:
        conn = sqlite3.connect('fajarmandiri.db')
        conn.row_factory = sqlite3.Row
        
        # Ambil semua template dari database
        all_templates = conn.execute('SELECT * FROM wedding_templates ORDER BY name').fetchall()
        
        print(f"\nMemeriksa {len(all_templates)} template di database...")
        
        deleted_count = 0
        orphaned_templates = []
        
        for template in all_templates:
            template_file = template['template_file']
            
            # Cek apakah file ada di direktori
            file_exists = False
            
            # Cek dengan path lengkap atau hanya nama file
            if template_file in existing_files:
                file_exists = True
            elif template_file.startswith('wedding_templates/'):
                filename_only = template_file.replace('wedding_templates/', '')
                if filename_only in existing_files:
                    file_exists = True
            elif template_file.startswith('templates/wedding_templates/'):
                filename_only = template_file.replace('templates/wedding_templates/', '')
                if filename_only in existing_files:
                    file_exists = True
            
            if not file_exists:
                orphaned_templates.append(template)
        
        if orphaned_templates:
            print(f"\nDitemukan {len(orphaned_templates)} template orphaned:")
            for template in orphaned_templates:
                print(f"  - {template['name']} ({template['template_file']})")
            
            # Konfirmasi penghapusan
            print(f"\nMenghapus {len(orphaned_templates)} template orphaned dari database...")
            
            for template in orphaned_templates:
                # Hapus dari database
                conn.execute('DELETE FROM wedding_templates WHERE id = ?', (template['id'],))
                print(f"✓ Deleted: {template['name']} (ID: {template['id']})")
                deleted_count += 1
            
            conn.commit()
            
        else:
            print("\n✅ Tidak ada template orphaned ditemukan!")
        
        # Tampilkan template yang tersisa
        remaining_templates = conn.execute('SELECT * FROM wedding_templates ORDER BY name').fetchall()
        
        print(f"\n{len(remaining_templates)} template tersisa di database:")
        for template in remaining_templates:
            print(f"  ✓ {template['name']} ({template['template_file']})")
        
        # Update undangan yang menggunakan template yang dihapus
        if deleted_count > 0:
            default_template = conn.execute(
                'SELECT id FROM wedding_templates WHERE template_file = ? LIMIT 1',
                ('MandiriTheme_elegant.html',)
            ).fetchone()
            
            if default_template:
                orphaned_invitations = conn.execute('''
                    SELECT COUNT(*) as count FROM wedding_invitations 
                    WHERE template_id NOT IN (SELECT id FROM wedding_templates)
                ''').fetchone()
                
                if orphaned_invitations['count'] > 0:
                    conn.execute('''
                        UPDATE wedding_invitations 
                        SET template_id = ? 
                        WHERE template_id NOT IN (SELECT id FROM wedding_templates)
                    ''', (default_template['id'],))
                    print(f"✓ Updated {orphaned_invitations['count']} orphaned invitations to use default template")
                    conn.commit()
        
        conn.close()
        
        print(f"\n✅ Database berhasil dibersihkan!")
        print(f"✅ {deleted_count} template orphaned telah dihapus!")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    clean_orphaned_templates()
