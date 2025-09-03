
import sqlite3
import json
import os

def setup_demo_data():
    """Setup demo wedding invitation with new names and demo photos"""
    
    # Connect to database
    conn = sqlite3.connect('fajarmandiri.db')
    cursor = conn.cursor()
    
    # Demo prewedding photos data
    demo_photos = [
        {"filename": "demo_prewedding_1.jpg", "orientation": "portrait"},
        {"filename": "demo_prewedding_2.jpg", "orientation": "portrait"},
        {"filename": "demo_prewedding_3.jpg", "orientation": "landscape"},
        {"filename": "demo_prewedding_4.jpg", "orientation": "landscape"}
    ]
    
    # Check if demo invitation already exists
    existing = cursor.execute(
        "SELECT id FROM wedding_invitations WHERE invitation_link = ?",
        ("syaidatu-andika-demo",)
    ).fetchone()
    
    if existing:
        # Update existing demo data
        cursor.execute("""
            UPDATE wedding_invitations SET
                couple_name = ?,
                bride_name = ?,
                bride_father = ?,
                bride_mother = ?,
                groom_name = ?,
                groom_father = ?,
                groom_mother = ?,
                prewedding_photos = ?
            WHERE invitation_link = ?
        """, (
            "Nimah & Andika",
            "Nimah Syaidatu",
            "Ummi",
            "Abi", 
            "Andika Papanjangana",
            "Abah",
            "Ambu",
            json.dumps(demo_photos),
            "syaidatu-andika-demo"
        ))
        print(" Updated existing demo invitation")
    else:
        # Create new demo invitation
        cursor.execute("""
            INSERT INTO wedding_invitations (
                user_id, couple_name, bride_name, bride_father, bride_mother,
                groom_name, groom_father, groom_mother, wedding_date, wedding_time,
                venue_name, venue_address, template_id, invitation_link,
                prewedding_photos, guest_limit, custom_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            1,  # user_id
            "Syaidatu & Andika",
            "Syaidatu",
            "Ummi", 
            "Abi",
            "Andika",
            "Abah",
            "Ambu",
            "2027-12-25",
            "14:00",
            "Masjid Agung",
            "Jl. Raya Utama No. 123, Kota",
            1,  # template_id
            "syaidatu-andika-demo",
            json.dumps(demo_photos),
            200,
            "Dengan penuh kebahagiaan, kami mengundang Anda untuk hadir dalam pernikahan kami"
        ))
        print(" Created new demo invitation")
    
    conn.commit()
    conn.close()
    print(" Demo data setup completed!")

if __name__ == "__main__":
    setup_demo_data()
