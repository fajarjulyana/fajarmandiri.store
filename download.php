
<?php
require_once 'config/database.php';
session_start();

if (!isset($_SESSION['admin'])) {
    die('Unauthorized');
}

if (isset($_GET['id'])) {
    $sql = "SELECT file_path FROM orders WHERE id = ?";
    $stmt = $db->prepare($sql);
    $stmt->execute([$_GET['id']]);
    $order = $stmt->fetch();
    
    if ($order && file_exists($order['file_path'])) {
        header('Content-Type: application/octet-stream');
        header('Content-Disposition: attachment; filename="' . basename($order['file_path']) . '"');
        header('Content-Length: ' . filesize($order['file_path']));
        readfile($order['file_path']);
        exit();
    }
}

header('Location: admin/index.php');
exit();
?>
