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



