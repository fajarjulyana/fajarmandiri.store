
<?php
require_once 'config/database.php';
require_once 'vendor/autoload.php';

use Dompdf\Dompdf;
use Dompdf\Options;

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    // Configure Dompdf
    $options = new Options();
    $options->set('defaultFont', 'DejaVu Sans');
    $options->set('isRemoteEnabled', true);
    $dompdf = new Dompdf($options);
    
    // Get data from form
    $nama = $_POST['nama'] ?? '';
    $profesi = $_POST['profesi'] ?? '';
    $email = $_POST['email'] ?? '';
    $telepon = $_POST['telepon'] ?? '';
    $alamat = $_POST['alamat'] ?? '';
    $ringkasan = $_POST['ringkasan'] ?? '';
    $template = $_POST['template'] ?? 'modern';
    
    // Handle foto
    $fotoBase64 = '';
    if (isset($_FILES['foto']) && $_FILES['foto']['error'] == 0) {
        $fotoData = file_get_contents($_FILES['foto']['tmp_name']);
        $fotoType = $_FILES['foto']['type'];
        $fotoBase64 = 'data:' . $fotoType . ';base64,' . base64_encode($fotoData);
    }
    
    // Process arrays
    $pendidikan = [];
    if (isset($_POST['pendidikan_institusi'])) {
        for ($i = 0; $i < count($_POST['pendidikan_institusi']); $i++) {
            if (!empty($_POST['pendidikan_institusi'][$i])) {
                $pendidikan[] = [
                    'institusi' => $_POST['pendidikan_institusi'][$i],
                    'jurusan' => $_POST['pendidikan_jurusan'][$i] ?? '',
                    'tahun' => $_POST['pendidikan_tahun'][$i] ?? '',
                    'nilai' => $_POST['pendidikan_nilai'][$i] ?? ''
                ];
            }
        }
    }
    
    $pengalaman = [];
    if (isset($_POST['pengalaman_perusahaan'])) {
        for ($i = 0; $i < count($_POST['pengalaman_perusahaan']); $i++) {
            if (!empty($_POST['pengalaman_perusahaan'][$i])) {
                $pengalaman[] = [
                    'perusahaan' => $_POST['pengalaman_perusahaan'][$i],
                    'posisi' => $_POST['pengalaman_posisi'][$i] ?? '',
                    'periode' => $_POST['pengalaman_periode'][$i] ?? '',
                    'deskripsi' => $_POST['pengalaman_deskripsi'][$i] ?? ''
                ];
            }
        }
    }
    
    $keahlian = [];
    if (isset($_POST['keahlian'])) {
        $keahlian = array_filter($_POST['keahlian'], function($skill) {
            return !empty(trim($skill));
        });
    }
    
    // Generate HTML based on template
    $html = generateCVHTML($template, $nama, $profesi, $email, $telepon, $alamat, $ringkasan, $fotoBase64, $pendidikan, $pengalaman, $keahlian);
    
    // Load HTML to Dompdf
    $dompdf->loadHtml($html);
    $dompdf->setPaper('A4', 'portrait');
    $dompdf->render();
    
    // Output PDF
    $dompdf->stream("CV-{$nama}.pdf", array("Attachment" => false));
    exit();
}

function generateCVHTML($template, $nama, $profesi, $email, $telepon, $alamat, $ringkasan, $foto, $pendidikan, $pengalaman, $keahlian) {
    $html = '<!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: "DejaVu Sans", sans-serif; font-size: 11px; line-height: 1.4; color: #333; }
            .container { max-width: 100%; margin: 0 auto; }
            .header { text-align: center; padding: 20px; margin-bottom: 20px; }
            .foto { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; margin-bottom: 10px; }
            .nama { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
            .profesi { font-size: 14px; color: #666; margin-bottom: 10px; }
            .kontak { font-size: 10px; color: #666; }
            .section { margin-bottom: 20px; }
            .section-title { font-size: 14px; font-weight: bold; margin-bottom: 10px; padding-bottom: 5px; border-bottom: 1px solid #ccc; }
            .item { margin-bottom: 10px; }
            .item-title { font-weight: bold; }
            .item-subtitle { color: #666; font-style: italic; }
            .item-desc { margin-top: 3px; }
            .skills { display: flex; flex-wrap: wrap; gap: 5px; }
            .skill { background: #f0f0f0; padding: 3px 8px; border-radius: 10px; font-size: 10px; }
        ';
    
    // Template-specific styles
    if ($template == 'modern') {
        $html .= '
            .header { background: linear-gradient(135deg, #667eea, #764ba2); color: white; }
            .section-title { color: #667eea; }
        ';
    } elseif ($template == 'professional') {
        $html .= '
            .header { background: #2196F3; color: white; }
            .section-title { color: #2196F3; }
        ';
    } elseif ($template == 'creative') {
        $html .= '
            .header { background: linear-gradient(135deg, #FF6B6B, #FFE66D); color: white; }
            .section-title { color: #FF6B6B; }
        ';
    }
    
    $html .= '</style></head><body><div class="container">';
    
    // Header
    $html .= '<div class="header">';
    if ($foto) {
        $html .= '<img src="' . $foto . '" class="foto" alt="Foto">';
    }
    $html .= '<div class="nama">' . htmlspecialchars($nama) . '</div>';
    if ($profesi) {
        $html .= '<div class="profesi">' . htmlspecialchars($profesi) . '</div>';
    }
    $html .= '<div class="kontak">';
    if ($email) $html .= $email . ' | ';
    if ($telepon) $html .= $telepon . ' | ';
    if ($alamat) $html .= $alamat;
    $html .= '</div></div>';
    
    // Ringkasan
    if ($ringkasan) {
        $html .= '<div class="section">
            <div class="section-title">RINGKASAN</div>
            <div>' . nl2br(htmlspecialchars($ringkasan)) . '</div>
        </div>';
    }
    
    // Pendidikan
    if (!empty($pendidikan)) {
        $html .= '<div class="section">
            <div class="section-title">PENDIDIKAN</div>';
        foreach ($pendidikan as $edu) {
            $html .= '<div class="item">
                <div class="item-title">' . htmlspecialchars($edu['institusi']) . '</div>
                <div class="item-subtitle">' . htmlspecialchars($edu['jurusan']) . '</div>
                <div class="item-desc">' . htmlspecialchars($edu['tahun']);
            if ($edu['nilai']) $html .= ' | ' . htmlspecialchars($edu['nilai']);
            $html .= '</div></div>';
        }
        $html .= '</div>';
    }
    
    // Pengalaman
    if (!empty($pengalaman)) {
        $html .= '<div class="section">
            <div class="section-title">PENGALAMAN KERJA</div>';
        foreach ($pengalaman as $exp) {
            $html .= '<div class="item">
                <div class="item-title">' . htmlspecialchars($exp['posisi']) . '</div>
                <div class="item-subtitle">' . htmlspecialchars($exp['perusahaan']) . ' | ' . htmlspecialchars($exp['periode']) . '</div>
                <div class="item-desc">' . nl2br(htmlspecialchars($exp['deskripsi'])) . '</div>
            </div>';
        }
        $html .= '</div>';
    }
    
    // Keahlian
    if (!empty($keahlian)) {
        $html .= '<div class="section">
            <div class="section-title">KEAHLIAN</div>
            <div class="skills">';
        foreach ($keahlian as $skill) {
            $html .= '<span class="skill">' . htmlspecialchars($skill) . '</span>';
        }
        $html .= '</div></div>';
    }
    
    $html .= '</div></body></html>';
    
    return $html;
}
?>
