# Step 8 — Hybrid product-search patch

## Files

- `ai/search/query_normalization.py`: dependency-light parser and alias tables.
- `ai/search/semantic_search.py`: normalize known English/Vietnamese aliases, infer one unambiguous product type/color, filter candidates by those attributes in PostgreSQL, then rank filtered candidates by SigLIP 2 text-embedding cosine distance. Known out-of-scope product types return an empty result when no supported type is also requested.
- `backend/scripts/test_semantic_search.py`: prints the raw query, normalized text passed to the encoder, inferred type/color, results and cosine scores.
- `tests/test_search_query_normalization.py`: small unit tests for the deterministic parsing layer.

## Apply

From `D:\\AI_Shopping_Assistants\\AI-Shopping-Assistants`, back up `ai\search\semantic_search.py` and `backend\scripts\test_semantic_search.py` first. Extract this ZIP into the repository root and overwrite the corresponding files. The added `ai\search\query_normalization.py` is new; merge the root `tests\` folder if it already exists.

The patch does not change SQLAlchemy models, database schema, catalog records, image paths, or stored embeddings. It keeps the SigLIP2 Base encoder and the 768-dimensional vector contract. The alias rules target the current seven leaf categories; the `Hoodie` intent maps to the existing `Sweatshirt` taxonomy node because no separate `Hoodie` category exists.

## Unit-test the parser (from repository root, after applying the patch)

```cmd
python -m unittest discover -s tests -p "test_search_query_normalization.py" -v
```

## Smoke-test commands

```cmd
docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/test_semantic_search.py "black hoodie" --limit 5
docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/test_semantic_search.py "áo hoodie đen" --limit 5
docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/test_semantic_search.py "white t-shirt" --limit 5
docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/test_semantic_search.py "giày chạy bộ màu đen" --limit 5
docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/test_semantic_search.py "blue jeans" --limit 5
```

Expected behavior: the first two infer `Sweatshirt` + `Black`; the third infers `T-Shirt` + `White`; the fourth infers `Sports Shoes` + `Black`; `blue jeans` returns zero results as the requested type is out of scope. The actual number of matches depends on catalog contents.

## Report-ready evaluation notes

The previous implementation is vector-only for query intent. It encodes the raw query directly, joins only the product text embeddings for the selected model, optionally filters by explicit `category_id`, `gender`, price bounds and a caller-supplied `min_similarity`, then sorts by cosine distance. It does not infer a product type or color from the natural-language query. `min_similarity` defaults to `None`; therefore, the previous implementation can return the nearest available items even when they are not a good match. The reported `similarity` is `1 - cosine_distance`, not a calibrated probability.

The catalog's locked leaf taxonomy uses `Sweatshirt`, not a separate `Hoodie` class. Thus “hoodie” is mapped to `Sweatshirt`; this is a taxonomy-level approximation, not a guarantee that every returned sweatshirt has a hood. The updated approach adds deterministic, inspectable rules for high-precision product type/color constraints before vector ranking. It also normalizes common Vietnamese aliases to canonical English terms, and does not silently relax a detected constraint when no product matches.

The listed tests verify parsing behavior; they do not by themselves prove retrieval quality. For the project report, save the actual command outputs and evaluate a small labelled query set with Precision@5 (relevant results in top five), category accuracy in top five, and no-result correctness. Compare the old and updated implementation on the same queries. Do not claim a measured improvement until those results are recorded.

## Dependency-light unit-test note

The patch also includes a lazy `ai/search/__init__.py`. Previously, importing
`ai.search.query_normalization` first executed the package initializer, which
immediately imported `semantic_search.py` and therefore required SQLAlchemy and
pgvector even for parser-only tests. The lazy export preserves
`from ai.search import semantic_search_products`, but defers loading the database
search dependencies until that symbol is requested.

You can now run parser unit tests using Python without installing the full
backend stack:

```cmd
python -m unittest discover -s tests -p "test_search_query_normalization.py" -v
```

The database-backed search smoke tests must still run inside the backend
container (or a Python environment with the backend dependencies installed).
