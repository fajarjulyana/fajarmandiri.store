
#!/usr/bin/env python3
import sqlite3
import os
import json

def clean_templates_and_fix_gallery():
    """Hapus semua template kecuali elegant_cream.html dan perbaiki masalah galeri"""
    
    # Connect to database
    conn = sqlite3.connect('fajarmandiri.db')
    conn.row_factory = sqlite3.Row
    
    print("🧹 Membersihkan template wedding...")
    
    # 1. Hapus semua template kecuali elegant_cream.html dari database
    templates_to_keep = ['elegant_cream.html']
    
    # Get all current templates
    all_templates = conn.execute('SELECT * FROM wedding_templates').fetchall()
    
    print(f"📋 Ditemukan {len(all_templates)} template di database")
    
    deleted_count = 0
    for template in all_templates:
        if template['template_file'] not in templates_to_keep:
            conn.execute('DELETE FROM wedding_templates WHERE id = ?', (template['id'],))
            print(f"✓ Deleted: {template['name']} ({template['template_file']})")
            deleted_count += 1
    
    # 2. Update elegant_cream.html template info
    conn.execute('''
        UPDATE wedding_templates 
        SET name = ?, description = ?, category = ?, is_premium = ?, price = ?
        WHERE template_file = ?
    ''', (
        'Elegant Cream - Premium',
        'Template pernikahan elegan dengan tema cream dan gold yang mewah',
        'Premium',
        0,  # Set sebagai free template
        0,  # Free
        'elegant_cream.html'
    ))
    
    conn.commit()
    
    # 3. Periksa template yang tersisa
    remaining_templates = conn.execute('SELECT * FROM wedding_templates').fetchall()
    print(f"\n✅ {len(remaining_templates)} template tersisa:")
    for template in remaining_templates:
        print(f"  - {template['name']} ({template['template_file']})")
    
    # 4. Cek dan perbaiki masalah galeri foto
    print("\n🖼️ Memeriksa masalah galeri foto...")
    
    # Get invitations with prewedding photos
    invitations_with_photos = conn.execute('''
        SELECT id, couple_name, prewedding_photos 
        FROM wedding_invitations 
        WHERE prewedding_photos IS NOT NULL AND prewedding_photos != ""
    ''').fetchall()
    
    if invitations_with_photos:
        print(f"📸 Ditemukan {len(invitations_with_photos)} undangan dengan foto prewedding:")
        
        for invitation in invitations_with_photos:
            try:
                photos_data = json.loads(invitation['prewedding_photos'])
                print(f"  - {invitation['couple_name']}: {len(photos_data)} foto")
                
                # Debug info untuk galeri
                for i, photo in enumerate(photos_data):
                    if isinstance(photo, dict):
                        filename = photo.get('filename', 'unknown')
                        orientation = photo.get('orientation', 'unknown')
                        print(f"    {i+1}. {filename} ({orientation})")
                    else:
                        print(f"    {i+1}. {photo} (format lama)")
                        
            except Exception as e:
                print(f"  - {invitation['couple_name']}: Error parsing photos - {str(e)}")
    else:
        print("📸 Tidak ada undangan dengan foto prewedding ditemukan")
    
    # 5. Bersihkan thumbnail files lama
    thumbnail_dir = 'static/images/wedding_templates'
    if os.path.exists(thumbnail_dir):
        thumbnail_files = [f for f in os.listdir(thumbnail_dir) if f.endswith('.jpg')]
        print(f"\n🖼️ Membersihkan {len(thumbnail_files)} thumbnail files lama...")
        
        for thumbnail in thumbnail_files:
            try:
                os.remove(os.path.join(thumbnail_dir, thumbnail))
                print(f"✓ Deleted thumbnail: {thumbnail}")
            except Exception as e:
                print(f"✗ Error deleting {thumbnail}: {str(e)}")
    
    conn.close()
    print(f"\n🎉 Selesai! Dihapus {deleted_count} template, tersisa hanya elegant_cream.html")
    print("💡 Silakan generate thumbnail baru untuk template yang tersisa melalui admin panel")

if __name__ == "__main__":
    clean_templates_and_fix_gallery()
