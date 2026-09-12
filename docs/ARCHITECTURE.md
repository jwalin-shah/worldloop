# WorldLoop Architecture

WorldLoop is a **self-improving context, resource, and execution compiler**. The hackathon loop remains the learning/debugging mechanism, but the production destination is a typed workflow/state machine: deterministic where possible, semantically intelligent only where necessary, explicit about evidence and transitions, and separated from authority and real-world verification.

See `DESIGN.md` for the broader behavioral specification and `TYPED_EXECUTION_IR.md` for the execution-IR contract.

## 1. End-to-end architecture

```mermaid
flowchart TB
    U[Task / objective] --> IC[Intent / Context Compiler]
    IC --> CM[Context Manifest + evidence obligations]
    CM --> IR[Typed Workflow IR]

    IR --> ENG[Workflow Engine]
    ENG --> DET[Deterministic node]
    ENG --> RET[Retrieval node]
    ENG --> SEM[Bounded semantic node]
    ENG --> TOOL[Tool node]

    RET --> MEM[Fixtures / BTW / LiveLM / source-native evidence]
    MEM --> PKT[Provenance-bearing EvidenceItem set]
    PKT --> RET

    SEM --> PRIM[GENERATE / CLASSIFY / DECIDE / EXTRACT / PLAN / CRITIQUE / PREDICT / VERIFY]
    PRIM --> PROVIDERS[Provider/model adapters]

    DET --> NEXT[Typed transition]
    RET --> NEXT
    SEM --> NEXT
    TOOL --> NEXT

    NEXT -->|non-consequential| OUT[Typed result / abstention]
    NEXT -->|consequential proposal| AUTH[HomeBase / Bridge authority]
    AUTH -->|admitted| ACT[Bounded actuator]
    ACT --> VER[Independent verifier]
    VER --> OUT

    IC -. versioned spans .-> WV[W&B Weave]
    IR -. graph/node version .-> WV
    ENG -. node outcomes .-> WV
    RET -. evidence refs .-> WV
    SEM -. decision + calibration .-> WV
    VER -. postcondition .-> WV

    WV --> AGG[Trajectory / evaluation dataset]
    AGG --> CR[Critic / failure classifier]
    CR --> LD[Loop Doctor / Policy Researcher]
    LD --> CAND[Candidate graph / node / context / model policy]
    AGG --> ARIA[ARIA hypothesis / experiment]
    ARIA --> CAND
    AGG --> TRAIN[Policy / node training]
    TRAIN --> CAND

    CAND --> HE[Frozen held-out evaluation]
    HE --> CMP[Correctness + regret + semantic surface + calibration + safety]
    CMP -->|wins + guardrails hold| PROMOTE[Promote version]
    CMP -->|regression| REJECT[Reject / rollback]
    PROMOTE --> IR

    LAB[marimo / molab WorldLoop Lab] <--> WV
    LAB <--> AGG
    LAB <--> CAND
```

The central invariant is now stronger than “the Critic is independent”: **the model does not own global control flow**. Semantic intelligence is local to typed nodes; explicit transition logic decides what happens next.

## 2. Runtime path vs learning loop

### Production/runtime path

```mermaid
sequenceDiagram
    participant User
    participant Compiler as Intent/Context Compiler
    participant Engine as Typed Workflow Engine
    participant Memory as Evidence Backend
    participant Semantic as Semantic Node
    participant Authority as Authority Boundary
    participant Verifier

    User->>Compiler: objective + budget
    Compiler->>Engine: typed workflow IR + Context Manifest
    Engine->>Memory: typed evidence request
    Memory-->>Engine: EvidenceItem[] + provenance
    Engine->>Semantic: bounded primitive input
    Semantic-->>Engine: typed value + uncertainty + refs
    Engine->>Engine: explicit transition predicate

    alt non-consequential result
        Engine-->>User: typed result / abstention
    else consequential effect
        Engine->>Authority: proposed effect
        Authority-->>Engine: admitted / denied / confirmation required
        Engine->>Verifier: verify postcondition after admitted actuation
        Verifier-->>User: verified receipt / failure
    end
```

A semantic node may inform a transition, but it never emits an arbitrary next-state instruction and never grants itself execution authority.

### Learning/debugging loop

```mermaid
flowchart LR
    X[Execute graph] --> W[Weave trace]
    W --> C[Critic classifies node/transition/evidence failure]
    C --> D[Loop Doctor / ARIA hypothesis]
    D --> P[Candidate graph/node/context/model change]
    P --> E[Frozen evaluation]
    E --> M[Compare verified success + cost + semantic surface + calibration]
    M -->|pass| U[Promote]
    M -->|fail| R[Reject / refine]
    U --> X
    R --> D
```

This loop is intentionally agentic and exploratory. Its job is to make the runtime graph more reliable and, where possible, less open-ended.

## 3. Intelligence primitives

Provider neutrality should exist below a typed semantic API rather than collapsing every model into `messages -> text`.

WorldLoop semantic primitives:

```text
GENERATE  context -> artifact
CLASSIFY  evidence -> enum + confidence
DECIDE    evidence + alternatives + stakes -> alternative | abstain + confidence
EXTRACT   evidence -> typed facts + provenance
PLAN      goal + world state -> typed proposed graph
CRITIQUE  artifact + invariants -> violations[]
PREDICT   state + intervention -> distribution(outcomes)
VERIFY    claim + evidence -> supported | contradicted | unknown
```

Different providers may implement different subsets. TypeSafe is evaluated as a possible provider for bounded machine-native decisions/classification/prediction if the real onsite interface supports them; no undocumented API is assumed.

## 4. Knowledge-location experiment

WorldLoop still treats knowledge location as an experimental variable:

```text
W = behaviorally accessible parameterized knowledge
C = active request/context
M = externally retrievable memory
```

```mermaid
flowchart LR
    Q[Synthetic task] --> R[Context/Resource Compiler]
    LW[W: base model + optional LoRA] --> R
    CTX[C: optional active context] --> R
    MEM[M: optional external memory] --> R
    R --> IR[Typed execution graph]
    IR --> V[Independent verification]
    V --> S[Correctness / provenance / regret / semantic surface]
```

The stronger question is not only “where did the fact come from?” but “how much semantic intelligence was actually necessary once the right evidence and workflow structure were available?”

## 5. Progressive compilation

WorldLoop should learn to compile repeated successful behavior into smaller typed programs.

```mermaid
flowchart LR
    O[Open exploratory behavior] --> T[Traced trajectories]
    T --> PAT[Repeated successful pattern]
    PAT --> G[Candidate typed graph]
    G --> MIN[Replace broad reasoning with deterministic or narrow semantic nodes]
    MIN --> E[Frozen held-out evaluation]
    E --> C[Compare success + routing regret + semantic surface + calibration]
    C -->|safe improvement| P[Promote]
    C -->|regression| R[Reject]
```

New metrics include semantic-node count, semantic-surface ratio, compilation ratio, calibration error, and authority-bypass attempts. A lower semantic surface is only better if verified correctness and guardrails hold.

## 6. Data and source boundaries

```mermaid
flowchart TB
    subgraph NEW[Hackathon-new WorldLoop]
      FIX[Sanitized / synthetic fixtures]
      COMP[Compiler + typed IR]
      ENG[Workflow engine]
      CRIT[Critic]
      DOC[Loop Doctor]
      MAR[marimo Lab]
      WEV[Weave eval schema]
    end

    subgraph PRIOR[Clearly labeled prior work / optional adapters]
      LO[LifeOps durable state]
      BTW[LiveLM / BTW index]
      HB[HomeBase / Bridge]
    end

    FIX --> COMP --> ENG
    LO -. optional continuity/evidence adapter .-> COMP
    BTW -. optional read-only real-world M backend .-> ENG
    ENG --> CRIT --> DOC --> COMP
    ENG -. consequential proposal only .-> HB
    COMP --> WEV
    ENG --> WEV
    CRIT --> WEV
    DOC --> WEV
    MAR <--> WEV
```

The public judging baseline cannot require prior/private systems. BTW can demonstrate generalization to a real changing-world memory backend, while HomeBase/Bridge remains a distinct authority boundary rather than part of WorldLoop reasoning.

## 7. Tool responsibilities

| Component | Owns | Does not own |
|---|---|---|
| **WorldLoop** | compilation, typed IR, context/resource policy, evaluation contracts | mutable world truth or authority |
| **Typed Workflow Engine** | explicit states/transitions and bounded node execution | semantic truth or permission minting |
| **W&B Weave** | trajectory/evaluation proof, graph/node versions, scores, comparisons | runtime authority |
| **marimo / molab** | live experiment/control/analysis, graph and W/C/M visualization | canonical durable state |
| **W&B Models / Artifacts** | dataset/model/policy lineage | runtime control flow |
| **W&B Inference** | comparable model fleet / optional LoRA serving | evaluation truth |
| **ARIA** | outer-loop hypotheses/experiments | direct unreviewed production mutation |
| **TypeSafe AI** | candidate semantic primitive implementation | authority or assumed undocumented capabilities |
| **CoreWeave Sandboxes** | isolated stateful/code-execution nodes | default static retrieval |
| **SkyPilot** | optional parallel job/compute execution | reasoning or project state |
| **LifeOps** | optional durable continuity (prior work) | hackathon-new claim |
| **BTW / LiveLM** | real-world evidence backend (prior work) | control flow or authority |
| **HomeBase / Bridge** | consequential authorization/admission | epistemic reasoning |
| **Independent verifier** | actual-world postcondition checks | authorization |

## 8. marimo WorldLoop Lab

The Lab should now expose six views:

1. **Live Execution** — task, Context Manifest, compiled graph, current node, evidence, typed outputs, transitions, final verification.
2. **Policy / Program Comparison** — v0/v1 held-out success, recovery, routing regret, semantic-node count, semantic-surface ratio, latency/cost.
3. **Knowledge Location** — W/C/M cube and conflict cases.
4. **Failure Explorer** — node/transition/evidence failure classes with trace drill-down.
5. **Compilation View** — before/after graph showing which open-ended operations became deterministic or narrow semantic nodes.
6. **Experiment Registry** — hypotheses, metrics, stop rules, status, artifact refs.

## 9. Primary proof hierarchy

1. **Required:** a failure is traced to a specific resource/context/node decision and repaired by changing an actual decision variable.
2. **Required for strong self-improvement claim:** candidate policy/program improves held-out first-pass success or routing/context regret without correctness regression.
3. **Stronger:** show the candidate also reduces semantic surface or replaces an open-ended step with an explicit typed transition.
4. **Strong extension:** real provider/model comparison and ARIA-generated graph/node experiment.
5. **Hero extension:** W/C/M causal cube plus trained router/semantic node.
6. **Real-world validation:** read-only BTW/LiveLM evidence backend under the same typed contract.

## 10. Safety and production invariants

- the model never owns global control flow;
- every node has typed inputs/outputs and explicit transitions;
- insufficient or unresolved conflicting evidence fails closed;
- exact code/data/evidence/workflow/node/model/policy/scorer versions are bound to runs;
- counterfactual oracle labels never leak into online routing inputs;
- candidate graphs/policies are evaluated before promotion and remain rollbackable;
- source-native evidence outranks stale model memory for mutable facts;
- confidence is not authority;
- authorization, actuation, and verification are distinct stages;
- no private prior system is required for the public demo.
