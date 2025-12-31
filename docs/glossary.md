---
title: Glossary
description: Domain terms, abbreviations, and concepts used in DIAL AI Chat Completions project
version: 1.0.0
last_updated: 2025-12-31
related: [README.md, architecture.md]
tags: [glossary, terminology, definitions]
---

# Glossary

## A

### Async/Await
Python asynchronous programming pattern. Functions marked `async def` return coroutines that must be `await`ed. Used in streaming implementations for non-blocking I/O.

**Example**:
```python
async def stream_completion(messages):
    async for chunk in response:
        await process(chunk)
```

### AsyncDial
Asynchronous client class from `aidial-client` library. Supports streaming responses with `async for` iteration.

---

## B

### BaseClient
Abstract base class defining the contract for all client implementations. Enforces `get_completion()` and `stream_completion()` methods.

**Location**: [task/clients/base.py](../task/clients/base.py)

---

## C

### Chat Completion
API operation that generates AI responses to conversation messages. Takes message history, returns assistant response.

**Endpoint**: `POST /openai/deployments/{model}/chat/completions`

### Chunk
Single incremental piece of streaming response. Contains partial content (e.g., one token or word) sent via SSE.

**Structure**:
```json
{
  "choices": [{
    "delta": {"content": "token"}
  }]
}
```

### Conversation
Stateful object maintaining message history. Includes system prompt, user inputs, and AI responses in chronological order.

**Class**: [task/models/conversation.py](../task/models/conversation.py)

### CustomDialClient
Low-level HTTP client implementation using `requests` and `aiohttp`. Includes verbose request/response logging for debugging.

**Location**: [task/clients/custom_client.py](../task/clients/custom_client.py)

---

## D

### Dataclass
Python decorator (`@dataclass`) providing automatic `__init__`, `__repr__`, and `__eq__` methods. Used for all model classes.

**Usage**:
```python
from dataclasses import dataclass

@dataclass
class Message:
    role: Role
    content: str
```

### Delta
Incremental change in streaming response. Contains `content` field with partial text. Part of SSE chunk structure.

### Deployment Name
Model identifier in DIAL API. Examples: `gpt-4o`, `gpt-35-turbo`, `gpt-4o-mini`.

**Configuration**: Set in [task/app.py](../task/app.py)

### DIAL
**Distributed Infrastructure for AI Labs** - EPAM's internal LLM API service. Provides standardized access to various AI models.

**Base URL**: `https://ai-proxy.lab.epam.com`

### DialClient
High-level SDK client implementation using `aidial-client` library. Minimal code, clean output.

**Location**: [task/clients/client.py](../task/clients/client.py)

---

## E

### EPAM VPN
Virtual Private Network required to access DIAL API. API endpoint only reachable from EPAM internal network.

**Required**: Yes, for all API calls

---

## F

### Flush
Python I/O operation forcing immediate output to console. Required for streaming to display tokens incrementally.

**Usage**: `print(token, end="", flush=True)`

---

## L

### LLM
**Large Language Model** - AI model trained on text data to generate human-like responses. Examples: GPT-4, GPT-3.5.

---

## M

### Message
Data structure representing single conversation entry. Contains `role` (system/user/assistant) and `content` (text).

**Class**: [task/models/message.py](../task/models/message.py)

---

## R

### Role
Enumeration of message sender types in chat completion:
- **system**: Instructions/context for AI behavior
- **user**: Human input
- **assistant**: AI-generated response (note: enum value is `AI`)

**Enum**: [task/models/role.py](../task/models/role.py)

### Rollback
Error recovery pattern. When API call fails, removes last user message from conversation history.

**Location**: [task/app.py](../task/app.py) exception handler

---

## S

### SSE (Server-Sent Events)
HTTP protocol for server-to-client streaming. Text-based format with `data:` prefix per line.

**Format**:
```
data: {"chunk": "content"}

data: [DONE]
```

### Streaming
Response delivery mode where content arrives incrementally (token-by-token) instead of all at once. Provides real-time feedback.

**Control**: `stream=True` parameter in API request

### StrEnum
Python 3.11+ enum type where values are strings. Used for `Role` to match API requirements.

**Definition**:
```python
from enum import StrEnum

class Role(StrEnum):
    USER = "user"  # .value returns "user"
```

### System Prompt
Initial message defining AI behavior. Sets tone, constraints, and persona for conversation.

**Example**: `"You are a Python expert who provides concise explanations."`

---

## T

### Token
Smallest unit of text processed by LLM. Roughly ¾ of a word on average. Streaming delivers one or more tokens per chunk.

**Examples**:
- "Hello" = 1 token
- "Hello, world!" ≈ 4 tokens
- "dataclass" = 2-3 tokens (model-dependent)

### Turn
Single request-response cycle in conversation. Consists of user message and AI response.

**Example**: User asks question (turn 1), AI answers (turn 1 complete).

---

## V

### Virtual Environment (venv)
Isolated Python environment with independent package installations. Prevents conflicts with system Python.

**Creation**: `python -m venv .venv`
**Activation**: `source .venv/bin/activate`

---

## Acronyms Quick Reference

| Acronym | Full Term | Definition |
|---------|-----------|------------|
| **DIAL** | Distributed Infrastructure for AI Labs | EPAM's LLM API service |
| **LLM** | Large Language Model | AI trained on text generation |
| **SSE** | Server-Sent Events | HTTP streaming protocol |
| **API** | Application Programming Interface | Service communication interface |
| **SDK** | Software Development Kit | Pre-built client library |
| **HTTP** | Hypertext Transfer Protocol | Web communication standard |
| **JSON** | JavaScript Object Notation | Data interchange format |
| **VPN** | Virtual Private Network | Secure network tunnel |
| **UUID** | Universally Unique Identifier | 128-bit unique ID |
| **CLI** | Command-Line Interface | Text-based user interface |

---

## Common Phrases

### "Deployment Name"
Refers to the model identifier required in API calls. Must be updated from placeholder `"gpt-4"` to actual model.

### "Flush the Stream"
Force immediate console output in streaming mode using `flush=True`.

### "Message History"
Ordered list of all messages in conversation. Sent with each API request for context.

### "Rollback on Error"
Remove last user message from history when API call fails, preventing state corruption.

### "SDK vs Raw HTTP"
Comparison of high-level library (`DialClient`) versus manual HTTP requests (`CustomDialClient`).

---

## Related Resources

- **DIAL API Documentation**: https://ai-proxy.lab.epam.com/docs
- **Python Dataclasses**: https://docs.python.org/3/library/dataclasses.html
- **Async/Await Guide**: https://docs.python.org/3/library/asyncio.html
- **SSE Specification**: https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events

---

**Next**: Return to [README](./README.md) for navigation or see [Architecture](./architecture.md) for system design.
