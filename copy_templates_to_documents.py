
import os
import shutil
from pathlib import Path
import sqlite3

def copy_all_to_documents():
    """Copy database, templates, music, dan semua assets ke Documents folder"""
    
    # Path ke Documents
    user_docs = os.path.join(os.path.expanduser("~"), "Documents", "FajarMandiriStore")
    
    # Buat folder utama
    os.makedirs(user_docs, exist_ok=True)
    
    # Buat subfolder yang diperlukan
    folders = [
        "wedding_templates",
        "cv_templates", 
        "music",
        "prewedding_photos",
        "thumbnails",
        "thumbnails/wedding_templates",
        "thumbnails/cv_templates",
        "js"
    ]
    
    for folder in folders:
        os.makedirs(os.path.join(user_docs, folder), exist_ok=True)
        print(f" Created folder: {folder}")
    
    copied_files = []
    
    # 1. Copy database
    if os.path.exists("fajarmandiri.db"):
        dest_db = os.path.join(user_docs, "fajarmandiri.db")
        shutil.copy2("fajarmandiri.db", dest_db)
        copied_files.append("Database: fajarmandiri.db")
        print(" Copied database to Documents")
    
    # 2. Copy wedding templates
    if os.path.exists("templates/wedding_templates"):
        dest_wedding = os.path.join(user_docs, "wedding_templates")
        for filename in os.listdir("templates/wedding_templates"):
            if filename.endswith('.html'):
                source_file = os.path.join("templates/wedding_templates", filename)
                dest_file = os.path.join(dest_wedding, filename)
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(f"Wedding Template: {filename}")
                    print(f" Copied wedding template: {filename}")
                except Exception as e:
                    print(f" Failed to copy {filename}: {str(e)}")
    
    # 3. Copy CV templates jika ada
    if os.path.exists("cv_templates"):
        dest_cv = os.path.join(user_docs, "cv_templates")
        for filename in os.listdir("cv_templates"):
            if filename.endswith('.html'):
                source_file = os.path.join("cv_templates", filename)
                dest_file = os.path.join(dest_cv, filename)
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(f"CV Template: {filename}")
                    print(f" Copied CV template: {filename}")
                except Exception as e:
                    print(f" Failed to copy {filename}: {str(e)}")
    
    # 4. Copy existing thumbnails
    if os.path.exists("static/images/wedding_templates"):
        dest_thumbs = os.path.join(user_docs, "thumbnails/wedding_templates")
        for filename in os.listdir("static/images/wedding_templates"):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                source_file = os.path.join("static/images/wedding_templates", filename)
                dest_file = os.path.join(dest_thumbs, filename)
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(f"Wedding Thumbnail: {filename}")
                    print(f" Copied wedding thumbnail: {filename}")
                except Exception as e:
                    print(f" Failed to copy thumbnail {filename}: {str(e)}")
    
    if os.path.exists("static/images/templates"):
        dest_cv_thumbs = os.path.join(user_docs, "thumbnails/cv_templates")
        for filename in os.listdir("static/images/templates"):
            if filename.endswith(('.jpg', '.jpeg', '.png')):
                source_file = os.path.join("static/images/templates", filename)
                dest_file = os.path.join(dest_cv_thumbs, filename)
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(f"CV Thumbnail: {filename}")
                    print(f" Copied CV thumbnail: {filename}")
                except Exception as e:
                    print(f" Failed to copy CV thumbnail {filename}: {str(e)}")
    
    # 5. Copy JS files
    if os.path.exists("static/js/gallery-sort.js"):
        dest_js = os.path.join(user_docs, "js", "gallery-sort.js")
        shutil.copy2("static/js/gallery-sort.js", dest_js)
        copied_files.append("JS: gallery-sort.js")
        print(" Copied gallery-sort.js")
    
    # 6. Create default music files
    default_music_path = os.path.join(user_docs, "music", "default.mp3")
    default_wedding_music_path = os.path.join(user_docs, "music", "default_wedding.mp3")
    
    if not os.path.exists(default_music_path):
        with open(default_music_path, 'wb') as f:
            f.write(b'')
        copied_files.append("Default music placeholder")
        print(" Created default.mp3 placeholder")
    
    if not os.path.exists(default_wedding_music_path):
        with open(default_wedding_music_path, 'wb') as f:
            f.write(b'')
        copied_files.append("Default wedding music placeholder")
        print(" Created default_wedding.mp3 placeholder")
    
    print(f"\n Total {len(copied_files)} files copied to Documents!")
    print(f" Main folder: {user_docs}")
    
    return copied_files

if __name__ == "__main__":
    copy_all_to_documents()
