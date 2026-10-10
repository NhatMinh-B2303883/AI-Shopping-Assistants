-- Inspect the first 10 coordinates of the stored 768-dimensional vectors.
-- Run from PowerShell / project root:
-- docker compose exec db psql -U postgres -d ai_shopping -x -c "SELECT p.external_id, p.name, e.embedding_type, vector_dims(e.embedding) AS dimensions, subvector(e.embedding, 1, 10)::text AS first_10_coordinates FROM product_embeddings e JOIN products p ON p.id = e.product_id WHERE e.model_name = 'google/siglip2-base-patch16-256' ORDER BY p.external_id, e.embedding_type LIMIT 4;"

-- Return a full 768-dimensional vector for one row (long output):
-- docker compose exec db psql -U postgres -d ai_shopping -x -c "SELECT p.external_id, p.name, e.embedding_type, e.embedding::text AS full_vector FROM product_embeddings e JOIN products p ON p.id = e.product_id WHERE e.model_name = 'google/siglip2-base-patch16-256' ORDER BY p.external_id, e.embedding_type LIMIT 1;"

-- Check dimensions and counts by embedding type:
-- docker compose exec db psql -U postgres -d ai_shopping -c "SELECT embedding_type, COUNT(*) AS count, MIN(vector_dims(embedding)) AS min_dims, MAX(vector_dims(embedding)) AS max_dims FROM product_embeddings WHERE model_name = 'google/siglip2-base-patch16-256' GROUP BY embedding_type ORDER BY embedding_type;"
