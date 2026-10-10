SigLIP 2 embedding refactor patch

Copy the folders in this archive into the project root:
  AI-Shopping-Assistants/

Files:
  ai/__init__.py
  ai/embedding/__init__.py
  ai/embedding/siglip2_encoder.py
  backend/scripts/generate_embeddings.py

Docker Compose change:
  In service backend -> volumes, preserve existing mounts and add:
    - ./ai:/workspace/ai:ro

This makes the `ai.embedding` package available inside the backend container.
The existing catalog mount must remain:
    - ./data/product/final:/data/products:ro

Run commands from the repository root:
  docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/generate_embeddings.py --dry-run --limit 2
  docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/generate_embeddings.py --limit 2
  docker compose exec -e PYTHONPATH=/app:/workspace backend python scripts/generate_embeddings.py

Do not run the 1,000-product command until the 2-product dry run and write test pass.
