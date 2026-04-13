---
name: tech-design-doc
description: |
  Write, review, or improve technical design documents for the user. Trigger when the user explicitly asks to produce a design document, architecture proposal, system design spec, RFC, or technical plan — for example: "help me write a design doc for X", "draft an RFC for Y", "review my tech spec". Also trigger when the user has been iterating on a technical solution and says "turn this into a design doc" or "write this up as a formal proposal". Do NOT trigger for casual questions about design doc best practices — only trigger when the user wants a document produced or reviewed.
---

# Tech Design Doc — Operational Guide

This skill helps the user produce high-quality technical design documents. The core principle: a design doc answers **"what" and "why"**, not "how to code". Express process logic with diagrams, declarative contracts with code, everything else with prose.

Before writing, read `references/writing-guide.md` for detailed principles on structure, diagram usage, code policy, and anti-patterns.

---

## Workflow

### Step 1: Gather Context

Before writing anything, collect these four inputs. If any are missing or ambiguous, **stop and ask the user** before proceeding.

| Input | Question to ask | Why it matters |
|-------|----------------|----------------|
| Problem | "What problem are you solving? What's the current pain point?" | Drives the entire doc — without this, everything else is guesswork |
| Audience | "Who will read this? Your dev team, leadership, or external partners?" | Determines depth, tone, and what to emphasize |
| Constraints | "Any hard requirements? (tech stack, timeline, team size, must-integrate-with-X)" | Narrows the solution space before you start designing |
| Scope | "What's explicitly out of scope?" | Prevents scope creep and misaligned expectations |

**Interaction rule**: Do NOT ask all four as a checklist. Infer what you can from the conversation history. Only ask what's genuinely missing. If the user has been discussing a technical solution for several turns, you likely already have most of these — summarize your understanding and confirm.

### Step 2: Generate Document Skeleton

Once context is clear, produce the skeleton using the **Output Template** below. Fill in what you know, mark unknowns with `[TBD - need input on X]`.

Present the skeleton to the user and ask: "Does this structure cover what you need? Anything to add or remove before I flesh it out?"

### Step 3: Fill In Core Sections

Fill the document template section by section, in this priority order:

- **Goals & Constraints** (template §1) — write first, since everything else depends on it.
- **Architecture overview** (template §2) — produce a Mermaid diagram + prose explanation.
- **Core design** (template §3) — data models, interfaces, key process flows (as Mermaid diagrams, NOT implementation code).
- **Alternatives considered** (template §3.4) — only where real tradeoffs exist. Don't fabricate comparisons.

**Interaction rule**: After completing Goals & Architecture, pause and share with the user. These are the foundation — if they're wrong, everything built on top is wasted. Only proceed to Core Design and Alternatives after user confirms direction.

### Step 4: Add Implementation Plan & Risks

- **Implementation plan** (template §4) — phased milestones with deliverables and verification criteria for each phase.
- **Risks & mitigations** (template §5) — only real concerns you encountered during design, not boilerplate.

**Interaction rule**: After completing all sections, share the full draft with the user before moving to the Review Pass. Don't self-review in isolation — the user may catch direction issues that the checklist won't.

### Step 5: Review Pass

Before presenting the final document, self-check against these criteria:

- [ ] Can a decision-maker understand the full picture in 5 minutes by reading only headings + architecture diagram?
- [ ] Can a developer understand how to start implementing by reading the full doc?
- [ ] Is every process flow expressed as a diagram, not implementation code?
- [ ] Does the doc contain ONLY interface definitions and data format specs as code — no implementation logic?
- [ ] Are scope boundaries ("what we don't do") explicitly stated?
- [ ] Does every phase have a verification criterion ("how do we know it's done right")?

### Step 6: Iterate

After presenting, ask: "Which sections need more depth? Anything I got wrong or missed?"

Expect multiple rounds. The first draft is a discussion artifact, not a final deliverable.

---

## Output Template

Use this skeleton. Adjust section depth to match project scale — a small feature doesn't need the same weight as a platform redesign.

```markdown
# [Project Name] — Technical Design Document

## 1. Goals & Constraints

### 1.1 Problem Statement
[1-2 paragraphs: what problem, why it matters, why now]

### 1.2 Core Goals
[Measurable, verifiable goals]

### 1.3 Scope Boundaries
[Explicitly: what this design does NOT cover]

### 1.4 Constraints
[Tech constraints, team constraints, timeline, dependencies]


## 2. Architecture

[Mermaid architecture diagram]

[Prose: responsibilities of each layer/module, how they interact,
 key design decisions and WHY they were made]


## 3. Core Design

### 3.1 Data Model
[Table definitions, JSON schemas, entity-relationship descriptions]

### 3.2 Interfaces
[API contracts, interface definitions, message formats between modules]

### 3.3 Key Processes
[Mermaid flowcharts / sequence diagrams / swimlane diagrams for
 critical logic. NO implementation code — diagrams only]

### 3.4 Alternatives Considered (if applicable)
[Comparison table with objective dimensions.
 State your recommendation and reasoning.]


## 4. Implementation Plan

### Phase 1: [Name] (estimated duration)
- Deliverables: ...
- Verification: [How to confirm it's done correctly]

### Phase 2: [Name] (estimated duration)
...


## 5. Risks & Mitigations

| Risk | Impact | Affected Area | Mitigation |
|------|--------|---------------|------------|
| [Real concern from design process] | [Concrete impact] | [Which modules/phases] | [Actionable mitigation] |
```

---

## What Goes Where

| Content type | Representation | Belongs in doc? |
|-------------|----------------|-----------------|
| Process logic, decision branches, algorithms | Mermaid diagram (flowchart / sequence / swimlane) | Yes |
| Interface definitions, API contracts | Code (interface / proto / schema) | Yes |
| Data formats, table schemas | Code (JSON / SQL DDL) | Yes |
| Build/deploy config snippets | Code (short, declarative) | Yes, if it's a design decision |
| Implementation logic, business code | — | **No** — use diagram or prose instead |
| Multi-language parallel implementations | — | **No** — pick one or use pseudocode |

---

## Examples

**Example 1: User asks to write a design doc from scratch**

> User: "Help me write a design doc for a notification service that supports email, SMS, and push notifications."

Claude should:
1. Gather missing context (Step 1): "Before I draft the doc — who's the audience? And are there constraints on tech stack or existing infrastructure I should know about?"
2. After getting answers, produce the document skeleton and confirm structure with the user (Step 2).
3. Fill in Goals & Architecture first, share for confirmation (Step 3 first pause point). Only after the user confirms direction, proceed to Core Design and remaining sections.

**Example 2: User has been discussing a solution and wants it formalized**

> User: [after 10 turns of technical discussion] "Can you turn this into a design doc?"

Claude should:
1. NOT ask questions it already has answers to from the conversation.
2. Summarize the key decisions made so far: "Based on our discussion, here's what I understand: [problem], [approach], [key decisions]. I'll structure this into a design doc — let me know if I'm missing anything."
3. Produce a complete first draft, since context is already rich.

**Example 3: User asks to review an existing design doc**

> User: "Review my design doc and suggest improvements." [attaches document]

Claude should:
1. Read `references/writing-guide.md` for evaluation criteria.
2. Evaluate against: audience clarity, problem-driven structure, diagram vs code usage, scope boundaries, verification criteria, risk quality.
3. Give structured feedback: what's strong, what's missing, specific rewrite suggestions for weak sections.
