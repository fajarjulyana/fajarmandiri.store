
import sqlite3
import os

def fix_template_paths():
    """Fix template file paths in wedding_templates table"""
    conn = sqlite3.connect('fajarmandiri.db')
    c = conn.cursor()
    
    # Get all templates
    templates = c.execute('SELECT id, name, template_file FROM wedding_templates').fetchall()
    
    print("Current template files in database:")
    for template in templates:
        print(f"ID: {template[0]}, Name: {template[1]}, File: {template[2]}")
    
    # Available template files in templates/wedding_templates/
    template_dir = 'templates/wedding_templates'
    if os.path.exists(template_dir):
        available_files = [f for f in os.listdir(template_dir) if f.endswith('.html')]
        print(f"\nAvailable template files in {template_dir}:")
        for file in available_files:
            print(f"  - {file}")
        
        # Update database with correct file names
        for template in templates:
            template_id, name, current_file = template
            
            # Try to find matching file
            matching_file = None
            name_lower = name.lower().replace(' ', '_').replace('-', '_')
            
            for file in available_files:
                file_lower = file.lower().replace('.html', '')
                if name_lower in file_lower or file_lower in name_lower:
                    matching_file = file
                    break
            
            if matching_file and matching_file != current_file:
                print(f"Updating template '{name}' from '{current_file}' to '{matching_file}'")
                c.execute('UPDATE wedding_templates SET template_file = ? WHERE id = ?', 
                         (matching_file, template_id))
    
    conn.commit()
    conn.close()
    print("\nTemplate paths updated!")

if __name__ == '__main__':
    fix_template_paths()
