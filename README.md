# AI Shopping Assistants

MVP e-commerce thời trang có tìm kiếm văn bản/hình ảnh/đa phương thức và gợi ý sản phẩm.

## Backend (Tuần 2)

Backend dùng FastAPI, PostgreSQL 16 + pgvector, SQLAlchemy và Alembic. API documentation được FastAPI tạo tại `http://localhost:8000/docs`.

### Khởi chạy lần đầu

1. Tạo tệp môi trường (không commit tệp này):

   ```powershell
   Copy-Item .env.example .env
   Copy-Item backend/.env.example backend/.env
   ```

2. Thay `POSTGRES_PASSWORD` trong `.env`, sau đó đặt cùng mật khẩu trong `DATABASE_URL` ở `backend/.env`. Đặt `JWT_SECRET_KEY` thành một chuỗi bí mật dài, ngẫu nhiên.

3. Khởi động database và backend. Migration được chạy tự động khi backend khởi động:

   ```powershell
   docker compose up --build
   ```

4. Kiểm tra:

   ```powershell
   Invoke-RestMethod http://localhost:8000/health
   ```

### Tạo administrator đầu tiên

Sau khi container `backend` đang chạy:

```powershell
docker compose exec backend python scripts/create_admin.py admin@example.com "MotMatKhauManh123" "Administrator"
```

Tài khoản tạo qua `POST /api/v1/auth/register` mặc định có role `USER`; chỉ administrator mới được tạo/sửa/xóa category và product.

### Các API hiện có

- `POST /api/v1/auth/register`, `POST /api/v1/auth/login`, `GET /api/v1/auth/me`
- `GET /api/v1/categories` và Category CRUD cho admin
- `GET /api/v1/products`, `GET /api/v1/products/{id}`; Product CRUD cho admin
- `GET|POST|DELETE /api/v1/users/me/wishlist`
- `GET|POST /api/v1/users/me/interactions`

Text semantic search, image search, multimodal search và recommendation sẽ được bổ sung ở các tuần AI tương ứng. Danh sách product hiện có filter/sort và tìm kiếm chuỗi cơ bản để hoàn thiện API nền.
