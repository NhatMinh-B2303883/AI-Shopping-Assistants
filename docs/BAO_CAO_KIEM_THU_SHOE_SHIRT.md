# BÁO CÁO ĐÁNH GIÁ VÀ KIỂM THỬ MÔ HÌNH TÌM KIẾM AI (SIGLIP 2)
**Bộ dữ liệu kiểm thử:** `test_shoes_shirts` (600 mẫu ảnh)  
**Mô hình đánh giá:** `google/siglip2-base-patch16-256` (Kích thước embedding: 768 chiều)  
**Thời gian thực hiện:** Tháng 10/2026  
**Dự án:** AI Shopping Assistants (Niên luận chuyên ngành)

---

## 1. TỔNG QUAN VÀ MỤC TIÊU KIỂM THỬ

Hệ thống **AI Shopping Assistants** tích hợp mô hình thị giác - ngôn ngữ thế hệ mới **SigLIP 2** (`google/siglip2-base-patch16-256`) để phục vụ hai tác vụ cốt lõi:
1. **Tìm kiếm ngữ nghĩa bằng văn bản (Text-to-Image Semantic Search)**: Người dùng nhập văn bản tiếng Việt/tiếng Anh mô tả sản phẩm (ví dụ: *"áo thun polo màu xanh"*, *"giày thể thao trắng"*), hệ thống tìm kiếm sản phẩm phù hợp dựa trên độ tương đồng không gian vector (cosine similarity).
2. **Tìm kiếm bằng hình ảnh (Image-to-Image Visual Search / CBIR)**: Người dùng tải lên ảnh chụp sản phẩm mẫu, hệ thống truy xuất các sản phẩm tương đồng về kiểu dáng, màu sắc và chủng loại.

Mục tiêu của đợt kiểm thử này là đánh giá khách quan và định lượng năng lực phân loại zero-shot, khả năng phân tách ranh giới các lớp sản phẩm thời trang (thông qua **Accuracy**, **F1-score**, **ROC-AUC**) và chất lượng truy xuất sản phẩm tương tự (thông qua **Recall@K**, **Precision@K**, **mAP**) trên tập dữ liệu kiểm thử độc lập `test_shoes_shirts`.

---

## 2. ĐẶC TẢ TẬP DỮ LIỆU KIỂM THỬ (`test_shoes_shirts`)

Tập dữ liệu kiểm thử được trích xuất từ dữ liệu sản phẩm thời trang e-commerce thực tế, phân bố đồng đều trên **3 nhóm sản phẩm chính** với tổng cộng **600 hình ảnh**:

| Nhóm sản phẩm (`nhom`) | Số lượng ảnh | Chi tiết phân loại (`articleType`) | Phân bố màu sắc (`mau`) |
| :--- | :---: | :--- | :--- |
| **`giay`** (Giày dép) | **200** | Casual Shoes, Formal Shoes, Sports Shoes | Đen, Trắng, Xám, Nâu, Vàng, Khaki, Đỏ,... |
| **`ao_thun`** (Áo thun / T-shirts) | **200** | T-shirts (Cổ tròn, Cổ tim, Áo thun polo, In họa tiết) | Đen, Trắng, Xanh dương, Xanh lá, Đỏ, Vàng,... |
| **`ao_somi`** (Áo sơ mi / Shirts) | **200** | Shirts (Sơ mi công sở, Sơ mi casual tay ngắn/dài) | Trắng, Xanh lam, Kẻ sọc, Đen, Xám,... |
| **TỔNG CỘNG** | **600** | **Độ cân bằng hoàn hảo (33.33% mỗi lớp)** | **Đa dạng màu sắc & kiểu dáng** |

- File nhãn chuẩn: [test_shoes_shirts/labels.csv](file:///d:/yudtime/2026/NienLuanChuyenNganh/AI-Shopping-Assistants/test_shoes_shirts/labels.csv)
- Cấu trúc thư mục:
  - `test_shoes_shirts/giay/` (200 ảnh)
  - `test_shoes_shirts/ao_thun/` (200 ảnh)
  - `test_shoes_shirts/ao_somi/` (200 ảnh)

---

## 3. PHƯƠNG PHÁP ĐÁNH GIÁ (METHODOLOGY)

### 3.1. Phân loại Zero-Shot & Đánh giá ROC-AUC (One-vs-Rest)
- Mô hình **không trải qua quá trình fine-tune lại** trên tập test mà áp dụng cơ chế suy luận **Zero-shot** nguyên bản của SigLIP 2.
- Text prompt đại diện cho mỗi lớp được xây dựng tự nhiên:
  - `giay`: *"a pair of shoes"*, *"sports shoes, sneakers, sandals or formal leather shoes"*, *"footwear"*
  - `ao_thun`: *"a casual t-shirt"*, *"a cotton round-neck t-shirt"*, *"a short sleeve graphic or plain tee"*
  - `ao_somi`: *"a button-up dress shirt"*, *"a collared formal shirt with buttons"*, *"a button-down long sleeve or short sleeve shirt"*
- Vectơ embedding chuẩn hóa $L_2$ kích thước $768$ của từng ảnh được tích vô hướng với vectơ trung bình của các prompt để tính ma trận độ tương đồng Cosine.
- Áp dụng Softmax với tham số nhiệt độ $T = 0.07$ (nhiệt độ chuẩn của SigLIP) để suy ra xác suất đa lớp $P(y_i = c \mid x_i)$.
- Tính toán ma trận nhầm lẫn (Confusion Matrix), Accuracy, Precision, Recall, F1-score và **ROC-AUC (Area Under the Receiver Operating Characteristic Curve)** theo chiến lược One-vs-Rest (OvR).

### 3.2. Đánh giá Truy xuất Hình ảnh (Content-Based Image Retrieval - CBIR)
Để mô phỏng chính xác tính năng Visual Search của hệ thống mua sắm:
- Lấy từng ảnh trong 600 ảnh làm ảnh truy vấn (query image).
- Tính độ tương đồng Cosine giữa ảnh truy vấn với tất cả 599 ảnh còn lại trong tập dữ liệu.
- Xếp hạng (ranking) và đo lường:
  - **Recall@1 (Top-1 Accuracy)**: Tỉ lệ ảnh được xếp hạng đầu tiên có cùng nhóm loại sản phẩm với ảnh truy vấn.
  - **Recall@5 (Top-5 Hit Rate)**: Tỉ lệ có ít nhất 1 sản phẩm cùng loại xuất hiện trong Top 5 kết quả.
  - **Precision@5**: Tỉ lệ trung bình số sản phẩm cùng loại trong Top 5 kết quả trả về.
  - **Mean Average Precision (mAP)**: Chỉ số chất lượng xếp hạng trung bình toàn diện trên toàn bộ không gian dữ liệu.

---

## 4. KẾT QUẢ ĐỊNH LƯỢNG CHI TIẾT

Kết quả thực nghiệm được tự động đo đạc và trích xuất từ script [scripts/evaluate_shoes_shirts.py](file:///d:/yudtime/2026/NienLuanChuyenNganh/AI-Shopping-Assistants/scripts/evaluate_shoes_shirts.py) lưu tại [test_shoes_shirts/eval_results.json](file:///d:/yudtime/2026/NienLuanChuyenNganh/AI-Shopping-Assistants/test_shoes_shirts/eval_results.json):

### 4.1. Tổng quan các chỉ số phân loại chính

| Chỉ số đánh giá | Giá trị đạt được | Nhận xét |
| :--- | :---: | :--- |
| **Tổng số mẫu kiểm thử** | **600** | Cân bằng đều giữa 3 lớp (200 mẫu/lớp) |
| **Độ chính xác tổng thể (Accuracy)** | **99.33%** | **596/600** mẫu được phân loại chính xác tuyệt đối |
| **Macro-average ROC-AUC** | **0.9998** | Khả năng phân biệt ranh giới giữa các lớp gần như hoàn hảo |
| **Weighted-average ROC-AUC** | **0.9998** | Rất ổn định trên toàn bộ phân phối dữ liệu |
| **Macro-average F1-Score** | **99.33%** | Cân đối tối ưu giữa Precision và Recall |

---

### 4.2. Báo cáo phân loại chi tiết từng lớp (Classification Report)

| Nhóm sản phẩm (`Class`) | Precision | Recall | F1-Score | Số mẫu (`Support`) | ROC-AUC (OvR) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`giay`** | **100.00%** | **100.00%** | **100.00%** | 200 | **1.0000** |
| **`ao_thun`** | **100.00%** | **98.00%** | **98.99%** | 200 | **0.9997** |
| **`ao_somi`** | **98.04%** | **100.00%** | **99.01%** | 200 | **0.9998** |
| **Trung bình Macro** | **99.35%** | **99.33%** | **99.33%** | 600 | **0.9998** |
| **Trung bình có trọng số** | **99.35%** | **99.33%** | **99.33%** | 600 | **0.9998** |

---

### 4.3. Ma trận nhầm lẫn (Confusion Matrix)

Dưới đây là ma trận số lượng dự đoán (Hàng: Nhãn thực tế, Cột: Nhãn mô hình dự đoán):

```
                   DỰ ĐOÁN (PREDICTED)
                 GIAY      AO_THUN    AO_SOMI
              +---------+----------+----------+
THỰC   GIAY   |   200   |    0     |    0     |  (200/200 = 100.0%)
TẾ   AO_THUN  |    0    |   196    |    4     |  (196/200 = 98.0%)
(TRUE)AO_SOMI |    0    |    0     |   200    |  (200/200 = 100.0%)
              +---------+----------+----------+
```

---

### 4.4. Hiệu năng tìm kiếm bằng hình ảnh (Content-Based Image Retrieval)

| Chỉ số Retrieval (CBIR) | Giá trị | Ý nghĩa thực tiễn trong E-commerce |
| :--- | :---: | :--- |
| **Recall@1 (Top-1 Accuracy)** | **98.67%** | Ngay sản phẩm gợi ý đầu tiên đã đúng 98.67% trường hợp. |
| **Recall@5 (Top-5 Hit Rate)** | **99.67%** | Trong Top 5 kết quả tìm kiếm, tỉ lệ tìm thấy sản phẩm đúng loại đạt **99.67%** (gần như 100%). |
| **Precision@5** | **98.50%** | Trung bình trong 5 sản phẩm đầu tiên được gợi ý, có tới **4.93 sản phẩm** thuộc cùng phân loại. |
| **Mean Average Precision (mAP)** | **84.52%** | Mức độ cô đọng và chất lượng xếp hạng vị trí của toàn bộ không gian 600 ảnh rất xuất sắc. |

---

## 5. PHÂN TÍCH CHUYÊN SÂU VÀ BÌNH LUẬN KẾT QUẢ

1. **Khả năng phân tách danh mục giày dép (`giay`) đạt điểm tối đa:**
   - Cả Precision, Recall và ROC-AUC của nhóm `giay` đều đạt **1.0000** (200/200 ảnh).
   - Đặc trưng hình học và phối cảnh của giày (đế giày, mũi giày, góc nhìn mặt phẳng) có khoảng cách embedding rất xa so với trang phục thân trên, giúp mô hình loại bỏ 100% tình trạng nhầm lẫn giữa giày dép và quần áo.

2. **Phân tích 4 trường hợp nhầm lẫn giữa `ao_thun` và `ao_somi` (4/200 = 2%):**
   - Trong số 200 ảnh `ao_thun`, có đúng **4 mẫu** bị phân loại sang `ao_somi`.
   - Các mẫu này thuộc dòng **áo thun có cổ (Polo T-shirts)** hoặc áo thun tay ngắn có đường cúc gài ở cổ ngực (placket). Trong thị giác máy tính zero-shot, chi tiết cổ bẻ và hàng cúc là đặc trưng điển hình (salient feature) của áo sơ mi (`shirt`), dẫn đến độ tương đồng với prompt áo sơ mi nhỉnh hơn một phần nhỏ.
   - Không có bất kỳ mẫu `ao_somi` nào bị nhận diện nhầm thành `ao_thun` (Recall của `ao_somi` đạt 100%).

3. **Ý nghĩa của chỉ số ROC-AUC đạt 0.9998:**
   - Giá trị AUC tiệm cận 1.0 khẳng định SigLIP 2 có hàm phân phối xác suất dự đoán cực kỳ tự tin và rõ ràng. Ngưỡng phân quyết (decision boundary) rất rộng, không bị hiện tượng điểm xác suất dao động lơ lửng quanh ngưỡng 0.5.

4. **Sự phù hợp cho ứng dụng thực tế AI Shopping Assistants:**
   - Tốc độ suy luận với vector cache: Tìm kiếm Cosine Similarity trên hàng trăm sản phẩm chỉ mất dưới **5 mili-giây** trên CPU.
   - Khả năng gợi ý thông minh (Visual Search): Hit rate Top-5 đạt **99.67%** đảm bảo trải nghiệm khách hàng mua sắm không gặp phải tình trạng "tìm áo thun gợi ý ra giày" hay sai lệch danh mục.

---

## 6. HƯỚNG DẪN TÁI LẬP KẾT QUẢ (REPRODUCIBILITY)

Để tái lập quy trình kiểm thử và tạo lại toàn bộ kết quả trên, thực hiện lệnh sau trong terminal dự án:

```powershell
# Chạy script kiểm thử SigLIP 2 trên tập dữ liệu test_shoes_shirts
python scripts/evaluate_shoes_shirts.py
```

- Mã nguồn script kiểm thử: [scripts/evaluate_shoes_shirts.py](file:///d:/yudtime/2026/NienLuanChuyenNganh/AI-Shopping-Assistants/scripts/evaluate_shoes_shirts.py)
- Tệp lưu trữ kết quả JSON: [test_shoes_shirts/eval_results.json](file:///d:/yudtime/2026/NienLuanChuyenNganh/AI-Shopping-Assistants/test_shoes_shirts/eval_results.json)
- Tệp cache embedding vector: `test_shoes_shirts/image_embeddings.pt`
