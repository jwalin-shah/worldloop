# Three-minute demo

1. Run `make demo` on `case-cross-entity` and show pass 1: vector retrieval finds only part of the support chain.
2. Point to the critic diagnosis: `cross_entity_join` with missing evidence IDs.
3. Show the Loop Doctor adding `graph` to the retrieval recipe.
4. Show pass 2 score improving to full fixture support and the provenance records for every supporting evidence item.
5. Run `make benchmark` to show the same loop across temporal, contradiction/staleness, alias/semantic-miss, cross-entity, and insufficient-evidence cases.
6. If `WANDB_API_KEY` is present, enable W&B Weave tracing without changing code. The offline smoke remains deterministic without remote credentials.

Do not present fixture success as production accuracy. The demo is evidence that the loop can diagnose a retrieval failure and change context-building behavior measurably.
