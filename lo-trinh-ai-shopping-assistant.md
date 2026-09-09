# Lộ trình xây dựng AI Shopping Assistant Platform

**Thời gian dự kiến:** ~6 tuần xây dựng + 1-2 tuần kiểm thử/hoàn thiện
**Stack chính:** Spring Boot (core business) + Python (AI/ML, RAG) + Kafka + Redis + Qdrant
**LLM:** `gemini-2.5-flash` · **Embedding:** `AITeamVN/Vietnamese_Embedding` (local, CPU)

> 🎯 **Thứ tự ưu tiên MVP (nếu tiến độ trễ, bám theo thứ tự này):**
> **Core Backend → Recommendation → Embedding/RAG → LLM → End-to-End**
> Kafka, WebSocket, API Gateway và scale ngang là các hạng mục **nâng cao**, không phải dependency bắt buộc để có MVP chạy được — có thể lùi/cắt nếu thiếu thời gian mà không ảnh hưởng luồng chính.

---

## Tuần 1 — Nền móng & Dữ liệu

- [ ] **Thiết kế schema DB** — PostgreSQL: User, Product, Order, Cart
- [ ] **Setup Docker Compose** — Postgres, Redis, Kafka, Qdrant chạy local
- [ ] **Khung Spring Boot cơ bản** — User Service, Product Service (CRUD, JWT auth)
- [ ] **Chuẩn bị dataset** — Sản phẩm mẫu + dữ liệu hành vi user (Retailrocket/synthetic)

> ⚠️ Đây là tuần nền tảng — nếu dataset chưa sẵn sàng cuối tuần này, các tuần sau (recommendation, embedding) sẽ bị trễ dây chuyền. Ưu tiên dataset công khai có sẵn thay vì tự crawl.

---

## Tuần 2 — Order flow & Recommendation

- [ ] **Order & Cart Service** — Spring Boot, giỏ hàng lưu session bằng Redis
- [ ] **Kafka event pipeline** *(nâng cao — không bắt buộc cho MVP)* — Publish event view/click/mua sản phẩm
- [ ] **Train recommendation model** — Baseline: Matrix Factorization/Collaborative Filtering. Two-Tower chỉ triển khai nếu còn thời gian
- [ ] **Đánh giá offline model** — Đo accuracy/hit-rate trước khi tích hợp

---

## Tuần 3 — Embedding & RAG pipeline

- [ ] **Setup local embedding** — `AITeamVN/Vietnamese_Embedding` chạy CPU trong Python service
- [ ] **Embed catalog sản phẩm** — Sinh vector, lưu vào Qdrant (dimension 1024)
- [ ] **Xây RAG pipeline** — Retrieve sản phẩm liên quan + gọi `gemini-2.5-flash` sinh câu trả lời
- [ ] **Expose RAG API** — FastAPI endpoint cho chatbot tư vấn
- [ ] **Frontend tối thiểu (bắt đầu từ đây, không chờ cuối)** — Next.js: product list/detail + search + chat widget

> 💡 Nên bắt đầu ghi log kết quả ngay (thời gian train, accuracy, độ trễ inference CPU) để tuần 6-7 có sẵn số liệu viết báo cáo.

---

## Tuần 4 — Real-time & Tích hợp hệ thống

- [ ] **Chat Gateway (WebSocket)** *(nâng cao — MVP có thể dùng REST polling/HTTP request thay thế)* — Spring Boot nhận tin nhắn user, forward sang RAG service
- [ ] **Kafka consumer cập nhật recommendation** *(nâng cao — không bắt buộc cho MVP)* — Cập nhật gợi ý liên tục theo hành vi mới
- [ ] **API Gateway routing** *(nâng cao — MVP có thể gọi thẳng service)* — Route giữa hệ Spring Boot và Python AI services
- [ ] **Test luồng end-to-end** — Chat → RAG → trả lời real-time (ưu tiên đảm bảo luồng này chạy được trước, dù chưa có các hạng mục nâng cao ở trên)

---

## Tuần 5 — Scale thật & Frontend

- [ ] **Load test hệ thống** — k6/Locust mô phỏng nhiều user đồng thời
- [ ] **Tối ưu hiệu năng** — Connection pooling, Redis cache sản phẩm hot
- [ ] **Thử nghiệm scale ngang** *(nâng cao — không bắt buộc cho MVP)* — Docker Compose scale hoặc minikube nếu còn thời gian
- [ ] **Hoàn thiện Frontend** — Mở rộng bản tối thiểu từ tuần 3 (product list/detail + search + chat) thêm UI polish, trang giỏ hàng/order

> 🎯 Tuần này là phần "ăn điểm" nhiều nhất cho tiêu chí Backend/DevOps — dành đủ thời gian đo và lưu biểu đồ throughput/latency trước/sau tối ưu, đây là bằng chứng thuyết phục nhất khi bảo vệ niên luận.
> Nếu tiến độ bị trễ: **cắt trước tiên** các hạng mục nâng cao (scale ngang, Kafka, WebSocket, API Gateway) — giữ nguyên Core Backend → Recommendation → Embedding/RAG → LLM → End-to-End vì đây là luồng bắt buộc của MVP.

---

## Tuần 6 — Kiểm thử

- [ ] **Unit test Spring Boot** — Test các service lõi
- [ ] **Test chất lượng AI** — So sánh `Vietnamese_Embedding` vs `Gemini Embedding` cho phần báo cáo
- [ ] **Bug fixing & polish UI** — Sửa lỗi phát sinh từ load test và test tích hợp

---

## Tuần 7 — Hoàn thiện

- [ ] **Viết báo cáo niên luận** — Kiến trúc, kết quả load test, đánh giá mô hình AI
- [ ] **Chuẩn bị demo/slide** — Video demo + slide bảo vệ
- [ ] **Polish GitHub repo** — README, kiến trúc, benchmark — sẵn sàng đưa vào CV

---

## Ghi chú cấu hình quan trọng

| Thành phần | Lựa chọn | Ghi chú |
|---|---|---|
| LLM (chat/RAG) | `gemini-2.5-flash` | Thay thế `gemini-2.0-flash` đã shutdown; nên đưa model name ra config/env, không hardcode |
| Embedding (chính) | `AITeamVN/Vietnamese_Embedding` | Fine-tune BGE-M3 cho tiếng Việt, chạy CPU, Apache 2.0, dim 1024 |
| Embedding (dự phòng) | `intfloat/multilingual-e5-base` | Nhẹ hơn, dùng khi cần tốc độ CPU nhanh hơn, dim 768, MIT |
| Vector DB | Qdrant | Lưu vector 1024 chiều từ embedding chính |
| Backend lõi | Spring Boot | User/Product/Order/Cart, WebSocket chat gateway |
| AI services | Python (FastAPI) | Recommendation engine, RAG orchestrator, Gemini API client |
| Message queue | Kafka | Event hành vi user → cập nhật recommendation |
| Cache | Redis | Session giỏ hàng, cache sản phẩm hot |
