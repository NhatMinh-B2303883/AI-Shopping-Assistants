# 📋 BÁO CÁO TỔNG HỢP THAY ĐỔI — Phiên làm việc 17/10/2026

> **Ngày:** 17/10/2026  
> **Thời gian:** 20:55 — 22:50 (~ 2 giờ)  
> **Nhánh:** `main`  
> **Trạng thái tổng thể:** ✅ Hoàn thành

---

## MỤC LỤC

1. [Cập nhật mã nguồn từ Git](#1-cập-nhật-mã-nguồn-từ-git)
2. [Tích hợp Frontend theo Tài liệu kỹ thuật](#2-tích-hợp-frontend-theo-tài-liệu-kỹ-thuật)
3. [Tạo Scripts khởi chạy hệ thống](#3-tạo-scripts-khởi-chạy-hệ-thống)
4. [Sửa lỗi Generate Embeddings](#4-sửa-lỗi-generate-embeddings)
5. [Sửa lỗi sản phẩm không hiển thị trên Web](#5-sửa-lỗi-sản-phẩm-không-hiển-thị-trên-web)
6. [Tổng hợp danh sách file thay đổi](#6-tổng-hợp-danh-sách-file-thay-đổi)

---

## 1. CẬP NHẬT MÃ NGUỒN TỪ GIT

**Mục tiêu:** Đồng bộ code mới nhất từ remote repository.

**Thao tác đã thực hiện:**
- `git fetch --all --prune` — Tải toàn bộ thay đổi từ remote
- `git pull origin main` — Cập nhật nhánh `main` (đã ở commit mới nhất `d86dbd9`)
- `git branch -f frontend/week1 origin/frontend/week1` — Đồng bộ nhánh `frontend/week1` lên `dbd206d`

**Kết quả:** Cả hai nhánh `main` và `frontend/week1` đều đã cập nhật mới nhất từ `origin`.

---

## 2. TÍCH HỢP FRONTEND THEO TÀI LIỆU KỸ THUẬT

**Mục tiêu:** Đọc và triển khai theo "TÀI LIỆU TÍCH HỢP FRONTEND NEXT.J.txt" — hợp đồng tích hợp giữa Frontend và Backend FastAPI + AI SigLIP 2.

### 2.1. Viết lại `frontend/app.js` (1634 dòng)

File `app.js` được viết lại hoàn toàn để tuân thủ đầy đủ tài liệu tích hợp, bao gồm:

| Module | Mô tả | Tài liệu tham chiếu |
|--------|-------|---------------------|
| **Cấu hình API** | `CONFIG` object với `API_BASE_URL`, `API_V1_URL`, placeholder image, giới hạn upload | Mục 1 |
| **Xử lý URL ảnh** | `resolveImageUrl()` — ghép relative path với domain backend | Mục 1.2 |
| **Xử lý giá null** | `formatProductPrice()` — hiển thị "Đang cập nhật" khi price = null | Mục 2 |
| **Tải danh mục** | `loadCategories()` — GET `/api/v1/categories` | Mục 4 |
| **Tải bộ lọc** | `loadFilters()` — GET `/api/v1/products/filters` (facets động) | Mục 4.2 |
| **Tải sản phẩm** | `loadProducts()` — GET `/api/v1/products` với phân trang & bộ lọc backend | Mục 4.1 |
| **Render catalog** | `renderCatalog()` — ưu tiên `image_web_url`, fallback `image_url` | Mục 1.2, 2 |
| **AI Visual Search** | `submitAiSearch()` — POST `/api/v1/search/visual` (upload ảnh) | Mục 3.1 |
| **AI Multimodal Search** | POST `/api/v1/search/multimodal` (ảnh + text + weight) | Mục 3.2 |
| **AI Score Badge** | Hiển thị phần trăm độ tương đồng trên mỗi kết quả AI | Mục 3.3 |
| **Chi tiết sản phẩm** | `openDetailModal()` — GET `/api/v1/products/{id}` với gallery ảnh | Mục 6 |
| **Tìm tương tự** | `findSimilarProducts()` — POST `/api/v1/search/visual` từ ảnh sản phẩm | Mục 3 |
| **Xác thực JWT** | Đăng nhập, đăng ký, đăng xuất, quản lý token trong localStorage | Mục 5 |
| **Giỏ hàng** | Cart drawer với thêm/sửa/xóa sản phẩm, voucher, freeship | — |
| **Bộ lọc** | Giới tính, màu sắc, khoảng giá, sắp xếp, danh mục con | Mục 4 |
| **Phân trang** | Offset-based pagination đồng bộ với backend | Mục 4.1 |
| **QR Code** | Tạo mã QR cho sản phẩm & quét mã QR bằng camera | — |

### 2.2. Cập nhật `frontend/index.html`

- Thêm cấu trúc HTML cho các tính năng mới: modal tìm kiếm ảnh AI, modal quét QR, modal chi tiết sản phẩm, modal xác thực, cart drawer
- Thêm thư viện bên ngoài: `qrcodejs` (tạo QR), `jsQR` (đọc QR từ camera)
- Cấu trúc semantic HTML5 chuẩn SEO

### 2.3. Cập nhật `frontend/styles.css`

- Bổ sung styles cho toàn bộ component mới: card sản phẩm, AI score badge, cart drawer, modals, bộ lọc động, phân trang, v.v.

---

## 3. TẠO SCRIPTS KHỞI CHẠY HỆ THỐNG

**Mục tiêu:** Tạo các tệp kịch bản tự động để khởi động Backend + Frontend chỉ bằng 1 lệnh.

### 3.1. `start_app.bat` (mới tạo)

Script batch cho Windows Command Prompt:
1. Khởi động Docker containers (PostgreSQL + Backend)
2. Chờ Backend khởi động (5 giây)
3. Mở trình duyệt tại `http://localhost:3000`
4. Chạy Python HTTP server cho Frontend trên port 3000

### 3.2. `run.ps1` (mới tạo)

Script PowerShell với chức năng tương tự nhưng thêm:
- Kiểm tra health check Backend qua `Invoke-RestMethod`
- Giao diện console có màu sắc
- Hiển thị bảng địa chỉ truy cập

### 3.3. `HUONG_DAN_CHAY_WEB.md` (mới tạo)

Tài liệu hướng dẫn đầy đủ bao gồm:
- Cách 1: Khởi chạy tự động (1 click)
- Cách 2: Chạy thủ công từng bước
- Các câu lệnh quản trị: seed data, tạo admin, generate embeddings
- Danh sách tài khoản mẫu để test
- Bảng địa chỉ truy cập

---

## 4. SỬA LỖI GENERATE EMBEDDINGS

**Lỗi ban đầu:**
```
ValueError: Product 04bdf5fc-1e53-4b99-8656-58daeea25f44 has empty canonical_text.
```

**Nguyên nhân:** Một số sản phẩm trong database có trường `canonical_text` rỗng (empty string hoặc NULL), khiến script `generate_embeddings.py` bị crash khi yêu cầu tất cả sản phẩm phải có text.

**File sửa:** `backend/app/service/ai.py`

**Giải pháp:** Cập nhật logic xử lý để:
- Tự động sinh `canonical_text` từ thông tin sản phẩm (name, category, gender, color) khi trường này rỗng
- Không crash khi gặp sản phẩm thiếu `canonical_text`

---

## 5. SỬA LỖI SẢN PHẨM KHÔNG HIỂN THỊ TRÊN WEB

### 5.1. Mô tả lỗi

Trang web EAST & SOUL hiển thị **0 sản phẩm** mặc dù database có **992 sản phẩm**.

### 5.2. Phân tích nguyên nhân gốc (Root Cause)

```
Frontend khởi tạo maxPrice = 3500000
    │
    ▼
API Request: GET /products?max_price=3500000
    │
    ▼
Backend SQL: WHERE price <= 3500000
    │
    ▼
Tất cả sản phẩm có price = NULL
SQL: NULL <= 3500000 → NULL (falsy)
    │
    ▼
Kết quả: 0 sản phẩm ← BUG
```

### 5.3. Các thay đổi

#### Backend — `backend/app/api/v1/endpoints/products.py`

```diff
  if min_price is not None:
-     statement = statement.where(Product.price >= min_price)
+     statement = statement.where(or_(Product.price >= min_price, Product.price.is_(None)))
  if max_price is not None:
-     statement = statement.where(Product.price <= max_price)
+     statement = statement.where(or_(Product.price <= max_price, Product.price.is_(None)))
```

#### Frontend — `frontend/app.js` (4 điểm sửa)

**a) Giá trị mặc định `maxPrice`:**
```diff
- maxPrice: 3500000,
+ maxPrice: null,
```

**b) Hàm `setPricePreset()` — preset "Tất cả" và "Trên 1.5tr":**
```diff
  if (preset === "all") {
-   appState.maxPrice = 3500000;
+   appState.maxPrice = null;
  }
  // ...
  if (preset === "over1500") {
-   appState.maxPrice = 3500000;
+   appState.maxPrice = null;
  }
```

**c) Hàm `updateFilterIndicator()`:**
```diff
- if (appState.minPrice != null || (appState.maxPrice && appState.maxPrice < 3500000)) {
+ if (appState.minPrice != null || appState.maxPrice != null) {
```

**d) Hàm `resetAll()`:**
```diff
- appState.maxPrice = 3500000;
+ appState.maxPrice = null;
```

### 5.4. Kết quả sau khi sửa

| Tiêu chí | Trước | Sau |
|----------|-------|-----|
| Số sản phẩm hiển thị | **0** | **992** (12 mỗi trang) |
| Hình ảnh sản phẩm | Không hiện | ✅ Hiển thị đầy đủ |
| Bộ lọc giá "Tất cả" | Gửi `max_price=3500000` | Không gửi `max_price` |
| Sản phẩm chưa có giá | Bị loại khỏi kết quả | ✅ Hiển thị "Đang cập nhật" |

---

## 6. TỔNG HỢP DANH SÁCH FILE THAY ĐỔI

### Files tạo mới

| # | File | Mô tả |
|---|------|-------|
| 1 | `frontend/app.js` | Viết lại hoàn toàn — tích hợp đầy đủ Backend API + AI Search (~1634 dòng) |
| 2 | `start_app.bat` | Script batch khởi chạy tự động hệ thống (Windows CMD) |
| 3 | `run.ps1` | Script PowerShell khởi chạy tự động hệ thống |
| 4 | `HUONG_DAN_CHAY_WEB.md` | Tài liệu hướng dẫn chạy dự án |
| 5 | `docs/BAO_CAO_SUA_LOI_HIEN_THI_SAN_PHAM.md` | Báo cáo chi tiết lỗi hiển thị sản phẩm |
| 6 | `docs/BAO_CAO_THAY_DOI.md` | Báo cáo tổng hợp (file này) |

### Files chỉnh sửa

| # | File | Loại | Mô tả |
|---|------|------|-------|
| 1 | `frontend/index.html` | Cập nhật | Thêm HTML cho modals, components, thư viện JS |
| 2 | `frontend/styles.css` | Cập nhật | Thêm styles cho toàn bộ UI components mới |
| 3 | `frontend/app.js` | Bug fix | Sửa lỗi `maxPrice` mặc định gây mất sản phẩm |
| 4 | `backend/app/api/v1/endpoints/products.py` | Bug fix | Lọc giá bao gồm sản phẩm `price IS NULL` |
| 5 | `backend/app/service/ai.py` | Bug fix | Tự sinh `canonical_text` khi rỗng (fix embeddings) |
| 6 | `start_app.bat` | Fix | Sửa ký tự `&` gây lỗi batch script |

---

## 7. GHI CHÚ QUAN TRỌNG

1. **Giá sản phẩm:** Toàn bộ 992 sản phẩm hiện có `price = NULL`. Cần cập nhật giá từ nguồn dữ liệu gốc.
2. **CORS:** Backend cho phép origin `http://localhost:3000`. Frontend **phải** truy cập qua HTTP server, không mở trực tiếp file HTML.
3. **Cách chạy nhanh:** Mở CMD → chạy `start_app.bat` → truy cập `http://localhost:3000`.
4. **AI Search:** Yêu cầu đã chạy `generate_embeddings.py` thành công để tìm kiếm bằng ảnh hoạt động.
