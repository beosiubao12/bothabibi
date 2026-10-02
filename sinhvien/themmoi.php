<?php
require_once 'ketnoisinhvien.php';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $ma_sv = trim($_POST['ma_sv'] ?? '');
    $ho_ten = trim($_POST['ho_ten'] ?? '');
    $diem_tb = (float)($_POST['diem_tb'] ?? 0);
    $gioi_tinh = $_POST['gioi_tinh'] ?? 'Nam';
    $id_khoa = (int)($_POST['id_khoa'] ?? 0);

    if (!empty($ma_sv) && !empty($ho_ten) && $id_khoa > 0) {
        $sql = "INSERT INTO sinhvien (ma_sv, ho_ten, diem_tb, gioi_tinh, id_khoa) 
                VALUES (:ma_sv, :ho_ten, :diem_tb, :gioi_tinh, :id_khoa)";
        $stmt = $pdo->prepare($sql);
        $stmt->execute([
            ':ma_sv' => $ma_sv,
            ':ho_ten' => $ho_ten,
            ':diem_tb' => $diem_tb,
            ':gioi_tinh' => $gioi_tinh,
            ':id_khoa' => $id_khoa
        ]);
    }
}

header('Location: quan_ly.php');
exit;