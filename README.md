
# Fajar Mandiri Store - Wedding & CV Management System

Platform digital untuk membuat undangan pernikahan dan CV profesional dengan sistem manajemen pesanan cetak yang terintegrasi.

## 🌟 Fitur Utama

### 1. Undangan Pernikahan Digital
- **Template Beragam**: 10+ template professional (Classic Elegant, Modern Minimal, Royal Gold, dll)
- **Customization Lengkap**: 
  - Data mempelai dan orang tua
  - Tanggal, waktu, dan lokasi acara
  - Pesan personal dan ucapan
  - Upload foto prewedding (maksimal 10 foto)
  - Background music (default atau upload custom)
- **Fitur Interaktif**:
  - RSVP konfirmasi kehadiran tamu
  - Ucapan dan doa dari tamu
  - QR Code untuk akses mudah
  - Link sharing yang mudah
- **Payment Integration**: 
  - Info rekening bank
  - QRIS code upload
- **Management**: Kelola status aktif/nonaktif, analytics dasar

### 2. CV Generator Professional
- **10 Template Premium**: Dari corporate hingga creative design
- **Input Lengkap**:
  - Data personal dan kontak
  - Riwayat pendidikan
  - Pengalaman kerja
  - Skills dan keahlian
  - Upload foto profile
- **Export Options**: Preview dan download dalam berbagai format

### 3. Sistem Cetak & Pesanan
Layanan cetak profesional untuk berbagai kebutuhan:

#### 📄 **Jenis Cetakan Tersedia:**
- **Dokumen Umum**: Surat, proposal, laporan
- **Foto Digital**: Berbagai ukuran dari 2x3 hingga A3
- **Undangan Cetak**: Versi fisik undangan digital
- **Kartu Nama**: Design custom dan template
- **Banner & Poster**: Indoor dan outdoor
- **Stiker & Label**: Berbagai bentuk dan ukuran
- **Sertifikat**: Template professional
- **ID Card**: Karyawan, mahasiswa, member

#### 🎨 **Spesifikasi Cetak:**
- **Ukuran Foto**: 2x3, 3x4, 4x6, 5x7, 8x10, A4, A3
- **Jenis Kertas**: 
  - HVS 70gsm (ekonomis)
  - HVS 80gsm (standard)
  - Art Paper 120gsm (semi glossy)
  - Art Carton 230gsm (tebal, premium)
  - Photo Paper (khusus foto)
- **Pilihan Warna**:
  - Hitam Putih (ekonomis)
  - Warna Full Color (premium)
- **Finishing**: Laminating, cutting, binding tersedia

#### 💰 **Estimasi Harga:**
- Foto 2x3 warna: Rp 500/lembar
- Foto 4x6 warna: Rp 1.500/lembar  
- Dokumen A4 HVS: Rp 300/lembar
- Dokumen A4 warna: Rp 500/lembar
- Banner A3: Rp 15.000/lembar
- *Harga dapat berubah, konfirmasi via WhatsApp*

### 4. Manajemen Admin
- **Dashboard Analytics**: Statistik user, pesanan, template
- **User Management**: Kelola akun dan status premium
- **Order Management**: Track dan update status pesanan
- **Template Management**: Upload dan kelola template baru
- **Content Management**: Update konten website

### 5. Sistem Authentication
- **Multi Login**: Google OAuth dan manual registration
- **Role Management**: User dan Admin terpisah
- **Session Security**: Secure session management
- **Premium Features**: Akses template eksklusif

## 🛠️ Teknologi

- **Backend**: Python Flask
- **Database**: SQLite dengan relational structure
- **Frontend**: Bootstrap 5, jQuery, FontAwesome
- **File Management**: Secure upload dengan validation
- **Authentication**: Flask-Login, Google OAuth 2.0
- **Media Handling**: Image processing, QR code generation

## 📦 Instalasi

1. Clone repository:
```bash
git clone <repository-url>
cd wedding-cv-store
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup environment variables:
```bash
export FLASK_SECRET_KEY="your-secret-key"
export GOOGLE_CLIENT_ID="your-google-client-id"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
```

4. Jalankan aplikasi:
```bash
python app.py
```

5. Akses di browser: `http://localhost:5000`

## 🔐 Default Admin

- Username: `admin`
- Password: `admin123`

*Pastikan untuk mengubah password default di production!*

## 📁 Struktur Database

### Tables:
- `users` - Data pengguna dan authentication
- `wedding_invitations` - Data undangan pernikahan
- `wedding_templates` - Template undangan
- `wedding_guests` - Data tamu dan RSVP
- `cv_templates` - Template CV
- `orders` - Pesanan cetak
- `admin` - Data admin

## 🚀 Deployment

Aplikasi siap deploy di:
- **Replit** (recommended)
- Heroku
- VPS dengan Python support
- Cloud platforms (AWS, GCP, Azure)

## 📞 Support & Kontak

- **WhatsApp**: +62-xxx-xxxx-xxxx
- **Email**: support@fajarmandiri.com
- **Website**: www.fajarmandiri.com

## 📝 Roadmap

- [ ] Payment gateway integration
- [ ] Mobile app version
- [ ] Advanced analytics
- [ ] Email notifications
- [ ] Template marketplace
- [ ] Multi-language support
- [ ] API for third-party integration

---

**© 2024 Fajar Mandiri Store. All rights reserved.**

*Platform digital terpercaya untuk kebutuhan undangan pernikahan dan CV profesional Anda.*
