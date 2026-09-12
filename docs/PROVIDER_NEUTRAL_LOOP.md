# Provider-neutral LifeOps loop

WorldLoop is an experiment client over a provider-neutral durable fabric. Gemini on a Mac, ChatGPT, Claude/Codex on OCI, or a future provider should not own canonical project state in chat memory. They should enter the same loop and leave behind the same typed evidence and receipts.

## Authority model

- **Source-native systems** own changing facts.
- **LifeOps / the Universal Knowledge Fabric** owns durable cross-provider continuity: project/object resolution, observations, checkpoints, proposals, receipts, and relationships.
- **WorldLoop** owns hackathon experiment code, retrieval/context policies, fixtures, and reproducible evaluation artifacts.
- **The active model/provider** is a replaceable reasoner. Its hidden/session memory is never canonical state.
- **HomeBase / Bridge** remains the authority boundary for consequential execution. A model, notebook, or MCP client cannot grant itself execution authority.

## Canonical lifecycle

```text
provider session
  -> LifeOps resolve(project/system/object)
  -> identify evidence obligations
  -> retrieve source-backed evidence / context packet
  -> WorldLoop compiles retrieval/context policy
  -> provider reasons over the packet
  -> evaluator scores grounding, completeness, freshness, contradiction handling
  -> if failure: Loop Doctor changes retrieval behavior and reruns
  -> if material durable delta: observation/checkpoint/proposal
  -> if action is needed: HomeBase/Bridge authorization
  -> bounded executor
  -> independent verification
  -> receipt/checkpoint
```

The correction loop may learn **how to build context**. It must not promote an unverified model inference into world truth.

## Provider-neutral run envelope

Every comparable run should carry the same identifiers even if the provider changes.

```json
{
  "run_id": "run-<uuid>",
  "experiment_id": "EXP-002",
  "provider": "gemini|openai|anthropic|other",
  "model": "provider-model-id",
  "project_ref": "prop-85dc72d46765",
  "question": "...",
  "as_of": "ISO-8601",
  "evidence_obligations": ["freshness", "entity identity", "provenance"],
  "retrieval_policy_version": "policy-v1",
  "budget": {"max_passes": 3, "max_latency_ms": 30000}
}
```

The result record should be serializable without provider-specific state:

```json
{
  "run_id": "run-<uuid>",
  "experiment_id": "EXP-002",
  "provider": "gemini",
  "model": "...",
  "passes": [
    {
      "pass": 1,
      "recipe": ["vector"],
      "evidence_refs": ["E03"],
      "score": 0.5,
      "failure_class": "cross_entity_join"
    },
    {
      "pass": 2,
      "recipe": ["vector", "graph"],
      "evidence_refs": ["E03", "E04", "E05"],
      "score": 1.0,
      "failure_class": null
    }
  ],
  "durable_delta": "checkpoint|observation|proposal|none",
  "execution_authority": false
}
```

## Provider rules

1. Resolve durable objects before substantial work.
2. Preserve the authoritative owner of each fact; do not copy changing truth into a competing store.
3. Treat evidence, extracted claims, hypotheses, decisions, work, authorization, execution, verification, and checkpoints as distinct object types.
4. Write only material deltas. Brainstorming is not durable truth.
5. A proposal is not authorization. Authorization is not execution. Execution is not verification.
6. Cross-provider comparisons must use the same task/evidence snapshot and record exact provider/model/policy revisions.

## Hackathon boundary

The public demo uses sanitized fixtures by default. Optional LifeOps/BTW adapters may demonstrate continuity or fresh evidence, but private corpora are never a hidden dependency for the reproducible benchmark.
