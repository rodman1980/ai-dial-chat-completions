# ADR-001: Dual Client Implementation Strategy

**Status**: Accepted

**Date**: 2025-12-31

**Decision Makers**: Project Team

**Last Updated**: 2025-12-31

---

## Context

This project is designed as an educational tool for learning DIAL API integration. Students need to understand:
1. How to use SDK libraries for production code
2. The underlying HTTP protocols that SDKs abstract
3. Request/response structures for debugging

A single implementation approach would either:
- Hide protocol details (SDK only) - easier but less educational
- Require manual HTTP everywhere (HTTP only) - more complex, production-inappropriate

## Decision

Implement **two parallel client implementations** sharing a common abstract interface:

1. **DialClient** ([client.py](../../task/clients/client.py))
   - Uses `aidial-client` SDK library
   - High-level abstraction with `Dial` and `AsyncDial`
   - Minimal code (~50 lines)
   - Clean console output (no request logging)
   - Recommended for production patterns

2. **CustomDialClient** ([custom_client.py](../../task/clients/custom_client.py))
   - Uses `requests` and `aiohttp` directly
   - Manual HTTP request construction
   - Verbose request/response logging
   - Manual SSE parsing (~140 lines)
   - Recommended for learning/debugging

**Common Interface**: [BaseClient](../../task/clients/base.py)
```python
class BaseClient(ABC):
    @abstractmethod
    def get_completion(messages: list[Message]) -> Message
    
    @abstractmethod
    async def stream_completion(messages: list[Message]) -> Message
```

## Consequences

### Positive ✅

1. **Educational Value**
   - Students see abstraction benefits firsthand
   - Can compare SDK vs. raw HTTP side-by-side
   - Learning path: try SDK, then understand internals with HTTP

2. **Debugging Flexibility**
   - CustomDialClient exposes full request/response payloads
   - Easy to diagnose API issues
   - Students learn what "magic" libraries actually do

3. **Production Patterns**
   - Demonstrates interface-based design
   - Shows strategy pattern implementation
   - Teaches abstraction through composition

4. **Runtime Switching**
   - Change implementations with single line
   - No application code changes needed
   - Easy A/B testing

### Negative ⚠️

1. **Duplicate Class Names**
   - Both classes named `DialClient`
   - Requires import aliases: `from ... import DialClient as CustomDialClient`
   - Can confuse beginners

2. **Maintenance Overhead**
   - Two implementations to keep in sync
   - API changes require updating both
   - More code to review

3. **Increased Complexity**
   - More files to navigate
   - Students must understand which to use when
   - Documentation burden higher

4. **Testing Complexity**
   - Must validate both implementations
   - Ensures consistent behavior
   - Manual testing required for both paths

### Neutral ⚖️

1. **Dependency Count**
   - Requires both `aidial-client` and `requests`/`aiohttp`
   - Total: 3 HTTP-related libraries
   - Acceptable for learning project

2. **Performance**
   - No significant difference in practice
   - Network latency dominates
   - SDK overhead negligible

## Alternatives Considered

### Alternative 1: SDK Only

**Approach**: Use `aidial-client` exclusively

**Pros**:
- ✅ Simpler codebase (half the code)
- ✅ Single implementation to maintain
- ✅ Production-appropriate pattern

**Cons**:
- ❌ Students don't learn underlying protocols
- ❌ Debugging harder (no request inspection)
- ❌ "Black box" effect - less educational
- ❌ Doesn't teach abstraction benefits

**Verdict**: Rejected - insufficient educational value

---

### Alternative 2: HTTP Only

**Approach**: Use `requests`/`aiohttp` exclusively

**Pros**:
- ✅ Full protocol visibility
- ✅ Complete learning of HTTP details
- ✅ No "magic" - everything explicit

**Cons**:
- ❌ More code complexity
- ❌ Not production-appropriate
- ❌ Doesn't teach SDK usage patterns
- ❌ Verbose, harder to read

**Verdict**: Rejected - poor production patterns

---

### Alternative 3: Single Implementation with Debug Flag

**Approach**: One class with `debug=True` parameter for logging

**Pros**:
- ✅ Single codebase
- ✅ Optional logging
- ✅ No duplicate names

**Cons**:
- ❌ Still needs to choose SDK or HTTP
- ❌ Mixed concerns (logic + logging)
- ❌ Doesn't show abstraction patterns
- ❌ Debug code complicates production code

**Verdict**: Rejected - mixed concerns antipattern

---

### Alternative 4: Separate Branch per Implementation

**Approach**: `main` branch with SDK, `http-implementation` branch with raw HTTP

**Pros**:
- ✅ No duplicate code in single branch
- ✅ Clear separation

**Cons**:
- ❌ Can't compare side-by-side
- ❌ Students must switch branches
- ❌ No runtime switching
- ❌ Doesn't demonstrate interface design

**Verdict**: Rejected - poor learning experience

## Implementation Notes

### Switching Implementations

Application code ([app.py](../../task/app.py)) switches via commenting:

```python
# SDK implementation (default)
client = DialClient(deployment_name)

# HTTP implementation (for debugging)
# client = CustomDialClient(deployment_name)
```

**Future Enhancement**: Could use environment variable:
```python
use_sdk = os.getenv('USE_SDK_CLIENT', 'true').lower() == 'true'
client = DialClient(name) if use_sdk else CustomDialClient(name)
```

### Naming Conflict Resolution

Both classes named `DialClient` to:
1. Show they're interchangeable
2. Emphasize interface contract
3. Force learning of import aliases

Import pattern:
```python
from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
```

**Alternative naming considered**:
- `HttpDialClient` - implies SDK client isn't HTTP-based
- `VerboseDialClient` - doesn't convey implementation difference
- `ManualDialClient` - unclear meaning

## Success Criteria

Decision successful if:
- ✅ Students complete exercises with both clients
- ✅ Debugging insights improve with CustomDialClient
- ✅ SDK usage patterns understood via DialClient
- ✅ Both clients produce equivalent results
- ✅ Abstract interface pattern internalized

## Related Decisions

- [ADR-004](./ADR-004-manual-sse-parsing.md): Manual SSE parsing justification
- [Architecture: Client Architecture](../architecture.md#client-architecture): System design

## References

- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
- [Interface-Based Programming](https://en.wikipedia.org/wiki/Interface-based_programming)
- [aidial-client Documentation](https://pypi.org/project/aidial-client/)

---

**Status**: This decision is **Accepted** and currently implemented.
