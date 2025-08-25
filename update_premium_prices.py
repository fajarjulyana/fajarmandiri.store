
import sqlite3

def update_premium_prices():
    conn = sqlite3.connect('fajarmandiri.db')
    c = conn.cursor()
    
    # List template premium dengan harga 35,000
    premium_templates = [
        'Elegant Golden',
        'Royal Burgundy', 
        'Ocean Waves',
        'MandiriTheme Style 2',
        'Garden Fresh',
        'Luxury Modern',
        'MandiriTheme Style 1'
    ]
    
    for template_name in premium_templates:
        c.execute('''UPDATE wedding_templates 
                     SET is_premium = 1, price = 35000.00 
                     WHERE name = ?''', (template_name,))
        print(f"Updated {template_name} to premium (35,000 IDR)")
    
    conn.commit()
    
    # Verify updates
    c.execute('SELECT name, is_premium, price FROM wedding_templates WHERE is_premium = 1')
    premium_templates_db = c.fetchall()
    
    print("\nCurrent premium templates:")
    for template in premium_templates_db:
        print(f"- {template[0]}: {template[2]:,.0f} IDR")
    
    conn.close()
    print("\nPremium template prices updated successfully!")

if __name__ == "__main__":
    update_premium_prices()
