
import os
import re
from datetime import datetime

def analyze_template(file_path):
    """Analisis template untuk mengecek fitur yang ada"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        features = {
            'cover_page': bool(re.search(r'cover-page|coverPage', content, re.IGNORECASE)),
            'open_button': bool(re.search(r'buka.*undangan|open.*invitation', content, re.IGNORECASE)),
            'countdown': bool(re.search(r'countdown|menuju.*hari', content, re.IGNORECASE)),
            'maps_link': bool(re.search(r'maps\.google|venue_address.*http', content, re.IGNORECASE)),
            'background_music': bool(re.search(r'backgroundMusic|background.*music', content, re.IGNORECASE))
        }
        
        return content, features
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None, None

def add_cover_page_and_countdown(content, template_name):
    """Menambahkan cover page dengan tombol buka undangan dan countdown"""
    
    # Check if already has cover page
    if 'cover-page' in content or 'coverPage' in content:
        print(f"Template {template_name} sudah memiliki cover page")
        return content
    
    # CSS untuk cover page dan countdown
    cover_css = """
        /* Cover Page Styles */
        .cover-page {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            text-align: center;
            color: white;
        }

        .cover-content {
            max-width: 400px;
            padding: 2rem;
        }

        .couple-initials {
            font-size: 4rem;
            font-family: 'Dancing Script', cursive;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 1rem;
        }

        .couple-initials .fas {
            font-size: 2rem;
            animation: heartbeat 1.5s ease-in-out infinite;
        }

        @keyframes heartbeat {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.2); }
        }

        .couple-names {
            font-family: 'Dancing Script', cursive;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }

        .wedding-date {
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }

        .open-invitation-btn {
            background: rgba(255,255,255,0.2);
            border: 2px solid white;
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }

        .open-invitation-btn:hover {
            background: white;
            color: #667eea;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.3);
        }

        /* Countdown Styles */
        .countdown-section {
            background: rgba(255,255,255,0.1);
            padding: 4rem 0;
            text-align: center;
        }

        .countdown-timer {
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 2rem;
        }

        .countdown-item {
            text-align: center;
            background: rgba(255,255,255,0.2);
            padding: 2rem 1.5rem;
            border-radius: 15px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.3);
            min-width: 120px;
        }

        .countdown-number {
            display: block;
            font-size: 3rem;
            font-weight: 700;
            color: white;
            font-family: 'Dancing Script', cursive;
        }

        .countdown-label {
            font-size: 0.9rem;
            color: rgba(255,255,255,0.8);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-top: 0.5rem;
        }
"""

    # HTML untuk cover page
    cover_html = """
    <!-- Cover Page -->
    <div id="coverPage" class="cover-page">
        <div class="cover-content">
            <div class="couple-initials">
                <span>{{ invitation.bride_name[0] if invitation.bride_name else 'B' }}</span>
                <i class="fas fa-heart"></i>
                <span>{{ invitation.groom_name[0] if invitation.groom_name else 'G' }}</span>
            </div>
            <h1 class="couple-names">{{ invitation.couple_name }}</h1>
            <p class="wedding-date">
                {% if invitation.wedding_date %}
                    {{ invitation.wedding_date.strftime('%d %B %Y') if invitation.wedding_date.__class__.__name__ == 'datetime' else invitation.wedding_date }}
                {% else %}
                    Segera
                {% endif %}
            </p>
            <button class="open-invitation-btn" onclick="openInvitation()">
                <i class="fas fa-envelope-open me-2"></i>Buka Undangan
            </button>
        </div>
    </div>
"""

    # HTML untuk countdown section
    countdown_html = """
        <!-- Countdown Section -->
        <section class="countdown-section">
            <h2 class="section-title">Menuju Hari Bahagia</h2>
            {% if invitation.wedding_date %}
            <div class="countdown-timer" id="countdownTimer">
                <div class="countdown-item">
                    <span class="countdown-number" id="days">00</span>
                    <span class="countdown-label">Hari</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-number" id="hours">00</span>
                    <span class="countdown-label">Jam</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-number" id="minutes">00</span>
                    <span class="countdown-label">Menit</span>
                </div>
                <div class="countdown-item">
                    <span class="countdown-number" id="seconds">00</span>
                    <span class="countdown-label">Detik</span>
                </div>
            </div>
            {% endif %}
        </section>
"""

    # JavaScript untuk cover page dan countdown
    cover_js = """
        // Open invitation function
        function openInvitation() {
            const coverPage = document.getElementById('coverPage');
            const mainContent = document.getElementById('mainContent');
            const music = document.getElementById('backgroundMusic');

            coverPage.style.transition = 'opacity 1s ease-out';
            coverPage.style.opacity = '0';

            setTimeout(() => {
                coverPage.style.display = 'none';
                mainContent.style.display = 'block';
                mainContent.style.opacity = '0';

                setTimeout(() => {
                    mainContent.style.transition = 'opacity 1s ease-in';
                    mainContent.style.opacity = '1';
                }, 100);

                // Play background music
                if (music) {
                    music.play().catch(e => console.log('Audio play failed:', e));
                }

                // Start countdown if wedding date exists
                {% if invitation.wedding_date %}
                startCountdown();
                {% endif %}
            }, 1000);
        }

        // Countdown function
        {% if invitation.wedding_date %}
        function startCountdown() {
            const weddingDate = new Date("{{ invitation.wedding_date.strftime('%Y-%m-%d') if invitation.wedding_date.__class__.__name__ == 'datetime' else invitation.wedding_date }}").getTime();

            function updateCountdown() {
                const now = new Date().getTime();
                const distance = weddingDate - now;

                if (distance > 0) {
                    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

                    document.getElementById('days').innerText = days.toString().padStart(2, '0');
                    document.getElementById('hours').innerText = hours.toString().padStart(2, '0');
                    document.getElementById('minutes').innerText = minutes.toString().padStart(2, '0');
                    document.getElementById('seconds').innerText = seconds.toString().padStart(2, '0');
                } else {
                    document.getElementById('countdownTimer').innerHTML = 
                        '<div class="text-center"><h3 style="color: #667eea;">Hari Bahagia Telah Tiba! 🎉</h3></div>';
                }
            }

            updateCountdown();
            setInterval(updateCountdown, 1000);
        }
        {% endif %}
"""

    # Tambahkan CSS ke dalam <style>
    if '<style>' in content:
        content = content.replace('<style>', f'<style>\n{cover_css}')
    else:
        # Jika tidak ada tag style, tambahkan setelah head
        content = content.replace('</head>', f'<style>\n{cover_css}\n</style>\n</head>')

    # Tambahkan cover page setelah body
    content = content.replace('<body>', f'<body>\n{cover_html}')

    # Wrap main content dengan id mainContent dan hide by default
    if 'mainContent' not in content:
        # Find main container
        container_patterns = [
            r'(<div[^>]*class[^>]*container[^>]*>)',
            r'(<section[^>]*class[^>]*hero[^>]*>)',
            r'(<div[^>]*class[^>]*invitation[^>]*>)',
            r'(<main[^>]*>)'
        ]
        
        for pattern in container_patterns:
            if re.search(pattern, content):
                content = re.sub(pattern, r'<div class="container" id="mainContent" style="display: none;">\1', content, count=1)
                # Close the wrapper div before </body>
                content = content.replace('</body>', '</div>\n</body>')
                break

    # Tambahkan countdown section setelah hero section
    hero_patterns = [
        r'(</section>)(\s*<!-- [^>]*Section -->|\s*<section)',
        r'(</div>)(\s*</section>)',
        r'(</header>)(\s*<section)'
    ]
    
    for pattern in hero_patterns:
        if re.search(pattern, content):
            content = re.sub(pattern, rf'\1\n{countdown_html}\n\2', content, count=1)
            break

    # Tambahkan JavaScript sebelum </body>
    content = content.replace('</body>', f'<script>\n{cover_js}\n</script>\n</body>')

    return content

def fix_maps_link(content):
    """Memperbaiki link Google Maps untuk mendukung link langsung"""
    
    # Pattern untuk venue address
    venue_pattern = r'(<a[^>]*href=["\']https://maps\.google\.com/\?q=\{\{\s*invitation\.venue_address\s*\}\}["\'][^>]*>)'
    
    # Replacement yang mendukung link langsung
    replacement = '''{% if invitation.venue_address.startswith('http') %}
                        <a href="{{ invitation.venue_address }}" target="_blank" class="maps-btn">
                            <i class="fas fa-map-marked-alt me-2"></i>View on Maps
                        </a>
                    {% else %}
                        <a href="https://maps.google.com/?q={{ invitation.venue_address }}" target="_blank" class="maps-btn">
                            <i class="fas fa-map-marked-alt me-2"></i>View on Maps
                        </a>
                    {% endif %}'''
    
    if re.search(venue_pattern, content):
        content = re.sub(venue_pattern, replacement, content)
    
    # Juga perbaiki tampilan alamat
    address_pattern = r'(<p[^>]*>\{\{\s*invitation\.venue_address\s*\}\}</p>)'
    address_replacement = '<p>{{ invitation.venue_address if not invitation.venue_address.startswith(\'http\') else \'Klik tombol di bawah untuk lokasi\' }}</p>'
    
    content = re.sub(address_pattern, address_replacement, content)
    
    return content

def process_template(file_path):
    """Memproses satu template"""
    template_name = os.path.basename(file_path)
    print(f"\n=== Memproses {template_name} ===")
    
    content, features = analyze_template(file_path)
    if content is None:
        return False
    
    # Tampilkan status fitur
    print(f"Status fitur:")
    print(f"  - Cover Page: {'✓' if features['cover_page'] else '✗'}")
    print(f"  - Open Button: {'✓' if features['open_button'] else '✗'}")
    print(f"  - Countdown: {'✓' if features['countdown'] else '✗'}")
    print(f"  - Maps Link: {'✓' if features['maps_link'] else '✗'}")
    print(f"  - Background Music: {'✓' if features['background_music'] else '✗'}")
    
    # Check if needs fixing
    needs_fixing = not (features['cover_page'] and features['countdown'])
    
    if not needs_fixing:
        print(f"Template {template_name} sudah lengkap!")
        return True
    
    print(f"Memperbaiki template {template_name}...")
    
    # Apply fixes
    original_content = content
    
    # Add cover page and countdown if missing
    if not features['cover_page'] or not features['countdown']:
        content = add_cover_page_and_countdown(content, template_name)
    
    # Fix maps link
    content = fix_maps_link(content)
    
    # Save backup
    backup_path = f"{file_path}.backup.{int(datetime.now().timestamp())}"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(original_content)
    print(f"Backup disimpan: {backup_path}")
    
    # Save fixed template
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Template {template_name} berhasil diperbaiki!")
        return True
    except Exception as e:
        print(f"✗ Error menyimpan {template_name}: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Wedding Template Fixer")
    print("=" * 50)
    
    templates_dir = "templates/wedding_templates"
    
    if not os.path.exists(templates_dir):
        print(f"❌ Directory {templates_dir} tidak ditemukan!")
        return
    
    # Get all HTML files
    template_files = [f for f in os.listdir(templates_dir) if f.endswith('.html')]
    
    if not template_files:
        print("❌ Tidak ada template HTML ditemukan!")
        return
    
    print(f"📁 Ditemukan {len(template_files)} template(s)")
    
    # Process each template
    success_count = 0
    for template_file in sorted(template_files):
        file_path = os.path.join(templates_dir, template_file)
        if process_template(file_path):
            success_count += 1
    
    print("\n" + "=" * 50)
    print(f"🎉 Selesai! {success_count}/{len(template_files)} template berhasil diproses")
    
    if success_count < len(template_files):
        print("⚠️  Beberapa template gagal diproses. Periksa error di atas.")

if __name__ == "__main__":
    main()
