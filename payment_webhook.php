<?php
header("Content-Type: application/json");

// Pastikan hanya menerima metode POST
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(["status" => "error", "message" => "Method Not Allowed"]);
    exit;
}

// Baca input JSON
$json = file_get_contents("php://input");
$data = json_decode($json, true);

// Cek apakah JSON valid
if (!$data) {
    http_response_code(400);
    echo json_encode(["status" => "error", "message" => "Invalid JSON"]);
    exit;
}

// Simpan log webhook untuk debugging
$logFile = "webhook_log.txt";
$logData = "[" . date("Y-m-d H:i:s") . "] " . json_encode($data) . "\n";
file_put_contents($logFile, $logData, FILE_APPEND);

// Contoh respons sukses
http_response_code(200);
echo json_encode(["status" => "success", "message" => "Webhook received"]);
?>
