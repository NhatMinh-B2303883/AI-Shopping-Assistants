# Text semantic search + vector inspection

This package adds a first text-search utility to `ai/search/` and a CLI smoke test.

## Integration assumptions

- The repo root is mounted into the backend at `/app` (`./backend:/app`).
- The `ai` directory is mounted into the container at `/workspace/ai:ro`.
- Run commands from the repository root with `PYTHONPATH=/app:/workspace`.
- `ProductEmbedding.embedding` is `Vector(768)` and `ProductEmbedding` includes
  `embedding_type`, `product_image_id`, `model_name`, and `product_id`.
- The stored text embeddings were made with `google/siglip2-base-patch16-256`.
- `ai/embedding/siglip2_encoder.py` already exists from the prior refactor.

## Add files

Copy:
- `ai/search/__init__.py` to `ai/search/__init__.py`
- `ai/search/semantic_search.py` to `ai/search/semantic_search.py`
- `backend/scripts/test_semantic_search.py` to `backend/scripts/test_semantic_search.py`
- `docs/inspect_embeddings.sql` to `docs/inspect_embeddings.sql`

Do not replace your existing root `ai/__init__.py` or embedding module.

## Smoke test

From repo root:

```powershell
docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/test_semantic_search.py "black hoodie" --limit 5
```

Try Vietnamese as well:

```powershell
docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/test_semantic_search.py "áo hoodie đen" --limit 5
```

The script loads the model once per invocation. It ranks candidates by pgvector cosine distance; lower distance means closer. Similarity is `1 - distance` because the model's output vectors are L2-normalized. It is a ranking score, not a probability.

## Inspect embedding coordinates

```powershell
docker compose exec db psql -U postgres -d ai_shopping -x -c "SELECT p.external_id, p.name, e.embedding_type, vector_dims(e.embedding) AS dimensions, subvector(e.embedding, 1, 10)::text AS first_10_coordinates FROM product_embeddings e JOIN products p ON p.id = e.product_id WHERE e.model_name = 'google/siglip2-base-patch16-256' ORDER BY p.external_id, e.embedding_type LIMIT 4;"
```

To show all coordinates of one vector, replace the selected coordinate expression with `e.embedding::text AS full_vector` and use `LIMIT 1`. A 768-D vector is a point in a learned latent space; an individual coordinate normally does not have a directly interpretable human meaning by itself.
