# Tech Design Doc — Writing Guide

This reference contains detailed principles for writing high-quality technical design documents. Read this when:
- Writing or reviewing a design doc (for evaluation criteria)
- Deciding how to represent information (diagram vs code vs prose)
- Structuring alternatives comparison
- Checking for common anti-patterns

---

## 1. Start from the Problem, Not the Technology

**Anti-pattern**: "We're going to use Neo4j + ASM + Cytoscape.js. Here's how."

**Correct approach**: State the problem and constraints first. Technology choices should follow naturally from the problem — the reader should understand *why* each technology was chosen, not be forced to accept the author's preferences.

A well-written Goals & Constraints section makes the Architecture section almost predictable. If readers are surprised by the tech choices, the problem statement wasn't clear enough.

---

## 2. Audience-Aware Layering

A good design doc works like a map with zoom levels:

| Level | Reader | What they get | How long |
|-------|--------|---------------|----------|
| High | Decision-makers | Architecture diagram + section headings = full picture | 5 min |
| Mid | Tech leads | Prose + flow diagrams = design decisions and tradeoffs | 20 min |
| Deep | Developers | Interface definitions + data formats = enough to start building | Full read |

Each level should be self-contained. A reader who stops at the high level should still have a coherent understanding — not a cliffhanger.

---

## 3. Diagram Usage

### Core Principle

**Process logic → diagrams. Declarative contracts → code. Everything else → prose.**

Diagrams beat code for design docs because they express logic flow, module collaboration, and decision branches — which is exactly what design docs need to communicate. Code is linear and sequential; the reader has to "execute" it mentally to reconstruct the full picture.

### When to Use Which Diagram

| What you're expressing | Diagram type | When to use |
|----------------------|-------------|-------------|
| Step-by-step logic with decision branches | Flowchart | Algorithm logic, processing pipelines, decision trees |
| Module-to-module call sequence | Sequence diagram | API call flows, request/response patterns, multi-service interactions |
| Parallel activities across roles/modules | Swimlane (flowchart + subgraph) | CI pipelines, multi-team workflows, build processes |
| Lifecycle, state transitions | State diagram | Entity lifecycles, status machines, feature flags |
| System modules and their relationships | Block diagram / flowchart | Architecture overviews, deployment topologies |
| Timeline, phases | Gantt chart | Implementation plans, migration schedules |

### When NOT to Use Diagrams

- Simple linear steps ("first A, then B, then C") — prose is enough.
- Fewer than 3 nodes with no branches — information density too low, not worth a diagram.
- The same information is already clear in a table — don't duplicate.

### Prefer Mermaid Format

Mermaid diagrams are plain text, version-controllable with the document, renderable in GitLab/GitHub/most doc platforms, and low-cost to modify. Avoid binary diagram formats (Visio, draw.io exports) that can't be diffed and tend to go stale.

---

## 4. Code Policy

### What Belongs in a Design Doc

| Type | Why it belongs | Examples |
|------|---------------|----------|
| Interface definitions | Design contract, not implementation detail | Java interface, gRPC proto, GraphQL schema |
| Data format specs | Module communication protocol | JSON structure, SQL DDL, message schemas |
| Config snippets | Deployment/integration contract | Maven plugin config, CI config fragments |

These share a common trait: they are **declarative and stable** — they define *what*, not *how*.

### What Does NOT Belong

| Type | Why it doesn't belong | What to do instead |
|------|----------------------|-------------------|
| Algorithm implementations | Reader must "execute" code to understand logic | Flowchart |
| Business logic code | Will diverge from actual implementation | Prose + diagram |
| Multi-language parallel implementations | Redundant, maintenance burden | Pseudocode or one language max |
| Utility/helper methods | Implementation detail | Omit entirely |

### Litmus Test

Before including any code, ask: **"If I delete this code and replace it with a paragraph of prose or a diagram, can the reader still understand my design intent?"** If yes, the code is redundant.

---

## 5. Alternatives Comparison

### When to Compare

Only compare when **real tradeoffs exist**. For decisions that are clearly correct given the constraints, just state the choice and move on. Fabricating comparisons for obvious decisions wastes the reader's time and dilutes the signal of genuine decision points.

### How to Compare

- Define objective comparison dimensions (e.g., deployment complexity, team learning curve, scalability, CI friendliness).
- Present a comparison table with all options scored on the same dimensions.
- State your recommendation explicitly and explain why.
- Let the reader disagree — give enough information for them to make their own judgment.

### Anti-pattern

Subtly biasing the comparison to make your preferred option look better. If you have a preference, say it directly: "We recommend Option B because..." Honest advocacy is more trustworthy than fake objectivity.

---

## 6. Scope Boundaries

Explicitly stating what the design does NOT cover is as important as stating what it does. This prevents:

- Readers assuming the design handles something it doesn't.
- Scope creep during implementation.
- Post-hoc arguments about "but the design should have covered X".

Write scope boundaries as affirmative design decisions, not disclaimers: "We do not handle reflection-based calls — this is a deliberate boundary, not an oversight."

---

## 7. Risks Section

### What Makes a Good Risk Entry

A good risk is something you **genuinely worried about during the design process**. It has a concrete impact and an actionable mitigation.

**Good**: "If the team doesn't trust the tool's output, the tool will be abandoned → Phase 1 will include validation against 10 known call chains to establish a trust baseline."

**Bad**: "There might be performance issues → We'll monitor performance." (Boilerplate, not actionable.)

### Structure

Each risk should have: the risk itself, its concrete impact, which parts of the design it affects, and a specific mitigation action.

---

## 8. Verification Criteria

Every implementation phase should answer: **"How do we know it's done correctly?"**

Without verification criteria, a project can reach "looks done" without anyone knowing if it actually works. Criteria should be specific and testable: "Manually verify 5-10 known call chains against tool output" is good; "confirm it works" is not.

---

## 9. Evolution & Iteration

Design docs are **discussion artifacts**, not final blueprints.

- The first draft exists to be discussed and challenged, not to be perfect.
- Leave extension points at key coupling boundaries — not over-engineering, but reasonable flexibility for foreseeable changes.
- Expect multiple revision rounds. A design doc that was never revised was probably never seriously reviewed.

---

## 10. Anti-Pattern Checklist

| Anti-pattern | Symptom | Fix |
|-------------|---------|-----|
| Tech-first writing | Opens with technology choices, problem unclear | Lead with problem and constraints |
| Code-as-documentation | Large implementation blocks in the doc | Replace with diagrams + interface definitions |
| Single-option proposal | Only one approach presented, no decision rationale | Add comparison where real tradeoffs exist |
| Boilerplate risks | "Might have issues → will monitor" | Write real concerns with actionable mitigations |
| No verification criteria | Phase ends with "deliver X" but no way to confirm correctness | Add testable verification for each phase |
| Over-design | Document more complex than the system | Match depth to project scale |
| Write-once mentality | Treat first draft as final | Plan for iteration, use draft to drive discussion |
