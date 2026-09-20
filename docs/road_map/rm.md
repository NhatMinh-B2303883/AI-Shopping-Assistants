# KẾ HOẠCH ĐỀ TÀI NIÊN LUẬN CHUYÊN NGÀNH

## 1. Thông tin đề tài

### Tên tiếng Việt

**Xây dựng hệ thống tìm kiếm và gợi ý sản phẩm thương mại điện tử đa phương thức sử dụng AI**

### Tên tiếng Anh

**Development of an AI-Based Multimodal Product Search and Recommendation System for E-Commerce**

### Lĩnh vực

* Kỹ thuật phần mềm
* Trí tuệ nhân tạo
* Machine Learning / Deep Learning
* Computer Vision
* Information Retrieval
* E-Commerce

### Định hướng

Đề tài tập trung vào việc xây dựng một **hệ thống thương mại điện tử có khả năng tìm kiếm sản phẩm bằng nhiều phương thức**, bao gồm văn bản, hình ảnh và kết hợp hình ảnh + văn bản.

AI được sử dụng như một thành phần thông minh bên trong hệ thống phần mềm, thay vì xây dựng một mô hình AI độc lập.

Hệ thống được thiết kế theo hướng **MVP có thể sử dụng thực tế**, đồng thời có khả năng mở rộng thành đề tài Luận văn tốt nghiệp trong tương lai.

---

# 2. Bối cảnh và vấn đề cần giải quyết

Trong các hệ thống thương mại điện tử truyền thống, người dùng thường tìm kiếm sản phẩm bằng cách nhập từ khóa.

Ví dụ:

> "giày chạy bộ nam màu đen"

Phương thức này phụ thuộc nhiều vào việc người dùng lựa chọn đúng từ khóa và thông tin sản phẩm có được mô tả đầy đủ hay không.

Một vấn đề khác là người dùng có thể **biết sản phẩm mình muốn trông như thế nào nhưng không biết tên hoặc từ khóa để tìm kiếm**.

Ví dụ:

* Người dùng có một bức ảnh đôi giày.
* Người dùng muốn tìm các sản phẩm có kiểu dáng tương tự.
* Người dùng muốn tìm sản phẩm giống hình ảnh nhưng có màu trắng.
* Người dùng muốn tìm sản phẩm tương tự phù hợp với mục đích chạy bộ.

Tìm kiếm bằng từ khóa truyền thống khó xử lý hiệu quả các trường hợp trên.

Do đó, đề tài hướng đến việc xây dựng một hệ thống có khả năng hiểu **nội dung hình ảnh và ngữ nghĩa của văn bản**, từ đó hỗ trợ tìm kiếm sản phẩm theo nhiều phương thức.

---

# 3. Mục tiêu đề tài

## 3.1. Làm gì?

Xây dựng một nền tảng thương mại điện tử thử nghiệm có:

* Quản lý sản phẩm.
* Đăng ký/đăng nhập người dùng.
* Tìm kiếm sản phẩm bằng văn bản.
* Tìm kiếm sản phẩm bằng hình ảnh.
* Tìm kiếm bằng hình ảnh kết hợp văn bản.
* Theo dõi hành vi người dùng.
* Gợi ý sản phẩm dựa trên lịch sử tương tác.
* Trang quản trị sản phẩm.
* Đánh giá hiệu quả của các phương thức tìm kiếm bằng các chỉ số phù hợp.

AI sẽ được sử dụng để tạo **vector biểu diễn (embedding)** cho hình ảnh và văn bản, sau đó thực hiện tìm kiếm sản phẩm dựa trên độ tương đồng.

---

## 3.2. Cho ai?

### Người dùng cuối

Những người mua sắm trên nền tảng thương mại điện tử, đặc biệt là người:

* Không biết chính xác tên sản phẩm.
* Muốn tìm sản phẩm dựa trên hình ảnh.
* Muốn tìm sản phẩm tương tự với một sản phẩm đang có.
* Muốn kết hợp nhiều điều kiện tìm kiếm.
* Muốn nhận được các sản phẩm phù hợp với sở thích hoặc lịch sử xem.

### Quản trị viên

Quản trị viên hệ thống có thể:

* Thêm/sửa/xóa sản phẩm.
* Quản lý danh mục.
* Quản lý thông tin sản phẩm.
* Theo dõi dữ liệu tương tác cơ bản.

### Đối tượng học thuật

Đề tài cũng hướng đến việc cung cấp một hệ thống thực nghiệm để:

* Nghiên cứu semantic search.
* Nghiên cứu image retrieval.
* Nghiên cứu multimodal retrieval.
* Đánh giá hiệu quả tìm kiếm.
* Làm cơ sở phát triển thành Luận văn tốt nghiệp.

---

# 4. Vì sao thực hiện đề tài?

Đề tài được thực hiện vì ba lý do chính.

### 4.1. Giải quyết một vấn đề thực tế

Người dùng thương mại điện tử không phải lúc nào cũng biết chính xác từ khóa cần tìm.

Việc cho phép tìm kiếm bằng hình ảnh hoặc kết hợp hình ảnh và văn bản giúp quá trình tìm kiếm linh hoạt hơn.

### 4.2. Kết hợp Kỹ thuật phần mềm và AI

Đề tài không chỉ tập trung vào việc huấn luyện một mô hình AI mà xây dựng một hệ thống hoàn chỉnh:

**Frontend → Backend → Database → AI → Search → Recommendation**

Điều này phù hợp với định hướng Kỹ thuật phần mềm nhưng vẫn có thành phần nghiên cứu AI rõ ràng.

### 4.3. Có khả năng phát triển thành Luận văn

Phiên bản Niên luận tập trung xây dựng hệ thống MVP và các thuật toán AI cơ bản.

Ở giai đoạn Luận văn có thể tiếp tục:

* Fine-tuning mô hình.
* Cải thiện multimodal retrieval.
* Xây dựng mô hình recommendation nâng cao.
* Reranking kết quả.
* Hard-negative mining.
* So sánh nhiều mô hình embedding.
* Thu thập dữ liệu thực tế.
* Đánh giá trên tập dữ liệu lớn hơn.

---

# 5. Phạm vi đề tài Niên luận

## 5.1. Chức năng chính

### Phía người dùng

1. Đăng ký tài khoản.
2. Đăng nhập.
3. Xem danh sách sản phẩm.
4. Xem chi tiết sản phẩm.
5. Tìm kiếm bằng văn bản.
6. Tìm kiếm bằng hình ảnh.
7. Tìm kiếm bằng hình ảnh + văn bản.
8. Xem lịch sử tương tác.
9. Thêm sản phẩm vào danh sách yêu thích.
10. Nhận gợi ý sản phẩm.

### Phía quản trị viên

1. Đăng nhập quản trị.
2. Thêm sản phẩm.
3. Chỉnh sửa sản phẩm.
4. Xóa sản phẩm.
5. Quản lý danh mục.
6. Quản lý dữ liệu sản phẩm.

---

# 6. Thành phần AI

Đề tài sử dụng mô hình embedding đa phương thức được huấn luyện trước, ví dụ **CLIP/OpenCLIP**, thay vì huấn luyện một mô hình lớn từ đầu.

Hệ thống gồm ba chức năng AI chính.

### 6.1. Semantic Text Search

Người dùng nhập:

> "giày chạy bộ nam màu đen"

Hệ thống chuyển câu truy vấn thành vector embedding.

Sau đó so sánh vector truy vấn với vector của các sản phẩm.

Kết quả là danh sách sản phẩm được sắp xếp theo mức độ tương đồng.

---

### 6.2. Image Search

Người dùng tải lên:

> `shoe.jpg`

Hệ thống:

**Image → AI Model → Image Embedding → Vector Search**

Sau đó trả về các sản phẩm có hình ảnh tương tự.

---

### 6.3. Multimodal Search

Người dùng có thể nhập đồng thời:

**Image + Text**

Ví dụ:

> [Ảnh một đôi giày]
> "màu trắng, dùng để chạy bộ"

Hệ thống tạo:

* Image embedding.
* Text embedding.

Sau đó kết hợp độ tương đồng:

**Final Score = α × Image Similarity + β × Text Similarity**

Ví dụ ban đầu:

**α = 0.7**

**β = 0.3**

Các trọng số này có thể được điều chỉnh và đánh giá trong quá trình thực nghiệm.

---

# 7. Luồng hoạt động tổng thể của hệ thống

```text
                    USER
                      │
                      ▼
              ┌───────────────┐
              │    FRONTEND   │
              │    Next.js    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │    BACKEND    │
              │    FastAPI    │
              └───────┬───────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
     PostgreSQL    AI Service   User Events
     + pgvector     CLIP
          │           │
          │           ▼
          │       Embeddings
          │           │
          └─────► Vector Search
                      │
                      ▼
                 Ranked Results
                      │
                      ▼
                   USER
```

---

# 8. Luồng hoạt động của User

## Luồng 1: Tìm kiếm bằng văn bản

### Input

Người dùng nhập:

> "giày chạy bộ nam màu đen"

### Xử lý

```text
Text Query
    ↓
Text Embedding
    ↓
Vector Search
    ↓
Calculate Similarity
    ↓
Rank Products
    ↓
Filter / Sort
```

### Output

Danh sách sản phẩm:

```text
1. Nike Running Shoes      0.91
2. Adidas Running Shoes    0.87
3. Asics Running Shoes     0.84
4. Puma Running Shoes      0.80
...
```

Trong giao diện thực tế, người dùng sẽ nhìn thấy sản phẩm, giá, hình ảnh và các thông tin liên quan thay vì chỉ nhìn thấy similarity score.

---

# 9. Luồng 2: Tìm kiếm bằng hình ảnh

### Input

Người dùng tải lên:

```text
shoe.jpg
```

### Xử lý

```text
Image
  ↓
CLIP / OpenCLIP
  ↓
Image Embedding
  ↓
Vector Similarity Search
  ↓
Ranking
```

### Output

Hệ thống trả về:

```text
Các sản phẩm có hình ảnh tương tự
```

Ví dụ:

```text
Uploaded Image
      ↓
┌──────────────────────────┐
│ Similar Products         │
├──────────────────────────┤
│ Product A                │
│ Product B                │
│ Product C                │
│ Product D                │
└──────────────────────────┘
```

---

# 10. Luồng 3: Tìm kiếm đa phương thức

Đây là chức năng quan trọng nhất của đề tài.

### Input

Người dùng cung cấp:

```text
Image:
[ảnh đôi giày]

Text:
"màu trắng, phù hợp chạy bộ"
```

### Xử lý

```text
                ┌──────────────┐
                │    IMAGE     │
                └──────┬───────┘
                       ↓
                 Image Embedding
                       │
                       │
                       ▼
                   Similarity
                       │
                       │
                       ├───────┐
                       │       │
                       │       ▼
                       │   Fusion
                       │       ▲
                       │       │
                       ▼       │
                Text Embedding ┘
                       ↑
                       │
                    TEXT
```

Sau đó:

```text
Image Similarity
       +
Text Similarity
       ↓
Weighted Fusion
       ↓
Final Score
       ↓
Ranking
       ↓
Top-K Products
```

### Output

Danh sách sản phẩm được xếp hạng theo mức độ phù hợp với **cả hình ảnh và yêu cầu văn bản**.

---

# 11. Luồng 4: Gợi ý sản phẩm

Sau khi người dùng sử dụng hệ thống, các hành vi được ghi nhận.

### Input

Ví dụ:

```text
User xem:
- Running Shoes A
- Running Shoes B

User wishlist:
- Running Shoes A

User click:
- Running Shoes C
```

### Dữ liệu được lưu

```text
User
 ↓
User Events
 ├── View
 ├── Click
 └── Wishlist
```

### Xử lý

Hệ thống xây dựng biểu diễn sở thích của người dùng dựa trên các sản phẩm đã tương tác.

Sau đó tìm những sản phẩm tương tự.

### Output

Ví dụ:

> "Có thể bạn sẽ thích"

```text
Product X
Product Y
Product Z
```

Trong phiên bản Niên luận, recommendation được triển khai theo hướng **content-based recommendation**, tránh làm hệ thống quá phức tạp trong thời gian 2 tháng.

---

# 12. Luồng hoạt động của Admin

```text
Admin Login
     ↓
Dashboard
     ↓
Product Management
     ├── Add Product
     ├── Edit Product
     ├── Delete Product
     └── View Products
              ↓
       Generate Embedding
              ↓
       Store in PostgreSQL
              +
           pgvector
```

Khi một sản phẩm mới được thêm vào, hệ thống có thể tạo embedding cho sản phẩm để sản phẩm đó có thể tham gia vào quá trình tìm kiếm AI.

---

# 13. Input và Output của hệ thống

| Chức năng         | Input                       | Xử lý                                     | Output               |
| ----------------- | --------------------------- | ----------------------------------------- | -------------------- |
| Đăng ký           | Email, password             | Validation + hashing                      | Account              |
| Đăng nhập         | Email, password             | Authentication                            | Access token         |
| Xem sản phẩm      | Product ID                  | Database query                            | Product information  |
| Text Search       | Text query                  | Text embedding + vector search            | Ranked products      |
| Image Search      | Image                       | Image embedding + vector search           | Similar products     |
| Multimodal Search | Image + text                | Image embedding + text embedding + fusion | Ranked products      |
| Wishlist          | Product ID                  | Store user event                          | Updated wishlist     |
| Recommendation    | User ID                     | User behavior + product similarity        | Recommended products |
| Admin Add Product | Product information + image | Store + generate embedding                | New product          |
| Admin Edit        | Product information         | Update database/embedding                 | Updated product      |

---

# 14. Dữ liệu sử dụng

Ban đầu sử dụng **dataset sản phẩm thời trang công khai** để xây dựng hệ thống.

Mục tiêu ban đầu:

```text
~10,000 sản phẩm
```

Có thể chia thành:

```text
8,000 products → development/indexing
1,000 products → validation
1,000 products → testing
```

Thông tin sản phẩm có thể bao gồm:

* Product ID
* Product name
* Category
* Sub-category
* Gender
* Color
* Price
* Image

Sau khi hệ thống hoàn thiện, có thể mở rộng bằng dữ liệu tự thu thập nếu cần.

---

# 15. Kiến trúc công nghệ dự kiến

## Frontend

* Next.js
* TypeScript
* Tailwind CSS

## Backend

* FastAPI
* Python
* SQLAlchemy
* Pydantic

## Database

* PostgreSQL
* pgvector

## AI

* PyTorch
* CLIP/OpenCLIP
* Vector embeddings
* Cosine similarity

## Testing

* Pytest
* Playwright

## Deployment / Environment

* Docker Compose
* Git
* GitHub

Kiến trúc:

```text
┌───────────────────────────────┐
│          Next.js              │
│          Frontend             │
└───────────────┬───────────────┘
                │ REST API
                ▼
┌───────────────────────────────┐
│           FastAPI             │
│            Backend            │
└───────┬───────────────┬───────┘
        │               │
        ▼               ▼
┌──────────────┐   ┌───────────────┐
│ PostgreSQL   │   │ AI / CLIP     │
│ + pgvector   │   │ Embedding     │
└──────────────┘   └───────────────┘
```

---

# 16. Cấu trúc chức năng

```text
E-Commerce AI System
│
├── Authentication
│   ├── Register
│   ├── Login
│   └── Logout
│
├── Product
│   ├── Browse
│   ├── Detail
│   ├── Category
│   └── Wishlist
│
├── Search
│   ├── Text Search
│   ├── Image Search
│   └── Multimodal Search
│
├── Recommendation
│   └── Content-based Recommendation
│
├── User
│   ├── Profile
│   └── History
│
└── Admin
    ├── Product CRUD
    └── Category Management
```

---

# 17. Mục tiêu kỹ thuật

Đề tài hướng đến đạt được các mục tiêu:

### Software Engineering

* Thiết kế kiến trúc hệ thống.
* Thiết kế database.
* REST API.
* Authentication/Authorization.
* Frontend–Backend integration.
* Testing.
* Security cơ bản.
* Docker hóa hệ thống.
* Git/GitHub workflow.
* Documentation.

### AI/ML

* Hiểu và sử dụng pretrained multimodal model.
* Tạo image embedding.
* Tạo text embedding.
* Vector similarity search.
* Multimodal fusion.
* Recommendation.
* Đánh giá chất lượng retrieval.

Tỷ trọng dự kiến:

**Software Engineering: ~50–70%**

**AI/ML: ~30–50%**

---

# 18. Đánh giá hệ thống

Không chỉ đánh giá bằng việc "chạy được", hệ thống sẽ có các thực nghiệm.

## 18.1. Đánh giá Search

Có thể sử dụng:

* Precision@K
* Recall@K
* MRR
* NDCG

Tùy khả năng xây dựng ground truth cho dataset.

Ví dụ:

```text
Query
 ↓
Top 5 Results
 ↓
Compare with Ground Truth
 ↓
Calculate Precision@5
```

---

## 18.2. So sánh các phương thức

Có thể thực nghiệm:

```text
Text Search
      vs
Image Search
      vs
Multimodal Search
```

Từ đó đánh giá sự khác biệt về chất lượng kết quả.

---

## 18.3. Đánh giá Recommendation

Đánh giá khả năng đưa ra sản phẩm liên quan dựa trên lịch sử tương tác của người dùng.

---

## 18.4. Đánh giá hiệu năng

Đo:

* API response time.
* Search latency.
* Vector search latency.
* Thời gian tạo embedding.
* CPU/GPU/RAM sử dụng.

---

# 19. Kế hoạch thực hiện trong 8 tuần

## Tuần 1 – Phân tích và thiết kế

### Công việc

* Xác định yêu cầu.
* Problem Statement.
* Xác định Actor.
* Use Case.
* Functional Requirements.
* Non-functional Requirements.
* Thiết kế database.
* Thiết kế kiến trúc.
* Tạo Git repository.
* Setup môi trường.

### Deliverables

* Problem Statement
* Requirement Specification
* Use Case Diagram
* System Architecture
* ERD
* Project repository

---

# Tuần 2 – Backend và Database

### Công việc

* PostgreSQL.
* pgvector.
* SQLAlchemy.
* Database migration.
* User.
* Product.
* Category.
* UserEvent.
* Wishlist.
* Authentication.
* Product CRUD.
* Basic Search API.

### Deliverables

Backend API phiên bản đầu tiên.

---

# Tuần 3 – Frontend

### Công việc

* Next.js.
* Layout.
* Homepage.
* Product Listing.
* Product Detail.
* Login/Register.
* Search interface.
* Connect Frontend ↔ Backend.

### Deliverables

Website thương mại điện tử cơ bản có thể sử dụng.

---

# Tuần 4 – AI Text Search

### Công việc

* Chuẩn hóa dataset.
* Cài đặt CLIP/OpenCLIP.
* Generate text embedding.
* Generate product embeddings.
* Lưu embedding vào pgvector.
* Implement cosine similarity.
* Text semantic search.

### Deliverables

**Text Semantic Search hoạt động.**

---

# Tuần 5 – Image Search

### Công việc

* Image upload API.
* Image embedding.
* Vector search.
* Ranking.
* Search result UI.
* Xử lý file không hợp lệ.

### Deliverables

**Image Search hoạt động.**

---

# Tuần 6 – Multimodal Search

### Công việc

* Image + Text input.
* Image embedding.
* Text embedding.
* Similarity calculation.
* Weighted fusion.
* Ranking.
* Frontend integration.

### Deliverables

**Multimodal Search hoàn chỉnh.**

---

# Tuần 7 – Recommendation + Evaluation

### Công việc

* Tracking user events.
* View.
* Click.
* Wishlist.
* Content-based recommendation.
* Recommendation API.
* Recommendation UI.
* Precision@K.
* Recall@K.
* Ranking metrics nếu phù hợp.
* Search latency.

### Deliverables

**Recommendation + Evaluation results.**

---

# Tuần 8 – Testing và hoàn thiện

### Công việc

* Unit testing.
* API testing.
* AI testing.
* E2E testing.
* Security testing.
* Performance testing.
* Bug fixing.
* UI polishing.
* Documentation.
* README.
* API documentation.
* ERD.
* Architecture documentation.
* Evaluation report.
* Chuẩn bị demo.

### Deliverables

**Phiên bản hoàn chỉnh của hệ thống.**

---

# 20. Mức độ ưu tiên khi không đủ thời gian

Nếu tiến độ bị chậm, ưu tiên theo thứ tự:

```text
1. Product System
        ↓
2. Text Search
        ↓
3. Image Search
        ↓
4. Multimodal Search
        ↓
5. Evaluation
        ↓
6. Recommendation
        ↓
7. UI Polish
```

Recommendation có thể được giảm phạm vi hoặc chuyển sang phần mở rộng nếu thời gian không đủ.

Tuy nhiên, **Text + Image + Multimodal Search** nên được giữ vì đây là phần thể hiện rõ nhất ý tưởng chính của đề tài.

---

# 21. Những nội dung KHÔNG thực hiện trong phiên bản Niên luận

Để đảm bảo hoàn thành trong khoảng 2 tháng, đề tài không tập trung vào:

* Thanh toán trực tuyến.
* Hệ thống vận chuyển.
* Mobile application.
* Chatbot LLM.
* AI Agent.
* Fine-tuning mô hình lớn từ đầu.
* Training CLIP từ đầu.
* Deep Learning recommender phức tạp.
* Microservices.
* Kubernetes.
* Hệ thống phân tán quy mô lớn.

Các nội dung này có thể trở thành hướng phát triển trong Luận văn.

---

# 22. Hướng phát triển thành Luận văn tốt nghiệp

Phiên bản Niên luận xây dựng hệ thống cơ sở.

Phiên bản Luận văn có thể tập trung nghiên cứu sâu hơn về AI.

### Hướng 1 – Cải thiện Multimodal Retrieval

Nghiên cứu:

* Fine-tuning.
* Fusion strategies.
* Hard-negative mining.
* Reranking.
* Domain-specific embedding.
* So sánh nhiều pretrained models.

### Hướng 2 – Cải thiện Recommendation

Có thể phát triển từ:

```text
Content-based
      ↓
Hybrid Recommendation
      ↓
Deep Recommendation
```

Kết hợp:

* User behavior.
* Product embedding.
* Collaborative filtering.
* Context.

### Hướng 3 – Dataset thực tế

Có thể:

```text
Public Dataset
      +
Self-collected Dataset
      ↓
Real-world Dataset
```

Từ đó đánh giá khả năng tổng quát hóa của mô hình.

### Hướng 4 – Multimodal Ranking

Nghiên cứu cách kết hợp:

```text
Image
+
Text
+
User Preference
+
Product Metadata
```

để tạo ranking tốt hơn.

---

# 23. Kết quả mong đợi

Sau khi hoàn thành Niên luận, hệ thống dự kiến có thể thực hiện đầy đủ quy trình:

```text
User
 ↓
Website
 ↓
Tìm kiếm sản phẩm
 ↓
Text / Image / Image + Text
 ↓
AI Embedding
 ↓
Vector Search
 ↓
Ranking
 ↓
Product Results
 ↓
User Interaction
 ↓
Recommendation
```

Sản phẩm cuối cùng không chỉ là một notebook AI mà là một **ứng dụng web hoàn chỉnh có tích hợp AI**.

---

# 24. Tiêu chí hoàn thành đề tài

Đề tài được xem là hoàn thành khi đạt được:

### Software

* [ ] Frontend hoạt động.
* [ ] Backend hoạt động.
* [ ] Database hoạt động.
* [ ] Authentication.
* [ ] Product management.
* [ ] User management.
* [ ] Admin management.
* [ ] REST API.
* [ ] Testing.
* [ ] Documentation.

### AI

* [ ] Text embedding.
* [ ] Semantic text search.
* [ ] Image embedding.
* [ ] Image similarity search.
* [ ] Multimodal search.
* [ ] Ranking.
* [ ] Recommendation cơ bản.
* [ ] AI evaluation.

### Demo

Người dùng có thể:

* [ ] Đăng nhập.
* [ ] Xem sản phẩm.
* [ ] Nhập câu tìm kiếm.
* [ ] Upload hình ảnh.
* [ ] Kết hợp hình ảnh + văn bản.
* [ ] Nhận danh sách sản phẩm được xếp hạng.
* [ ] Tương tác với sản phẩm.
* [ ] Nhận sản phẩm được đề xuất.

---

# 25. Giá trị của đề tài

Đề tài tạo ra một sản phẩm kết hợp giữa **Kỹ thuật phần mềm và Trí tuệ nhân tạo**, trong đó AI được tích hợp trực tiếp vào quy trình tìm kiếm và gợi ý của một hệ thống thương mại điện tử.

Về mặt kỹ thuật, đề tài cho phép triển khai một quy trình tương đối đầy đủ:

**Requirement → Design → Development → AI Integration → Testing → Evaluation → Deployment**

Đồng thời, kiến trúc được thiết kế theo hướng module hóa để có thể tiếp tục phát triển trong Luận văn tốt nghiệp.

---

# 26. Tóm tắt đề tài để trình bày với giảng viên

> Đề tài hướng đến xây dựng một hệ thống thương mại điện tử có tích hợp AI nhằm hỗ trợ người dùng tìm kiếm và khám phá sản phẩm thông minh hơn. Khác với tìm kiếm truyền thống chỉ dựa trên từ khóa, hệ thống cho phép người dùng tìm kiếm bằng văn bản, hình ảnh hoặc kết hợp hình ảnh và văn bản. Hệ thống sử dụng mô hình embedding đa phương thức được huấn luyện trước để biểu diễn sản phẩm và truy vấn dưới dạng vector, sau đó sử dụng vector similarity search để tìm và xếp hạng các sản phẩm phù hợp.
>
> Bên cạnh chức năng tìm kiếm, hệ thống ghi nhận các hành vi như xem, click và yêu thích sản phẩm để xây dựng chức năng gợi ý sản phẩm theo hướng content-based recommendation. Đề tài tập trung vào việc xây dựng một hệ thống web hoàn chỉnh gồm frontend, backend, database, AI service và testing, thay vì chỉ xây dựng một mô hình AI độc lập.
>
> Trong phạm vi Niên luận, hệ thống được giới hạn ở mức MVP với các chức năng tìm kiếm văn bản, tìm kiếm hình ảnh, tìm kiếm đa phương thức và gợi ý sản phẩm cơ bản. Trong giai đoạn Luận văn tốt nghiệp, hệ thống có thể tiếp tục được nghiên cứu theo hướng fine-tuning mô hình, cải thiện multimodal retrieval, reranking, recommendation và đánh giá trên dữ liệu thực tế.
