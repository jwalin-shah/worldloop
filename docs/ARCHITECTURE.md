# Architecture

```mermaid
flowchart LR
  Q[Question] --> C[Context Compiler]
  C --> R[Evidence Retriever]
  R --> P[Provenance-bearing packet]
  P --> E[Critic / Evaluator]
  E -->|sufficient| A[Grounded answer]
  E -->|failure class| D[Loop Doctor]
  D -->|change retrieval recipe| C
  R --> X[(SQLite FTS5)]
  R --> V[Deterministic vector]
  R --> G[Graph traversal]
  R --> T[Temporal filter]
  E -. optional traces/evals .-> W[W&B Weave]
```

The critical distinction is that the Loop Doctor changes retrieval behavior rather than merely rephrasing an answer. Evidence keeps source, event time, and observation time. The fixture evaluator fails closed when required support is absent.
