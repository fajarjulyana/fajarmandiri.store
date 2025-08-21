
<?php require_once 'config/database.php'; ?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CV Generator - Fajar Mandiri Fotocopy</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .template-preview {
            width: 100%;
            height: 150px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            margin-bottom: 10px;
            position: relative;
            overflow: hidden;
        }
        .template-modern {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .template-professional {
            background: linear-gradient(135deg, #2196F3 0%, #21CBF3 100%);
        }
        .template-creative {
            background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%);
        }
        .template-select {
            cursor: pointer;
            border: 3px solid transparent;
            border-radius: 15px;
            transition: all 0.3s ease;
        }
        .template-select:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        .template-select.selected {
            border-color: #0d6efd;
            box-shadow: 0 8px 25px rgba(13,110,253,0.3);
        }
        .cv-preview {
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .preview-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .preview-foto img {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            border: 3px solid white;
            object-fit: cover;
        }
        .form-section {
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .section-title {
            color: #495057;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .btn-action {
            padding: 12px 30px;
            border-radius: 25px;
            font-weight: 600;
        }
        .skill-input {
            margin-bottom: 10px;
        }
        .experience-item, .education-item {
            border: 1px solid #e9ecef;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            background: #f8f9fa;
        }
    </style>
</head>
<body style="background-color: #f8f9fa;">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand fw-bold" href="index.php">Fajar Mandiri Fotocopy</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="order.php">Buat Pesanan</a>
                    <a class="nav-link" href="status.php">Cek Status</a>
                    <a class="nav-link active" href="cv_generator.php">CV Generator</a>
                    <a class="nav-link" href="about.php">Tentang</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="text-center mb-4">
            <h2 class="fw-bold text-primary">
                <i class="fas fa-file-alt me-2"></i>CV Generator Profesional
            </h2>
            <p class="text-muted">Buat CV profesional dengan mudah dan cepat</p>
        </div>

        <div class="row">
            <div class="col-lg-8">
                <form id="cvForm" enctype="multipart/form-data">
                    <!-- Template Selection -->
                    <div class="form-section">
                        <h4 class="section-title">
                            <i class="fas fa-palette me-2"></i>Pilih Template
                        </h4>
                        <div class="row">
                            <div class="col-md-4">
                                <div class="template-select" data-template="modern">
                                    <div class="template-preview template-modern">
                                        <div>
                                            <i class="fas fa-user-tie fa-2x mb-2"></i>
                                            <div>Modern</div>
                                        </div>
                                    </div>
                                    <p class="text-center fw-bold">Modern & Clean</p>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="template-select" data-template="professional">
                                    <div class="template-preview template-professional">
                                        <div>
                                            <i class="fas fa-briefcase fa-2x mb-2"></i>
                                            <div>Professional</div>
                                        </div>
                                    </div>
                                    <p class="text-center fw-bold">Professional</p>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="template-select" data-template="creative">
                                    <div class="template-preview template-creative">
                                        <div>
                                            <i class="fas fa-paint-brush fa-2x mb-2"></i>
                                            <div>Creative</div>
                                        </div>
                                    </div>
                                    <p class="text-center fw-bold">Creative & Bold</p>
                                </div>
                            </div>
                        </div>
                        <input type="hidden" id="selectedTemplate" name="template" required>
                    </div>

                    <!-- Personal Information -->
                    <div class="form-section">
                        <h4 class="section-title">
                            <i class="fas fa-user me-2"></i>Informasi Pribadi
                        </h4>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Foto Profil</label>
                                    <input type="file" class="form-control" id="foto" accept="image/*">
                                    <div id="preview" class="mt-2"></div>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Nama Lengkap *</label>
                                    <input type="text" class="form-control" id="nama" required>
                                </div>
                                <div class="mb-3">
                                    <label class="form-label">Profesi/Posisi yang Dilamar</label>
                                    <input type="text" class="form-control" id="profesi">
                                </div>
                            </div>
                        </div>
                        <div class="row">
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Email *</label>
                                    <input type="email" class="form-control" id="email" required>
                                </div>
                            </div>
                            <div class="col-md-6">
                                <div class="mb-3">
                                    <label class="form-label">Nomor Telepon/WhatsApp</label>
                                    <input type="tel" class="form-control" id="telepon">
                                </div>
                            </div>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Alamat</label>
                            <textarea class="form-control" id="alamat" rows="2"></textarea>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">Ringkasan Diri/Objektif</label>
                            <textarea class="form-control" id="ringkasan" rows="3" placeholder="Ceritakan singkat tentang diri Anda dan tujuan karir..."></textarea>
                        </div>
                    </div>

                    <!-- Pendidikan -->
                    <div class="form-section">
                        <h4 class="section-title">
                            <i class="fas fa-graduation-cap me-2"></i>Pendidikan
                        </h4>
                        <div id="pendidikanContainer">
                            <div class="education-item">
                                <div class="row">
                                    <div class="col-md-6">
                                        <input type="text" class="form-control mb-2" placeholder="Nama Institusi" name="pendidikan_institusi[]">
                                        <input type="text" class="form-control mb-2" placeholder="Program Studi/Jurusan" name="pendidikan_jurusan[]">
                                    </div>
                                    <div class="col-md-6">
                                        <input type="text" class="form-control mb-2" placeholder="Tahun (2020-2024)" name="pendidikan_tahun[]">
                                        <input type="text" class="form-control mb-2" placeholder="IPK/Nilai (opsional)" name="pendidikan_nilai[]">
                                    </div>
                                </div>
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="addEducation()">
                            <i class="fas fa-plus me-1"></i>Tambah Pendidikan
                        </button>
                    </div>

                    <!-- Pengalaman Kerja -->
                    <div class="form-section">
                        <h4 class="section-title">
                            <i class="fas fa-briefcase me-2"></i>Pengalaman Kerja
                        </h4>
                        <div id="pengalamanContainer">
                            <div class="experience-item">
                                <div class="row">
                                    <div class="col-md-6">
                                        <input type="text" class="form-control mb-2" placeholder="Nama Perusahaan" name="pengalaman_perusahaan[]">
                                        <input type="text" class="form-control mb-2" placeholder="Posisi/Jabatan" name="pengalaman_posisi[]">
                                    </div>
                                    <div class="col-md-6">
                                        <input type="text" class="form-control mb-2" placeholder="Periode (Jan 2020 - Des 2022)" name="pengalaman_periode[]">
                                        <textarea class="form-control" rows="2" placeholder="Deskripsi pekerjaan dan pencapaian..." name="pengalaman_deskripsi[]"></textarea>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="addExperience()">
                            <i class="fas fa-plus me-1"></i>Tambah Pengalaman
                        </button>
                    </div>

                    <!-- Keahlian -->
                    <div class="form-section">
                        <h4 class="section-title">
                            <i class="fas fa-cogs me-2"></i>Keahlian & Kemampuan
                        </h4>
                        <div id="keahlianContainer">
                            <div class="skill-input">
                                <input type="text" class="form-control mb-2" placeholder="Masukkan keahlian (misal: Microsoft Office, Photoshop, dll)" name="keahlian[]">
                            </div>
                        </div>
                        <button type="button" class="btn btn-outline-primary btn-sm" onclick="addSkill()">
                            <i class="fas fa-plus me-1"></i>Tambah Keahlian
                        </button>
                    </div>

                    <!-- Tombol Aksi -->
                    <div class="form-section text-center">
                        <button type="button" class="btn btn-outline-primary btn-action me-2" onclick="previewCV()">
                            <i class="fas fa-eye me-2"></i>Preview CV
                        </button>
                        <button type="submit" class="btn btn-success btn-action">
                            <i class="fas fa-download me-2"></i>Download PDF
                        </button>
                    </div>
                </form>
            </div>

            <div class="col-lg-4">
                <!-- Preview CV -->
                <div id="cvPreview" class="cv-preview mb-4" style="display: none;">
                    <div class="preview-header">
                        <div class="preview-foto mb-2"></div>
                        <h4 class="preview-nama mb-1"></h4>
                        <div class="preview-profesi mb-2"></div>
                        <div class="preview-kontak"></div>
                    </div>
                    <div class="p-3">
                        <div class="preview-content"></div>
                    </div>
                </div>

                <!-- Panduan -->
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">
                            <i class="fas fa-info-circle me-2"></i>Panduan Penggunaan
                        </h5>
                        <div class="card-text">
                            <div class="mb-2">
                                <i class="fas fa-check text-success me-2"></i>
                                Pilih template yang sesuai dengan bidang pekerjaan
                            </div>
                            <div class="mb-2">
                                <i class="fas fa-check text-success me-2"></i>
                                Upload foto profil yang profesional
                            </div>
                            <div class="mb-2">
                                <i class="fas fa-check text-success me-2"></i>
                                Isi semua informasi dengan lengkap dan akurat
                            </div>
                            <div class="mb-2">
                                <i class="fas fa-check text-success me-2"></i>
                                Gunakan fitur preview sebelum download
                            </div>
                            <div class="mb-2">
                                <i class="fas fa-check text-success me-2"></i>
                                CV akan diformat otomatis sesuai template
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Preview foto
        document.getElementById('foto').addEventListener('change', function(e) {
            const preview = document.getElementById('preview');
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    preview.innerHTML = `<img src="${e.target.result}" style="max-width: 150px; max-height: 150px; border-radius: 10px; object-fit: cover;">`;
                }
                reader.readAsDataURL(file);
            }
        });

        // Pilih template
        document.querySelectorAll('.template-select').forEach(template => {
            template.addEventListener('click', function() {
                document.querySelectorAll('.template-select').forEach(t => t.classList.remove('selected'));
                this.classList.add('selected');
                document.getElementById('selectedTemplate').value = this.dataset.template;
            });
        });

        // Fungsi tambah pendidikan
        function addEducation() {
            const container = document.getElementById('pendidikanContainer');
            const div = document.createElement('div');
            div.className = 'education-item';
            div.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <input type="text" class="form-control mb-2" placeholder="Nama Institusi" name="pendidikan_institusi[]">
                        <input type="text" class="form-control mb-2" placeholder="Program Studi/Jurusan" name="pendidikan_jurusan[]">
                    </div>
                    <div class="col-md-6">
                        <input type="text" class="form-control mb-2" placeholder="Tahun (2020-2024)" name="pendidikan_tahun[]">
                        <input type="text" class="form-control mb-2" placeholder="IPK/Nilai (opsional)" name="pendidikan_nilai[]">
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.parentElement.remove()">
                    <i class="fas fa-trash"></i> Hapus
                </button>
            `;
            container.appendChild(div);
        }

        // Fungsi tambah pengalaman
        function addExperience() {
            const container = document.getElementById('pengalamanContainer');
            const div = document.createElement('div');
            div.className = 'experience-item';
            div.innerHTML = `
                <div class="row">
                    <div class="col-md-6">
                        <input type="text" class="form-control mb-2" placeholder="Nama Perusahaan" name="pengalaman_perusahaan[]">
                        <input type="text" class="form-control mb-2" placeholder="Posisi/Jabatan" name="pengalaman_posisi[]">
                    </div>
                    <div class="col-md-6">
                        <input type="text" class="form-control mb-2" placeholder="Periode (Jan 2020 - Des 2022)" name="pengalaman_periode[]">
                        <textarea class="form-control" rows="2" placeholder="Deskripsi pekerjaan dan pencapaian..." name="pengalaman_deskripsi[]"></textarea>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger" onclick="this.parentElement.remove()">
                    <i class="fas fa-trash"></i> Hapus
                </button>
            `;
            container.appendChild(div);
        }

        // Fungsi tambah keahlian
        function addSkill() {
            const container = document.getElementById('keahlianContainer');
            const div = document.createElement('div');
            div.className = 'skill-input';
            div.innerHTML = `
                <div class="input-group mb-2">
                    <input type="text" class="form-control" placeholder="Masukkan keahlian" name="keahlian[]">
                    <button type="button" class="btn btn-outline-danger" onclick="this.parentElement.parentElement.remove()">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(div);
        }

        // Preview CV
        function previewCV() {
            const preview = document.getElementById('cvPreview');
            preview.style.display = 'block';
            
            // Update preview nama dan profesi
            document.querySelector('.preview-nama').textContent = document.getElementById('nama').value || 'Nama Lengkap';
            document.querySelector('.preview-profesi').textContent = document.getElementById('profesi').value || 'Profesi';
            
            // Update kontak
            const email = document.getElementById('email').value;
            const telepon = document.getElementById('telepon').value;
            const alamat = document.getElementById('alamat').value;
            
            document.querySelector('.preview-kontak').innerHTML = `
                ${email ? `<div><i class="fas fa-envelope me-1"></i>${email}</div>` : ''}
                ${telepon ? `<div><i class="fas fa-phone me-1"></i>${telepon}</div>` : ''}
                ${alamat ? `<div><i class="fas fa-map-marker-alt me-1"></i>${alamat}</div>` : ''}
            `;
            
            // Update foto
            const fotoInput = document.getElementById('foto');
            if (fotoInput.files && fotoInput.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.querySelector('.preview-foto').innerHTML = `<img src="${e.target.result}">`;
                }
                reader.readAsDataURL(fotoInput.files[0]);
            } else {
                document.querySelector('.preview-foto').innerHTML = `<i class="fas fa-user fa-3x"></i>`;
            }
            
            // Update konten
            let content = '';
            
            const ringkasan = document.getElementById('ringkasan').value;
            if (ringkasan) {
                content += `<h6><i class="fas fa-user-circle me-2"></i>Ringkasan</h6><p class="small">${ringkasan}</p>`;
            }
            
            // Pendidikan
            const pendidikanInstitusi = document.querySelectorAll('input[name="pendidikan_institusi[]"]');
            if (pendidikanInstitusi.length > 0 && pendidikanInstitusi[0].value) {
                content += `<h6><i class="fas fa-graduation-cap me-2"></i>Pendidikan</h6>`;
                pendidikanInstitusi.forEach((input, index) => {
                    if (input.value) {
                        const jurusan = document.querySelectorAll('input[name="pendidikan_jurusan[]"]')[index].value;
                        const tahun = document.querySelectorAll('input[name="pendidikan_tahun[]"]')[index].value;
                        content += `<div class="small mb-2"><strong>${input.value}</strong><br>${jurusan}<br><em>${tahun}</em></div>`;
                    }
                });
            }
            
            // Pengalaman
            const pengalamanPerusahaan = document.querySelectorAll('input[name="pengalaman_perusahaan[]"]');
            if (pengalamanPerusahaan.length > 0 && pengalamanPerusahaan[0].value) {
                content += `<h6><i class="fas fa-briefcase me-2"></i>Pengalaman</h6>`;
                pengalamanPerusahaan.forEach((input, index) => {
                    if (input.value) {
                        const posisi = document.querySelectorAll('input[name="pengalaman_posisi[]"]')[index].value;
                        const periode = document.querySelectorAll('input[name="pengalaman_periode[]"]')[index].value;
                        const deskripsi = document.querySelectorAll('textarea[name="pengalaman_deskripsi[]"]')[index].value;
                        content += `<div class="small mb-2"><strong>${posisi}</strong> - ${input.value}<br><em>${periode}</em><br>${deskripsi}</div>`;
                    }
                });
            }
            
            // Keahlian
            const keahlianInputs = document.querySelectorAll('input[name="keahlian[]"]');
            const keahlianList = Array.from(keahlianInputs).map(input => input.value).filter(value => value.trim() !== '');
            if (keahlianList.length > 0) {
                content += `<h6><i class="fas fa-cogs me-2"></i>Keahlian</h6><p class="small">${keahlianList.join(', ')}</p>`;
            }
            
            document.querySelector('.preview-content').innerHTML = content;
            
            // Scroll ke preview
            document.getElementById('cvPreview').scrollIntoView({ behavior: 'smooth', block: 'start' });
        }

        // Submit form
        document.getElementById('cvForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!document.getElementById('selectedTemplate').value) {
                alert('Silakan pilih template terlebih dahulu!');
                return;
            }
            
            if (!document.getElementById('nama').value || !document.getElementById('email').value) {
                alert('Nama dan email wajib diisi!');
                return;
            }
            
            // Kirim ke generate_cv.php
            this.action = 'generate_cv.php';
            this.method = 'POST';
            this.submit();
        });
    </script>
</body>
</html>
