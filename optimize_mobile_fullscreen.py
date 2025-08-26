
#!/usr/bin/env python3
"""
Script untuk mengoptimalkan semua wedding template agar fullscreen di mobile dan desktop
- Auto fullscreen browser (Android/iOS)
- Hapus link foto pada galeri yang sudah ada
- Optimasi mobile viewport dan CSS
"""

import os
import re
import shutil
from datetime import datetime

def backup_file(file_path):
    """Buat backup file sebelum dimodifikasi"""
    timestamp = int(datetime.now().timestamp())
    backup_path = f"{file_path}.backup.mobile_fullscreen.{timestamp}"
    shutil.copy2(file_path, backup_path)
    return backup_path

def optimize_mobile_css():
    """CSS optimasi untuk mobile fullscreen"""
    return """
    /* Mobile Fullscreen Optimization */
    @media screen and (max-width: 768px) {
        body {
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            -webkit-overflow-scrolling: touch;
            -webkit-text-size-adjust: 100%;
            -ms-text-size-adjust: 100%;
        }
        
        .invitation-container,
        .wedding-container {
            width: 100vw;
            min-height: 100vh;
            margin: 0;
            padding: 0;
            box-shadow: none;
        }
        
        /* Remove photo links for existing galleries */
        .gallery-item {
            cursor: default;
            pointer-events: none;
        }
        
        .gallery-item img {
            pointer-events: none;
        }
        
        .gallery-overlay {
            display: none !important;
        }
        
        /* Mobile viewport fixes */
        .content-section {
            padding: 30px 20px;
        }
        
        .section-title {
            font-size: 1.5rem;
        }
        
        .couple-names-hero {
            font-size: 2.2rem;
        }
        
        .couple-name {
            font-size: 1.8rem;
        }
        
        /* Touch-friendly buttons */
        .btn, .maps-btn, .btn-rsvp {
            min-height: 48px;
            padding: 12px 24px;
        }
        
        /* Form optimization */
        .form-control {
            min-height: 48px;
            font-size: 16px; /* Prevent zoom on iOS */
        }
        
        /* Remove modal functionality for photos */
        .modal {
            display: none !important;
        }
    }
    
    /* Desktop fullscreen */
    @media screen and (min-width: 769px) {
        body {
            margin: 0;
            padding: 0;
        }
        
        .invitation-container,
        .wedding-container {
            max-width: 100%;
            width: 100vw;
            margin: 0;
        }
        
        /* Keep gallery functionality on desktop but remove links */
        .gallery-item {
            cursor: default;
        }
        
        .gallery-item img {
            pointer-events: none;
        }
        
        .gallery-overlay {
            display: none !important;
        }
    }
    
    /* Universal photo gallery fixes */
    .gallery-item[onclick] {
        cursor: default !important;
    }
    
    .gallery-item img[onclick] {
        pointer-events: none !important;
    }
    """

def get_viewport_meta():
    """Meta tag untuk mobile optimization"""
    return '<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">'

def get_mobile_scripts():
    """JavaScript untuk mobile optimization"""
    return """
    <script>
    // Mobile fullscreen optimization
    document.addEventListener('DOMContentLoaded', function() {
        // Remove all photo gallery click events
        const galleryItems = document.querySelectorAll('.gallery-item');
        galleryItems.forEach(item => {
            item.removeAttribute('onclick');
            item.style.cursor = 'default';
            const img = item.querySelector('img');
            if (img) {
                img.removeAttribute('onclick');
                img.style.pointerEvents = 'none';
            }
        });
        
        // Remove modal functionality
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
        
        // Hide overlay buttons
        const overlays = document.querySelectorAll('.gallery-overlay');
        overlays.forEach(overlay => {
            overlay.style.display = 'none';
        });
        
        // Mobile viewport height fix
        function setViewportHeight() {
            document.documentElement.style.setProperty('--vh', window.innerHeight * 0.01 + 'px');
        }
        
        setViewportHeight();
        window.addEventListener('resize', setViewportHeight);
        window.addEventListener('orientationchange', setViewportHeight);
        
        // Prevent zoom on form focus (iOS)
        const inputs = document.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (input.style.fontSize === '' || parseFloat(input.style.fontSize) < 16) {
                input.style.fontSize = '16px';
            }
        });
    });
    
    // Override photo modal functions
    function openModal() { return false; }
    function closeModal() { return false; }
    function openPhotoModal() { return false; }
    </script>
    """

def process_template(file_path):
    """Process individual template file"""
    print(f"Processing: {os.path.basename(file_path)}")
    
    # Buat backup
    backup_path = backup_file(file_path)
    print(f"Backup created: {backup_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Update viewport meta tag
    viewport_pattern = r'<meta name="viewport"[^>]*>'
    if re.search(viewport_pattern, content):
        content = re.sub(viewport_pattern, get_viewport_meta(), content)
    else:
        # Add viewport if not exists
        head_pattern = r'(<head[^>]*>)'
        content = re.sub(head_pattern, f'\\1\n    {get_viewport_meta()}', content)
    
    # Add mobile CSS optimization
    mobile_css = optimize_mobile_css()
    
    # Find closing </style> tag and add mobile CSS before it
    style_pattern = r'(.*</style>)'
    if re.search(style_pattern, content, re.DOTALL):
        content = re.sub(r'(</style>)', mobile_css + '\n    </style>', content, count=1)
    else:
        # If no style tag, add in head
        head_close_pattern = r'(</head>)'
        content = re.sub(head_close_pattern, f'    <style>{mobile_css}</style>\n</head>', content)
    
    # Remove photo gallery onclick events
    content = re.sub(r'onclick="[^"]*openModal[^"]*"', '', content)
    content = re.sub(r'onclick="[^"]*openPhotoModal[^"]*"', '', content)
    content = re.sub(r'onclick="[^"]*closeModal[^"]*"', '', content)
    
    # Add mobile scripts before closing </body>
    mobile_js = get_mobile_scripts()
    content = re.sub(r'(</body>)', mobile_js + '\n</body>', content)
    
    # Write updated content
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Successfully updated: {os.path.basename(file_path)}")

def main():
    print("🚀 Starting mobile fullscreen optimization for all wedding templates...")
    print("=" * 80)
    
    # Template directory
    template_dir = "templates/wedding_templates"
    
    if not os.path.exists(template_dir):
        print(f"❌ Template directory not found: {template_dir}")
        return
    
    # Find all HTML template files
    template_files = []
    for filename in os.listdir(template_dir):
        if filename.endswith('.html') and not filename.endswith('.backup'):
            template_files.append(os.path.join(template_dir, filename))
    
    template_files.sort()
    
    print(f"📋 Found {len(template_files)} template files to process:")
    for file_path in template_files:
        print(f"   - {os.path.basename(file_path)}")
    
    print(f"\n🚀 Starting template processing...\n")
    
    # Process each template
    success_count = 0
    for file_path in template_files:
        try:
            process_template(file_path)
            success_count += 1
            print()
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(file_path)}: {str(e)}")
            print()
    
    print("=" * 80)
    print(f"✨ Processing completed!")
    print(f"✅ Successfully updated: {success_count}/{len(template_files)} templates")
    print(f"\n📁 Backup files saved with suffix .backup.mobile_fullscreen.[timestamp]")
    
    print(f"\n📝 Optimizations applied:")
    print(f"   🔹 Mobile fullscreen viewport optimization")
    print(f"   🔹 Removed photo gallery click/link functionality")
    print(f"   🔹 Touch-friendly UI elements")
    print(f"   🔹 iOS/Android specific fixes")
    print(f"   🔹 Desktop fullscreen support")
    print(f"   🔹 Responsive design improvements")
    
    print(f"\n💡 Features:")
    print(f"   • Auto fullscreen on mobile browsers")
    print(f"   • Gallery photos display only (no modal/links)")
    print(f"   • Touch-optimized interface")
    print(f"   • Viewport height fixes for mobile")
    print(f"   • Form zoom prevention on iOS")

if __name__ == "__main__":
    main()
