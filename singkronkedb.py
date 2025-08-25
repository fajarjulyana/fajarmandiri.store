import os
import sqlite3

DB_PATH = "fajarmandiri.db"   # sesuaikan dengan lokasi database kamu
TEMPLATE_FOLDER = os.path.join("templates", "wedding_templates")

def sync_templates_with_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if not os.path.exists(TEMPLATE_FOLDER):
        print(f" Folder {TEMPLATE_FOLDER} tidak ditemukan.")
        return

    files = [f for f in os.listdir(TEMPLATE_FOLDER) if f.endswith(".html")]

    for f in files:
        # cek apakah sudah ada di DB
        c.execute("SELECT COUNT(*) FROM wedding_templates WHERE template_file = ?", 
                  (f"wedding_templates/{f}",))
        exists = c.fetchone()[0]

        if exists == 0:
            # Nama template lebih rapi
            base_name = os.path.splitext(f)[0]
            name = base_name.replace("_", " ").replace("-", " ").title()
            desc = f"Template otomatis dari file {f}"
            thumbnail = f.replace(".html", "_thumbnail.jpg")

            # Auto background music & ornaments
            background_music = base_name + ".mp3"
            ornaments = base_name + "_ornaments"

            # Insert default data
            c.execute("""
                INSERT INTO wedding_templates
                (name, description, category, template_file, preview_image,
                 color_scheme, animations, background_music, ornaments,
                 is_premium, price)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, desc, "custom", f"wedding_templates/{f}", thumbnail,
                "default", "fadeIn", background_music, ornaments, 0, 0
            ))
            print(f" Ditambahkan ke database: {f} -> {thumbnail}, musik={background_music}, ornamen={ornaments}")

    conn.commit()
    conn.close()
    print(" Sinkronisasi selesai!")

if __name__ == "__main__":
    sync_templates_with_db()
