
import sqlite3
import os
from datetime import datetime

def backup_database():
    """Backup database before modification"""
    if not os.path.exists('fajarmandiri.db'):
        print("❌ Database fajarmandiri.db tidak ditemukan!")
        return False
    
    timestamp = str(int(datetime.now().timestamp()))
    backup_path = f"fajarmandiri_backup_multi_venue_{timestamp}.db"
    
    import shutil
    shutil.copy('fajarmandiri.db', backup_path)
    print(f"✅ Database backup created: {backup_path}")
    return True

def update_wedding_invitations_table():
    """Add new columns for multiple venues"""
    try:
        conn = sqlite3.connect('fajarmandiri.db')
        cursor = conn.cursor()
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(wedding_invitations)")
        columns = [column[1] for column in cursor.fetchall()]
        
        new_columns = [
            # Akad Nikah
            ('akad_date', 'DATE'),
            ('akad_time', 'TEXT'),
            ('akad_venue_name', 'TEXT'),
            ('akad_venue_address', 'TEXT'),
            
            # Resepsi
            ('resepsi_date', 'DATE'),
            ('resepsi_time', 'TEXT'),
            ('resepsi_venue_name', 'TEXT'),
            ('resepsi_venue_address', 'TEXT'),
            
            # Bride's separate event
            ('bride_event_date', 'DATE'),
            ('bride_event_time', 'TEXT'),
            ('bride_event_venue_name', 'TEXT'),
            ('bride_event_venue_address', 'TEXT'),
            
            # Groom's separate event
            ('groom_event_date', 'DATE'),
            ('groom_event_time', 'TEXT'),
            ('groom_event_venue_name', 'TEXT'),
            ('groom_event_venue_address', 'TEXT'),
        ]
        
        added_columns = []
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f"ALTER TABLE wedding_invitations ADD COLUMN {column_name} {column_type}")
                    added_columns.append(column_name)
                    print(f"✅ Added column: {column_name}")
                except sqlite3.OperationalError as e:
                    print(f"⚠️  Column {column_name} might already exist: {e}")
        
        conn.commit()
        conn.close()
        
        if added_columns:
            print(f"\n✅ Successfully added {len(added_columns)} new columns to wedding_invitations table")
            return True
        else:
            print("ℹ️  All columns already exist in the database")
            return True
            
    except Exception as e:
        print(f"❌ Error updating database schema: {str(e)}")
        return False

def migrate_existing_data():
    """Migrate existing single venue data to new multiple venue structure"""
    try:
        conn = sqlite3.connect('fajarmandiri.db')
        cursor = conn.cursor()
        
        # Get all existing invitations
        cursor.execute('''
            SELECT id, wedding_date, wedding_time, venue_name, venue_address
            FROM wedding_invitations
            WHERE (akad_date IS NULL OR resepsi_date IS NULL)
            AND (wedding_date IS NOT NULL OR venue_address IS NOT NULL)
        ''')
        
        invitations = cursor.fetchall()
        
        if not invitations:
            print("ℹ️  No data migration needed")
            return True
        
        print(f"📋 Migrating {len(invitations)} existing invitations...")
        
        for invitation in invitations:
            inv_id, wedding_date, wedding_time, venue_name, venue_address = invitation
            
            # Set akad and resepsi to same date/venue by default
            cursor.execute('''
                UPDATE wedding_invitations SET
                    akad_date = ?,
                    akad_time = ?,
                    akad_venue_name = ?,
                    akad_venue_address = ?,
                    resepsi_date = ?,
                    resepsi_time = ?,
                    resepsi_venue_name = ?,
                    resepsi_venue_address = ?
                WHERE id = ?
            ''', (
                wedding_date, wedding_time, venue_name, venue_address,  # Akad
                wedding_date, wedding_time, venue_name, venue_address,  # Resepsi
                inv_id
            ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Successfully migrated {len(invitations)} invitations")
        return True
        
    except Exception as e:
        print(f"❌ Error migrating data: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Starting database schema update for multiple venues...")
    
    # Backup database
    if not backup_database():
        return
    
    # Update schema
    if not update_wedding_invitations_table():
        print("❌ Failed to update database schema")
        return
    
    # Migrate existing data
    if not migrate_existing_data():
        print("❌ Failed to migrate existing data")
        return
    
    print("\n✨ Database update completed successfully!")
    print("\n📝 New database fields available:")
    print("   🔹 Akad Nikah: akad_date, akad_time, akad_venue_name, akad_venue_address")
    print("   🔹 Resepsi: resepsi_date, resepsi_time, resepsi_venue_name, resepsi_venue_address")
    print("   🔹 Bride Event: bride_event_date, bride_event_time, bride_event_venue_name, bride_event_venue_address")
    print("   🔹 Groom Event: groom_event_date, groom_event_time, groom_event_venue_name, groom_event_venue_address")
    
    print("\n💡 Next steps:")
    print("   1. Run update_wedding_templates.py to update all template files")
    print("   2. Update create_wedding_invitation.html form to include new fields")
    print("   3. Test the new multiple venue functionality")

if __name__ == "__main__":
    main()
