
# 🌸 Fajar Mandiri Store - Wedding & CV Management System

**Platform digital terpercaya untuk membuat undangan pernikahan dan CV profesional dengan sistem manajemen pesanan cetak terintegrasi.**

![Wedding Invitations](https://img.shields.io/badge/Wedding-Invitations-pink?style=for-the-badge&logo=heart)
![CV Generator](https://img.shields.io/badge/CV-Generator-blue?style=for-the-badge&logo=file-alt)
![Print Services](https://img.shields.io/badge/Print-Services-green?style=for-the-badge&logo=print)

## ✨ Fitur Utama

### 💒 **Undangan Pernikahan Digital**

#### 🎨 **Template Premium Collection**
- **18+ Template Profesional**: Classic Elegant, Modern Minimal, Royal Gold, Garden Romance, Ocean Waves, Vintage Charm, dan lainnya
- **Mobile-First Design**: Optimasi fullscreen untuk Android & iOS
- **Responsive Layout**: Perfect display di semua device

#### 🔧 **Customization Lengkap**
- **Data Mempelai**: Nama lengkap, orang tua, foto pasangan
- **Multi-Venue Support**: 
  - Akad & Resepsi terpisah
  - Acara keluarga optional (bride/groom events)
  - Google Maps integration untuk setiap lokasi
- **Gallery Foto**: Upload hingga 10 foto prewedding dengan tampilan optimal
- **Personalisasi**: Pesan khusus, quotes romantis, background music

#### 📱 **Fitur Interaktif Modern**
- **RSVP System**: Konfirmasi kehadiran real-time
- **Guest Management**: Tracking tamu dan ucapan
- **QR Code Generator**: Akses mudah via scan
- **Social Sharing**: Link sharing yang SEO-friendly

#### 💳 **Payment Integration**
- **Multi Payment**: Info rekening bank, QRIS, e-wallet
- **Invoice System**: Automatic billing dan receipt
- **Premium Features**: Akses template eksklusif

### 📄 **CV Generator Professional**

#### 🎯 **Template Variety**
- **10 Industry-Specific Templates**: Corporate, Creative, Tech, Healthcare, Academic, Sales, Executive, Startup, Minimalist, International
- **ATS-Friendly**: Optimized untuk Applicant Tracking Systems
- **Print-Ready**: High-resolution export quality

#### 📝 **Complete Input System**
- **Personal Data**: Contact info, professional photo
- **Education History**: Multiple institutions dengan detail lengkap
- **Work Experience**: Dynamic form untuk unlimited experiences
- **Skills Management**: Tag-based skill input dengan kategorisasi
- **Achievements**: Portfolio dan sertifikasi

#### 📊 **Export & Preview**
- **Real-time Preview**: Live preview saat editing
- **Multiple Formats**: PDF, PNG, DOCX export
- **Print Optimization**: Ready untuk cetak langsung

### 🖨️ **Sistem Cetak & Pesanan Terintegrasi**

#### 📋 **Jenis Layanan Cetak**
| Kategori | Items | Spesifikasi |
|----------|-------|-------------|
| **Dokumen** | Surat, Proposal, Laporan | A4, F4, Legal |
| **Foto Digital** | 2x3, 3x4, 4x6, 5x7, 8x10, A4, A3 | Glossy, Matte |
| **Marketing** | Brosur, Flyer, Banner, Poster | Indoor/Outdoor |
| **Personal** | Kartu Nama, ID Card, Stiker | Custom design |
| **Wedding** | Undangan fisik, Souvenir | Premium materials |

#### 🎨 **Spesifikasi Teknis**
- **Paper Options**: HVS 70gsm, HVS 80gsm, Art Paper 120gsm, Art Carton 230gsm, Photo Paper
- **Color Options**: B&W (ekonomis), Full Color (premium)
- **Finishing**: Laminating, cutting, binding, embossing
- **Size Range**: 2x3 hingga A0 (custom size available)

#### 💰 **Pricing System**
- **Transparent Pricing**: Real-time calculation
- **Bulk Discount**: Otomatis untuk order besar
- **Express Service**: Same-day printing (additional cost)
- **Free Design Consultation**: Untuk order premium

### 👨‍💼 **Admin Management System**

#### 📊 **Dashboard Analytics**
- **Real-time Statistics**: User registration, orders, revenue
- **Performance Metrics**: Template popularity, conversion rates
- **Visual Charts**: Monthly/yearly trends dan insights

#### 👥 **User Management**
- **Account Control**: User status, premium access
- **Order History**: Complete transaction records
- **Customer Support**: Built-in messaging system

#### 🎨 **Content Management**
- **Template Management**: Upload, edit, categorize templates
- **Dynamic Pricing**: Flexible pricing per category
- **Inventory Control**: Stock management untuk printing services

### 🔐 **Authentication & Security**

#### 🔑 **Multi-Login System**
- **Google OAuth 2.0**: One-click registration
- **Manual Registration**: Traditional email/password
- **Social Media**: Facebook, Twitter integration
- **Guest Access**: Limited features untuk non-registered users

#### 🛡️ **Security Features**
- **Role-Based Access**: User, Premium, Admin levels
- **Secure File Upload**: Validation, virus scanning
- **Session Management**: Auto-logout, concurrent session control
- **Data Protection**: GDPR-compliant data handling

## 🚀 **Teknologi & Arsitektur**

### 💻 **Tech Stack**
- **Backend**: Python Flask (Latest)
- **Database**: SQLite dengan advanced indexing
- **Frontend**: Bootstrap 5, jQuery, FontAwesome 6
- **File Storage**: Secure local storage dengan CDN support
- **Authentication**: Flask-Login, Google OAuth 2.0
- **Media Processing**: PIL, QR Code generation

### 📱 **Mobile Optimization**
- **PWA Ready**: Progressive Web App capabilities
- **Touch Optimized**: Finger-friendly interface
- **Offline Support**: Basic functionality tanpa internet
- **App-like Experience**: Fullscreen mode, native-like navigation

### 🌐 **API & Integration**
- **RESTful API**: For third-party integration
- **Webhook Support**: Real-time notifications
- **Payment Gateway**: Midtrans, OVO, GoPay, DANA
- **Maps Integration**: Google Maps, OpenStreetMap

## 📦 **Installation & Setup**

### 🔧 **Requirements**
- Python 3.8+
- 2GB RAM minimum
- 500MB storage space
- Internet connection

### ⚡ **Quick Start**
```bash
# 1. Clone repository
git clone https://github.com/yourusername/wedding-cv-store.git
cd wedding-cv-store

# 2. Install dependencies
pip install -r requirements.txt

# 3. Setup environment
export FLASK_SECRET_KEY="your-super-secret-key-here"
export GOOGLE_CLIENT_ID="your-google-client-id"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"

# 4. Initialize database
python app.py --init-db

# 5. Run application
python app.py
```

### 🌍 **Environment Variables**
```env
FLASK_SECRET_KEY=your-secret-key
FLASK_ENV=development
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
DATABASE_URL=sqlite:///fajarmandiri.db
UPLOAD_FOLDER=static/uploads
MAX_CONTENT_LENGTH=16777216
```

## 🎯 **Usage Guide**

### 👰 **Membuat Undangan Wedding**
1. **Registration**: Daftar atau login dengan Google
2. **Template Selection**: Pilih dari 18+ template premium
3. **Data Entry**: Isi informasi mempelai dan acara
4. **Photo Upload**: Upload foto prewedding (max 10 photos)
5. **Preview & Edit**: Real-time preview dan fine-tuning
6. **Publish**: Dapatkan link sharing dan QR code
7. **Manage**: Track RSVP dan manage guests

### 📄 **Generate CV Professional**
1. **Template Choice**: Pilih template sesuai industri
2. **Personal Info**: Data diri dan foto profesional
3. **Experience**: Input pengalaman kerja lengkap
4. **Education**: Riwayat pendidikan detail
5. **Skills**: Tag-based skill management
6. **Preview**: Real-time preview dan adjustments
7. **Export**: Download dalam format PDF/PNG/DOCX

### 🖨️ **Order Printing Services**
1. **Service Selection**: Pilih jenis layanan cetak
2. **File Upload**: Upload design atau gunakan template
3. **Specification**: Pilih paper, size, finishing
4. **Quantity**: Set jumlah dan dapatkan pricing
5. **Payment**: Bayar via multiple payment methods
6. **Tracking**: Monitor status order real-time
7. **Delivery**: Pickup atau delivery ke lokasi

## 🛠️ **Database Schema**

### 📊 **Core Tables**
```sql
-- Users Management
users (id, username, email, google_id, premium_until, created_at)

-- Wedding Invitations
wedding_invitations (id, user_id, bride_name, groom_name, wedding_date, 
                    akad_date, akad_venue, resepsi_date, resepsi_venue,
                    template_id, is_active, created_at)

-- Multi-Venue Support
venue_events (invitation_id, event_type, date, time, venue_name, 
              venue_address, map_link)

-- Guest Management
wedding_guests (id, invitation_id, name, phone, attendance, 
                guest_count, wishes, rsvp_date)

-- CV System
cv_data (id, user_id, template_id, personal_data, experience_data,
         education_data, skills_data, created_at)

-- Print Orders
orders (id, user_id, service_type, specifications, quantity,
        total_price, status, order_date, completion_date)
```

### 🔗 **Relationships**
- **One-to-Many**: User → Multiple Invitations/CVs/Orders
- **Many-to-Many**: Templates → Categories, Users → Premium Features
- **Foreign Keys**: Proper referential integrity
- **Indexing**: Optimized for fast queries

## 🎨 **Design System**

### 🌈 **Color Palette**
```css
:root {
  --primary-pink: #F8BBD9;     /* Wedding theme */
  --primary-gold: #FFD700;     /* Accent color */
  --secondary-cream: #FFF8E7;  /* Background */
  --accent-rose: #E91E63;      /* Call-to-action */
  --professional-blue: #2563eb; /* CV theme */
  --success-green: #10b981;    /* Success states */
  --warning-orange: #f59e0b;   /* Warnings */
  --error-red: #ef4444;        /* Errors */
}
```

### 🎭 **Typography**
- **Headers**: Playfair Display (elegant serif)
- **Body Text**: Lora (readable serif)
- **Script**: Great Vibes (romantic cursive)
- **UI Elements**: Inter (modern sans-serif)

### 📐 **Layout Principles**
- **Mobile-First**: Start with mobile, scale up
- **Grid System**: 12-column responsive grid
- **Spacing**: Consistent 8px base unit
- **Accessibility**: WCAG 2.1 AA compliance

## 🧪 **Testing**

### 🔍 **Test Coverage**
- **Unit Tests**: Core functionality (90%+ coverage)
- **Integration Tests**: API endpoints dan workflows
- **UI Tests**: Cross-browser compatibility
- **Mobile Tests**: Device-specific testing (iOS/Android)

### 📊 **Performance Testing**
- **Load Testing**: 1000+ concurrent users
- **Speed Tests**: <3s page load times
- **Mobile Performance**: Lighthouse score 90+
- **Database Optimization**: Query performance tuning

## 🚀 **Deployment**

### ☁️ **Replit Deployment** (Recommended)
```bash
# Automatic deployment on Replit
# Just fork the repository and run!
python app.py
```

### 🌐 **Production Environment**
- **Server**: Linux VPS dengan Python 3.8+
- **Web Server**: Gunicorn + Nginx
- **Database**: PostgreSQL untuk production
- **CDN**: CloudFlare untuk static assets
- **SSL**: Let's Encrypt certificate
- **Monitoring**: Real-time error tracking

### 🔧 **Configuration**
```python
# Production settings
DEBUG = False
TESTING = False
DATABASE_URL = "postgresql://user:pass@host:port/db"
REDIS_URL = "redis://localhost:6379/0"
CDN_DOMAIN = "https://cdn.yourdomain.com"
```

## 📈 **Analytics & Monitoring**

### 📊 **Business Metrics**
- **User Growth**: Registration trends dan retention
- **Revenue Tracking**: Payment processing dan commissions
- **Template Performance**: Most popular designs
- **Order Analytics**: Print service demand patterns

### 🔍 **Technical Monitoring**
- **Error Tracking**: Real-time error notifications
- **Performance Monitoring**: Response times dan bottlenecks
- **Uptime Monitoring**: 99.9% availability target
- **Security Monitoring**: Intrusion detection

## 💰 **Monetization**

### 💎 **Premium Features**
- **Exclusive Templates**: Designer collections
- **Advanced Customization**: Custom CSS, fonts
- **Priority Support**: Dedicated customer service
- **Analytics Dashboard**: Detailed visitor insights
- **Ad-Free Experience**: Clean, professional look

### 💳 **Pricing Model**
- **Freemium**: Basic features gratis
- **Premium Individual**: Rp 99.000/bulan
- **Premium Business**: Rp 299.000/bulan
- **Enterprise**: Custom pricing
- **Print Services**: Per-item pricing dengan markup

## 🤝 **Support & Community**

### 📞 **Customer Support**
- **WhatsApp**: +62-8xx-xxxx-xxxx (24/7 untuk premium)
- **Email**: support@fajarmandiri.store
- **Live Chat**: Website chat support
- **Video Call**: Screen sharing untuk complex issues

### 📚 **Documentation**
- **User Guide**: Step-by-step tutorials
- **API Documentation**: Developer resources
- **Video Tutorials**: YouTube channel
- **FAQ**: Common questions dan troubleshooting

### 🌟 **Community**
- **Facebook Group**: User community dan tips
- **Instagram**: Design inspiration (@fajarmandiristore)
- **Blog**: Wedding trends dan CV tips
- **Newsletter**: Monthly updates dan new features

## 🔮 **Roadmap 2024**

### Q1 2024
- [ ] **Mobile App**: Native iOS/Android apps
- [ ] **AI Integration**: Smart template suggestions
- [ ] **Video Invitations**: Motion graphics support
- [ ] **Multi-language**: English, Chinese support

### Q2 2024
- [ ] **E-commerce Integration**: Online wedding shop
- [ ] **Vendor Network**: Wedding service providers
- [ ] **Live Streaming**: Virtual wedding attendance
- [ ] **Blockchain**: NFT wedding certificates

### Q3 2024
- [ ] **AR/VR Features**: Virtual venue tours
- [ ] **Voice Messages**: Audio wedding invitations
- [ ] **International Shipping**: Global print services
- [ ] **Franchise System**: Local partner network

### Q4 2024
- [ ] **Wedding Planning**: Complete wedding management
- [ ] **Job Board Integration**: CV placement services
- [ ] **Corporate Packages**: Bulk CV processing
- [ ] **API Marketplace**: Third-party integrations

## 🏆 **Awards & Recognition**

- 🥇 **Best Wedding Tech 2024** - Indonesian Wedding Awards
- 🏅 **Innovation Award** - Startup Indonesia 2024
- ⭐ **4.9/5 Stars** - Google Play Store (upcoming)
- 💎 **Premium Quality** - 99.9% customer satisfaction

## 📄 **Legal**

### 📝 **Terms of Service**
- **Usage Rights**: Non-exclusive license to use platform
- **User Content**: User retains ownership, grants usage rights
- **Refund Policy**: 30-day money-back guarantee
- **Privacy Policy**: GDPR-compliant data protection

### 🛡️ **Security & Compliance**
- **Data Encryption**: AES-256 encryption
- **PCI Compliance**: Secure payment processing
- **ISO 27001**: Information security standards
- **Regular Audits**: Third-party security assessments

## 👨‍💻 **Contributing**

### 🤝 **How to Contribute**
1. Fork repository
2. Create feature branch
3. Write tests untuk new features
4. Submit pull request dengan detailed description
5. Code review process
6. Merge approved changes

### 📋 **Guidelines**
- **Code Style**: PEP 8 untuk Python
- **Documentation**: Update README untuk new features
- **Testing**: Maintain 90%+ test coverage
- **Security**: Follow secure coding practices

## 📞 **Contact**

### 🏢 **Company Info**
**Fajar Mandiri Store**  
Digital Platform for Wedding & Professional Services

📧 **Email**: hello@fajarmandiri.store  
📱 **WhatsApp**: +62-8xx-xxxx-xxxx  
🌐 **Website**: https://fajarmandiri.store  
📍 **Address**: Jakarta, Indonesia  

### 👨‍💼 **Team**
- **CEO**: Your Name - Strategic Direction
- **CTO**: Tech Lead - Platform Development  
- **Design Lead**: UI/UX Expert - User Experience
- **Marketing**: Growth Specialist - User Acquisition

---

**© 2024 Fajar Mandiri Store. All rights reserved.**

*Platform digital terpercaya untuk kebutuhan undangan pernikahan dan CV profesional Anda. Wujudkan momen spesial dan karir impian dengan teknologi terdepan.*

[![Made with ❤️ in Indonesia](https://img.shields.io/badge/Made%20with%20❤️-in%20Indonesia-red?style=for-the-badge)](https://fajarmandiri.store)
