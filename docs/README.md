---
title: DIAL AI Chat Completions - Documentation
description: Educational Python project for learning DIAL API integration with synchronous and streaming chat completions
version: 1.0.0
last_updated: 2025-12-31
related: [architecture.md, setup.md, api.md]
tags: [python, dial, llm, streaming, educational]
---

# DIAL AI Chat Completions

A hands-on educational project for learning how to integrate with EPAM's DIAL (Distributed Infrastructure for AI Labs) API. This command-line chat application demonstrates both synchronous and streaming LLM completions with two different implementation approaches.

## Table of Contents

- [Project Overview](#project-overview)
- [Key Features](#key-features)
- [Quick Start](#quick-start)
- [Learning Objectives](#learning-objectives)
- [Project Structure](#project-structure)
- [Documentation Map](#documentation-map)
- [Getting Help](#getting-help)

## Project Overview

This project is designed as a learning exercise to demystify LLM API integration. It provides:
- **Two client implementations**: High-level SDK wrapper vs. raw HTTP requests
- **Streaming support**: Real-time token-by-token response display
- **Conversation management**: Stateful message history handling
- **Production patterns**: Error handling, logging, environment configuration

**Target Audience**: Python developers learning LLM API integration, EPAM employees using DIAL services

**Technology Stack**: Python 3.11+, `aidial-client`, `requests`, `aiohttp`

## Key Features

### Dual Client Architecture
- **DialClient** ([client.py](../task/clients/client.py)) - Uses official `aidial-client` library
- **CustomDialClient** ([custom_client.py](../task/clients/custom_client.py)) - Raw HTTP with detailed logging

### Streaming & Synchronous Modes
- **Synchronous**: Complete response returned at once
- **Streaming**: Server-Sent Events (SSE) with incremental token display

### Conversation State Management
- Persistent message history with UUID tracking
- System prompt configuration
- Error rollback on failed requests

## Quick Start

### Prerequisites
```bash
# Python 3.11 or higher
python --version

# EPAM VPN connection (required for API access)
# API key from https://support.epam.com/ess?id=sc_cat_item&table=sc_cat_item&sys_id=910603f1c3789e907509583bb001310c
```

### Installation
```bash
# Clone and navigate to project
cd ai-dial-chat-completions

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
```bash
# Set API key (required)
export DIAL_API_KEY='your-api-key-here'

# Verify available models
curl -H "api-key: $DIAL_API_KEY" https://ai-proxy.lab.epam.com/openai/models
```

Update deployment name in [task/app.py](../task/app.py):
```python
deployment_name = "gpt-4"  # Replace with actual model name
```

### Run Application
```bash
# Start chat (streaming mode by default)
python -m task.app

# Example interaction:
# Enter system prompt (or press Enter to use default):
# > You are a helpful Python tutor
# 
# You: What is a dataclass?
# Assistant: [streaming response...]
```

## Learning Objectives

By completing this project, you will understand:

1. **LLM API Fundamentals**
   - `/chat/completions` endpoint structure
   - Request/response payload format
   - Role-based message system

2. **Streaming Protocols**
   - Server-Sent Events (SSE) parsing
   - Async/await patterns in Python
   - Incremental response handling

3. **Client Design Patterns**
   - Abstraction via base classes
   - SDK wrapper vs. direct HTTP
   - Synchronous vs. asynchronous APIs

4. **Production Best Practices**
   - Environment-based configuration
   - Error handling and rollback strategies
   - Request/response logging

## Project Structure

```
ai-dial-chat-completions/
├── task/
│   ├── app.py                    # Main application entry point
│   ├── constants.py               # Configuration and environment variables
│   ├── clients/
│   │   ├── base.py               # Abstract base client
│   │   ├── client.py             # aidial-client implementation
│   │   └── custom_client.py      # Raw HTTP implementation
│   └── models/
│       ├── conversation.py       # Message history manager
│       ├── message.py            # Message data model
│       └── role.py               # Role enumeration
├── docs/                          # This documentation
├── requirements.txt               # Python dependencies
└── dial-basics.postman_collection.json  # API examples
```

## Documentation Map

- **[Architecture](./architecture.md)** - System design, data flow, component interactions, diagrams
- **[Setup Guide](./setup.md)** - Detailed environment configuration, troubleshooting
- **[API Reference](./api.md)** - Public interfaces, classes, methods, DIAL endpoints
- **[Testing Guide](./testing.md)** - Manual testing approach, debugging strategies
- **[Glossary](./glossary.md)** - Domain terms, abbreviations, concepts
- **[ADR Index](./adr/)** - Architecture Decision Records

## Getting Help

### Common Issues
- **"API key cannot be null or empty"**: Set `DIAL_API_KEY` environment variable
- **HTTP 401**: Verify API key and VPN connection
- **Import errors**: Ensure virtual environment is activated and dependencies installed
- **No streaming output**: Check `flush=True` in print statements

### Resources
- [DIAL API Documentation](https://ai-proxy.lab.epam.com/docs)
- [Available Models](https://ai-proxy.lab.epam.com/openai/models)
- [API Key Request](https://support.epam.com/ess?id=sc_cat_item&table=sc_cat_item&sys_id=910603f1c3789e907509583bb001310c)

### Contact
TODO: Add maintainer contact information or repository issue tracker

---

**Next Steps**: Review [Architecture](./architecture.md) for system design details, then follow [Setup Guide](./setup.md) for detailed installation.
