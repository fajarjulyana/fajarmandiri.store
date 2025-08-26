
import re

def update_create_wedding_form():
    """Update create_wedding_invitation.html to support multiple venues"""
    
    file_path = 'templates/create_wedding_invitation.html'
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup original file
        with open(f'{file_path}.backup.multi_venue', 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Find Step 3 (Wedding Details) and replace with enhanced version
        step3_pattern = r'(<!-- Step 3: Wedding Details -->.*?)</div>\s*</div>\s*</div>'
        
        enhanced_step3 = '''<!-- Step 3: Wedding Details -->
        <div class="step-content" id="step-3">
            <div class="step-header">
                <h3 class="font-heading text-gradient mb-2">
                    <i class="fas fa-calendar-heart me-2"></i>Detail Acara Pernikahan
                </h3>
                <p class="text-muted mb-4">Tentukan waktu dan tempat untuk setiap acara</p>
            </div>
            <div class="step-body">
                
                <!-- Event Type Selection -->
                <div class="form-section mb-4">
                    <div class="section-title">
                        <i class="fas fa-list-alt me-2"></i>
                        <h6 class="mb-0">Jenis Acara</h6>
                    </div>
                    <div class="event-type-selection">
                        <div class="row g-3">
                            <div class="col-md-6">
                                <div class="form-check custom-radio">
                                    <input class="form-check-input" type="radio" name="event_type" id="same_venue" value="same" checked>
                                    <label class="form-check-label" for="same_venue">
                                        <i class="fas fa-map-marker-alt me-2"></i>Akad & Resepsi di Lokasi yang Sama
                                    </label>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="form-check custom-radio">
                                    <input class="form-check-input" type="radio" name="event_type" id="different_venue" value="different">
                                    <label class="form-check-label" for="different_venue">
                                        <i class="fas fa-map-marked-alt me-2"></i>Akad & Resepsi di Lokasi Berbeda
                                    </label>
                                </div>
                            </div>
                            <div class="col-12">
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="separate_family_events" name="separate_family_events">
                                    <label class="form-check-label" for="separate_family_events">
                                        <i class="fas fa-users me-2"></i>Tambahkan acara terpisah untuk kedua keluarga mempelai
                                    </label>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Same Venue Section -->
                <div class="venue-section" id="sameVenueSection">
                    <div class="form-section">
                        <div class="section-title">
                            <i class="fas fa-calendar-alt me-2"></i>
                            <h6 class="mb-0">Informasi Acara</h6>
                        </div>
                        <div class="row g-4">
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">
                                        <i class="fas fa-calendar-alt me-1"></i>Tanggal Pernikahan
                                    </label>
                                    <input type="date" name="wedding_date" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">
                                        <i class="fas fa-clock me-1"></i>Waktu Acara
                                    </label>
                                    <input type="time" name="wedding_time" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">
                                        <i class="fas fa-building me-1"></i>Nama Tempat/Gedung
                                    </label>
                                    <input type="text" name="venue_name" class="form-control" placeholder="Contoh: Ballroom Hotel Grand">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label required">
                                        <i class="fas fa-map-marker-alt me-1"></i>Alamat Lengkap Venue
                                    </label>
                                    <textarea name="venue_address" class="form-control" rows="3" required placeholder="Alamat lengkap venue pernikahan/acara atau link Google Maps"></textarea>
                                    <div class="invalid-feedback">
                                        Alamat venue wajib diisi!
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Different Venues Section -->
                <div class="venue-section d-none" id="differentVenueSection">
                    <!-- Akad Nikah -->
                    <div class="form-section">
                        <div class="section-title">
                            <i class="fas fa-ring me-2"></i>
                            <h6 class="mb-0">Akad Nikah</h6>
                        </div>
                        <div class="row g-4">
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Tanggal Akad</label>
                                    <input type="date" name="akad_date" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Waktu Akad</label>
                                    <input type="time" name="akad_time" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Nama Tempat Akad</label>
                                    <input type="text" name="akad_venue_name" class="form-control" placeholder="Contoh: Masjid Al-Ikhlas">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Alamat Tempat Akad</label>
                                    <textarea name="akad_venue_address" class="form-control" rows="2" placeholder="Alamat lengkap tempat akad"></textarea>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Resepsi -->
                    <div class="form-section">
                        <div class="section-title">
                            <i class="fas fa-glass-cheers me-2"></i>
                            <h6 class="mb-0">Resepsi</h6>
                        </div>
                        <div class="row g-4">
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Tanggal Resepsi</label>
                                    <input type="date" name="resepsi_date" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Waktu Resepsi</label>
                                    <input type="time" name="resepsi_time" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Nama Tempat Resepsi</label>
                                    <input type="text" name="resepsi_venue_name" class="form-control" placeholder="Contoh: Ballroom Hotel Grand">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label required">Alamat Tempat Resepsi</label>
                                    <textarea name="resepsi_venue_address" class="form-control" rows="2" placeholder="Alamat lengkap tempat resepsi"></textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Separate Family Events Section -->
                <div class="venue-section d-none" id="familyEventsSection">
                    <!-- Bride Family Event -->
                    <div class="form-section">
                        <div class="section-title">
                            <i class="fas fa-female me-2 text-pink"></i>
                            <h6 class="mb-0">Acara Keluarga Mempelai Wanita (Opsional)</h6>
                        </div>
                        <div class="row g-4">
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Tanggal Acara</label>
                                    <input type="date" name="bride_event_date" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Waktu Acara</label>
                                    <input type="time" name="bride_event_time" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Nama Tempat</label>
                                    <input type="text" name="bride_event_venue_name" class="form-control" placeholder="Contoh: Rumah Keluarga">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Alamat</label>
                                    <textarea name="bride_event_venue_address" class="form-control" rows="2" placeholder="Alamat lengkap"></textarea>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Groom Family Event -->
                    <div class="form-section">
                        <div class="section-title">
                            <i class="fas fa-male me-2 text-blue"></i>
                            <h6 class="mb-0">Acara Keluarga Mempelai Pria (Opsional)</h6>
                        </div>
                        <div class="row g-4">
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Tanggal Acara</label>
                                    <input type="date" name="groom_event_date" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Waktu Acara</label>
                                    <input type="time" name="groom_event_time" class="form-control">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Nama Tempat</label>
                                    <input type="text" name="groom_event_venue_name" class="form-control" placeholder="Contoh: Gedung Serbaguna">
                                </div>
                            </div>
                            <div class="col-lg-6">
                                <div class="form-group">
                                    <label class="form-label">Alamat</label>
                                    <textarea name="groom_event_venue_address" class="form-control" rows="2" placeholder="Alamat lengkap"></textarea>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Custom Message -->
                <div class="form-section">
                    <div class="section-title">
                        <i class="fas fa-comment-dots me-2"></i>
                        <h6 class="mb-0">Pesan Khusus</h6>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Pesan untuk Tamu</label>
                        <textarea name="custom_message" class="form-control" rows="4" placeholder="Tulis pesan khusus atau ucapan untuk tamu undangan Anda"></textarea>
                    </div>
                </div>

            </div>
        </div>'''
        
        # Replace Step 3 content
        content = re.sub(step3_pattern, enhanced_step3 + '\n\n        </div>\n    </div>\n</div>', content, flags=re.DOTALL)
        
        # Add JavaScript for venue section toggling
        additional_js = '''
// Event type handling for venue sections
document.querySelectorAll('input[name="event_type"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const sameVenueSection = document.getElementById('sameVenueSection');
        const differentVenueSection = document.getElementById('differentVenueSection');
        
        if (this.value === 'same') {
            sameVenueSection.classList.remove('d-none');
            differentVenueSection.classList.add('d-none');
        } else {
            sameVenueSection.classList.add('d-none');
            differentVenueSection.classList.remove('d-none');
        }
    });
});

// Family events toggle
document.getElementById('separate_family_events').addEventListener('change', function() {
    const familyEventsSection = document.getElementById('familyEventsSection');
    
    if (this.checked) {
        familyEventsSection.classList.remove('d-none');
    } else {
        familyEventsSection.classList.add('d-none');
    }
});

// Copy same venue data to different venue sections
function copySameVenueData() {
    const eventType = document.querySelector('input[name="event_type"]:checked').value;
    
    if (eventType === 'different') {
        const weddingDate = document.querySelector('input[name="wedding_date"]').value;
        const weddingTime = document.querySelector('input[name="wedding_time"]').value;
        const venueName = document.querySelector('input[name="venue_name"]').value;
        const venueAddress = document.querySelector('textarea[name="venue_address"]').value;
        
        // Copy to akad fields
        document.querySelector('input[name="akad_date"]').value = weddingDate;
        document.querySelector('input[name="akad_time"]').value = weddingTime;
        document.querySelector('input[name="akad_venue_name"]').value = venueName;
        document.querySelector('textarea[name="akad_venue_address"]').value = venueAddress;
        
        // Copy to resepsi fields
        document.querySelector('input[name="resepsi_date"]').value = weddingDate;
        document.querySelector('input[name="resepsi_time"]').value = weddingTime;
        document.querySelector('input[name="resepsi_venue_name"]').value = venueName;
        document.querySelector('textarea[name="resepsi_venue_address"]').value = venueAddress;
    }
}

// Add auto-copy functionality when switching from same to different venue
document.querySelector('input[name="event_type"][value="different"]').addEventListener('change', function() {
    if (this.checked) {
        setTimeout(copySameVenueData, 100);
    }
});
'''
        
        # Insert the new JavaScript before the closing script tag
        content = content.replace('});', '});\n\n' + additional_js + '\n\n')
        
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Successfully updated {file_path}")
        print("📋 Backup saved as: templates/create_wedding_invitation.html.backup.multi_venue")
        return True
        
    except Exception as e:
        print(f"❌ Error updating create form: {str(e)}")
        return False

def main():
    """Main function"""
    print("🚀 Updating create wedding invitation form...")
    
    if update_create_wedding_form():
        print("\n✨ Form update completed successfully!")
        print("\n📝 New form features:")
        print("   🔹 Radio buttons to choose same/different venues")
        print("   🔹 Separate sections for Akad and Resepsi")
        print("   🔹 Optional separate family events")
        print("   🔹 Auto-copy functionality between venue sections")
        print("   🔹 Enhanced UI with proper icons and styling")
    else:
        print("❌ Failed to update form")

if __name__ == "__main__":
    main()
