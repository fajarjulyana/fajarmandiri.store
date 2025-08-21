
<?php
session_start();
if (!isset($_SESSION['admin'])) {
    header('Location: login.php');
    exit();
}

require_once '../config/database.php';

if (!isset($_GET['id'])) {
    header('Location: index.php');
    exit();
}

$sql = "SELECT * FROM orders WHERE id = ?";
$stmt = $db->prepare($sql);
$stmt->execute([$_GET['id']]);
$order = $stmt->fetch(PDO::FETCH_ASSOC);

if (!$order) {
    header('Location: index.php');
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>View Order - Admin Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="index.php">Admin Dashboard</a>
            <a href="logout.php" class="btn btn-light">Logout</a>
        </div>
    </nav>

    <div class="container mt-5">
        <h2>Detail Pesanan #<?= $order['id'] ?></h2>
        <div class="card mt-4">
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-3"><strong>Nama:</strong></div>
                    <div class="col-md-9"><?= htmlspecialchars($order['nama']) ?></div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-3"><strong>Email:</strong></div>
                    <div class="col-md-9"><?= htmlspecialchars($order['email']) ?></div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-3"><strong>WhatsApp:</strong></div>
                    <div class="col-md-9"><?= htmlspecialchars($order['whatsapp']) ?></div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-3"><strong>Jenis Cetakan:</strong></div>
                    <div class="col-md-9"><?= htmlspecialchars($order['jenis_cetakan']) ?></div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-3"><strong>Jumlah:</strong></div>
                    <div class="col-md-9"><?= $order['jumlah'] ?></div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-3"><strong>Catatan:</strong></div>
                    <div class="col-md-9"><?= nl2br(htmlspecialchars($order['catatan'])) ?></div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-3"><strong>File:</strong></div>
                    <div class="col-md-9">
                        <?php if ($order['file_path']): ?>
                            <a href="../download.php?id=<?= $order['id'] ?>" class="btn btn-success">Download File</a>
                        <?php else: ?>
                            <em>No file uploaded</em>
                        <?php endif; ?>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-3"><strong>Status:</strong></div>
                    <div class="col-md-9">
                        <form method="POST" action="index.php" class="d-inline">
                            <input type="hidden" name="order_id" value="<?= $order['id'] ?>">
                            <select name="status" class="form-select" onchange="this.form.submit()">
                                <option value="Pending" <?= $order['status'] == 'Pending' ? 'selected' : '' ?>>Pending</option>
                                <option value="Processing" <?= $order['status'] == 'Processing' ? 'selected' : '' ?>>Processing</option>
                                <option value="Completed" <?= $order['status'] == 'Completed' ? 'selected' : '' ?>>Completed</option>
                            </select>
                            <input type="hidden" name="update_status" value="1">
                        </form>
                    </div>
                </div>
                <div class="row mb-3">
                    <div class="col-md-3"><strong>Tanggal Order:</strong></div>
                    <div class="col-md-9"><?= $order['created_at'] ?></div>
                </div>
            </div>
        </div>
        <a href="index.php" class="btn btn-secondary mt-3">Kembali</a>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
