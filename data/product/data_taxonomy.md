Clothing
├── T-Shirt        200
├── Sweatshirt     100
├── Jacket         150
└── Polo           150

Shoes
├── Casual Shoes   150
├── Sports Shoes   150
└── Sandals        100

### Normalization
Mapping Table chính thức
Source articleType	Project category	Project sub_category	Rule xử lý	Trạng thái
Tshirts	Clothing	T-Shirt	articleType == "Tshirts" và tên không chứa Polo	✅ Giữ
Tshirts	Clothing	Polo	articleType == "Tshirts" và productDisplayName chứa Polo	✅ Giữ
Sweatshirts	Clothing	Sweatshirt	articleType == "Sweatshirts"; không phân biệt Hoodie	✅ Giữ
Jackets	Clothing	Jacket	Exact match	✅ Giữ
Rain Jacket	Clothing	Jacket	Gộp vào Jacket	✅ Giữ
Nehru Jackets	—	—	Loại	❌ Bỏ
Casual Shoes	Shoes	Casual Shoes	Exact match	✅ Giữ
Sports Shoes	Shoes	Sports Shoes	Exact match	✅ Giữ
Sandals	Shoes	Sandals	Exact match	✅ Giữ
Sports Sandals	Shoes	Sandals	Gộp vào Sandals	✅ Giữ
Boots	—	—	Không có trong dataset	❌ Không dùng
Booties	—	—	Loại; thực tế thuộc nhóm trẻ em/socks trong dữ liệu hiện tại	❌ Bỏ


if articleType == "Tshirts" and "Polo" in productDisplayName:
    sub_category = "Polo"
else:
    sub_category = "T-Shirt"


### Result
=== CATEGORY ===
# Clothing: 6,983 ≈ 54.8%
# Shoes: 5,755 ≈ 45.2%

T-Shirt       5,221
Casual Shoes  2,807
Sports Shoes  2,030
Polo          1,177
Sandals         913
Sweatshirt      280
Jacket          269

và:

Men       10,248  (80.71%)
Women      1,994  (15.70%)
Unisex       455  (3.58%)

Phân bổ 1,000 sản phẩm:

Sub-category	Số lượng
T-Shirt	        261
Casual Shoes	177
Sports Shoes	150
Polo	        121
Sandals	        112
Sweatshirt	    90
Jacket	        89
Tổng	        1,000

canonical_text

-[ RECORD 1 ]--+-------------------------------------------------------------------------------------------------------------------------------
external_id    | FP001528
name           | Puma Men Ferrari Black Fleece Jacket
category       | Jacket
gender         | Men
color          | Black
canonical_text | Product: Puma Men Ferrari Black Fleece Jacket. Category: Clothing. Subcategory: Jacket. Gender: Men. Color: Black.


Trong dự án AI Shopping Assistant, canonical_text là văn bản được chuẩn hóa từ thông tin sản phẩm để làm đầu vào cho text encoder của SigLIP 2.

Luồng xử lý:

Thông tin sản phẩm

Tên, danh mục, giới tính, màu sắc và metadata có sẵn

Chuẩn hóa thành canonical_text

SigLIP 2 Text Encoder

Tạo vector embedding 768 chiều

Lưu vào product_embeddings

Dùng cho tìm kiếm tương đồng ngữ nghĩa

### Chuẩn hóa văn bản sản phẩm (`canonical_text`)

Trong hệ thống, trường `canonical_text` được sử dụng để biểu diễn thông tin sản phẩm dưới dạng văn bản chuẩn hóa trước khi đưa vào mô hình SigLIP 2. Nội dung này được xây dựng từ metadata sẵn có của sản phẩm, giúp biểu diễn các thuộc tính như tên sản phẩm, loại sản phẩm, giới tính và màu sắc dưới dạng đầu vào thống nhất.

Sau bước chuẩn hóa, văn bản được đưa vào text encoder của mô hình `google/siglip2-base-patch16-256` để trích xuất vector embedding có 768 chiều. Vector được lưu trong bảng `product_embeddings`, cùng với mã sản phẩm, loại embedding và tên mô hình được sử dụng. Quá trình này tạo cơ sở cho chức năng tìm kiếm sản phẩm theo ngữ nghĩa văn bản và so sánh độ tương đồng với biểu diễn hình ảnh trong không gian embedding chung.
