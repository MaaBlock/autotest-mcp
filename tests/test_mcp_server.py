"""
Unit tests for AutoTest AI MCP Server (mcp_server.py).
Verifies JSON-RPC 2.0 protocol conformance, tool execution, dual wallet addresses,
notification handling, and paywall triggers.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
import pytest

# Add parent directory to sys.path so mcp_server can be imported directly
sys.path.insert(0, str(Path(__file__).parent.parent))
import mcp_server


def test_initialize_handler():
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "clientInfo": {"name": "cursor", "version": "0.45.0"}
        }
    }
    res = mcp_server.handle_request(req)
    assert res is not None
    assert res["jsonrpc"] == "2.0"
    assert res["id"] == 1
    result = res["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert "tools" in result["capabilities"]
    
    server_info = result["serverInfo"]
    assert server_info["name"] == "autotest-ai"
    assert server_info["version"] == "1.0.0"
    assert server_info["sponsor_wallet"] == "0x267e548ab3444aa0a671914ac7c644306a6b90b4"
    assert server_info["sponsor_wallets"]["polygon_usdc"] == "0x267e548ab3444aa0a671914ac7c644306a6b90b4"
    assert server_info["sponsor_wallets"]["tron_usdt"] == "TWvzvF4FszbXM6qnBS947aNJHfyvA1kdZC"
    assert "workers.dev" in server_info["web3_paywall"]


def test_notification_suppression():
    """MCP notifications without id or with notifications/ prefix must return None."""
    notification_req = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
        "params": {}
    }
    res = mcp_server.handle_request(notification_req)
    assert res is None

    no_id_req = {
        "jsonrpc": "2.0",
        "method": "cancelled",
        "params": {}
    }
    assert mcp_server.handle_request(no_id_req) is None


def test_tools_list():
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
    res = mcp_server.handle_request(req)
    assert res is not None
    tools = res["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "generate_edge_tests" in tool_names
    assert "audit_code_defenses" in tool_names
    assert "get_paywall_status" in tool_names


def test_generate_edge_tests_python():
    sample_code = """
def calculate_pnl(entry_price: float, exit_price: float, volume: float) -> float:
    if entry_price <= 0 or exit_price <= 0:
        raise ValueError("Prices must be positive")
    return (exit_price - entry_price) * volume
"""
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "generate_edge_tests",
            "arguments": {
                "code": sample_code,
                "language": "python",
                "framework": "pytest",
                "tier": "community"
            }
        }
    }
    res = mcp_server.handle_request(req)
    assert res is not None
    content = res["result"]["content"][0]["text"]
    assert "def test_calculate_pnl_parameterized_boundaries" in content
    assert "def test_calculate_pnl_fault_injection_and_exceptions" in content
    assert "0x267e548ab3444aa0a671914ac7c644306a6b90b4" in content
    assert "TWvzvF4FszbXM6qnBS947aNJHfyvA1kdZC" in content
    assert "https://autotest-ai.sweet-possum.workers.dev" in content


def test_generate_edge_tests_pro_tier():
    sample_code = "def add(a, b): return a + b"
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "generate_edge_tests",
            "arguments": {
                "code": sample_code,
                "tier": "pro",
                "tx_hash": "0xabc123mocktxforverification"
            }
        }
    }
    res = mcp_server.handle_request(req)
    content = res["result"]["content"][0]["text"]
    assert "Tier: PRO" in content
    assert "test_add_pro_mutation_fuzz_matrix" in content


def test_generate_edge_tests_typescript():
    sample_ts = "function executeTrade(pair: string, amount: number) { return true; }"
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "generate_edge_tests",
            "arguments": {
                "code": sample_ts,
                "language": "typescript",
                "framework": "jest"
            }
        }
    }
    res = mcp_server.handle_request(req)
    content = res["result"]["content"][0]["text"]
    assert "describe('executeTrade'" in content
    assert "0x267e548ab3444aa0a671914ac7c644306a6b90b4" in content
    assert "TWvzvF4FszbXM6qnBS947aNJHfyvA1kdZC" in content


def test_audit_code_defenses():
    sample_code = """
def route_order(book, side, size):
    if side == 'BUY':
        if size > 100:
            return 'SPLIT'
        return 'MARKET'
    elif side == 'SELL':
        return 'LIMIT'
    else:
        raise ValueError('Invalid side')
"""
    req = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "tools/call",
        "params": {
            "name": "audit_code_defenses",
            "arguments": {"code": sample_code, "language": "python"}
        }
    }
    res = mcp_server.handle_request(req)
    content = json.loads(res["result"]["content"][0]["text"])
    assert content["complexity_score"] >= 3
    assert len(content["functions_detected"]) >= 1
    assert content["functions_detected"][0]["name"] == "route_order"
    assert content["sponsorship"]["polygon_usdc"] == "0x267e548ab3444aa0a671914ac7c644306a6b90b4"
    assert content["sponsorship"]["tron_usdt"] == "TWvzvF4FszbXM6qnBS947aNJHfyvA1kdZC"


def test_get_paywall_status():
    req = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "get_paywall_status",
            "arguments": {}
        }
    }
    res = mcp_server.handle_request(req)
    content = json.loads(res["result"]["content"][0]["text"])
    assert "1 USDC" in content["fee_amount"]
    networks = {net["token"]: net["address"] for net in content["supported_networks"]}
    assert networks["USDC"] == "0x267e548ab3444aa0a671914ac7c644306a6b90b4"
    assert networks["USDT"] == "TWvzvF4FszbXM6qnBS947aNJHfyvA1kdZC"


def test_stdio_roundtrip():
    """Verifies stdio JSON-RPC process communication end-to-end."""
    server_script = Path(__file__).parent.parent / "mcp_server.py"
    proc = subprocess.Popen(
        [sys.executable, str(server_script)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    init_msg = json.dumps({
        "jsonrpc": "2.0",
        "id": "test-init-1",
        "method": "initialize",
        "params": {}
    }) + "\n"

    notify_msg = json.dumps({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }) + "\n"

    list_msg = json.dumps({
        "jsonrpc": "2.0",
        "id": "test-list-2",
        "method": "tools/list",
        "params": {}
    }) + "\n"

    proc.stdin.write(init_msg)
    proc.stdin.write(notify_msg)
    proc.stdin.write(list_msg)
    proc.stdin.flush()

    line1 = proc.stdout.readline()
    resp1 = json.loads(line1)
    assert resp1["id"] == "test-init-1"
    assert resp1["result"]["serverInfo"]["name"] == "autotest-ai"

    # Notification should NOT emit anything, so next line should be list_msg response
    line2 = proc.stdout.readline()
    resp2 = json.loads(line2)
    assert resp2["id"] == "test-list-2"
    assert len(resp2["result"]["tools"]) == 3

    proc.stdin.close()
    proc.terminate()
    proc.wait(timeout=3)
