# Fajar Mandiri Store - Wedding & CV Management System

Platform digital untuk membuat undangan pernikahan dan CV profesional dengan sistem manajemen pesanan cetak yang terintegrasi.

## 🌟 Fitur Utama

### 1. Undangan Pernikahan Digital
- **18 Template Premium**: Koleksi lengkap template modern dan elegan
  - MandiriTheme Series (Style, Modern, Classic, Elegant)
  - Luxury Modern & Royal Collections
  - Themed Templates (Ocean Waves, Garden Fresh, Vintage Charm)
  - Specialized Designs (Minimal Blush, Classic Romance, Elegant Golden)

- **Opening Screen Interactive**: 
  - Tombol "BUKA UNDANGAN" dengan animasi menarik
  - Countdown timer real-time menuju hari pernikahan
  - Animasi transisi yang smooth dan professional
  - Background music auto-play setelah user interaction

- **Customization Lengkap**: 
  - **Data Mempelai**: Nama lengkap, gelar (opsional), nama orang tua
  - **Detail Acara**: Tanggal, waktu, nama venue, alamat lengkap
  - **Pesan Personal**: Custom message dan ucapan khusus
  - **Media**: Upload foto prewedding (maksimal 10 foto)
  - **Audio**: Background music (default atau upload custom)
  - **Payment Info**: Info rekening bank dan upload QRIS code

- **Fitur Interaktif Modern**:
  - **Smart RSVP**: Konfirmasi kehadiran dengan jumlah tamu
  - **Guest Book Digital**: Ucapan dan doa dari tamu dengan moderasi
  - **Location Integration**: Link langsung ke Google Maps & Navigasi
  - **QR Code Generator**: Untuk akses mudah dan sharing
  - **Mobile-First Design**: Responsif di semua device
  - **Music Player**: Kontrol background music dengan animasi
  - **Photo Gallery**: Lightbox gallery untuk foto prewedding

- **Advanced Features**:
  - **Countdown Timer**: Real-time countdown ke hari H
  - **Share Integration**: Easy sharing via WhatsApp, social media
  - **Analytics**: Basic view statistics dan RSVP tracking
  - **Status Management**: Aktif/nonaktif invitation control
  - **Guest Limit**: Kontrol jumlah maksimal tamu

### 2. CV Generator Professional
- **10+ Template Premium**: Dari corporate hingga creative design
- **Multi-Category**: Modern, Classic, Creative, Professional, Minimalist
- **Input Lengkap**:
  - Data personal dan kontak lengkap
  - Riwayat pendidikan dengan detail institusi
  - Pengalaman kerja dengan deskripsi
  - Skills dan keahlian teknis/soft skills
  - Upload foto profile professional
  - Portfolio dan project showcase
- **Export Options**: 
  - Preview real-time
  - Download PDF high-quality
  - Multiple format support
  - Print-ready templates

### 3. Sistem Cetak & Pesanan Professional
Layanan cetak berkualitas tinggi untuk berbagai kebutuhan:

#### 📄 **Jenis Cetakan Tersedia:**
- **Dokumen Bisnis**: Surat resmi, proposal, laporan, kontrak
- **Foto Digital**: Semua ukuran dari 2x3 hingga A3+ dengan berbagai paper
- **Undangan Fisik**: Versi cetak dari undangan digital dengan finishing premium
- **Marketing Materials**: Kartu nama, brosur, flyer, poster
- **Large Format**: Banner, spanduk, backdrop event
- **Specialty Items**: Stiker vinyl, label, sertifikat, ID card
- **Wedding Stationery**: Save the date, menu, program book

#### 🎨 **Spesifikasi Cetak Premium:**
- **Ukuran Lengkap**: 2x3, 3x4, 4x6, 5x7, 8x10, A5, A4, A3, A2, A1
- **Jenis Kertas Professional**: 
  - HVS 70gsm (ekonomis untuk draft)
  - HVS 80gsm (standard office quality)
  - Art Paper 120gsm (semi glossy, premium feel)
  - Art Carton 230gsm (tebal, business cards)
  - Photo Paper (khusus foto dengan coating)
  - Canvas (untuk artistic prints)
- **Pilihan Warna Advanced**:
  - Grayscale (hitam putih profesional)
  - Full Color CMYK (warna akurat)
  - Pantone Spot Colors (untuk brand consistency)
- **Finishing Premium**: 
  - Laminating (glossy/matte)
  - UV Coating (extra protection)
  - Cutting & trimming precision
  - Binding (spiral, perfect, saddle)
  - Embossing & debossing (luxury effect)

#### 💰 **Harga Kompetitif 2024:**
- **Foto 2x3 warna**: Rp 500/lembar (min 10 pcs)
- **Foto 4x6 premium**: Rp 1.500/lembar  
- **Dokumen A4 HVS**: Rp 300/lembar (bulk discount available)
- **Dokumen A4 full color**: Rp 500/lembar
- **Banner A3 vinyl**: Rp 15.000/lembar
- **Kartu nama (250gsm)**: Rp 50.000/500pcs
- **Wedding invitation**: Mulai Rp 3.000/pcs (include envelope)
- *Harga dapat berubah, konfirmasi terkini via WhatsApp*

### 4. Admin Dashboard Comprehensive
- **Analytics Dashboard**: 
  - Real-time statistics (users, orders, revenue)
  - Popular templates tracking
  - RSVP completion rates
  - Geographic distribution of users
- **User Management Advanced**: 
  - User roles & permissions
  - Premium subscription management
  - Activity logs & audit trail
  - Bulk user operations
- **Order Management System**: 
  - Complete order lifecycle tracking
  - Status updates with notifications
  - Payment verification
  - Printing queue management
  - Customer communication tools
- **Template Management & Architecture**:
- **Unified Template System** - Single wedding_invitation_view.html handles all invitations
- **Design Reference Templates** - Individual template files in wedding_templates/ for designers
- **Base Template (Admin)** - templates/admin/base_template.html as design standard
- **Template Upload** - New templates follow unified structure
- **A/B Testing Ready** - Easy template comparison and analytics
- **Usage Analytics** - Per template performance tracking
- **Version Control** - Template rollback and update management
- **Developer Friendly** - Clear separation of view logic and design assets
- **Content Management**: 
  - Dynamic website content updates
  - SEO optimization tools
  - Multi-language support preparation
  - Media library management

### 5. Security & Authentication
- **Multi-Authentication**: 
  - Google OAuth 2.0 seamless login
  - Traditional email/password with 2FA
  - Social media login integration
  - Guest access for certain features
- **Data Protection**: 
  - HTTPS encryption throughout
  - Secure file upload with virus scanning
  - GDPR compliance ready
  - Automatic data backup
- **Role-Based Access**: 
  - Admin, Premium User, Free User tiers
  - Feature-based permissions
  - Session management with timeout
  - IP-based access control

## 🛠️ Teknologi Stack

- **Backend Framework**: Python Flask (Production-ready)
- **Database**: SQLite with migration to PostgreSQL ready
- **Frontend**: Bootstrap 5.3, Vanilla JS, Progressive Web App ready
- **File Processing**: PIL/Pillow for images, PDF generation
- **Authentication**: Flask-Login, OAuthLib, JWT tokens
- **Media Handling**: 
  - Image optimization & resizing
  - QR code generation with custom logos
  - Audio file processing
  - PDF manipulation
- **API Integration**: 
  - Google Maps API
  - Payment Gateway (Midtrans ready)
  - WhatsApp Business API
  - Email service (SendGrid ready)

## 📦 Quick Setup & Installation

### Prerequisites
- Python 3.8+ (recommended 3.10+)
- Git
- Modern web browser
- Internet connection for dependencies

### Installation Steps

1. **Clone & Navigate**:
```bash
git clone <repository-url>
cd wedding-cv-store
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

3. **Environment Configuration**:
```bash
# Create .env file
export FLASK_SECRET_KEY="your-super-secret-key-here"
export GOOGLE_CLIENT_ID="your-google-oauth-client-id"
export GOOGLE_CLIENT_SECRET="your-google-oauth-client-secret"

# Optional for production
export MAIL_SERVER="smtp.gmail.com"
export MAIL_USERNAME="your-email@gmail.com" 
export MAIL_PASSWORD="your-app-password"
```

4. **Database Initialization**:
```bash
python app.py
# Database will be created automatically on first run
```

5. **Access Application**:
- Open browser: `http://localhost:5000`
- Admin panel: `http://localhost:5000/admin`

## 🔐 Default Admin Access

- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANT**: Change default password immediately in production!

## 📊 Database Schema

### Core Tables:
- **`users`** - Authentication & user profiles
- **`wedding_invitations`** - Complete invitation data with all form fields
- **`wedding_templates`** - Template metadata & settings
- **`wedding_guests`** - RSVP responses & guest messages
- **`cv_templates`** - CV template configurations
- **`orders`** - Print order management with status tracking
- **`admin`** - Admin user management

### Key Features:
- Foreign key relationships for data integrity
- JSON fields for flexible template configurations
- Indexing for performance optimization
- Soft delete capability for audit trail

## 🚀 Deployment Options

### Recommended: Replit (Zero Config)
- One-click deployment
- Automatic SSL certificates
- Built-in database
- Real-time collaboration
- Instant scaling

### Alternative Platforms:
- **Heroku**: `git push heroku main`
- **Railway**: Connect GitHub repo
- **DigitalOcean App Platform**: Dockerfile included
- **VPS**: Nginx + Gunicorn configuration provided

### Production Checklist:
- [ ] Change default admin password
- [ ] Configure environment variables
- [ ] Set up SSL certificates (auto with Replit)
- [ ] Configure backup strategies
- [ ] Set up monitoring (uptime, errors)
- [ ] Configure CDN for static files

## 📞 Support & Contact

- **WhatsApp Business**: +62-821-1234-5678 (24/7 Support)
- **Email Support**: support@fajarmandiri.com
- **Website**: www.fajarmandiri.com
- **Documentation**: docs.fajarmandiri.com
- **Community**: discord.gg/fajarmandiri

## 📈 Roadmap 2024-2025

### Q4 2024
- [ ] Advanced payment gateway integration (Midtrans, QRIS)
- [ ] WhatsApp API for notifications
- [ ] Advanced template editor (drag & drop)
- [ ] Mobile app (PWA) optimization

### Q1 2025
- [ ] Multi-language support (ID, EN)
- [ ] Advanced analytics & reporting
- [ ] Email marketing integration
- [ ] Customer feedback system

### Q2 2025
- [ ] AI-powered template recommendations
- [ ] Video invitation support
- [ ] Advanced photo editing tools
- [ ] Franchise management system

### Q3 2025
- [ ] Enterprise features (white-label)
- [ ] API marketplace for developers
- [ ] Advanced automation workflows
- [ ] International expansion ready

## 🏆 Key Improvements in Latest Version

### Wedding Templates Enhancement:
- **18 Completely Renovated Templates** - All templates now support full form data
- **Universal Opening Screen** - Interactive "BUKA UNDANGAN" button with countdown
- **Enhanced Form Integration** - Every optional field now displays properly
- **Consistent Experience** - Unified UX across all template themes
- **Mobile Optimization** - Perfect responsive design on all devices
- **Performance Optimized** - Faster loading with lazy loading images

### New Template Features:
- Real-time countdown to wedding date
- Smooth animations and transitions
- Background music with user control
- Photo gallery with lightbox
- Maps integration (Google Maps + Navigation)
- RSVP with guest count selection
- Wedding gift section (Bank + QRIS)
- Social sharing capabilities

## 📄 License & Legal

**© 2024 Fajar Mandiri Store. All rights reserved.**

This software is licensed under MIT License. See [LICENSE](LICENSE) file for details.

### Third-Party Attributions:
- Bootstrap 5.3 (MIT License)
- Font Awesome 6.0 (Font Awesome License)
- Google Fonts (OFL)
- Various JavaScript libraries (respective licenses)

### Privacy & Data Protection:
- User data encrypted at rest and in transit
- GDPR compliance ready
- Regular security audits
- Transparent privacy policy

---

**🎉 Platform digital terpercaya untuk kebutuhan undangan pernikahan dan CV profesional Anda.**

*Transforming special moments into beautiful digital experiences since 2024.*

### 🌟 Why Choose Fajar Mandiri Store?

✅ **Professional Quality** - Industry-standard templates and printing
✅ **User-Friendly** - Intuitive interface for all skill levels  
✅ **Comprehensive** - Everything you need in one platform
✅ **Reliable Support** - 24/7 customer service in Indonesian
✅ **Affordable** - Competitive pricing with premium features
✅ **Constantly Updated** - Regular new features and templates
✅ **Local Indonesian** - Built for Indonesian market needs

**Start creating your perfect wedding invitation or professional CV today! 🚀**