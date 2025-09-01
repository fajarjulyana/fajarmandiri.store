
import os
import shutil
from pathlib import Path

def copy_templates_to_documents():
    """Copy all templates from app folder to Documents folder"""
    
    # Path ke Documents
    user_docs = os.path.join(os.path.expanduser("~"), "Documents", "FajarMandiriStore")
    
    # Source dan destination paths
    source_wedding = "templates/wedding_templates"
    dest_wedding = os.path.join(user_docs, "wedding_templates")
    
    source_cv = "cv_templates"  
    dest_cv = os.path.join(user_docs, "cv_templates")
    
    # Buat folder tujuan
    os.makedirs(dest_wedding, exist_ok=True)
    os.makedirs(dest_cv, exist_ok=True)
    
    # Buat folder tambahan untuk assets wedding
    js_folder = os.path.join(user_docs, "js")
    music_folder = os.path.join(user_docs, "music")
    os.makedirs(js_folder, exist_ok=True)
    os.makedirs(music_folder, exist_ok=True)
    
    # Copy file JS jika ada
    if os.path.exists("static/js/gallery-sort.js"):
        shutil.copy2("static/js/gallery-sort.js", os.path.join(js_folder, "gallery-sort.js"))
        print(" Copied gallery-sort.js to Documents")
    
    # Buat file musik default jika belum ada
    default_music_path = os.path.join(music_folder, "default.mp3")
    default_wedding_music_path = os.path.join(music_folder, "default_wedding.mp3")
    
    if not os.path.exists(default_music_path):
        # Buat file placeholder
        with open(default_music_path, 'wb') as f:
            f.write(b'')  # File kosong sebagai placeholder
        print(" Created default.mp3 placeholder")
    
    if not os.path.exists(default_wedding_music_path):
        with open(default_wedding_music_path, 'wb') as f:
            f.write(b'')  # File kosong sebagai placeholder  
        print(" Created default_wedding.mp3 placeholder")
    
    copied_files = []
    
    # Copy wedding templates
    if os.path.exists(source_wedding):
        for filename in os.listdir(source_wedding):
            if filename.endswith('.html'):
                source_file = os.path.join(source_wedding, filename)
                dest_file = os.path.join(dest_wedding, filename)
                
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(f"Wedding: {filename}")
                    print(f" Copied wedding template: {filename}")
                except Exception as e:
                    print(f" Failed to copy {filename}: {str(e)}")
    
    # Copy CV templates jika ada
    if os.path.exists(source_cv):
        for filename in os.listdir(source_cv):
            if filename.endswith('.html'):
                source_file = os.path.join(source_cv, filename)
                dest_file = os.path.join(dest_cv, filename)
                
                try:
                    shutil.copy2(source_file, dest_file)
                    copied_files.append(f"CV: {filename}")
                    print(f" Copied CV template: {filename}")
                except Exception as e:
                    print(f" Failed to copy {filename}: {str(e)}")
    
    print(f"\n Total {len(copied_files)} template files copied to Documents!")
    print(f" Wedding templates: {dest_wedding}")
    print(f" CV templates: {dest_cv}")
    
    return copied_files

if __name__ == "__main__":
    copy_templates_to_documents()
