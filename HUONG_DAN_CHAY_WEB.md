# 🚀 HƯỚNG DẪN CHẠY DỰ ÁN AI SHOPPING ASSISTANTS

Tài liệu này tổng hợp toàn bộ câu lệnh và các bước cần thiết để khởi chạy **Backend (FastAPI + PostgreSQL pgvector)** và **Frontend Web (EAST & SOUL)**.

---

## ⚡ CÁCH 1: KHỞI CHẠY TỰ ĐỘNG (NHANH NHẤT)

Bạn chỉ cần chạy 1 tệp kịch bản được tạo sẵn tại thư mục gốc:

### Cách A: Dùng Command Prompt / Double Click (Windows)
* Nhấp đúp chuột vào file: **`start_app.bat`**
* Hoặc mở CMD gõ:
  ```cmd
  start_app.bat
  ```

### Cách B: Dùng PowerShell
* Mở PowerShell tại thư mục dự án và chạy:
  ```powershell
  .\run.ps1
  ```

> Kịch bản sẽ tự động:
> 1. Khởi động PostgreSQL 16 (pgvector) & Backend FastAPI qua Docker (`docker compose up -d`).
> 2. Chờ Backend sẵn sàng tại `http://localhost:8000/health`.
> 3. Tự động mở trình duyệt web và chạy server Frontend tại `http://localhost:3000`.

---

## 🛠️ CÁCH 2: CÁC CÂU LỆNH CHẠY THỦ CÔNG TỪNG BƯỚC

Nếu bạn muốn tự mở từng Terminal để theo dõi log:

### Bước 1: Khởi động Database & Backend (Docker)
Mở **Terminal 1** tại thư mục gốc dự án:

```powershell
# Khởi động container ngầm
docker compose up -d

# Xem log hoạt động của Backend
docker compose logs -f backend
```

* Kiểm tra trạng thái Backend: Mở trình duyệt vào [http://localhost:8000/health](http://localhost:8000/health) thấy `{"status": "ok"}`.
* Xem tài liệu API (Swagger UI): [http://localhost:8000/docs](http://localhost:8000/docs).

---

### Bước 2: Khởi chạy Frontend Web (Cổng 3000)
Mở **Terminal 2** tại thư mục gốc dự án:

```powershell
# Dùng Python (có sẵn trên máy)
python -m http.server 3000 --directory frontend
```

*Hoặc nếu bạn có Node.js / npx:*
```bash
npx serve frontend -p 3000
```

Truy cập giao diện Web mua sắm tại: 👉 **[http://localhost:3000](http://localhost:3000)**

---

## 📋 CÁC CÂU LỆNH QUẢN TRỊ & DỮ LIỆU CẦN THIẾT

### 1. Đổ dữ liệu mẫu (Seed Data / Catalog)
Nếu cơ sở dữ liệu mới tinh chưa có sản phẩm:

```powershell
# Nạp catalog sản phẩm thời trang đầy đủ
docker compose exec backend python scripts/import_catalog.py

# Hoặc nạp 25 sản phẩm mẫu
docker compose exec backend python scripts/seed.py
```

### 2. Tạo tài khoản Quản trị viên (Admin)
```powershell
docker compose exec backend python scripts/create_admin.py admin@example.com "Admin123!" "Quản Trị Viên"
```

### 3. Tạo vector embeddings AI cho sản phẩm
```powershell
docker compose exec backend python scripts/generate_embeddings.py
```

---

## 🛑 DỪNG HỆ THỐNG KHI KHÔNG DÙNG

1. **Dừng Frontend**: Tại Terminal đang chạy `python -m http.server`, nhấn tổ hợp phím **`Ctrl + C`**.
2. **Dừng Backend & Database**:
   ```powershell
   docker compose down
   ```
   *(Dữ liệu trong Database được giữ nguyên an toàn qua Docker Volume)*.

---

## 🔑 DANH SÁCH TÀI KHOẢN MẪU ĐỂ TEST TRÊN WEB

| Vai trò | Email | Mật khẩu | Chức năng |
| :--- | :--- | :--- | :--- |
| **Quản trị viên (Admin)** | `admin@example.com` | `Admin123!` | Toàn quyền quản trị catalog & danh mục |
| **Khách hàng 1** | `an.nguyen@example.com` | `User123!` | Đăng nhập, giỏ hàng, tìm kiếm AI |
| **Khách hàng 2** | `bich.tran@example.com` | `User123!` | Đăng nhập, giỏ hàng, tìm kiếm AI |

*(Bạn cũng có thể bấm nút **Đăng nhập** trên góc phải Web và chọn tab **Đăng ký mới** để tạo tài khoản riêng của mình).*

---

## 🌐 DANH SÁCH ĐỊA CHỈ TRUY CẬP

* **Giao diện Web Mua Sắm (Frontend)**: [http://localhost:3000](http://localhost:3000)
* **Backend API Base**: [http://localhost:8000](http://localhost:8000)
* **API Documentation (Swagger UI)**: [http://localhost:8000/docs](http://localhost:8000/docs)
* **Kiểm tra sức khỏe Backend**: [http://localhost:8000/health](http://localhost:8000/health)
