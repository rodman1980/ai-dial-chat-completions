---
title: API Reference
description: Complete interface documentation for classes, methods, and DIAL API endpoints
version: 1.0.0
last_updated: 2025-12-31
related: [architecture.md, README.md]
tags: [api, reference, interfaces, endpoints]
---

# API Reference

## Table of Contents

- [Module Overview](#module-overview)
- [Application Layer](#application-layer)
- [Client Layer](#client-layer)
- [Data Models](#data-models)
- [Constants & Configuration](#constants--configuration)
- [DIAL API Endpoints](#dial-api-endpoints)
- [Type Reference](#type-reference)

## Module Overview

```
task/
├── app.py                 # Application entry point
├── constants.py           # Configuration values
├── clients/
│   ├── base.py           # Abstract client interface
│   ├── client.py         # SDK-based implementation
│   └── custom_client.py  # HTTP-based implementation
└── models/
    ├── conversation.py   # Conversation state manager
    ├── message.py        # Message data structure
    └── role.py           # Role enumeration
```

---

## Application Layer

### `task.app`

Main application module providing the command-line chat interface.

#### Functions

##### `start(stream: bool) -> None`

**Async coroutine** that runs the main chat loop.

**Parameters**:
- `stream` (bool): Enable streaming mode if `True`, synchronous completion if `False`

**Behavior**:
1. Initialize client (DialClient or CustomDialClient)
2. Create conversation and set system prompt
3. Loop:
   - Read user input
   - Exit on `"exit"` command
   - Add user message to conversation
   - Call appropriate completion method
   - Add assistant response to history
   - On error: rollback last user message

**Usage**:
```python
import asyncio
from task.app import start

# Run with streaming
asyncio.run(start(True))

# Run without streaming
asyncio.run(start(False))
```

**Error Handling**:
- Catches all exceptions during API calls
- Prints error message to console
- Pops last user message from conversation history
- Continues loop (does not exit)

**Environment Requirements**:
- `DIAL_API_KEY` must be set
- `deployment_name` must be updated with valid model

---

## Client Layer

### `task.clients.base`

#### `BaseClient` (Abstract Base Class)

Defines the contract all client implementations must follow.

**Abstract Methods**:

##### `get_completion(messages: list[Message]) -> Message`

Perform **synchronous** API request for chat completion.

**Parameters**:
- `messages` (list[Message]): Conversation history

**Returns**:
- `Message`: Assistant response with `Role.AI`

**Raises**:
- `Exception`: On API errors (status codes, empty responses, etc.)

**Must Implement**:
- Message format conversion
- HTTP request/response handling
- Error checking
- Content extraction
- Console output (prints response)

---

##### `stream_completion(messages: list[Message]) -> Message`

Perform **asynchronous streaming** API request for chat completion.

**Parameters**:
- `messages` (list[Message]): Conversation history

**Returns**:
- `Message`: Complete assistant response assembled from chunks

**Raises**:
- `Exception`: On API errors, connection issues, parse errors

**Must Implement**:
- Async HTTP request
- SSE stream parsing
- Incremental console output (print each token with `flush=True`)
- Content accumulation
- Stream termination detection

---

**Constructor**:

##### `__init__(deployment_name: str)`

**Parameters**:
- `deployment_name` (str): Model identifier (e.g., `"gpt-4o"`, `"gpt-35-turbo"`)

**Raises**:
- `ValueError`: If `API_KEY` is null or empty string

**Sets**:
- `self._api_key`: Retrieved from `constants.API_KEY`
- `self._deployment_name`: Stored for request construction

---

### `task.clients.client`

#### `DialClient(BaseClient)`

High-level client using the `aidial-client` SDK library.

**Constructor**:

##### `__init__(deployment_name: str)`

**Parameters**:
- `deployment_name` (str): Model name from DIAL API

**Initializes**:
- `self._client`: `Dial` instance for sync requests
- `self._async_client`: `AsyncDial` instance for streaming

**Configuration**:
```python
Dial(
    base_url=DIAL_ENDPOINT,  # "https://ai-proxy.lab.epam.com"
    api_key=self._api_key
)
```

---

**Methods**:

##### `get_completion(messages: list[Message]) -> Message`

Synchronous completion using `aidial-client`.

**Implementation**:
```python
messages_dict = [msg.to_dict() for msg in messages]
response = self._client.chat.completions.create(
    deployment_name=self._deployment_name,
    messages=messages_dict
)
content = response.choices[0].message.content
print(content)
return Message(role=Role.AI, content=content)
```

**Error Cases**:
- Raises `Exception` if `response.choices` is empty
- Propagates SDK exceptions (network, auth, etc.)

---

##### `stream_completion(messages: list[Message]) -> Message`

Asynchronous streaming completion.

**Implementation**:
```python
messages_dict = [msg.to_dict() for msg in messages]
response = await self._async_client.chat.completions.create(
    deployment_name=self._deployment_name,
    messages=messages_dict,
    stream=True
)

contents = []
async for chunk in response:
    if chunk.choices and chunk.choices[0].delta.content:
        content_chunk = chunk.choices[0].delta.content
        print(content_chunk, end="", flush=True)
        contents.append(content_chunk)

print()  # Newline after streaming
return Message(role=Role.AI, content="".join(contents))
```

**Streaming Details**:
- Checks `chunk.choices` before accessing (may be empty)
- Uses `delta.content` (not `message.content`)
- Prints incrementally with `flush=True`
- Returns assembled message after `[DONE]`

---

### `task.clients.custom_client`

#### `DialClient(BaseClient)`

Low-level client using raw HTTP libraries (`requests`, `aiohttp`).

**Note**: Class name is `DialClient` (same as SDK version) - use import aliases to distinguish.

**Constructor**:

##### `__init__(deployment_name: str)`

**Parameters**:
- `deployment_name` (str): Model name

**Initializes**:
- `self._endpoint`: Full URL path for completions endpoint

**Endpoint Construction**:
```python
self._endpoint = DIAL_ENDPOINT + f"/openai/deployments/{deployment_name}/chat/completions"
# Example: "https://ai-proxy.lab.epam.com/openai/deployments/gpt-4o/chat/completions"
```

---

**Methods**:

##### `get_completion(messages: list[Message]) -> Message`

Synchronous completion using `requests` library.

**Implementation**:
```python
headers = {
    "api-key": self._api_key,
    "Content-Type": "application/json"
}

request_data = {
    "messages": [msg.to_dict() for msg in messages]
}

response = requests.post(
    self._endpoint,
    headers=headers,
    json=request_data
)

if response.status_code != 200:
    raise Exception(f"HTTP {response.status_code}: {response.text}")

content = response.json()["choices"][0]["message"]["content"]
print(content)
return Message(role=Role.AI, content=content)
```

**Logging**:
- Prints full request (URL, headers, body) before sending
- Prints full response (status, JSON) after receiving
- Uses `json.dumps(indent=2)` for readable formatting

---

##### `stream_completion(messages: list[Message]) -> Message`

Asynchronous streaming using `aiohttp` with manual SSE parsing.

**Implementation**:
```python
headers = {
    "api-key": self._api_key,
    "Content-Type": "application/json"
}

request_data = {
    "stream": True,
    "messages": [msg.to_dict() for msg in messages]
}

contents = []
async with aiohttp.ClientSession() as session:
    async with session.post(self._endpoint, json=request_data, headers=headers) as response:
        async for line in response.content:
            line_str = line.decode('utf-8').strip()
            
            if not line_str:
                continue
            
            if line_str.startswith('data: '):
                data_content = line_str[6:]  # Remove "data: " prefix
                
                if data_content == '[DONE]':
                    break
                
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

print()
return Message(role=Role.AI, content="".join(contents))
```

**SSE Protocol**:
- Each line format: `data: {json}\n\n`
- Termination marker: `data: [DONE]`
- Skips empty lines and malformed JSON
- Handles missing `choices` or `delta` gracefully

---

## Data Models

### `task.models.message`

#### `Message` (Dataclass)

Represents a single message in the conversation.

**Fields**:
- `role` (Role): Message sender role
- `content` (str): Message text

**Methods**:

##### `to_dict() -> dict[str, str]`

Convert to DIAL API format.

**Returns**:
```python
{
    "role": self.role.value,  # "system", "user", or "assistant"
    "content": self.content
}
```

**Usage**:
```python
from task.models.message import Message
from task.models.role import Role

msg = Message(role=Role.USER, content="Hello")
api_format = msg.to_dict()
# {"role": "user", "content": "Hello"}
```

---

### `task.models.role`

#### `Role` (StrEnum)

Enumeration of message roles in chat completion API.

**Values**:
- `SYSTEM = "system"`: System instructions/context
- `USER = "user"`: User input messages
- `AI = "assistant"`: AI-generated responses

**Important**: `Role.AI` maps to string `"assistant"` (not `"ai"`).

**Usage**:
```python
from task.models.role import Role

role = Role.USER
assert role.value == "user"
assert Role.AI.value == "assistant"
```

---

### `task.models.conversation`

#### `Conversation` (Dataclass)

Manages conversation state and message history.

**Fields**:
- `id` (str): UUID generated at creation (default factory: `uuid.uuid4()`)
- `messages` (list[Message]): Ordered message history (default: empty list)

**Methods**:

##### `add_message(message: Message) -> None`

Append message to conversation history.

**Parameters**:
- `message` (Message): Message to add

**Side Effects**:
- Modifies `self.messages` in place

**Usage**:
```python
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

conv = Conversation()
conv.add_message(Message(role=Role.SYSTEM, content="You are helpful"))
conv.add_message(Message(role=Role.USER, content="Hi"))
```

---

##### `get_messages() -> list[Message]`

Retrieve all messages in conversation order.

**Returns**:
- `list[Message]`: Reference to internal message list (not a copy)

**Warning**: Returned list is mutable. Modifications affect conversation state.

---

## Constants & Configuration

### `task.constants`

Module-level configuration values.

#### `DEFAULT_SYSTEM_PROMPT: str`

Default system message content.

**Value**: `"You are an assistant who answers concisely and informatively."`

**Usage**: Fallback when user presses Enter without providing custom system prompt.

---

#### `DIAL_ENDPOINT: str`

Base URL for DIAL API.

**Value**: `"https://ai-proxy.lab.epam.com"`

**Network Requirements**:
- Requires EPAM VPN connection
- Internal EPAM network only

---

#### `API_KEY: str`

DIAL API authentication key.

**Source**: `os.getenv('DIAL_API_KEY', '')`

**Validation**: Empty string raises `ValueError` in `BaseClient.__init__`

**Security**:
- Never hardcoded
- Retrieved from environment at runtime
- Not logged or printed

---

## DIAL API Endpoints

### Base URL
```
https://ai-proxy.lab.epam.com
```

### Chat Completions

#### `POST /openai/deployments/{deployment_id}/chat/completions`

Create a chat completion (sync or streaming).

**Path Parameters**:
- `deployment_id` (string): Model identifier (e.g., `gpt-4o`, `gpt-35-turbo`)

**Headers**:
```
api-key: {your-api-key}
Content-Type: application/json
```

**Request Body** (JSON):
```json
{
  "messages": [
    {"role": "system", "content": "System prompt"},
    {"role": "user", "content": "User message"}
  ],
  "stream": false  // Optional: true for streaming
}
```

**Response (Non-Streaming)**:
```json
{
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "Response text"
      }
    }
  ]
}
```

**Response (Streaming)** - Server-Sent Events:
```
data: {"choices":[{"delta":{"content":"token"}}]}

data: {"choices":[{"delta":{"content":"next"}}]}

data: [DONE]
```

**Status Codes**:
- `200 OK`: Success
- `401 Unauthorized`: Invalid/missing API key
- `404 Not Found`: Invalid deployment name
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: API error

---

### List Models

#### `GET /openai/models`

Retrieve available models.

**Headers**:
```
api-key: {your-api-key}
```

**Response**:
```json
{
  "data": [
    {"id": "gpt-4o", "object": "model"},
    {"id": "gpt-35-turbo", "object": "model"}
  ]
}
```

**Usage**:
```bash
curl -H "api-key: $DIAL_API_KEY" https://ai-proxy.lab.epam.com/openai/models
```

---

## Type Reference

### Common Type Aliases

```python
# Message list for API calls
MessageList = list[Message]

# API response dictionary structure
APIResponse = dict[str, Any]

# Streaming chunk structure
StreamChunk = dict[str, Any]
```

### Import Paths

```python
# Application
from task.app import start

# Clients
from task.clients.base import BaseClient
from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient

# Models
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

# Constants
from task.constants import API_KEY, DIAL_ENDPOINT, DEFAULT_SYSTEM_PROMPT
```

---

## Usage Examples

### Basic Synchronous Chat

```python
from task.clients.client import DialClient
from task.models.message import Message
from task.models.role import Role

client = DialClient("gpt-4o")
messages = [
    Message(role=Role.SYSTEM, content="Be concise"),
    Message(role=Role.USER, content="What is Python?")
]

response = client.get_completion(messages)
print(response.content)
```

### Streaming Chat

```python
import asyncio
from task.clients.client import DialClient
from task.models.message import Message
from task.models.role import Role

async def chat():
    client = DialClient("gpt-4o")
    messages = [
        Message(role=Role.USER, content="Explain async/await")
    ]
    
    response = await client.stream_completion(messages)
    # Tokens printed incrementally during call
    print(f"\nFull response: {response.content}")

asyncio.run(chat())
```

### Conversation Management

```python
from task.models.conversation import Conversation
from task.models.message import Message
from task.models.role import Role

conv = Conversation()
conv.add_message(Message(role=Role.SYSTEM, content="Be helpful"))
conv.add_message(Message(role=Role.USER, content="Hi"))

messages = conv.get_messages()
# Use messages for API call
```

---

**Related**: See [Architecture](./architecture.md) for system design or [Setup](./setup.md) for configuration details.
