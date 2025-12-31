# ADR-003: Ephemeral State Management

**Status**: Accepted

**Date**: 2025-12-31

**Decision Makers**: Project Team

**Last Updated**: 2025-12-31

---

## Context

The chat application maintains conversation history (system prompt + user/AI messages). State management options:

1. **In-memory only** - Lost on application exit
2. **File-based** - JSON/text files on disk
3. **Database** - SQLite, PostgreSQL, etc.
4. **Cloud storage** - S3, cloud database
5. **Session management** - Web framework sessions

### Requirements

- Educational project (not production)
- Simple implementation for learning
- Focus on API integration, not data persistence
- Single-user command-line application
- Clear start/stop boundaries

### Non-Requirements

- Multi-user support
- Conversation resumption
- History search/export
- Long-term storage
- Backup/recovery

## Decision

Implement **ephemeral (in-memory only) state management**:

- Conversation exists only during application runtime
- No persistence to disk or database
- `Conversation` object created at app start, destroyed at exit
- History lost when program terminates

### Implementation

```python
# task/app.py
async def start(stream: bool) -> None:
    # Create conversation (in-memory)
    conversation = Conversation()
    
    # Add messages
    conversation.add_message(system_message)
    
    # Loop until exit
    while True:
        # ... add messages to conversation
        # All state in 'conversation' object
        
    # Exit - conversation destroyed, history lost
```

No file I/O, no database connections, no serialization.

## Consequences

### Positive ✅

1. **Simplicity**
   - Zero persistence code
   - No file path management
   - No serialization/deserialization
   - ~50 fewer lines of code

2. **Clear Scope**
   - Obvious when history starts (app launch)
   - Obvious when history ends (app exit)
   - No confusion about "saved sessions"
   - Predictable behavior

3. **No Dependencies**
   - No database libraries
   - No file locking concerns
   - No disk space requirements
   - No backup strategy needed

4. **Educational Focus**
   - Students concentrate on API integration
   - Not distracted by persistence concerns
   - Shorter time to working prototype
   - Simpler debugging (no file corruption issues)

5. **Testing Simplicity**
   - No test data cleanup needed
   - No fixture files required
   - Fresh state every run
   - Reproducible behavior

6. **Security**
   - No sensitive data persisted to disk
   - No conversation logs to secure
   - API keys not written to files
   - Privacy by default

### Negative ⚠️

1. **No History Preservation**
   - Conversations lost on exit
   - Can't resume previous sessions
   - No conversation export
   - Accidental exit = data loss

2. **Limited Practical Use**
   - Not suitable for real-world scenarios
   - Can't share conversations
   - No conversation analysis possible
   - Must complete in single session

3. **No Undo Beyond Session**
   - Can't restore previous day's work
   - Testing long conversations tedious
   - Must recreate context each run

4. **Memory Constraints**
   - Very long conversations consume RAM
   - No pagination/truncation
   - Potential memory issues (rare in practice)

### Neutral ⚖️

1. **Educational Trade-off**
   - Simplicity vs. real-world patterns
   - Acceptable for learning exercise
   - Students can add persistence later

2. **Session Duration**
   - Typical learning sessions: 15-30 minutes
   - Memory sufficient for hundreds of messages
   - Not a practical limitation

## Alternatives Considered

### Alternative 1: JSON File Persistence

**Approach**:
```python
import json

def save_conversation(conv: Conversation, path: str):
    with open(path, 'w') as f:
        json.dump({
            'id': conv.id,
            'messages': [m.to_dict() for m in conv.messages]
        }, f)

def load_conversation(path: str) -> Conversation:
    with open(path, 'r') as f:
        data = json.load(f)
    conv = Conversation(id=data['id'])
    for msg in data['messages']:
        conv.add_message(Message(**msg))
    return conv
```

**Pros**:
- ✅ Human-readable format
- ✅ Easy to implement
- ✅ No dependencies
- ✅ Can resume sessions

**Cons**:
- ❌ +50 lines of code
- ❌ File path management
- ❌ Serialization errors possible
- ❌ When to save? (after each message? on exit?)
- ❌ File corruption handling needed
- ❌ Distracts from API learning

**Verdict**: Rejected - adds complexity without educational value

---

### Alternative 2: SQLite Database

**Approach**:
```python
import sqlite3

# Schema: conversations, messages tables
# CRUD operations for history management
```

**Pros**:
- ✅ Structured data storage
- ✅ Query capabilities
- ✅ Multi-conversation support
- ✅ Scalable

**Cons**:
- ❌ +200 lines of code
- ❌ Database schema design
- ❌ SQL knowledge required
- ❌ Migration management
- ❌ Major scope increase
- ❌ Overkill for single-user CLI

**Verdict**: Rejected - massive scope creep

---

### Alternative 3: Pickle Serialization

**Approach**:
```python
import pickle

with open('conversation.pkl', 'wb') as f:
    pickle.dump(conversation, f)
```

**Pros**:
- ✅ Simplest serialization (2 lines)
- ✅ No custom serialization code
- ✅ Preserves object structure

**Cons**:
- ❌ Binary format (not human-readable)
- ❌ Security concerns (don't unpickle untrusted data)
- ❌ Python version compatibility issues
- ❌ Still need file management
- ❌ Bad practice to teach (pickle security issues)

**Verdict**: Rejected - security concerns, bad educational example

---

### Alternative 4: Cloud Storage (S3/Database)

**Approach**: Store conversations in cloud service

**Pros**:
- ✅ Scalable
- ✅ Accessible from anywhere
- ✅ Backup built-in

**Cons**:
- ❌ Requires cloud account setup
- ❌ Network dependency for basic operation
- ❌ Cost considerations
- ❌ Authentication/credentials management
- ❌ Extreme overkill for learning project

**Verdict**: Rejected - absurdly overengineered

---

### Alternative 5: Optional Persistence Flag

**Approach**: Add `--save` command-line flag for optional persistence

```bash
python -m task.app --save conversation.json
```

**Pros**:
- ✅ Flexible: persistence when needed
- ✅ Default remains simple
- ✅ Best of both worlds

**Cons**:
- ❌ Still need to implement persistence
- ❌ Argument parsing added
- ❌ Two code paths to maintain
- ❌ Testing both modes required
- ❌ Documentation complexity

**Verdict**: Rejected - complicates "simple by default" goal

## Implementation Notes

### Memory Management

For very long conversations (100+ messages), could add truncation:

```python
MAX_HISTORY = 100

def add_message(self, message: Message):
    self.messages.append(message)
    if len(self.messages) > MAX_HISTORY:
        # Keep system prompt (first message)
        self.messages = [self.messages[0]] + self.messages[-MAX_HISTORY+1:]
```

**Current decision**: Not implemented - not needed for typical educational usage

### Future Enhancement Path

If persistence becomes needed:
1. Add `ConversationRepository` interface
2. Implement `InMemoryRepository` (current behavior)
3. Add `JsonFileRepository` (optional)
4. Dependency injection in `app.py`

This preserves current simplicity while allowing growth.

### Error Rollback

Ephemeral state enables simple error recovery:

```python
try:
    conversation.add_message(user_message)
    response = await client.stream_completion(conversation.get_messages())
    conversation.add_message(response)
except Exception as e:
    # Rollback: remove last message
    conversation.messages.pop()
```

No file rollback or transaction management needed.

## Success Criteria

Decision successful if:
- ✅ Students focus on API integration, not file I/O
- ✅ No persistence-related bugs reported
- ✅ Application remains simple to understand
- ✅ Typical sessions complete without memory issues
- ✅ Code remains under 150 lines total

## Related Decisions

- [ADR-002](./ADR-002-dataclass-for-models.md): Dataclass models enable easy serialization if persistence added later
- Error handling in [app.py](../../task/app.py): Rollback strategy relies on ephemeral state

## References

- [YAGNI Principle](https://en.wikipedia.org/wiki/You_aren%27t_gonna_need_it)
- [KISS Principle](https://en.wikipedia.org/wiki/KISS_principle)
- Educational software design: prioritize learning objectives over features

---

**Status**: This decision is **Accepted** and currently implemented.

**Note**: Can be revisited if project evolves beyond educational scope.
