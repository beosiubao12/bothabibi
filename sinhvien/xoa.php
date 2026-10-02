<?php
require_once 'ketnoisinhvien.php';

$id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

if ($id > 0) {
    $stmt = $pdo->prepare("DELETE FROM sinhvien WHERE id = :id");
    $stmt->execute(['id' => $id]);
}

header("Location: quan_ly.php");
exit();
?>