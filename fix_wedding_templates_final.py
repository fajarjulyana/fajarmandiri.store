
import os
import re
from datetime import datetime

def fix_countdown_and_music(content, template_name):
    """Memperbaiki countdown timer dan music playback"""
    
    # Fix JavaScript untuk countdown yang lebih robust
    fixed_js = """
        // Global variables
        let countdownInterval;
        let musicPlaying = false;

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
                    music.play().then(() => {
                        musicPlaying = true;
                        console.log('Music started playing');
                    }).catch(e => {
                        console.log('Audio play failed:', e);
                        // Try to play with user interaction
                        document.addEventListener('click', function playOnClick() {
                            music.play().then(() => {
                                musicPlaying = true;
                                document.removeEventListener('click', playOnClick);
                            }).catch(e => console.log('Audio play still failed:', e));
                        });
                    });
                }

                // Start countdown if wedding date exists
                {% if invitation.wedding_date %}
                startCountdown();
                {% endif %}
            }, 1000);
        }

        // Music control function
        function toggleMusic() {
            const music = document.getElementById('backgroundMusic');
            const musicBtn = document.getElementById('musicBtn');

            if (music) {
                if (musicPlaying) {
                    music.pause();
                    if (musicBtn) musicBtn.classList.add('paused');
                    musicPlaying = false;
                } else {
                    music.play().then(() => {
                        if (musicBtn) musicBtn.classList.remove('paused');
                        musicPlaying = true;
                    }).catch(e => {
                        console.log('Could not play music:', e);
                    });
                }
            }
        }

        // Countdown function
        {% if invitation.wedding_date %}
        function startCountdown() {
            // Clear any existing countdown
            if (countdownInterval) {
                clearInterval(countdownInterval);
            }

            const weddingDate = new Date("{{ invitation.wedding_date.strftime('%Y-%m-%d') if invitation.wedding_date.__class__.__name__ == 'datetime' else invitation.wedding_date }}").getTime();

            function updateCountdown() {
                const now = new Date().getTime();
                const distance = weddingDate - now;

                if (distance > 0) {
                    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
                    const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                    const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
                    const seconds = Math.floor((distance % (1000 * 60)) / 1000);

                    // Update countdown display
                    const daysEl = document.getElementById('days');
                    const hoursEl = document.getElementById('hours');
                    const minutesEl = document.getElementById('minutes');
                    const secondsEl = document.getElementById('seconds');

                    if (daysEl) daysEl.innerText = days.toString().padStart(2, '0');
                    if (hoursEl) hoursEl.innerText = hours.toString().padStart(2, '0');
                    if (minutesEl) minutesEl.innerText = minutes.toString().padStart(2, '0');
                    if (secondsEl) secondsEl.innerText = seconds.toString().padStart(2, '0');
                } else {
                    // Wedding day has arrived
                    const countdownTimer = document.getElementById('countdownTimer');
                    if (countdownTimer) {
                        countdownTimer.innerHTML = 
                            '<div class="text-center"><h3 style="color: #667eea; font-family: Dancing Script, cursive;">Hari Bahagia Telah Tiba! 🎉</h3></div>';
                    }
                    clearInterval(countdownInterval);
                }
            }

            // Start countdown immediately
            updateCountdown();
            
            // Update every second
            countdownInterval = setInterval(updateCountdown, 1000);
        }
        {% endif %}

        // Initialize when page loads
        document.addEventListener('DOMContentLoaded', function() {
            // Auto-start music if user has interacted
            document.addEventListener('click', function() {
                const music = document.getElementById('backgroundMusic');
                if (music && !musicPlaying) {
                    music.play().then(() => {
                        musicPlaying = true;
                    }).catch(e => console.log('Auto music play failed:', e));
                }
            }, { once: true });
        });

        // Copy text function for bank accounts
        function copyText(text) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(text).then(() => {
                    alert('Nomor rekening berhasil disalin!');
                }).catch(err => {
                    console.log('Could not copy text: ', err);
                    // Fallback
                    const textArea = document.createElement('textarea');
                    textArea.value = text;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    alert('Nomor rekening berhasil disalin!');
                });
            }
        }
"""

    # Cari dan replace JavaScript yang lama
    js_patterns = [
        r'<script>\s*// Open invitation function.*?</script>',
        r'<script>\s*function openInvitation\(\).*?</script>',
        r'// Open invitation function.*?(?=</script>|<script>)',
        r'function startCountdown\(\).*?(?=function|</script>|$)',
    ]
    
    # Remove old JavaScript
    for pattern in js_patterns:
        content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # Add new fixed JavaScript before closing body tag
    content = content.replace('</body>', f'<script>\n{fixed_js}\n</script>\n</body>')
    
    # Ensure countdown section has proper structure
    countdown_section = """
        <!-- Countdown Section -->
        <section class="countdown-section" style="background: rgba(255,255,255,0.1); padding: 4rem 0; text-align: center;">
            <div class="container">
                <h2 class="section-title" style="color: white; font-family: 'Dancing Script', cursive; font-size: 2.5rem; margin-bottom: 2rem;">Menuju Hari Bahagia</h2>
                {% if invitation.wedding_date %}
                <div class="countdown-timer" id="countdownTimer" style="display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem;">
                    <div class="countdown-item" style="text-align: center; background: rgba(255,255,255,0.2); padding: 2rem 1.5rem; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); min-width: 120px;">
                        <span class="countdown-number" id="days" style="display: block; font-size: 3rem; font-weight: 700; color: white; font-family: 'Dancing Script', cursive;">00</span>
                        <span class="countdown-label" style="font-size: 0.9rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;">Hari</span>
                    </div>
                    <div class="countdown-item" style="text-align: center; background: rgba(255,255,255,0.2); padding: 2rem 1.5rem; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); min-width: 120px;">
                        <span class="countdown-number" id="hours" style="display: block; font-size: 3rem; font-weight: 700; color: white; font-family: 'Dancing Script', cursive;">00</span>
                        <span class="countdown-label" style="font-size: 0.9rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;">Jam</span>
                    </div>
                    <div class="countdown-item" style="text-align: center; background: rgba(255,255,255,0.2); padding: 2rem 1.5rem; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); min-width: 120px;">
                        <span class="countdown-number" id="minutes" style="display: block; font-size: 3rem; font-weight: 700; color: white; font-family: 'Dancing Script', cursive;">00</span>
                        <span class="countdown-label" style="font-size: 0.9rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;">Menit</span>
                    </div>
                    <div class="countdown-item" style="text-align: center; background: rgba(255,255,255,0.2); padding: 2rem 1.5rem; border-radius: 15px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.3); min-width: 120px;">
                        <span class="countdown-number" id="seconds" style="display: block; font-size: 3rem; font-weight: 700; color: white; font-family: 'Dancing Script', cursive;">00</span>
                        <span class="countdown-label" style="font-size: 0.9rem; color: rgba(255,255,255,0.8); text-transform: uppercase; letter-spacing: 1px; margin-top: 0.5rem;">Detik</span>
                    </div>
                </div>
                {% endif %}
            </div>
        </section>
"""
    
    # Insert countdown section if not exists or replace existing
    if 'countdown-section' not in content:
        # Add after first section
        content = re.sub(r'(</section>)', rf'\1\n{countdown_section}', content, count=1)
    else:
        # Replace existing countdown section
        content = re.sub(r'<!-- Countdown Section -->.*?</section>', countdown_section, content, flags=re.DOTALL)
    
    # Ensure background music element exists
    if 'backgroundMusic' not in content:
        music_html = '''
    <!-- Background Music -->
    <audio id="backgroundMusic" loop preload="auto">
        <source src="/static/music/{{ template_name }}.mp3" type="audio/mpeg">
        <source src="/static/music/default_wedding.mp3" type="audio/mpeg">
    </audio>
    
    <!-- Music Control Button -->
    <button id="musicBtn" onclick="toggleMusic()" style="position: fixed; top: 20px; right: 20px; z-index: 1000; background: rgba(255,255,255,0.2); border: none; color: white; padding: 10px; border-radius: 50%; cursor: pointer; backdrop-filter: blur(10px);">
        <i class="fas fa-music"></i>
    </button>
'''
        content = content.replace('</body>', f'{music_html}\n</body>')
    
    return content

def process_template(file_path):
    """Memproses satu template untuk memperbaiki countdown dan music"""
    template_name = os.path.basename(file_path)
    print(f"\n=== Memperbaiki {template_name} ===")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if template needs fixing
        needs_countdown_fix = 'startCountdown()' in content and ('clearInterval' not in content or 'countdownInterval' not in content)
        needs_music_fix = 'backgroundMusic' in content and ('musicPlaying' not in content or 'toggleMusic' not in content)
        
        if not needs_countdown_fix and not needs_music_fix:
            print(f"Template {template_name} sudah benar!")
            return True
        
        print(f"Masalah ditemukan:")
        if needs_countdown_fix:
            print(f"  - Countdown timer perlu diperbaiki")
        if needs_music_fix:
            print(f"  - Music playback perlu diperbaiki")
        
        # Apply fixes
        original_content = content
        content = fix_countdown_and_music(content, template_name.replace('.html', ''))
        
        # Save backup
        backup_path = f"{file_path}.backup.final.{int(datetime.now().timestamp())}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        print(f"Backup disimpan: {backup_path}")
        
        # Save fixed template
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✓ Template {template_name} berhasil diperbaiki!")
        return True
        
    except Exception as e:
        print(f"✗ Error memproses {template_name}: {e}")
        return False

def main():
    """Main function"""
    print("🔧 Wedding Template Final Fixer")
    print("Memperbaiki countdown timer dan music playback")
    print("=" * 60)
    
    templates_dir = "templates/wedding_templates"
    
    if not os.path.exists(templates_dir):
        print(f"❌ Directory {templates_dir} tidak ditemukan!")
        return
    
    # Get all HTML files
    template_files = [f for f in os.listdir(templates_dir) if f.endswith('.html') and not f.endswith('.backup')]
    
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
    
    print("\n" + "=" * 60)
    print(f"🎉 Selesai! {success_count}/{len(template_files)} template berhasil diperbaiki")
    
    if success_count < len(template_files):
        print("⚠️  Beberapa template gagal diproses. Periksa error di atas.")
    else:
        print("\n✅ Semua template sekarang memiliki:")
        print("  - Countdown timer real-time yang berfungsi")
        print("  - Music playback yang otomatis saat buka undangan")
        print("  - Tombol kontrol musik")
        print("  - Error handling yang lebih baik")

if __name__ == "__main__":
    main()
