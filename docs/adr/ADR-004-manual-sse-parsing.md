# ADR-004: Manual SSE Parsing in CustomDialClient

**Status**: Accepted

**Date**: 2025-12-31

**Decision Makers**: Project Team

**Last Updated**: 2025-12-31

---

## Context

The DIAL API supports streaming responses via Server-Sent Events (SSE) protocol. CustomDialClient needs to parse SSE format to extract incremental content chunks.

### SSE Format

```
data: {"choices":[{"delta":{"content":"token"}}]}

data: {"choices":[{"delta":{"content":" next"}}]}

data: [DONE]
```

**Format Rules**:
- Each event: `data: <json>\n\n`
- Termination: `data: [DONE]`
- Empty lines separate events

### Options for Parsing

1. **Manual parsing** - Read lines, strip `data:` prefix, parse JSON
2. **SSE library** - Use `sseclient`, `aiohttp-sse-client`, or similar
3. **Streaming JSON parser** - Use `ijson` or similar
4. **Regex-based** - Extract JSON with regular expressions

### Requirements

- Parse SSE format correctly
- Extract `delta.content` from chunks
- Detect `[DONE]` termination
- Educational value (show protocol internals)
- Handle malformed chunks gracefully

## Decision

Implement **manual SSE parsing** in [CustomDialClient.stream_completion()](../../task/clients/custom_client.py):

```python
async for line in response.content:
    line_str = line.decode('utf-8').strip()
    
    if not line_str:
        continue  # Skip empty lines
    
    if line_str.startswith('data: '):
        data_content = line_str[6:]  # Remove "data: " prefix
        
        if data_content == '[DONE]':
            break  # End of stream
        
        try:
            chunk_json = json.loads(data_content)
            if 'choices' in chunk_json and len(chunk_json['choices']) > 0:
                delta = chunk_json['choices'][0].get('delta', {})
                if 'content' in delta:
                    content_chunk = delta['content']
                    print(content_chunk, end="", flush=True)
                    contents.append(content_chunk)
        except json.JSONDecodeError:
            continue  # Skip malformed chunks
```

## Consequences

### Positive ✅

1. **Educational Value**
   - Students see SSE protocol mechanics
   - Understand what libraries abstract
   - Learn parsing strategies
   - Debugging skills improved

2. **No Dependencies**
   - No SSE library needed
   - Uses only `json` (standard library)
   - Lighter dependency tree
   - Fewer version conflicts

3. **Full Control**
   - Can customize parsing logic
   - Easy to add logging
   - Handle edge cases explicitly
   - Clear error handling

4. **Transparency**
   - Every step visible
   - Easy to debug malformed responses
   - Students understand data flow
   - No "magic" happening

5. **Simplicity**
   - ~30 lines of straightforward code
   - No library API to learn
   - Standard Python patterns
   - Easy to modify

### Negative ⚠️

1. **Potential Bugs**
   - Manual parsing error-prone
   - Edge cases may be missed
   - No battle-tested implementation
   - Must handle encoding issues

2. **Code Complexity**
   - More code than using library
   - String manipulation required
   - JSON error handling needed
   - Multiple nested conditions

3. **Incomplete SSE Implementation**
   - No `event:` field handling
   - No `id:` field handling
   - No `retry:` field handling
   - (Not needed for DIAL API)

4. **Maintenance**
   - Must update if SSE format changes
   - More test cases needed
   - Library would auto-update
   - Custom code = custom maintenance

### Neutral ⚖️

1. **Performance**
   - Manual parsing likely faster (no library overhead)
   - Network latency dominates anyway
   - No practical difference

2. **Robustness**
   - Try/except handles malformed JSON
   - Skips empty lines
   - Continues on errors
   - Good enough for educational use

## Alternatives Considered

### Alternative 1: SSE Client Library

**Approach**: Use `sseclient-py` or `aiohttp-sse-client`

```python
from aiohttp_sse_client import client as sse_client

async with sse_client.EventSource(url, headers=headers, json=data) as event_source:
    async for event in event_source:
        chunk = json.loads(event.data)
        # ... extract content
```

**Pros**:
- ✅ Battle-tested implementation
- ✅ Handles all SSE fields
- ✅ Robust error handling
- ✅ Standard interface

**Cons**:
- ❌ Extra dependency
- ❌ Hides protocol details (bad for learning)
- ❌ Library-specific API to learn
- ❌ Potential version conflicts
- ❌ Overkill for simple use case

**Verdict**: Rejected - reduces educational value

---

### Alternative 2: Regex-Based Parsing

**Approach**:
```python
import re

pattern = r'data: (.+)\n\n'
matches = re.findall(pattern, response_text)
for match in matches:
    if match == '[DONE]':
        break
    chunk = json.loads(match)
```

**Pros**:
- ✅ Concise
- ✅ Pattern matching power

**Cons**:
- ❌ Requires buffering entire response
- ❌ Regex harder to understand than string operations
- ❌ Less efficient for streaming
- ❌ Regex overkill for simple format

**Verdict**: Rejected - worse than line-by-line parsing

---

### Alternative 3: Streaming JSON Parser (ijson)

**Approach**: Use `ijson` to parse JSON incrementally

**Pros**:
- ✅ Handles large JSON objects
- ✅ Memory efficient

**Cons**:
- ❌ Still need to strip `data:` prefix
- ❌ Extra dependency
- ❌ Complex API for simple task
- ❌ SSE is line-based, not JSON streaming

**Verdict**: Rejected - wrong tool for the job

---

### Alternative 4: Use DialClient SDK for Streaming

**Approach**: Only use `AsyncDial` from `aidial-client`, eliminate CustomDialClient streaming

**Pros**:
- ✅ No SSE parsing needed
- ✅ Simpler codebase

**Cons**:
- ❌ Loses educational value of showing protocol
- ❌ No debugging visibility for streaming
- ❌ Defeats purpose of CustomDialClient
- ❌ Violates dual-implementation decision ([ADR-001](./ADR-001-dual-client-implementation.md))

**Verdict**: Rejected - conflicts with architectural goals

## Implementation Notes

### Line-by-Line Iteration

```python
async for line in response.content:
```

`response.content` is `aiohttp.StreamReader` which yields chunks of bytes. Each chunk may contain multiple lines or partial lines. The implementation assumes complete lines per iteration, which works in practice for SSE.

**Potential Issue**: Line splitting across chunks

**Current Mitigation**: DIAL API sends complete `data:` lines in practice

**Future Enhancement**: Buffer partial lines:
```python
buffer = ""
async for chunk in response.content:
    buffer += chunk.decode('utf-8')
    lines = buffer.split('\n')
    buffer = lines[-1]  # Keep incomplete line
    for line in lines[:-1]:
        # Process complete line
```

### Error Handling Strategy

```python
try:
    chunk_json = json.loads(data_content)
except json.JSONDecodeError:
    continue  # Skip malformed chunks
```

**Philosophy**: Best-effort parsing
- Don't crash on malformed data
- Skip bad chunks, continue streaming
- User still gets most of response
- Logged if needed (could add logging)

### Encoding Assumptions

```python
line_str = line.decode('utf-8').strip()
```

Assumes UTF-8 encoding (standard for HTTP/JSON). DIAL API always uses UTF-8.

**Edge Case**: Emoji/Unicode handling
- UTF-8 decode handles correctly
- Emoji may span multiple tokens
- Displayed correctly with `flush=True`

### `[DONE]` Detection

```python
if data_content == '[DONE]':
    break
```

**Why not JSON parse**: `[DONE]` is literal string, not JSON array. Parsing would fail.

**Alternative formats not handled**:
- `data: {"done": true}` (some APIs use this)
- Just closing connection (no explicit marker)

DIAL API consistently uses `data: [DONE]`.

## Testing Strategy

### Manual Testing

Run with CustomDialClient and verify:
1. Streaming output appears incrementally
2. Complete response assembled correctly
3. No crashes on malformed data
4. `[DONE]` terminates properly

### Debug Logging

Add temporary logging to verify parsing:
```python
print(f"\nDEBUG: Raw line: {line_str}")
print(f"DEBUG: Data content: {data_content}")
print(f"DEBUG: Parsed chunk: {chunk_json}")
```

### Comparison Testing

Run same query with:
1. CustomDialClient (manual SSE parsing)
2. DialClient (SDK SSE handling)

Results should match exactly.

## Success Criteria

Decision successful if:
- ✅ Streaming works correctly with DIAL API
- ✅ Students understand SSE format after reading code
- ✅ No external SSE dependencies required
- ✅ Error handling prevents crashes
- ✅ Code remains maintainable (~30 lines)

## Related Decisions

- [ADR-001](./ADR-001-dual-client-implementation.md): CustomDialClient purpose
- [Architecture: Streaming Flow](../architecture.md#streaming-request-flow)

## References

- [SSE Specification](https://html.spec.whatwg.org/multipage/server-sent-events.html)
- [MDN: Server-Sent Events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [DIAL API Documentation](https://ai-proxy.lab.epam.com/docs) (internal)

---

**Status**: This decision is **Accepted** and currently implemented.

**Note**: If DIAL API changes SSE format significantly, may need to reconsider library usage.
