
import os
from PIL import Image, ImageDraw, ImageFont

def create_favicon_variants():
    """Create different sizes of favicon and OG image"""
    
    # Create a simple logo design
    sizes = [16, 32, 180, 512]  # Different favicon sizes + Apple touch icon
    
    for size in sizes:
        # Create new image
        img = Image.new('RGB', (size, size), '#667eea')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple logo - FMS initials
        try:
            # Try to use a font, fallback to default if not available
            font_size = max(8, size // 4)
            font = ImageFont.load_default()
        except:
            font = None
        
        # Draw background gradient effect
        for i in range(size):
            for j in range(size):
                # Create gradient effect
                distance_from_center = ((i - size/2)**2 + (j - size/2)**2)**0.5
                if distance_from_center < size/2:
                    # Gradient from center
                    ratio = distance_from_center / (size/2)
                    r = int(102 + (118 - 102) * ratio)
                    g = int(126 + (79 - 126) * ratio) 
                    b = int(234 + (162 - 234) * ratio)
                    img.putpixel((i, j), (r, g, b))
        
        # Add text overlay for larger sizes
        if size >= 32:
            text = "FM"
            # Calculate text position to center it
            try:
                bbox = draw.textbbox((0, 0), text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
            except:
                text_width = len(text) * (font_size // 2)
                text_height = font_size
            
            x = (size - text_width) // 2
            y = (size - text_height) // 2
            
            # Draw white text
            draw.text((x, y), text, fill='white', font=font)
        
        # Save different formats
        if size == 16:
            img.save('static/favicon-16x16.png', 'PNG')
        elif size == 32:
            img.save('static/favicon-32x32.png', 'PNG')
            img.save('static/favicon.ico', 'ICO')
        elif size == 180:
            img.save('static/apple-touch-icon.png', 'PNG')
        elif size == 512:
            # Create OG image (larger for social sharing)
            og_img = Image.new('RGB', (1200, 630), '#667eea')
            og_draw = ImageDraw.Draw(og_img)
            
            # Gradient background
            for i in range(1200):
                for j in range(630):
                    ratio_x = i / 1200
                    ratio_y = j / 630
                    r = int(102 + (118 - 102) * ratio_x)
                    g = int(126 + (79 - 126) * ratio_y)
                    b = int(234 + (162 - 234) * (ratio_x + ratio_y) / 2)
                    og_img.putpixel((i, j), (r, g, b))
            
            # Add text
            try:
                og_font = ImageFont.load_default()
            except:
                og_font = None
            
            title = "Fajar Mandiri Store"
            subtitle = "Digital Creative Studio"
            
            # Title
            title_bbox = og_draw.textbbox((0, 0), title, font=og_font)
            title_width = title_bbox[2] - title_bbox[0]
            title_x = (1200 - title_width) // 2
            og_draw.text((title_x, 250), title, fill='white', font=og_font)
            
            # Subtitle
            subtitle_bbox = og_draw.textbbox((0, 0), subtitle, font=og_font)
            subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
            subtitle_x = (1200 - subtitle_width) // 2
            og_draw.text((subtitle_x, 350), subtitle, fill='white', font=og_font)
            
            og_img.save('static/images/og-image.jpg', 'JPEG', quality=90)
    
    print("✅ Favicon variants dan OG image berhasil dibuat!")

if __name__ == "__main__":
    # Create static/images directory if not exists
    os.makedirs('static/images', exist_ok=True)
    create_favicon_variants()
