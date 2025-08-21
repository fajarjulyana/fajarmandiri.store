
<?php
require_once 'config/database.php';

// Handle search/filter
$search = isset($_GET['search']) ? trim($_GET['search']) : '';
$status_filter = isset($_GET['status']) ? trim($_GET['status']) : '';

$sql = "SELECT * FROM orders WHERE 1=1";
$params = [];

if (!empty($search)) {
    $sql .= " AND (nama LIKE ? OR email LIKE ? OR whatsapp LIKE ? OR id = ?)";
    $search_param = "%$search%";
    $params[] = $search_param;
    $params[] = $search_param;
    $params[] = $search_param;
    $params[] = $search;
}

if (!empty($status_filter)) {
    $sql .= " AND status = ?";
    $params[] = $status_filter;
}

$sql .= " ORDER BY id DESC";

try {
    $stmt = $db->prepare($sql);
    $stmt->execute($params);
    $orders = $stmt->fetchAll(PDO::FETCH_ASSOC);
} catch(PDOException $e) {
    $orders = [];
}
?>
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Status Pesanan - Fajar Mandiri Fotocopy</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .status-badge {
            font-size: 0.875rem;
            padding: 0.5rem 1rem;
        }
        .order-card {
            transition: transform 0.2s;
        }
        .order-card:hover {
            transform: translateY(-2px);
        }
        .navbar {
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body class="bg-light">
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand fw-bold" href="index.php">Fajar Mandiri Fotocopy</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <div class="navbar-nav ms-auto">
                    <a class="nav-link" href="order.php">Buat Pesanan</a>
                    <a class="nav-link active" href="status.php">Cek Status</a>
                    <a class="nav-link" href="cv_generator.php">CV Generator</a>
                    <a class="nav-link" href="about.php">Tentang</a>
                    <a class="nav-link" href="admin/login.php">
                        <i class="fas fa-user-shield me-1"></i>Admin
                    </a>
                </div>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <div class="row">
            <div class="col-md-8 mx-auto">
                <div class="card shadow-sm">
                    <div class="card-header bg-primary text-white">
                        <h4 class="mb-0">
                            <i class="fas fa-search me-2"></i>Cek Status Pesanan
                        </h4>
                    </div>
                    <div class="card-body">
                        <form method="GET" class="mb-4">
                            <div class="row g-3">
                                <div class="col-md-6">
                                    <label class="form-label">Cari Pesanan</label>
                                    <input type="text" class="form-control" name="search" 
                                           placeholder="ID Pesanan, Nama, Email, atau WhatsApp"
                                           value="<?= htmlspecialchars($search) ?>">
                                </div>
                                <div class="col-md-4">
                                    <label class="form-label">Filter Status</label>
                                    <select class="form-select" name="status">
                                        <option value="">Semua Status</option>
                                        <option value="Pending" <?= $status_filter == 'Pending' ? 'selected' : '' ?>>
                                            Pending
                                        </option>
                                        <option value="Processing" <?= $status_filter == 'Processing' ? 'selected' : '' ?>>
                                            Processing
                                        </option>
                                        <option value="Completed" <?= $status_filter == 'Completed' ? 'selected' : '' ?>>
                                            Selesai
                                        </option>
                                    </select>
                                </div>
                                <div class="col-md-2">
                                    <label class="form-label">&nbsp;</label>
                                    <button type="submit" class="btn btn-primary w-100">
                                        <i class="fas fa-search"></i>
                                    </button>
                                </div>
                            </div>
                        </form>

                        <?php if (empty($orders)): ?>
                            <div class="text-center py-5">
                                <i class="fas fa-clipboard-list fa-3x text-muted mb-3"></i>
                                <h5 class="text-muted">
                                    <?= !empty($search) || !empty($status_filter) ? 'Tidak ada pesanan yang sesuai dengan pencarian' : 'Belum ada pesanan' ?>
                                </h5>
                                <?php if (!empty($search) || !empty($status_filter)): ?>
                                    <a href="status.php" class="btn btn-outline-primary mt-2">
                                        <i class="fas fa-refresh me-1"></i>Reset Filter
                                    </a>
                                <?php endif; ?>
                            </div>
                        <?php else: ?>
                            <div class="row">
                                <?php foreach ($orders as $order): ?>
                                    <div class="col-md-6 mb-3">
                                        <div class="card order-card h-100">
                                            <div class="card-body">
                                                <div class="d-flex justify-content-between align-items-start mb-2">
                                                    <h6 class="card-title mb-0">
                                                        <i class="fas fa-hashtag text-muted"></i>
                                                        Pesanan #<?= $order['id'] ?>
                                                    </h6>
                                                    <?php
                                                    $badge_class = '';
                                                    $icon = '';
                                                    switch ($order['status']) {
                                                        case 'Pending':
                                                            $badge_class = 'warning';
                                                            $icon = 'fas fa-clock';
                                                            break;
                                                        case 'Processing':
                                                            $badge_class = 'info';
                                                            $icon = 'fas fa-cog fa-spin';
                                                            break;
                                                        case 'Completed':
                                                            $badge_class = 'success';
                                                            $icon = 'fas fa-check-circle';
                                                            break;
                                                    }
                                                    ?>
                                                    <span class="badge bg-<?= $badge_class ?> status-badge">
                                                        <i class="<?= $icon ?> me-1"></i><?= $order['status'] ?>
                                                    </span>
                                                </div>
                                                
                                                <div class="mb-2">
                                                    <i class="fas fa-user text-muted me-2"></i>
                                                    <strong><?= htmlspecialchars($order['nama']) ?></strong>
                                                </div>
                                                
                                                <div class="mb-2">
                                                    <i class="fas fa-print text-muted me-2"></i>
                                                    <?= htmlspecialchars($order['jenis_cetakan']) ?>
                                                    <span class="badge bg-secondary ms-2"><?= $order['jumlah'] ?> pcs</span>
                                                </div>
                                                
                                                <div class="mb-2">
                                                    <i class="fas fa-calendar text-muted me-2"></i>
                                                    <small><?= date('d/m/Y H:i', strtotime($order['created_at'])) ?></small>
                                                </div>
                                                
                                                <?php if (!empty($order['catatan'])): ?>
                                                    <div class="mb-2">
                                                        <i class="fas fa-comment text-muted me-2"></i>
                                                        <small class="text-muted"><?= htmlspecialchars($order['catatan']) ?></small>
                                                    </div>
                                                <?php endif; ?>
                                                
                                                <div class="mt-3">
                                                    <div class="row g-2">
                                                        <div class="col-6">
                                                            <small class="text-muted">
                                                                <i class="fas fa-envelope me-1"></i>
                                                                <?= htmlspecialchars($order['email']) ?>
                                                            </small>
                                                        </div>
                                                        <div class="col-6">
                                                            <small class="text-muted">
                                                                <i class="fab fa-whatsapp me-1"></i>
                                                                <?= htmlspecialchars($order['whatsapp']) ?>
                                                            </small>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                <?php endforeach; ?>
                            </div>
                        <?php endif; ?>
                    </div>
                </div>
                
                <div class="text-center mt-4">
                    <a href="order.php" class="btn btn-primary">
                        <i class="fas fa-plus me-2"></i>Buat Pesanan Baru
                    </a>
                    <a href="index.php" class="btn btn-outline-secondary ms-2">
                        <i class="fas fa-home me-2"></i>Kembali ke Beranda
                    </a>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
