<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fajar Mandiri Fotocopy - Print Order System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .hero-section {
            background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('assets/hero.jpg') center/cover;
            min-height: 80vh;
            display: flex;
            align-items: center;
        }
        .service-card {
            transition: transform 0.3s;
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .service-card:hover {
            transform: translateY(-5px);
        }
        .service-icon {
            font-size: 2.5rem;
            color: #0d6efd;
            margin-bottom: 1rem;
        }
        .navbar {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .btn-primary, .btn-outline-light {
            padding: 12px 30px;
            border-radius: 30px;
            font-weight: 600;
        }
    </style>
</head>
<body>
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
                    <a class="nav-link" href="cv_generator.php">CV Generator</a>
                    <a class="nav-link" href="about.php">Tentang</a>
                    <a class="nav-link" href="admin/login.php">
                        <i class="fas fa-user-shield me-1"></i>Admin
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <div class="hero-section text-white">
        <div class="container">
            <div class="row">
                <div class="col-md-8 mx-auto text-center">
                    <h1 class="display-4 fw-bold mb-4">Selamat Datang di Fajar Mandiri Fotocopy</h1>
                    <p class="lead mb-4">Solusi Cetak Berkualitas untuk Semua Kebutuhan Anda dengan Layanan Profesional dan Harga Terjangkau</p>
                    <div class="d-grid gap-3 d-sm-flex justify-content-sm-center">
                        <a href="order.php" class="btn btn-primary btn-lg">Pesan Sekarang</a>
                        <a href="about.php" class="btn btn-outline-light btn-lg">Tentang Kami</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="container my-5">
        <h2 class="text-center mb-5">Layanan Kami</h2>
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card service-card h-100 p-4">
                    <div class="card-body text-center">
                        <i class="fas fa-print service-icon"></i>
                        <h5 class="card-title">Print & Fotocopy</h5>
                        <p class="card-text">Layanan cetak dan fotocopy berkualitas tinggi untuk dokumen Anda</p>
                        <a href="order.php" class="btn btn-primary">Pesan</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card service-card h-100 p-4">
                    <div class="card-body text-center">
                        <i class="fas fa-file-alt service-icon"></i>
                        <h5 class="card-title">CV Generator</h5>
                        <p class="card-text">Buat CV profesional dengan template modern dan menarik</p>
                        <a href="cv_generator.php" class="btn btn-primary">Buat CV</a>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card service-card h-100 p-4">
                    <div class="card-body text-center">
                        <i class="fas fa-tasks service-icon"></i>
                        <h5 class="card-title">Cek Status</h5>
                        <p class="card-text">Pantau status pesanan Anda secara real-time</p>
                        <a href="status.php" class="btn btn-primary">Cek Status</a>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
