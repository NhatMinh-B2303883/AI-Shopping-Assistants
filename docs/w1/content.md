# 1. PROBLEM STATEMENT

## 1.1. Bối cảnh

Các nền tảng thương mại điện tử thời trang hiện nay cung cấp số lượng sản phẩm lớn, khiến việc tìm kiếm đúng sản phẩm trở thành một vấn đề quan trọng đối với người dùng.

Phương thức tìm kiếm phổ biến dựa trên từ khóa, trong đó người dùng nhập tên hoặc các thuộc tính của sản phẩm cần tìm. Tuy nhiên, phương thức này phụ thuộc vào khả năng mô tả nhu cầu bằng từ khóa của người dùng cũng như thông tin mô tả được lưu trữ trong hệ thống.

Trong thực tế, người dùng có thể gặp những trường hợp như:

* Biết sản phẩm cần tìm có hình dáng như thế nào nhưng không biết tên sản phẩm.
* Có một hình ảnh tham khảo và muốn tìm các sản phẩm có kiểu dáng tương tự.
* Muốn tìm sản phẩm tương tự một hình ảnh nhưng có thêm các yêu cầu bằng văn bản.
* Muốn tìm các sản phẩm phù hợp với sở thích dựa trên những sản phẩm đã xem hoặc yêu thích.

Các trường hợp trên khó được xử lý đầy đủ nếu hệ thống chỉ sử dụng phương thức tìm kiếm dựa trên từ khóa truyền thống.

## 1.2. Vấn đề

Đề tài tập trung giải quyết vấn đề:

> **Làm thế nào để xây dựng một hệ thống thương mại điện tử thời trang cho phép người dùng tìm kiếm sản phẩm một cách linh hoạt thông qua văn bản, hình ảnh và sự kết hợp giữa hình ảnh với văn bản, đồng thời cung cấp khả năng gợi ý sản phẩm dựa trên hành vi của người dùng?**

Để giải quyết vấn đề này, đề tài tích hợp một module AI sử dụng mô hình embedding đa phương thức để biểu diễn hình ảnh và văn bản dưới dạng vector.

Các vector này được sử dụng để thực hiện tìm kiếm sản phẩm dựa trên mức độ tương đồng.

---

# 2. OBJECTIVES

## 2.1. Mục tiêu tổng quát

Xây dựng một hệ thống thương mại điện tử thời trang có khả năng **tìm kiếm và gợi ý sản phẩm thông minh**, trong đó AI được tích hợp như một module hỗ trợ quá trình tìm kiếm và khám phá sản phẩm.

Hệ thống tập trung vào hai nhóm sản phẩm chính:

* Giày.
* Quần áo.

---

## 2.2. Mục tiêu cụ thể

### Mục tiêu 1 — Xây dựng nền tảng thương mại điện tử

Xây dựng hệ thống web cho phép:

* Người dùng đăng ký và đăng nhập.
* Xem danh sách sản phẩm.
* Xem chi tiết sản phẩm.
* Tìm kiếm sản phẩm.
* Lưu sản phẩm yêu thích.
* Xem lịch sử tương tác.
* Nhận sản phẩm được gợi ý.

Đối với quản trị viên:

* Quản lý sản phẩm.
* Quản lý danh mục.
* Quản lý thông tin sản phẩm.

---

### Mục tiêu 2 — Xây dựng tìm kiếm bằng văn bản

Cho phép người dùng nhập các truy vấn tự nhiên, ví dụ:

> "giày chạy bộ nam màu trắng"

Hệ thống sử dụng semantic embedding để tìm các sản phẩm có nội dung phù hợp với ý định tìm kiếm thay vì chỉ tìm kiếm chính xác theo chuỗi ký tự.

---

### Mục tiêu 3 — Xây dựng tìm kiếm bằng hình ảnh

Cho phép người dùng tải lên một hình ảnh sản phẩm.

Hệ thống sẽ:

```text
Image
 ↓
AI Embedding
 ↓
Vector Search
 ↓
Similarity Ranking
 ↓
Similar Products
```

Mục tiêu là tìm ra các sản phẩm có đặc trưng hình ảnh tương tự.

---

### Mục tiêu 4 — Xây dựng tìm kiếm đa phương thức

Cho phép người dùng kết hợp:

```text
Hình ảnh + Văn bản
```

Ví dụ:

> [Ảnh đôi giày] + "màu trắng, phù hợp chạy bộ"

Hệ thống kết hợp thông tin từ hai phương thức để xếp hạng sản phẩm.

Đây là chức năng AI trọng tâm của đề tài.

---

### Mục tiêu 5 — Xây dựng hệ thống gợi ý sản phẩm

Ghi nhận các hành vi của người dùng như:

* Xem sản phẩm.
* Click sản phẩm.
* Yêu thích sản phẩm.

Từ đó xây dựng hệ thống **content-based recommendation** để đề xuất các sản phẩm tương tự với những sản phẩm mà người dùng quan tâm.

---

### Mục tiêu 6 — Đánh giá hệ thống

Đánh giá:

* Chất lượng kết quả tìm kiếm.
* Chất lượng gợi ý.
* Search latency.
* API response time.
* Khả năng xử lý các phương thức tìm kiếm khác nhau.

Có thể sử dụng các chỉ số như:

* Precision@K.
* Recall@K.
* MRR.
* NDCG.

Tùy thuộc vào khả năng xây dựng ground truth cho dataset.

---

# 3. SCOPE

## 3.1. Phạm vi sản phẩm

Hệ thống chỉ tập trung vào lĩnh vực **thời trang**, với hai nhóm chính:

```text
Fashion
│
├── Shoes
│
└── Clothing
```

Có thể mở rộng thêm các nhóm sản phẩm thời trang khác trong tương lai.

---

## 3.2. Phạm vi người dùng

### Guest

Có thể:

* Xem sản phẩm.
* Tìm kiếm sản phẩm.
* Xem chi tiết sản phẩm.

### Registered User

Có thể:

* Đăng nhập.
* Tìm kiếm.
* Upload hình ảnh.
* Sử dụng multimodal search.
* Yêu thích sản phẩm.
* Xem lịch sử tương tác.
* Nhận recommendation.

### Admin

Có thể:

* Quản lý sản phẩm.
* Quản lý danh mục.
* Quản lý thông tin sản phẩm.

---

## 3.3. Phạm vi AI

Trong Niên luận, AI tập trung vào:

```text
Text Embedding
      ↓
Semantic Search

Image Embedding
      ↓
Visual Search

Image Embedding
      +
Text Embedding
      ↓
Multimodal Search

Product Embedding
      +
User Behavior
      ↓
Content-based Recommendation
```

Mô hình AI được sử dụng là mô hình pretrained, dự kiến sử dụng CLIP/OpenCLIP hoặc mô hình embedding đa phương thức phù hợp.

Không đặt mục tiêu huấn luyện một mô hình lớn từ đầu.

---

## 3.4. Những nội dung nằm ngoài phạm vi

Trong phiên bản Niên luận không triển khai:

* Thanh toán trực tuyến.
* Giỏ hàng hoàn chỉnh.
* Vận chuyển.
* Quản lý đơn hàng phức tạp.
* Mobile application.
* Chatbot LLM.
* AI Agent.
* Training CLIP từ đầu.
* Deep recommender system.
* Microservices.
* Kubernetes.

Các chức năng này có thể được xem xét trong hướng phát triển sau Niên luận hoặc Luận văn tốt nghiệp.

---

# 4. ĐỊNH HƯỚNG PHÂN BỔ TRỌNG TÂM

Đề tài được định hướng theo:

**Software Engineering: khoảng 60%**

**AI/ML: khoảng 40%**

### Software Engineering

```text
Requirements
    ↓
System Design
    ↓
Database
    ↓
Backend
    ↓
Frontend
    ↓
Authentication
    ↓
API
    ↓
Testing
    ↓
Deployment
```

### AI

```text
Pretrained Model
       ↓
Embedding
       ↓
Vector Database
       ↓
Similarity Search
       ↓
Multimodal Fusion
       ↓
Recommendation
       ↓
Evaluation
```

AI không hoạt động độc lập mà được tích hợp trực tiếp vào hệ thống phần mềm.

---

# 5. KẾT QUẢ MONG ĐỢI

Sau khi hoàn thành Niên luận, người dùng có thể thực hiện quy trình:

```text
                 USER
                   │
                   ▼
              Fashion Website
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
      Text       Image    Image + Text
        │          │          │
        └──────────┼──────────┘
                   ▼
               AI Module
                   │
                   ▼
             Vector Search
                   │
                   ▼
               Ranking
                   │
                   ▼
            Search Results
                   │
                   ▼
             User Actions
                   │
                   ▼
           Recommendation
```

Kết quả cuối cùng là một **ứng dụng web thương mại điện tử thời trang có tích hợp AI**, trong đó người dùng có thể tìm kiếm sản phẩm bằng nhiều phương thức thay vì chỉ nhập từ khóa.

---

# 6. TIÊU CHÍ ĐỂ CHUYỂN SANG LUẬN VĂN

Kiến trúc của hệ thống được thiết kế để có thể tiếp tục phát triển.

Niên luận:

```text
Pretrained Model
      +
Basic Retrieval
      +
Basic Recommendation
```

Luận văn:

```text
Niên luận
   ↓
Fine-tuning
   +
Better Multimodal Fusion
   +
Reranking
   +
Advanced Recommendation
   +
Larger / Real-world Dataset
   +
Experimental Comparison
```

Như vậy, phần mềm được xây dựng trong Niên luận không bị bỏ đi khi chuyển sang Luận văn mà trở thành **nền tảng thực nghiệm cho nghiên cứu tiếp theo**.
