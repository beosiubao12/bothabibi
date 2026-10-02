<?php
require_once 'ketnoisinhvien.php';

// Lấy tham số Tìm kiếm & Lọc
$search = isset($_GET['search']) ? trim($_GET['search']) : '';
$filter_khoa = isset($_GET['filter_khoa']) ? (int)$_GET['filter_khoa'] : 0;

// Truy vấn danh sách Khoa
$stmt_khoa = $pdo->query("SELECT * FROM khoa");
$departments = $stmt_khoa->fetchAll();

// 1. Thống kê nhanh cho các thẻ Stat Card
$total_students = $pdo->query("SELECT COUNT(*) FROM sinhvien")->fetchColumn();
$avg_gpa = $pdo->query("SELECT AVG(diem_tb) FROM sinhvien")->fetchColumn() ?? 0;
$excellent_count = $pdo->query("SELECT COUNT(*) FROM sinhvien WHERE diem_tb >= 8.5")->fetchColumn() ?? 0;

// 2. Xây dựng câu truy vấn SQL lấy Sinh viên
$sql = "SELECT sv.*, k.ten_khoa 
        FROM sinhvien sv 
        LEFT JOIN khoa k ON sv.id_khoa = k.id 
        WHERE 1=1";
$params = [];

if (!empty($search)) {
    $sql .= " AND (sv.ho_ten LIKE :search OR sv.ma_sv LIKE :search)";
    $params['search'] = "%$search%";
}

if ($filter_khoa > 0) {
    $sql .= " AND sv.id_khoa = :filter_khoa";
    $params['filter_khoa'] = $filter_khoa;
}

$sql .= " ORDER BY sv.id DESC";

$stmt = $pdo->prepare($sql);
$stmt->execute($params);
$students = $stmt->fetchAll();
?>

<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hệ Thống Quản Lý Sinh Viên </title>
    
    <!-- Bootstrap 5 CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- FontAwesome Icon -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <!-- Google Font (Nunito - Phông chữ cute, bo tròn mềm) -->
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">

    <style>
        * {
            font-family: 'Nunito', sans-serif;
        }

        body {
            background: linear-gradient(135deg, #f0f3ff 0%, #e0e7ff 50%, #f3e8ff 100%);
            color: #334155;
            min-height: 100vh;
            position: relative;
        }

        /* Nền họa tiết chìm mờ cute */
        body::before {
            content: "";
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: radial-gradient(#c7d2fe 0.8px, transparent 0.8px), radial-gradient(#c7d2fe 0.8px, #f0f3ff 0.8px);
            background-size: 32px 32px;
            background-position: 0 0, 16px 16px;
            opacity: 0.35;
            z-index: -1;
        }

        .glass-card {
            background: rgba(255, 255, 255, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.8);
            border-radius: 20px;
            box-shadow: 0 10px 25px -5px rgba(99, 102, 241, 0.08), 0 8px 10px -6px rgba(99, 102, 241, 0.04);
        }

        /* Stat cards thiết kế nhí nhảnh pastel */
        .stat-card {
            transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
            position: relative;
            overflow: hidden;
            border: none;
        }

        .stat-card:hover {
            transform: translateY(-6px);
            box-shadow: 0 16px 30px rgba(99, 102, 241, 0.15);
        }

        .stat-card-1 {
            background: linear-gradient(135deg, #ffffff 0%, #e0f2fe 100%);
            border-left: 5px solid #0284c7;
        }
        .stat-card-2 {
            background: linear-gradient(135deg, #ffffff 0%, #fef3c7 100%);
            border-left: 5px solid #d97706;
        }
        .stat-card-3 {
            background: linear-gradient(135deg, #ffffff 0%, #dcfce7 100%);
            border-left: 5px solid #16a34a;
        }

        .stat-icon {
            font-size: 3rem;
            opacity: 0.18;
            position: absolute;
            right: 18px;
            bottom: 8px;
        }

        /* Bảng dữ liệu phong cách sáng sủa */
        .custom-table {
            color: #334155;
            margin-bottom: 0;
        }

        .custom-table thead th {
            background: #f1f5f9;
            color: #475569;
            border-bottom: 2px solid #e2e8f0;
            text-transform: uppercase;
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            padding: 16px;
        }

        .custom-table tbody tr {
            transition: all 0.2s ease;
            border-bottom: 1px solid #f1f5f9;
        }

        .custom-table tbody tr:hover {
            background: rgba(243, 232, 255, 0.4);
        }

        /* Ô nhập liệu cute bo cong */
        .form-control, .form-select {
            background-color: #ffffff;
            border: 1.5px solid #cbd5e1;
            color: #1e293b;
            border-radius: 12px;
            font-weight: 600;
            padding: 9px 14px;
            transition: all 0.2s ease;
        }

        .form-control:focus, .form-select:focus {
            background-color: #ffffff;
            border-color: #818cf8;
            color: #0f172a;
            box-shadow: 0 0 0 0.25rem rgba(129, 140, 248, 0.25);
        }

        /* Badge Khoa / Ngành pastel cute */
        .badge-dept {
            background: linear-gradient(135deg, #818cf8 0%, #6366f1 100%);
            color: #fff;
            font-weight: 700;
            padding: 7px 14px;
            border-radius: 10px;
            box-shadow: 0 3px 8px rgba(99, 102, 241, 0.25);
        }

        /* Avatar bo tròn cá tính */
        .student-avatar {
            width: 46px;
            height: 46px;
            object-fit: cover;
            border-radius: 50%;
            border: 2px solid #fff;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        }

        /* Button Gradient sinh động */
        .btn-gradient-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            border: none;
            color: white;
            font-weight: 700;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.25);
            transition: all 0.2s ease;
        }
        .btn-gradient-success:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(16, 185, 129, 0.35);
            color: white;
        }

        .btn-gradient-primary {
            background: linear-gradient(135deg, #6366f1 0%, #4f46e5 100%);
            border: none;
            color: white;
            font-weight: 700;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
            transition: all 0.2s ease;
        }
        .btn-gradient-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 16px rgba(99, 102, 241, 0.35);
            color: white;
        }

        .btn-cute-reset {
            background: #ffffff;
            border: 1.5px solid #cbd5e1;
            color: #64748b;
            font-weight: 700;
            border-radius: 12px;
            transition: all 0.2s ease;
        }
        .btn-cute-reset:hover {
            background: #f1f5f9;
            color: #334155;
        }

        /* Badge xếp loại xinh xắn */
        .badge-xl {
            font-size: 0.8rem;
            font-weight: 800;
            padding: 6px 12px;
            border-radius: 10px;
        }
        .badge-xs { background: linear-gradient(135deg, #34d399, #10b981); color: #fff; }
        .badge-gioi { background: linear-gradient(135deg, #38bdf8, #0284c7); color: #fff; }
        .badge-kha { background: linear-gradient(135deg, #fbbf24, #d97706); color: #fff; }
        .badge-yeu { background: linear-gradient(135deg, #f87171, #dc2626); color: #fff; }
    </style>
</head>
<body class="py-4">

<div class="container-fluid px-4" style="max-width: 1400px;">
    
    <!-- HEADER -->
    <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
            <h2 class="fw-extrabold m-0" style="color: #4f46e5; font-weight: 900;">
                <i class="fa-solid fa-graduation-cap text-warning me-2"></i>HỆ THỐNG QUẢN LÝ SINH VIÊN 
            </h2>
            <p class="text-muted fw-semibold mb-0">Theo dõi thông tin, điểm trung bình và xếp loại học lực sinh viên</p>
        </div>
        <span class="badge bg-white text-indigo border px-3 py-2 rounded-pill shadow-sm" style="color: #4f46e5; font-weight: 700;">
            <i class="fa-solid fa-sparkles text-warning me-1"></i> Cao Đẳng Công Nghệ Bách Khoa Hà Nội 2026
        </span>
    </div>

    <!-- 3 THẺ STAT CARDS THỐNG KÊ -->
    <div class="row g-3 mb-4">
        <div class="col-md-4">
            <div class="glass-card stat-card stat-card-1 p-3">
                <div class="text-secondary small fw-bold text-uppercase">Tổng số sinh viên</div>
                <div class="fs-2 fw-black text-dark mt-1" style="font-weight: 900;">
                    <?= number_format($total_students) ?> <span class="fs-6 text-muted fw-normal">sinh viên</span>
                </div>
                <i class="fa-solid fa-users stat-icon text-info"></i>
            </div>
        </div>
        <div class="col-md-4">
            <div class="glass-card stat-card stat-card-2 p-3">
                <div class="text-secondary small fw-bold text-uppercase">Điểm TB Toàn Khoá (GPA)</div>
                <div class="fs-2 fw-black text-warning mt-1" style="font-weight: 900; color: #d97706 !important;">
                    <?= number_format($avg_gpa, 2) ?> <span class="fs-6 text-muted fw-normal">/ 10</span>
                </div>
                <i class="fa-solid fa-chart-line-up stat-icon text-warning"></i>
            </div>
        </div>
        <div class="col-md-4">
            <div class="glass-card stat-card stat-card-3 p-3">
                <div class="text-secondary small fw-bold text-uppercase">Sinh viên Xuất sắc</div>
                <div class="fs-2 fw-black text-success mt-1" style="font-weight: 900; color: #16a34a !important;">
                    <?= number_format($excellent_count) ?> <span class="fs-6 text-muted fw-normal">sinh viên</span>
                </div>
                <i class="fa-solid fa-award stat-icon text-success"></i>
            </div>
        </div>
    </div>

    <!-- FORM THÊM MỚI SINH VIÊN -->
    <div class="glass-card p-4 mb-4">
        <h5 class="fw-bold mb-3" style="color: #4338ca;"><i class="fa-solid fa-user-plus text-primary me-2"></i>Thêm sinh viên mới </h5>
        <form action="themmoi.php" method="POST" class="row g-3">
            <div class="col-md-2">
                <label class="form-label text-dark small fw-bold">Mã Sinh Viên (*)</label>
                <input type="text" name="ma_sv" class="form-control" placeholder="VD: SV001" required>
            </div>
            <div class="col-md-3">
                <label class="form-label text-dark small fw-bold">Họ và Tên (*)</label>
                <input type="text" name="ho_ten" class="form-control" placeholder="Nhập họ tên..." required>
            </div>
            <div class="col-md-2">
                <label class="form-label text-dark small fw-bold">Điểm TB (GPA)</label>
                <input type="number" name="diem_tb" min="0" max="10" step="0.1" class="form-control" placeholder="0.0" required>
            </div>
            <div class="col-md-2">
                <label class="form-label text-dark small fw-bold">Giới tính</label>
                <select name="gioi_tinh" class="form-select">
                    <option value="Nam">♂️ Nam</option>
                    <option value="Nữ">♀️ Nữ</option>
                </select>
            </div>
            <div class="col-md-2">
                <label class="form-label text-dark small fw-bold">Khoa (*)</label>
                <select name="id_khoa" class="form-select" required>
                    <option value="">-- Chọn khoa --</option>
                    <?php foreach ($departments as $d): ?>
                        <option value="<?= $d['id'] ?>"><?= htmlspecialchars($d['ten_khoa']) ?></option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-md-1 d-flex align-items-end">
                <button type="submit" class="btn btn-gradient-success w-100 py-2"><i class="fa-solid fa-check me-1"></i> Lưu</button>
            </div>
        </form>
    </div>

    <!-- BỘ LỌC VÀ TÌM KIẾM -->
    <div class="glass-card p-3 mb-4">
        <form method="GET" action="quan_ly.php" class="row g-2 align-items-center">
            <div class="col-md-5">
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0 border-slate text-muted" style="border-radius: 12px 0 0 12px; border: 1.5px solid #cbd5e1;"><i class="fa-solid fa-magnifying-glass"></i></span>
                    <input type="text" name="search" class="form-control border-start-0" style="border-radius: 0 12px 12px 0;" placeholder="Tìm theo Mã SV hoặc Họ tên..." value="<?= htmlspecialchars($search) ?>">
                </div>
            </div>
            <div class="col-md-4">
                <select name="filter_khoa" class="form-select">
                    <option value="0"> -- Tất cả các Khoa --</option>
                    <?php foreach ($departments as $d): ?>
                        <option value="<?= $d['id'] ?>" <?= $filter_khoa == $d['id'] ? 'selected' : '' ?>>
                            <?= htmlspecialchars($d['ten_khoa']) ?>
                        </option>
                    <?php endforeach; ?>
                </select>
            </div>
            <div class="col-md-3 d-flex gap-2">
                <button type="submit" class="btn btn-gradient-primary w-50"><i class="fa-solid fa-filter me-1"></i> Lọc</button>
                <a href="quan_ly.php" class="btn btn-cute-reset w-50 text-center text-decoration-none py-2"><i class="fa-solid fa-rotate me-1"></i> Reset</a>
            </div>
        </form>
    </div>

    <!-- BẢNG DANH SÁCH SINH VIÊN -->
    <div class="glass-card overflow-hidden">
        <div class="table-responsive">
            <table class="table custom-table align-middle">
                <thead>
                    <tr>
                        <th width="80" class="text-center">Mã SV</th>
                        <th width="70" class="text-center">Ảnh</th>
                        <th>Họ và Tên</th>
                        <th>Giới tính</th>
                        <th>Khoa / Ngành</th>
                        <th width="160">Điểm TB (GPA)</th>
                        <th>Xếp loại</th>
                        <th width="120" class="text-center">Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if (count($students) > 0): ?>
                        <?php foreach ($students as $row): ?>
                            <tr>
                                <td class="text-center fw-bold text-primary"><?= htmlspecialchars($row['ma_sv']) ?></td>
                                
                                <!-- AVATAR SINH VIÊN -->
                                <td class="text-center">
                                    <img src="https://ui-avatars.com/api/?name=<?= urlencode($row['ho_ten']) ?>&background=random&color=fff&bold=true" 
                                         alt="Avatar" 
                                         class="student-avatar">
                                </td>

                                <!-- HỌ TÊN -->
                                <td>
                                    <div class="fw-bold text-dark fs-6"><?= htmlspecialchars($row['ho_ten']) ?></div>
                                    <small class="text-muted"><i class="fa-regular fa-envelope me-1"></i><?= strtolower($row['ma_sv']) ?>@st.edu.vn</small>
                                </td>

                                <!-- GIỚI TÍNH -->
                                <td>
                                    <?php if (($row['gioi_tinh'] ?? '') == 'Nam'): ?>
                                        <span class="badge bg-info-subtle text-info fw-bold px-2 py-1"><i class="fa-solid fa-mars me-1"></i>Nam</span>
                                    <?php else: ?>
                                        <span class="badge bg-danger-subtle text-danger fw-bold px-2 py-1"><i class="fa-solid fa-venus me-1"></i>Nữ</span>
                                    <?php endif; ?>
                                </td>

                                <!-- KHOA -->
                                <td>
                                    <span class="badge-dept"><i class="fa-solid fa-building-columns me-1"></i><?= htmlspecialchars($row['ten_khoa'] ?? 'Chưa gán') ?></span>
                                </td>

                                <!-- ĐIỂM TB & PROGRESS BAR (ĐÃ SỬA CHỮ HIỂN THỊ RÕ RÀNG MÀU ĐEN/TÍM) -->
                                <td>
                                    <div class="d-flex align-items-center justify-content-between mb-1">
                                        <span class="fw-black text-dark fs-6" style="font-weight: 800;"><?= number_format($row['diem_tb'], 1) ?></span>
                                        <small class="text-muted" style="font-size: 0.75rem;">/ 10</small>
                                    </div>
                                    <div class="progress" style="height: 6px; background-color: #e2e8f0; border-radius: 10px;">
                                        <?php 
                                            $percent = ($row['diem_tb'] / 10) * 100;
                                            $bg_bar = $row['diem_tb'] >= 8.5 ? 'bg-success' : ($row['diem_tb'] >= 7.0 ? 'bg-info' : ($row['diem_tb'] >= 5.0 ? 'bg-warning' : 'bg-danger'));
                                        ?>
                                        <div class="progress-bar <?= $bg_bar ?> rounded-pill" style="width: <?= $percent ?>%"></div>
                                    </div>
                                </td>

                                <!-- XẾP LOẠI HỌC LỰC -->
                                <td>
                                    <?php if ($row['diem_tb'] >= 8.5): ?>
                                        <span class="badge badge-xl badge-xs"><i class="fa-solid fa-star me-1"></i>Xuất sắc</span>
                                    <?php elseif ($row['diem_tb'] >= 7.0): ?>
                                        <span class="badge badge-xl badge-gioi"><i class="fa-solid fa-graduation-cap me-1"></i>Giỏi</span>
                                    <?php elseif ($row['diem_tb'] >= 5.0): ?>
                                        <span class="badge badge-xl badge-kha"><i class="fa-solid fa-user-check me-1"></i>Khá</span>
                                    <?php else: ?>
                                        <span class="badge badge-xl badge-yeu"><i class="fa-solid fa-triangle-exclamation me-1"></i>Trung Bình</span>
                                    <?php endif; ?>
                                </td>

                                <!-- THAO TÁC -->
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm">
                                        <a href="chinh_sua.php?id=<?= $row['id'] ?>" class="btn btn-outline-primary border-0 rounded-circle me-1" title="Sửa"><i class="fa-solid fa-pen"></i></a>
                                        <a href="xoa.php?id=<?= $row['id'] ?>" class="btn btn-outline-danger border-0 rounded-circle" onclick="return confirm('Xóa sinh viên này?')" title="Xóa"><i class="fa-solid fa-trash"></i></a>
                                    </div>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    <?php else: ?>
                        <tr>
                            <td colspan="8" class="text-center text-muted py-5">
                                <i class="fa-solid fa-user-slash fs-1 d-block mb-2 text-secondary"></i>
                                Không tìm thấy sinh viên nào!
                            </td>
                        </tr>
                    <?php endif; ?>
                </tbody>
            </table>
        </div>
    </div>

</div>

</body>
</html>