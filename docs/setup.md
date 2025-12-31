---
title: Setup Guide
description: Detailed environment configuration, installation, troubleshooting, and deployment instructions
version: 1.0.0
last_updated: 2025-12-31
related: [README.md, testing.md]
tags: [setup, installation, configuration, troubleshooting]
---

# Setup Guide

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)
- [IDE Configuration](#ide-configuration)

## Prerequisites

### System Requirements

- **Python**: 3.11 or higher
- **Operating System**: macOS, Linux, or Windows with WSL
- **Network**: EPAM VPN connection (required for API access)
- **Memory**: 100MB+ available
- **Disk Space**: ~50MB for dependencies

### Verify Python Version

```bash
python --version
# Expected output: Python 3.11.x or higher

# If python3 is used instead of python:
python3 --version
```

If Python 3.11+ is not installed:

**macOS** (via Homebrew):
```bash
brew install python@3.11
```

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip
```

**Windows**:
Download from [python.org](https://www.python.org/downloads/) or use Microsoft Store.

### EPAM VPN Connection

The DIAL API endpoint (`ai-proxy.lab.epam.com`) is only accessible within EPAM's internal network.

**Setup**:
1. Install EPAM VPN client (Cisco AnyConnect or GlobalProtect)
2. Connect to EPAM VPN
3. Verify connectivity:
```bash
ping ai-proxy.lab.epam.com
# Should receive responses if connected
```

**Verify API Access**:
```bash
curl https://ai-proxy.lab.epam.com/openai/models
# Should return JSON (even without API key, endpoint is reachable)
```

### API Key Acquisition

1. **Access EPAM Support Portal**:
   - URL: https://support.epam.com/ess
   - Navigate to: Service Catalog → AI/ML Services → DIAL API Access
   - Direct link: https://support.epam.com/ess?id=sc_cat_item&table=sc_cat_item&sys_id=910603f1c3789e907509583bb001310c

2. **Request Process**:
   - Fill out service request form
   - Provide justification (e.g., "Learning DIAL API integration")
   - Submit request

3. **Receive API Key**:
   - Key delivered via email (typically within 1-2 business days)
   - Format: Long alphanumeric string
   - Keep secure - do not commit to version control

## Installation

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd ai-dial-chat-completions
```

### Step 2: Create Virtual Environment

**Why**: Isolates project dependencies from system Python packages.

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate

# Windows (Command Prompt):
.venv\Scripts\activate.bat

# Windows (PowerShell):
.venv\Scripts\Activate.ps1
```

**Verify Activation**:
```bash
which python
# Should show: /path/to/ai-dial-chat-completions/.venv/bin/python

python --version
# Should show Python 3.11+
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Expected Output**:
```
Collecting requests==2.28.0
Collecting aiohttp==3.13.2
Collecting aidial-client==0.3.0
...
Successfully installed aiohttp-3.13.2 aidial-client-0.3.0 requests-2.28.0 ...
```

**Verify Installation**:
```bash
pip list
# Should show:
# aiohttp         3.13.2
# aidial-client   0.3.0
# requests        2.28.0
```

## Configuration

### Environment Variables

#### Set API Key (Required)

**macOS/Linux** (temporary - current session only):
```bash
export DIAL_API_KEY='your-api-key-here'
```

**macOS/Linux** (persistent - add to shell profile):
```bash
# For bash:
echo 'export DIAL_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# For zsh (macOS default):
echo 'export DIAL_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (Command Prompt)**:
```cmd
set DIAL_API_KEY=your-api-key-here
```

**Windows (PowerShell)**:
```powershell
$env:DIAL_API_KEY="your-api-key-here"
```

**Verify**:
```bash
echo $DIAL_API_KEY  # macOS/Linux
echo %DIAL_API_KEY%  # Windows CMD
echo $env:DIAL_API_KEY  # Windows PowerShell
```

#### Alternative: `.env` File (Optional)

While not currently supported by the code, you can modify `constants.py` to load from `.env`:

Create `.env` file:
```bash
DIAL_API_KEY=your-api-key-here
```

Update `task/constants.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('DIAL_API_KEY', '')
```

Install `python-dotenv`:
```bash
pip install python-dotenv
```

### Update Deployment Name

The default `"gpt-4"` in `task/app.py` is a placeholder.

**Step 1**: List available models:
```bash
curl -H "api-key: $DIAL_API_KEY" https://ai-proxy.lab.epam.com/openai/models | python -m json.tool
```

**Example Response**:
```json
{
  "data": [
    {"id": "gpt-4o", "object": "model"},
    {"id": "gpt-4o-mini", "object": "model"},
    {"id": "gpt-35-turbo", "object": "model"}
  ]
}
```

**Step 2**: Update [task/app.py](../task/app.py):
```python
# Change this line (around line 11):
deployment_name = "gpt-4"

# To actual model name:
deployment_name = "gpt-4o"
```

## Running the Application

### Standard Execution

```bash
python -m task.app
```

**Expected Interaction**:
```
Enter system prompt (or press Enter to use default):
> You are a Python expert

System prompt set: You are a Python expert

Chat started. Type 'exit' to quit.

You: What is a dataclass?
Assistant: [streaming response appears here...]
```

### Streaming vs. Non-Streaming

Controlled in [task/app.py](../task/app.py) at the bottom:

**Streaming Mode** (default):
```python
if __name__ == "__main__":
    asyncio.run(start(True))  # True = streaming
```

**Non-Streaming Mode**:
```python
if __name__ == "__main__":
    asyncio.run(start(False))  # False = complete response at once
```

### Client Selection

Switch between implementations by editing [task/app.py](../task/app.py):

**SDK Client** (default, cleaner output):
```python
client = DialClient(deployment_name)
# client = CustomDialClient(deployment_name)  # Commented out
```

**Custom Client** (verbose logging for debugging):
```python
# client = DialClient(deployment_name)  # Commented out
client = CustomDialClient(deployment_name)
```

## Development Setup

### Editor Configuration

#### VS Code

**Recommended Extensions**:
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "ms-python.black-formatter"
  ]
}
```

**Python Interpreter**:
1. Press `Cmd+Shift+P` (macOS) or `Ctrl+Shift+P` (Windows/Linux)
2. Select "Python: Select Interpreter"
3. Choose `.venv/bin/python`

**Launch Configuration** (`.vscode/launch.json`):
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: task.app",
      "type": "python",
      "request": "launch",
      "module": "task.app",
      "console": "integratedTerminal",
      "env": {
        "DIAL_API_KEY": "${env:DIAL_API_KEY}"
      }
    }
  ]
}
```

#### PyCharm

1. **Interpreter**: Settings → Project → Python Interpreter → Add → Existing Environment → `.venv/bin/python`
2. **Run Configuration**:
   - Script path: (leave empty)
   - Module name: `task.app`
   - Environment variables: `DIAL_API_KEY=your-key`

### Code Style (Optional)

Install development tools:
```bash
pip install black isort mypy
```

**Format code**:
```bash
black task/
isort task/
```

**Type checking**:
```bash
mypy task/
```

## Troubleshooting

### API Key Issues

#### Error: "API key cannot be null or empty"

**Cause**: `DIAL_API_KEY` environment variable not set

**Solution**:
```bash
export DIAL_API_KEY='your-key'
python -m task.app
```

**Verify**:
```bash
python -c "import os; print(os.getenv('DIAL_API_KEY', 'NOT SET'))"
```

#### Error: HTTP 401 Unauthorized

**Cause**: Invalid API key or not connected to VPN

**Solutions**:
1. Verify VPN connection: `ping ai-proxy.lab.epam.com`
2. Check API key format (no quotes, spaces, or newlines)
3. Request new key if expired

### Network Issues

#### Error: "Connection refused" or "Name or service not known"

**Cause**: Not connected to EPAM VPN

**Solution**:
1. Connect to EPAM VPN
2. Verify: `curl https://ai-proxy.lab.epam.com/openai/models`

#### Error: Timeout / No response

**Possible Causes**:
- VPN disconnected
- Firewall blocking requests
- API service down

**Solutions**:
1. Reconnect VPN
2. Check corporate firewall settings
3. Verify service status with EPAM IT support

### Python Environment Issues

#### Error: Module not found

**Example**: `ModuleNotFoundError: No module named 'aidial_client'`

**Cause**: Virtual environment not activated or dependencies not installed

**Solution**:
```bash
source .venv/bin/activate  # Activate venv
pip install -r requirements.txt
```

#### Error: Wrong Python version

**Example**: `SyntaxError: invalid syntax` (on StrEnum usage)

**Cause**: Python < 3.11

**Solution**: Install Python 3.11+ and recreate venv:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Runtime Issues

#### No streaming output visible

**Cause**: Missing `flush=True` in print statements

**Solution**: Ensure client implementation uses:
```python
print(content_chunk, end="", flush=True)
```

#### Error: "No choices in response found"

**Cause**: Invalid model name or API error

**Solutions**:
1. Verify deployment name matches available models
2. Check CustomDialClient logs for actual API response
3. Try different model

### Import Issues

#### Error: Duplicate DialClient names

**Cause**: Both `client.py` and `custom_client.py` define `DialClient` class

**Solution**: Use import aliases:
```python
from task.clients.client import DialClient
from task.clients.custom_client import DialClient as CustomDialClient
```

## IDE Configuration

### VS Code Settings (`.vscode/settings.json`)

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.mypyEnabled": true,
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.organizeImports": true
    }
  }
}
```

### PyCharm Settings

**Code Style**:
- File → Settings → Editor → Code Style → Python
- Set line length: 120
- Enable: Import optimization on save

**Run Configuration Template**:
- Run → Edit Configurations → Templates → Python
- Working directory: Project root
- Add environment variable: `DIAL_API_KEY`

---

**Next Steps**: See [Testing Guide](./testing.md) for debugging strategies or [API Reference](./api.md) for interface details.
