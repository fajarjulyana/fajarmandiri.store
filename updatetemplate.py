import sqlite3
from datetime import datetime

DB_PATH = "fajarmandiri.db"

# Daftar semua template
all_templates = [
    ("MandiriTheme Elegant", "MandiriTheme_elegant.html"),
    ("Emerald Gold", "emerald_gold.html"),
    ("Modern Minimalist", "modern_minimalist.html"),
    ("Burgundy Gold", "burgundy_gold.html"),
    ("Garden Romance", "garden_romance.html"),
    ("Royal Blue Gold", "royal_blue_gold.html"),
    ("Elegant Cream", "elegant_cream.html"),
]

def get_color_scheme(name: str) -> str:
    """Deteksi color scheme dari nama template"""
    name_lower = name.lower()
    if "gold" in name_lower:
        return "Gold"
    elif "burgundy" in name_lower:
        return "Burgundy"
    elif "emerald" in name_lower:
        return "Emerald"
    elif "blue" in name_lower:
        return "Royal Blue"
    elif "cream" in name_lower:
        return "Cream"
    elif "minimalist" in name_lower:
        return "Minimalist"
    elif "romance" in name_lower:
        return "Romance"
    elif "elegant" in name_lower:
        return "Elegant"
    return "Custom"

def reset_wedding_templates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Hapus semua data lama
    cursor.execute("DELETE FROM wedding_templates")

    # Siapkan data baru
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_to_insert = []
    for name, filename in all_templates:
        premium = 1 if ("gold" in filename.lower() or "luxury" in filename.lower()) else 0
        price = 500000 if premium else 0
        category = "Premium" if premium else "Standard"
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
    print(" Semua template berhasil diperbarui ke database!")

if __name__ == "__main__":
    reset_wedding_templates()
