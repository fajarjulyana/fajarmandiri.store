
<?php
$host = 'localhost';
$dbname = 'u535477861_fj_mandiri';
$username = 'u535477861_fajar';
$password = '54321Fajar';

try {
    $db = new PDO("mysql:host=$host;dbname=$dbname", $username, $password);
    $db->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
} catch(PDOException $e) {
    echo "Connection failed: " . $e->getMessage();
}
?>
