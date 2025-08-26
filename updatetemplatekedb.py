import sqlite3
from datetime import datetime

DB_PATH = "fajarmandiri.db"

# Hanya 4 template sekarang
all_templates = [
    ("Black Luxury Gold", "black_luxury_gold.html"),
    ("Blue Luxury Gold", "blue_luxury_gold.html"),
    ("Red Luxury Gold", "red_luxury_gold.html"),
    ("Elegant Cream", "elegant_cream.html"),
]

def get_color_scheme(name: str) -> str:
    """Deteksi color scheme dari nama template"""
    name_lower = name.lower()
    if "black" in name_lower:
        return "Black Gold"
    elif "blue" in name_lower:
        return "Blue Gold"
    elif "red" in name_lower:
        return "Red Gold"
    elif "cream" in name_lower:
        return "Cream"
    return "Custom"

def reset_wedding_templates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hapus semua data lama
    cursor.execute("DELETE FROM wedding_templates")

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_to_insert = []

    for name, filename in all_templates:
        if filename == "elegant_cream.html":
            premium = 0
            price = 0
            category = "Gratis"
        else:
            premium = 1
            price = 35000
            category = "Premium"

        color_scheme = get_color_scheme(name)
        preview_image = f"images/previews/{filename.replace('.html', '.jpg')}"

        data_to_insert.append((
            name,                                  # name
            f"Template pernikahan {name}.",        # description
            category,                              # category
            filename,                              # template_file
            preview_image,                         # preview_image
            color_scheme,                          # color_scheme
            "default",                             # animations
            "default.mp3",                         # background_music
            "default",                             # ornaments
            premium,                               # is_premium
            price,                                 # price
            now                                    # created_at
        ))

    query = """
    INSERT INTO wedding_templates 
    (name, description, category, template_file, preview_image, 
     color_scheme, animations, background_music, ornaments, 
     is_premium, price, created_at) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    cursor.executemany(query, data_to_insert)

    conn.commit()
    conn.close()
    print("Semua template (4) berhasil diperbarui ke database!")

if __name__ == "__main__":
    reset_wedding_templates()
