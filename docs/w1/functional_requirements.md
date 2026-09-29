# FR01 — Product Browsing
    Hệ thống phải cho phép Guest/User:
        Xem danh sách sản phẩm.
        Xem thông tin cơ bản.
        Lọc sản phẩm.
        Sắp xếp sản phẩm.

# FR02 — Product Detail
    Hệ thống phải hiển thị:
        Tên sản phẩm
        Hình ảnh
        Giá
        Danh mục
        Loại sản phẩm
        Giới tính
        Màu sắc
        Các thông tin liên quan khác

# FR03 — Text Search
    Người dùng nhập truy vấn văn bản.

# Image Search

# Multimodal Search

# Recommendation
    Recommendation không phải một hệ thống recommendation deep learning phức tạp ở giai đoạn Niên luận.
    Ban đầu dùng Content-Based Recommendation.
    Product Embeddings
        +
    User Interaction History
        ↓
    User Preference Representation
        ↓
    Similarity Calculation
        ↓
    Recommended Products

# Non-functional Requirements
    NFR01 — Performance
        Search phải trả kết quả trong thời gian hợp lý.
    NFR02 — Usability
        Giao diện phải cho phép người dùng thực hiện:
        Search → View → Explore
    NFR03 — Security
        Password phải được hash.
        API phải xác thực User/Admin.
        Guest không được truy cập API yêu cầu authentication.
        User không được truy cập chức năng Admin.
    NFR04 — Maintainability
        Backend và AI module phải được tách tương đối rõ:
    NFR05 — Scalability
        Thiết kế cho phép mở rộng mà không phải thay đổi toàn bộ hệ thống.

## Database
# user (id, name, email, password_hash, role, created_at)
# role (USER, ADMIN)
# category (id, name, parent_id, created_at)  Có parent_id để sau này hỗ trợ:
            Fashion
            ├── Shoes
            │   ├── Running Shoes
            │   ├── Sneakers
            │   └── ...
            └── Clothing
                ├── T-Shirt
                ├── Hoodie
                └── ...
# product (id, name, description, category_id, gender, color, price, created_at, updated_at)
# product_image (id, product_id, image_url, is_primary, created_at)
# product_embedding (product_id, embedding, model_name, created_at)
# search_history (id, user_id, search_type, text_query, image_url, created_at)
# interaction_history (id, user_id, product_id, interaction_type, created_at)
# wishlist (id, user_id, product_id, created_at)

# AI Architecture
    Model: CLIP/OpenCLIP pretrained
        Không train CLIP từ đầu.
            Embedding
                Product Image
                    ↓
                CLIP Image Encoder
                    ↓
                Image Embedding
                    ↓
                PostgreSQL + pgvector

                Text:
                    Text
                    ↓
                    CLIP Text Encoder
                    ↓
                    Text Embedding
                    ↓
                    Search

# Tech
    Thành phần	        Công nghệ
    Frontend	        Next.js + TypeScript
    UI	                Tailwind CSS
    Backend	            FastAPI
    AI	                PyTorch + CLIP/OpenCLIP
    Database	        PostgreSQL
    Vector DB	        pgvector
    ORM	                SQLAlchemy
    Validation	        Pydantic
    Testing	            Pytest
    E2E	                Playwright
    Container	        Docker Compose
    Version Control	    Git + GitHub

# Dataset
    Mục tiêu ban đầu: ~10,000 products
    Mỗi sản phẩm tối thiểu:
        Product ID
        Name
        Category
        Sub-category
        Gender
        Color
        Price
        Image
    Có thể chia:
        8,000 → Development / Indexing
        1,000 → Validation
        1,000 → Testing