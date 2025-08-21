
<?php
require_once 'config/database.php';

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $nama = $_POST['nama'];
    $email = $_POST['email'];
    $whatsapp = $_POST['whatsapp'];
    $jenis_cetakan = $_POST['jenis_cetakan'];
    $jumlah = $_POST['jumlah'];
    $catatan = $_POST['catatan'];
    
    $file_path = '';
    if (isset($_FILES['file']) && $_FILES['file']['error'] == 0) {
        $upload_dir = 'uploads/';
        if (!file_exists($upload_dir)) {
            mkdir($upload_dir, 0777, true);
        }
        
        $file_name = time() . '_' . $_FILES['file']['name'];
        $target_path = $upload_dir . $file_name;
        
        if (move_uploaded_file($_FILES['file']['tmp_name'], $target_path)) {
            $file_path = $target_path;
        }
    }
    
    $sql = "INSERT INTO orders (nama, email, whatsapp, jenis_cetakan, jumlah, catatan, file_path, status) 
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')";
    $stmt = $db->prepare($sql);
    $stmt->execute([$nama, $email, $whatsapp, $jenis_cetakan, $jumlah, $catatan, $file_path]);
    
    header('Location: status.php');
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Buat Pesanan - Fajar Mandiri Fotocopy</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="index.php">Fajar Mandiri Fotocopy</a>
        </div>
    </nav>

    <div class="container mt-5">
        <h2>Form Pemesanan Cetakan</h2>
        <form method="POST" action="order.php" class="mt-4" enctype="multipart/form-data">
            <div class="mb-3">
                <label class="form-label">Nama</label>
                <input type="text" class="form-control" name="nama" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Email</label>
                <input type="email" class="form-control" name="email" required>
            </div>
            <div class="mb-3">
                <label class="form-label">WhatsApp</label>
                <input type="tel" class="form-control" name="whatsapp" placeholder="contoh: 081234567890" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Jenis Cetakan</label>
                <select class="form-select" name="jenis_cetakan" required>
                    <option value="Fotocopy B/W">Fotocopy B/W</option>
                    <option value="Print Warna">Print Warna</option>
                    <option value="Print B/W">Print B/W</option>
                    <option value="Scanning">Scanning</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Jumlah</label>
                <input type="number" class="form-control" name="jumlah" required>
            </div>
            <div class="mb-3">
                <label class="form-label">Catatan</label>
                <textarea class="form-control" name="catatan" rows="3"></textarea>
            </div>
            <div class="mb-3">
                <label class="form-label">Upload File</label>
                <input type="file" class="form-control" name="file" required>
            </div>
            <button type="submit" class="btn btn-primary">Kirim Pesanan</button>
        </form>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
