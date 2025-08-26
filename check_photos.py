
import sqlite3
import json

def check_photo_data():
    """Check existing photo data in database"""
    conn = sqlite3.connect('fajarmandiri.db')
    conn.row_factory = sqlite3.Row
    
    invitations = conn.execute('''
        SELECT id, couple_name, prewedding_photos 
        FROM wedding_invitations 
        WHERE prewedding_photos IS NOT NULL AND prewedding_photos != ""
    ''').fetchall()
    
    print(f"Found {len(invitations)} invitations with photos:")
    
    for inv in invitations:
        try:
            photos = json.loads(inv['prewedding_photos'])
            print(f"\n{inv['couple_name']} (ID: {inv['id']}):")
            print(f"  Total photos: {len(photos)}")
            
            for i, photo in enumerate(photos):
                if isinstance(photo, dict):
                    filename = photo.get('filename', 'N/A')
                    orientation = photo.get('orientation', 'N/A')
                    print(f"    {i+1}. {filename} - {orientation}")
                else:
                    print(f"    {i+1}. {photo} - OLD FORMAT")
                    
        except Exception as e:
            print(f"  Error parsing photos: {str(e)}")
    
    conn.close()

if __name__ == "__main__":
    check_photo_data()
