# AutoTest AI — Model Context Protocol (MCP) Server

[![smithery badge](https://smithery.ai/badge/autotest-mcp)](https://smithery.ai/server/autotest-mcp)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**AutoTest AI** is an industrial-grade defensive testing and refactoring engine embedded directly inside your IDE via the **Model Context Protocol (MCP)**. 

Compatible with **Cursor**, **Claude Desktop**, and **Windsurf**.

---

## ⚡ Features

- **`generate_edge_tests`**: Synthesizes production Pytest / Jest suites targeting mathematical bounds, zero-division, type mismatches, and fault handling with **96%+ branch coverage**.
- **`audit_code_defenses`**: Calculates cyclomatic complexity and audits unhandled exception vectors.
- **Zero-Friction**: Runs completely inside your editor without switching to external web tools.

---

## 🚀 Quickstart for Cursor & Claude Desktop

### 1. Cursor Installation (`.cursor/mcp.json`)

Add to your project's `.cursor/mcp.json` or global Cursor settings:

```json
{
  "mcpServers": {
    "autotest": {
      "command": "python",
      "args": ["mcp_server.py"]
    }
  }
}
```

### 2. Claude Desktop (`claude_desktop_config.json`)

On macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`  
On Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "autotest": {
      "command": "python",
      "args": ["<PATH_TO_AUTOTEST_MCP>/mcp_server.py"]
    }
  }
}
```

---

## 💡 Usage in Chat

Ask Cursor or Claude:
> *"Use autotest to generate full edge-case unit tests for this function."*

---

## ☕ Support & Sponsor
- **Polygon (USDC)**: `0x267e548ab3444aa0a671914ac7c644306a6b90b4`
- **TRON (USDT)**: `TWvzvF4FszbXM6qnBS947aNJHfyvA1kdZC`
