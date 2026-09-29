# 🚀 HƯỚNG DẪN CÀI ĐẶT & KHỞI CHẠY BACKEND CHO DỰ ÁN FRONTEND (TUẦN 3)

Tài liệu này dành cho thành viên phát triển **Frontend (Next.js)** để thiết lập môi trường Backend trên máy mới chỉ trong 5 phút.

---

## 1. Yêu cầu trước khi cài đặt (Prerequisites)

* **Docker Desktop**: Đã cài đặt và đang chạy (trên Windows cần bật WSL2).
* **Git**: Đã cài đặt.
* **Cổng mạng (Ports)**: Đảm bảo cổng `8000` (Backend) và `5432` (PostgreSQL) không bị ứng dụng khác chiếm dụng.

---

## 2. Các bước cài đặt từng bước (Step-by-step Setup)

### Bước 1: Clone Repository và mở Terminal
Mở terminal (PowerShell, Command Prompt hoặc Bash) tại thư mục gốc dự án:
```powershell
git clone <URL_REPO>
cd AI-Shopping-Assistants
```

---

### Bước 2: Thiết lập biến môi trường (`.env`)
Dự án cần 2 tệp `.env`: một ở thư mục gốc (cho Docker) và một trong thư mục `backend/`.

1. **Tạo file `.env` ở thư mục gốc:**
   ```powershell
   Copy-Item .env.example .env
   # Trên macOS/Linux: cp .env.example .env
   ```
   *Mở file `.env` vừa tạo và đặt mật khẩu database, ví dụ:*
   ```env
   POSTGRES_DB=ai_shopping
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=MatKhauDatabase123!
   POSTGRES_PORT=5432
   BACKEND_PORT=8000
   ```

2. **Tạo file `.env` trong thư mục `backend/`:**
   ```powershell
   Copy-Item backend/.env.example backend/.env
   # Trên macOS/Linux: cp backend/.env.example backend/.env
   ```
   *Mở file `backend/.env` và cập nhật:*
   ```env
   APP_NAME=AI Shopping Assistants API
   ENVIRONMENT=development
   DEBUG=true
   API_V1_PREFIX=/api/v1
   # Lưu ý: Mật khẩu ở DATABASE_URL phải khớp chính xác với POSTGRES_PASSWORD ở trên:
   DATABASE_URL=postgresql+psycopg://postgres:MatKhauDatabase123!@db:5432/ai_shopping
   JWT_SECRET_KEY=mot-chuoi-ngau-nhien-that-dai-va-bao-mat-123456789
   JWT_ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=1440
   CORS_ORIGINS=http://localhost:3000
   ```

> ⚠️ **LƯU Ý QUAN TRỌNG:** Giá trị mật khẩu giữa `.env` gốc và chuỗi kết nối trong `backend/.env` **bắt buộc phải trùng nhau**, nếu không backend sẽ không kết nối được database!

---

### Bước 3: Khởi chạy hệ thống bằng Docker Compose
Chạy lệnh sau tại thư mục gốc của dự án:
```powershell
docker compose up --build -d
```
*(Hệ thống sẽ tải image PostgreSQL 16 có pgvector, build container FastAPI và **tự động chạy migration** tạo đầy đủ 8 bảng trong database).*

**Kiểm tra container đang chạy:**
```powershell
docker compose ps
```
Nếu thấy cả 2 service `ai-shopping-db (healthy)` và `ai-shopping-backend (Up)` là thành công!

Kiểm tra API qua trình duyệt: truy cập [http://localhost:8000/health](http://localhost:8000/health) thấy trả về `{"status": "ok"}`.

---

### Bước 4: Đổ dữ liệu mẫu (Seed Data) & Tạo Admin
Sau khi container backend đã chạy, thực thi 2 lệnh sau:

1. **Đổ dữ liệu mẫu (25 sản phẩm + danh mục + user mẫu):**
   ```powershell
   docker compose exec backend python scripts/seed.py
   ```
   *(Script sẽ tự động tạo cây danh mục Shoes/Clothing, 25 sản phẩm kèm ảnh placeholder, giá, màu sắc, giới tính).*

2. **Tạo tài khoản Quản trị viên (Admin):**
   ```powershell
   docker compose exec backend python scripts/create_admin.py admin@example.com "Admin123!" "Quản Trị Viên"
   ```

---

## 3. Danh sách tài khoản mẫu để test

| Vai trò | Email | Mật khẩu | Quyền hạn |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@example.com` | `Admin123!` | Toàn quyền (Thêm/Sửa/Xóa sản phẩm, danh mục) |
| **User 1** | `an.nguyen@example.com` | `User123!` | Người dùng thường (Yêu thích, xem hàng) |
| **User 2** | `bich.tran@example.com` | `User123!` | Người dùng thường |

---

## 4. Tài liệu API (Swagger UI)
Sau khi chạy backend, bạn có thể xem chi tiết tất cả các endpoint, schema request/response tại:
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

---

## 5. ⚠️ NHỮNG LƯU Ý ĐẶC BIỆT KHI LÀM FRONTEND (TUẦN 3)

### 1. Cấu hình Cổng CORS
* Backend mặc định cấu hình CORS cho `http://localhost:3000` (cổng mặc định của Next.js).
* Nếu máy bạn mở Next.js bị trùng cổng và nhảy sang `http://localhost:3001`, bạn hãy mở file `backend/.env` sửa thành:
  ```env
  CORS_ORIGINS=http://localhost:3000,http://localhost:3001
  ```
  Sau đó khởi động lại backend: `docker compose restart backend`.

### 2. Cấu hình Next.js Image Domain (`placehold.co`)
* Hiện tại ảnh sản phẩm dùng placeholder từ domain `placehold.co`.
* Nếu bạn dùng component `<Image />` của Next.js (`next/image`), bạn **bắt buộc** phải khai báo domain này trong `next.config.js` (hoặc `next.config.mjs`):
  ```javascript
  /** @type {import('next').NextConfig} */
  const nextConfig = {
    images: {
      remotePatterns: [
        {
          protocol: 'https',
          hostname: 'placehold.co',
        },
      ],
    },
  };

  export default nextConfig;
  ```
  *(Nếu không cấu hình, Next.js sẽ báo lỗi chặn tải ảnh từ domain lạ).*

### 3. API Base URL và Đính kèm Token
* Tất cả API đều có tiền tố: `http://localhost:8000/api/v1`
* Các API cá nhân như `/users/me/wishlist`, `/users/me/interactions`, `/auth/me` yêu cầu gắn header:
  ```
  Authorization: Bearer <access_token>
  ```
* **Đăng ký tự đăng nhập:** Khi gọi `POST /api/v1/auth/register`, backend sẽ trả về luôn `access_token` và object `user`. Bạn có thể lưu token vào cookie/localStorage và cho người dùng đăng nhập ngay mà không cần bắt họ đăng nhập lại.

### 4. Cấu trúc dữ liệu phân trang (Pagination)
* API `GET /api/v1/products` không trả về mảng trực tiếp mà trả về cấu trúc:
  ```json
  {
    "items": [ /* danh sách sản phẩm */ ],
    "total": 25,
    "limit": 24,
    "offset": 0
  }
  ```
  Dùng `total` để tính tổng số trang: `Math.ceil(total / limit)`.

### 5. API lấy bộ lọc (Filter Sidebar)
* Trước khi render sidebar bộ lọc trang Shop, bạn gọi:
  `GET /api/v1/products/filters`
  Backend sẽ trả về danh sách `colors`, `genders`, và khoảng giá `min` - `max` thực tế từ cơ sở dữ liệu để bạn render checkbox và slider khoảng giá.

---

## 6. Các lệnh hữu ích thường dùng

* **Xem log backend:** `docker compose logs -f backend`
* **Tạm dừng hệ thống:** `docker compose stop`
* **Bật lại hệ thống:** `docker compose start`
* **Xóa sạch làm lại từ đầu (kèm xóa database):**
  ```powershell
  docker compose down -v
  docker compose up --build -d
  docker compose exec backend python scripts/seed.py
  ```
