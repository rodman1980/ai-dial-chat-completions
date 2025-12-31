# ADR-002: Use Dataclasses for Data Models

**Status**: Accepted

**Date**: 2025-12-31

**Decision Makers**: Project Team

**Last Updated**: 2025-12-31

---

## Context

The project requires several data structures to represent:
- **Messages**: Role + content pairs
- **Conversations**: Message history with metadata
- **Roles**: Enumeration of message types

Options for implementing these structures:
1. Plain dictionaries
2. Named tuples
3. Regular classes with `__init__`
4. Python dataclasses
5. Pydantic models
6. attrs library

Requirements:
- Simple, readable code (educational project)
- Type hints for IDE support
- Automatic equality and representation
- Easy serialization to API format
- Minimal boilerplate
- No runtime overhead for validation (not critical for learning)

## Decision

Use Python **dataclasses** (`@dataclass` decorator) for all data models:

- **Message** ([message.py](../../task/models/message.py))
- **Conversation** ([conversation.py](../../task/models/conversation.py))

Use **StrEnum** for role enumeration:
- **Role** ([role.py](../../task/models/role.py))

### Example Implementation

```python
from dataclasses import dataclass, field
from enum import StrEnum

class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    AI = "assistant"

@dataclass
class Message:
    role: Role
    content: str
    
    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role.value,
            "content": self.content
        }

@dataclass
class Conversation:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    messages: list[Message] = field(default_factory=list)
```

## Consequences

### Positive ✅

1. **Zero Boilerplate**
   - No manual `__init__` methods
   - Automatic `__repr__` for debugging
   - Automatic `__eq__` for comparisons
   - Reduces code by ~15 lines per class

2. **Type Safety**
   - Full type hints built-in
   - IDE autocomplete works perfectly
   - Mypy validation without extra configuration
   - Prevents common bugs (wrong field types)

3. **Readability**
   - Intent clear at a glance
   - Field types visible in definition
   - Educational - shows modern Python patterns
   - Clean, idiomatic code

4. **Default Values**
   - `default_factory` for mutable defaults
   - UUID generation automatic
   - Empty list initialization safe
   - No "mutable default argument" pitfall

5. **Simplicity**
   - Standard library (no dependencies)
   - Well-documented feature
   - Students already learn dataclasses
   - Compatible with all Python 3.11+ projects

### Negative ⚠️

1. **No Validation**
   - Empty content strings allowed
   - No field constraints
   - Invalid roles possible (if not using enum)
   - Must validate manually if needed

2. **No Automatic Serialization**
   - Must implement `to_dict()` manually
   - No JSON schema generation
   - No automatic API format conversion
   - (Acceptable for simple project)

3. **Mutable by Default**
   - Fields can be changed after creation
   - No immutability enforcement
   - Could lead to bugs in complex scenarios
   - (Not a concern for this project)

4. **Limited Field Customization**
   - No field validators
   - No custom setters/getters
   - No transformation on assignment
   - (Not needed here)

### Neutral ⚖️

1. **Python 3.7+ Required**
   - Dataclasses introduced in 3.7
   - Project requires 3.11 anyway (for StrEnum)
   - Not a limitation in practice

2. **Learning Curve**
   - Students must understand decorators
   - Field factory pattern new to some
   - (Part of learning objectives)

## Alternatives Considered

### Alternative 1: Plain Dictionaries

**Approach**:
```python
message = {
    "role": "user",
    "content": "Hello"
}
```

**Pros**:
- ✅ No class definition needed
- ✅ Directly API-compatible

**Cons**:
- ❌ No type hints
- ❌ Easy to misspell keys
- ❌ No IDE autocomplete
- ❌ No structure enforcement

**Verdict**: Rejected - too error-prone, poor educational value

---

### Alternative 2: Named Tuples

**Approach**:
```python
from typing import NamedTuple

class Message(NamedTuple):
    role: str
    content: str
```

**Pros**:
- ✅ Immutable
- ✅ Type hints
- ✅ Lightweight

**Cons**:
- ❌ Immutability too restrictive (can't update conversation)
- ❌ No default values (before Python 3.6.1)
- ❌ Awkward `to_dict()` implementation

**Verdict**: Rejected - immutability conflicts with conversation updates

---

### Alternative 3: Regular Classes

**Approach**:
```python
class Message:
    def __init__(self, role: Role, content: str):
        self.role = role
        self.content = content
    
    def __repr__(self):
        return f"Message(role={self.role!r}, content={self.content!r})"
    
    def __eq__(self, other):
        return self.role == other.role and self.content == other.content
```

**Pros**:
- ✅ Full control
- ✅ No magic decorators
- ✅ Explicit everything

**Cons**:
- ❌ ~15 lines vs. 5 lines with dataclass
- ❌ Boilerplate for every class
- ❌ Easy to forget `__repr__` or `__eq__`
- ❌ Not idiomatic modern Python

**Verdict**: Rejected - unnecessary boilerplate

---

### Alternative 4: Pydantic Models

**Approach**:
```python
from pydantic import BaseModel

class Message(BaseModel):
    role: Role
    content: str
```

**Pros**:
- ✅ Runtime validation
- ✅ Automatic serialization
- ✅ JSON schema generation
- ✅ Data conversion

**Cons**:
- ❌ Extra dependency (`pydantic`)
- ❌ Overkill for simple models
- ❌ Validation overhead (runtime cost)
- ❌ More complex than needed for learning

**Verdict**: Rejected - unnecessary complexity and dependencies

---

### Alternative 5: attrs Library

**Approach**:
```python
import attr

@attr.s(auto_attribs=True)
class Message:
    role: Role
    content: str
```

**Pros**:
- ✅ Similar to dataclasses
- ✅ More features (validators, converters)
- ✅ Mature library

**Cons**:
- ❌ External dependency
- ❌ Dataclasses now standard
- ❌ No significant advantage for this use case
- ❌ Less familiar to students

**Verdict**: Rejected - standard library preference

## Implementation Notes

### StrEnum Usage

Python 3.11 introduced `StrEnum` which is perfect for `Role`:

```python
from enum import StrEnum

class Role(StrEnum):
    SYSTEM = "system"
    USER = "user"
    AI = "assistant"  # Maps to "assistant" for API
```

**Benefits**:
- `.value` returns string automatically
- Type-safe enumeration
- Auto-completion in IDE
- Prevents typos

**Alternative considered**: Plain string constants
```python
ROLE_SYSTEM = "system"
ROLE_USER = "user"
ROLE_AI = "assistant"
```
Rejected: No type safety, not enforced

### Default Factory Pattern

For mutable defaults (lists, dicts), use `default_factory`:

```python
from dataclasses import field

@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)
```

**Why**: Prevents shared mutable default bug:
```python
# WRONG - all instances share same list:
messages: list[Message] = []

# CORRECT - each instance gets new list:
messages: list[Message] = field(default_factory=list)
```

### Serialization Pattern

Add custom `to_dict()` method for API compatibility:

```python
def to_dict(self) -> dict[str, str]:
    return {
        "role": self.role.value,  # Enum to string
        "content": self.content
    }
```

**Why not `asdict()`**: Need to convert enum to string, not `Role` object.

## Success Criteria

Decision successful if:
- ✅ Models concise (<10 lines each)
- ✅ Type checking works in IDE
- ✅ No boilerplate `__init__` methods
- ✅ Students understand dataclass pattern
- ✅ Easy to add new fields

## Related Decisions

- Python 3.11+ requirement (enables StrEnum)
- No validation framework needed (simple project)

## References

- [PEP 557: Data Classes](https://peps.python.org/pep-0557/)
- [Python dataclasses documentation](https://docs.python.org/3/library/dataclasses.html)
- [PEP 663: Str Enum](https://peps.python.org/pep-0663/)

---

**Status**: This decision is **Accepted** and currently implemented.
