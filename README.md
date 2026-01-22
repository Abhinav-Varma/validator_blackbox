# Python-JSLT Transformer – Deep-Dive README

**Audience:** you want to add new transformation functions, understand how the engine chains them, and build new `OutputModel`s without surprises.

---

## 1. 30-second recap

- You **never write imperative code** to transform JSON.  
- You **declare** how each field is computed by chaining **typed Step objects**.  
- Only functions **explicitly exported** from `function_pool.py` can be used – no `eval`, no `exec`, no escape hatches.  
- The DSL is **pure Python**, so **autocomplete**, **type-checking**, and **refactor** work out of the box.

---

## 2. File map & responsibility

| File | Responsibility |
|------|----------------|
| `main.py` | **Runner**. Imports models from `rules.py`, loads JSON, prints results. *Never edited after scaffolding.* |
| `rules.py` | **User catalogue**. All `TransformBaseModel` subclasses live here. You add new models / fields here only. |
| `custom_basemodel.py` | **Pydantic glue**. Gives you `Field(..., transform=Step)` and the automatic execution hook. *Rarely touched.* |
| `step_engine.py` | **Micro-kernel**. Defines `Step`, `|`, and **only** `path(...)`. *Never contains business logic.* |
| `function_pool.py` | **Function supermarket**. Every transformation primitive you can use. *This is where you commit new code.* |

---

## 3. `step_engine.py` – line-by-line walk-through

```python
from __future__ import annotations
from typing import TypeVar, Callable, Any, Dict, Generic
```
- Future import lets us use lowercase generics (`Step[Dict[str, Any], str]`) inside the same file.  
- `Generic[T, U]` is the trick that gives **static type inference** for every transformation.

---

```python
T = TypeVar("T")
U = TypeVar("U")
V = TypeVar("V")
```
- One type-var per **position** in the chain:  
  `Step[T, U]` means “input type T, output type U”.

---

```python
class Step(Generic[T, U]):
    __slots__ = ("_fn",)

    def __init__(self, fn: Callable[[T], U]) -> None:
        self._fn = fn
```
- `Step` is **just a boxed function**.  
- `__slots__` keeps instances tiny (no per-instance `__dict__`).

---

```python
    def __call__(self, value: T) -> U:
        return self._fn(value)
```
- Makes the object **callable like a plain function** – important for the final execution inside `TransformBaseModel`.

---

```python
    def __or__(self, other: Step[U, V]) -> Step[T, V]:
        return Step(lambda v: other(self(v)))
```
- **Composition operator**.  
  `a | b` produces a **new** Step that first runs `a`, then feeds the result into `b`.  
  Because the lambda closes over `self` and `other`, **no new syntax** is required – it is still **pure Python**.

---

```python
class Path(Step[Dict[str, Any], Any]):
    def __init__(self, jsonpath: str) -> None:
        self._path = jsonpath
        super().__init__(self._resolve)
```
- `Path` **is-a** `Step` – therefore it can live on either side of `|`.  
- We **delay** the actual JSON-Path library import until **runtime** to keep start-up fast.

---

```python
    def _resolve(self, blob: Dict[str, Any]) -> Any:
        from jsonpath_ng import parse
        matches = parse(self._path).find(blob)
        if not matches:
            return ""          # legacy compatibility
        if len(matches) == 1:
            return matches[0].value
        return [m.value for m in matches]
```
- **Single walk** per path **per document**.  
- Returns **scalar** when only one hit, **list** otherwise – mimics `jsonpath_ng` default.

---

```python
path = Path  # convenience alias
```
- Lets users write `path("$.foo")` instead of `Path("$.foo")`.

---

That is **literally the whole kernel** – < 50 LOC, no magic, no exec.

---

## 4. Function pool catalogue – exhaustive examples

Every function **returns** a `Step[In, Out]` so it can be chained.

### 1. `CAPITALIZE` – simplest unary step
```python
from src.function_pool import CAPITALIZE
step = path("$.name") | CAPITALIZE()
assert step({"name": "alice"}) == "Alice"
```

### 2. `CONCAT` – configurable separator
```python
from src.function_pool import CONCAT
step = CONCAT(" - ")([path("$.a"), path("$.b")])
assert step({"a": "A", "b": "B"}) == "A - B"
```

### 3. `JOIN` – glue a list of strings
```python
from src.function_pool import JOIN
step = JOIN()(["foo", "bar"])
assert step({}) == "foobar"
```

### 4. `SUBSTR` – slice with bounds check
```python
from src.function_pool import SUBSTR
step = SUBSTR(0, 3)
assert step("abcdef") == "abc"
```

### 5. `GST_STATE_NAME` – dictionary lookup
```python
from src.function_pool import GST_STATE_NAME
step = path("$.gstin") | GST_STATE_NAME()
assert step({"gstin": "27AABCU9603R1ZX"}) == "Maharashtra"
```

### 6. `GST_DETAILS_ALL` – list-in, list-out
```python
from src.function_pool import GST_DETAILS_ALL
step = path("$.gst_records") | GST_DETAILS_ALL()
data = {"gst_records": [{"gst_number": "27AABCU9603R1ZX"}]}
assert step(data) == [{"gst_number": "27AABCU9603R1ZX", "pan_number": "AABCU9603R", "state_name": "Maharashtra"}]
```

### 7. `join_parts` – mixed literals + paths (high-level helper)
```python
from src.function_pool import join_parts
step = join_parts(
    path("$.first_name") | CAPITALIZE(),
    " ",
    path("$.last_name") | CAPITALIZE(),
)
assert step({"first_name": "john", "last_name": "doe"}) == "John Doe"
```

---

## 5. Combining many steps – real model snippet

```python
from src.rules import TransformBaseModel, Field
from src.step_engine import path
from src.function_pool import CAPITALIZE, join_parts, GST_DETAILS_ALL, SUBSTR

class CustomerModel(TransformBaseModel):
    display_name: str = Field(
        transform=join_parts(
            path("$.first_name") | CAPITALIZE(),
            " ",
            path("$.last_name") | CAPITALIZE(),
        )
    )

    initials: str = Field(
        transform=join_parts(
            path("$.first_name") | SUBSTR(0, 1) | CAPITALIZE(),
            ".",
            path("$.last_name") | SUBSTR(0, 1) | CAPITALIZE(),
            ".",
        )
    )

    gst_info: list[dict[str, str]] = Field(
        transform=path("$.gst_list") | GST_DETAILS_ALL()
    )
```

---

## 6. Step-by-step: adding a brand-new function

**Goal:** create `REVERSE()` that reverses a string.

### ① Implement the logic in `function_pool.py`

```python
def REVERSE() -> "Step[str, str]":
    from src.step_engine import Step
    return Step(lambda s: s[::-1])
```

### ② Export it (so it appears in autocomplete)

Add `REVERSE` to the `__all__` list at the bottom of `function_pool.py`:

```python
__all__ = [
    "CAPITALIZE",
    "CONCAT",
    "JOIN",
    "join_parts",
    "SUBSTR",
    "GST_STATE_NAME",
    "GST_DETAILS_ALL",
    "REVERSE",   # <-- new
]
```

### ③ Use in `rules.py`

```python
from src.function_pool import REVERSE   # now auto-suggested by IDE

class PlayModel(TransformBaseModel):
    backwards: str = Field(
        transform=path("$.word") | REVERSE()
    )
```

### ④ Test quickly in a REPL

```python
>>> from src.rules import PlayModel
>>> PlayModel(json_data={"word": "stressed"}).backwards
'desserts'
```

That is **literally all that is required** – no kernel change, no registration call, no AST whitelist update.

---
### Multipart Commands

A Step is unary by definition: Step[T, U] = one input → one output.
#### Method 1
We will need to create a blob of the type of input required for the output in order for the helper to ingest as follows

Helper:
```python
def function(...Can be any variable it needs to take...) -> Step[List/Dict/etc.[Any], str]:
    return Step(lambda blob: function(blob)
    )
```

Usage:
```python
# build the container with pure Python, then pipe
transform = (
    lambda blob: [path("$..a")(blob), path("$..b")(blob), "literal",...]
) | function()
```
#### Method 2
Pass multiple values into the function itself and create the blob* in the helper. Look at join_parts() for example.

*depends on usage
#### Multipart Outputs
When a Step must return several independent pieces (a tuple, dict, list, named tuple, dataclass, etc.) you simply let the Step emit that object – the next Step in the chain must expect that shape as its input type.

Next Step can pick what it needs:
```python
step = (
    path("$.gst_number")
    | EXTRACT_GST_COMPONENTS()
    | Step(lambda d: d["state_code"])   # only state code
    | GST_STATE_NAME()                  # returns string
)
```
## 7. Common pitfalls & how to avoid them

| Symptom | Reason | Fix |
|---------|--------|-----|
| `TypeError: sequence item 0: expected str instance, Path found` | You passed a **list containing raw Path objects** to `JOIN`/`CONCAT`. | Use `join_parts()` or **resolve each path yourself** inside a lambda. |
| `NameError: name 'print' is not defined` | You tried to use something **not imported from function_pool**. | Import only from `function_pool`; add new helpers there. Or use qualified imports (fp.CAPITALIZE)|
| IDE shows `Any` for chain result | You forgot to **parameterise** the step or **return type hint**. | Add `-> "Step[In, Out]"` to your helper. |

---

## 8. Cheatsheet (print & pin)

```
Chaining:          path("$.x") | CAPITALIZE() | CONCAT(" ")
New helper:        def FOO() -> "Step[I, O]": return Step(fn)
New model field:   my_field: str = Field(transform=path("$.json") | FOO())
Security:          Only objects you import from function_pool exist – no eval.
Performance:       AST cache already in place; bulk-extract later if needed.
```

Happy transforming!