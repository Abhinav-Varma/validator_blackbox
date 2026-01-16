# 🧩 Transformation Blackbox  
### Marshmallow‑Driven Mapping with Pydantic Output Contracts

---

## 📌 Overview

This project implements a **schema‑driven transformation blackbox** that converts **arbitrary input JSON** into **strict, validated Pydantic output models**.

The design intentionally separates **input flexibility** from **output correctness** by using:

- **Marshmallow** → input normalization and mapping  
- **Pydantic** → final output contracts and validation  
  

All transformations are **explicit, deterministic, and explainable**.

---

## 🎯 Core Design Principle

> **Flexible input, strict output**

- Input JSON may vary in structure, nesting, and field names
- Output must always conform to a well‑defined schema
- Mapping logic must not leak into output validation
- Validation logic must not depend on input shape

---


## 🏗️ Architectural Layers

The system is composed of **three clearly separated layers**:

1. **Mapping Layer (Marshmallow)**  
   Handles input variability and produces a canonical shape

2. **Orchestration Layer**  
   Coordinates transformation and validation steps

3. **Contract Layer (Pydantic)**  
   Enforces strict, consumer‑ready output schemas

---

## 🔄 High‑Level Flow

```mermaid
flowchart TD
    A[Raw Input JSON] --> B[Marshmallow Schema<br/>Mapping & Normalization]
    B --> C[Canonical Intermediate Dict]
    C --> D[Orchestrator]
    D --> E[Pydantic Output Model<br/>Contract Validation]
    E --> F[Final Validated Output]



## 🪜 Step-by-Step Flow of Events

### Step 1: Input JSON is Received
- The system accepts a **raw JSON dictionary**
- No assumptions are made about its structure
- No validation occurs at this stage

---

### Step 2: Marshmallow Schema Normalizes Input
- Each output has a corresponding **Marshmallow schema**
- The schema:
  - Resolves multiple possible input paths
  - Normalizes nested or inconsistent structures
  - Produces a canonical intermediate dictionary

At this stage:
- Keys are **stable**
- Values are **not yet trusted**

---

### Step 3: Canonical Dictionary is Produced
- Marshmallow emits a **normalized dictionary**
- This dictionary represents the best possible interpretation of the input
- It is still considered **unvalidated**

---

### Step 4: Orchestrator Assembles Output Payload
The orchestrator:
- Invokes the appropriate Marshmallow schema
- Performs minimal, explicit derivations (e.g. concatenation)
- Prepares a payload matching the output model’s shape

**Constraints:**
- Contains no business rules
- Contains only coordination logic

---

### Step 5: Pydantic Output Model Validates the Contract
- The prepared payload is passed into a **Pydantic output model**
- Pydantic enforces:
  - Required fields
  - Types
  - Declarative constraints (patterns, lengths, formats)

If validation fails:
- Execution stops immediately
- No partial or incorrect output is emitted

---

### Step 6: Final Output is Emitted
On successful validation:
- The output is serialized
- The result is consumer-ready

All downstream systems can **fully trust the output schema**

---

## 📐 Output Models as Contracts
Output models define **what must exist**, not **how data is derived**.

They:
- Contain no transformation logic
- Contain no mapping logic
- Act as strict runtime contracts

This ensures:
- Schema drift is detected immediately
- Invalid data never propagates downstream

---

## 🔑 Key Architectural Guarantees
- ✅ Input variability is isolated
- ✅ Output correctness is enforced centrally
- ✅ Transformation logic is explicit and reviewable
- ✅ No silent failures or heuristic guessing
- ✅ Clear ownership of responsibilities
