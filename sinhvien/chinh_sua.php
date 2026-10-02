<?php
require_once 'ketnoisinhvien.php';

$id = isset($_GET['id']) ? (int)$_GET['id'] : 0;

// Lấy thông tin sinh viên cần sửa
$stmt = $pdo->prepare("SELECT * FROM sinhvien WHERE id = ?");
$stmt->execute([$id]);
$student = $stmt->fetch();

if (!$student) {    
    header("Location: quan_ly.php");
    exit();
}

// Lấy danh sách khoa
$departments = $pdo->query("SELECT * FROM khoa")->fetchAll();

// Xử lý Cập nhật khi nhấn nút Lưu
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $ma_sv = trim($_POST['ma_sv']);
    $ho_ten = trim($_POST['ho_ten']);
    $diem_tb = (float)$_POST['diem_tb'];
    $gioi_tinh = $_POST['gioi_tinh'];
    $id_khoa = (int)$_POST['id_khoa'];

    if (!empty($ma_sv) && !empty($ho_ten) && $id_khoa > 0) {
        $stmt_update = $pdo->prepare("UPDATE sinhvien SET ma_sv = ?, ho_ten = ?, gioi_tinh = ?, diem_tb = ?, id_khoa = ? WHERE id = ?");
        $stmt_update->execute([$ma_sv, $ho_ten, $gioi_tinh, $diem_tb, $id_khoa, $id]);
    }

    header("Location: quan_ly.php");
    exit();
}
?>

<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chỉnh Sửa Sinh Viên ✨</title>
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <!-- Google Fonts Cute (Nunito) -->
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">

    <style>
        * {
            font-family: 'Nunito', sans-serif;
        }

        body {
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0;
            background: linear-gradient(135deg, #f0f3ff 0%, #e0e7ff 50%, #f3e8ff 100%);
            position: relative;
            overflow-x: hidden;
        }

        /* Lớp ảnh nền */
        body::before {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, #f0f3ff 0%, #e0e7ff 50%, #f3e8ff 100%);
            opacity: 0.5; 
            z-index: -2;
        }

        /* Lớp overlay tối nhẹ */
        body::after {
            content: "";
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.75), rgba(30, 41, 59, 0.75));
            z-index: -1;
        }

        /* Khung Form */
        .cute-card {
            background: rgba(30, 41, 59, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.15);
            border-radius: 24px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 
                        0 0 20px rgba(168, 85, 247, 0.2); /* Glow nhẹ màu tím pastel */
            padding: 2.2rem;
            width: 100%;
            max-width: 520px;
            color: #f8fafc;
            animation: fadeInDown 0.5s ease-out;
        }

        @keyframes fadeInDown {
            from { opacity: 0; transform: translateY(-20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .avatar-badge {
            width: 70px;
            height: 70px;
            background: linear-gradient(135deg, #a855f7, #ec4899);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 12px;
            font-size: 1.8rem;
            color: #fff;
            box-shadow: 0 8px 16px rgba(236, 72, 153, 0.3);
        }

        .form-label {
            font-weight: 700;
            color: #cbd5e1;
            font-size: 0.9rem;
            margin-bottom: 6px;
        }

        /* Ô nhập liệu Cute Soft Style */
        .form-control, .form-select {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 12px;
            color: #f8fafc;
            padding: 10px 14px;
            font-size: 0.95rem;
            transition: all 0.3s ease;
        }

        .form-control:focus, .form-select:focus {
            background: rgba(15, 23, 42, 0.85);
            border-color: #c084fc;
            box-shadow: 0 0 0 0.25rem rgba(192, 132, 252, 0.25);
            color: #fff;
        }

        .form-select option {
            background-color: #1e293b;
            color: #fff;
        }

        /* Nút bấm Gradient Cute */
        .btn-save {
            background: linear-gradient(135deg, #a855f7, #6366f1);
            border: none;
            color: #fff;
            font-weight: 700;
            border-radius: 12px;
            padding: 12px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(168, 85, 247, 0.3);
        }

        .btn-save:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(168, 85, 247, 0.5);
            color: #fff;
        }

        .btn-cancel {
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.15);
            color: #cbd5e1;
            font-weight: 600;
            border-radius: 12px;
            padding: 12px;
            transition: all 0.3s ease;
        }

        .btn-cancel:hover {
            background: rgba(255, 255, 255, 0.18);
            color: #fff;
        }
    </style>
</head>
<body>

<div class="cute-card">
    <div class="text-center mb-4">
        <div class="avatar-badge">
            <i class="fa-solid fa-user-pen"></i>
        </div>
        <h4 class="fw-bold mb-1" style="color: #f472b6;">Sửa Thông Tin Sinh Viên 🌸</h4>
        <p class="text-muted small mb-0">Cập nhật chi tiết mã số, điểm số & ngành học</p>
    </div>

    <form method="POST">
        <!-- Mã sinh viên -->
        <div class="mb-3">
            <label class="form-label"><i class="fa-solid fa-id-card text-info me-1"></i> Mã Sinh Viên (*)</label>
            <input type="text" name="ma_sv" class="form-control" value="<?= htmlspecialchars($student['ma_sv']) ?>" required placeholder="VD: SV001">
        </div>

        <!-- Họ và tên -->
        <div class="mb-3">
            <label class="form-label"><i class="fa-solid fa-signature text-warning me-1"></i> Họ và Tên (*)</label>
            <input type="text" name="ho_ten" class="form-control" value="<?= htmlspecialchars($student['ho_ten']) ?>" required placeholder="VD: Nguyễn Văn A">
        </div>

        <!-- Điểm TB & Giới tính -->
        <div class="row mb-3">
            <div class="col-6">
                <label class="form-label"><i class="fa-solid fa-star text-warning me-1"></i> Điểm TB (GPA)</label>
                <input type="number" name="diem_tb" min="0" max="10" step="0.1" class="form-control" value="<?= $student['diem_tb'] ?>" required>
            </div>
            <div class="col-6">
                <label class="form-label"><i class="fa-solid fa-venus-mars text-primary me-1"></i> Giới tính</label>
                <select name="gioi_tinh" class="form-select">
                    <option value="Nam" <?= $student['gioi_tinh'] == 'Nam' ? 'selected' : '' ?>>♂️ Nam</option>
                    <option value="Nữ" <?= $student['gioi_tinh'] == 'Nữ' ? 'selected' : '' ?>>♀️ Nữ</option>
                </select>
            </div>
        </div>

        <!-- Khoa / Ngành -->
        <div class="mb-4">
            <label class="form-label"><i class="fa-solid fa-graduation-cap text-success me-1"></i> Khoa / Ngành (*)</label>
            <select name="id_khoa" class="form-select" required>
                <?php foreach ($departments as $d): ?>
                    <option value="<?= $d['id'] ?>" <?= $student['id_khoa'] == $d['id'] ? 'selected' : '' ?>>
                        🏫 <?= htmlspecialchars($d['ten_khoa']) ?>
                    </option>
                <?php endforeach; ?>
            </select>
        </div>

        <!-- Nút thao tác -->
        <div class="d-flex gap-2">
            <button type="submit" class="btn btn-save w-50">
                <i class="fa-solid fa-floppy-disk me-1"></i> Lưu Thay Đổi
            </button>
            <a href="quan_ly.php" class="btn btn-cancel w-50 text-center text-decoration-none">
                <i class="fa-solid fa-xmark me-1"></i> Hủy Bỏ
            </a>
        </div>
    </form>
</div>

</body>
</html>