
from src.tools_definitions import TOOL_DEFINITIONS
from src.tools import get_transaction


def test_tool_definitions_exist():
    """Check that the agent has tool definitions."""
    assert len(TOOL_DEFINITIONS) > 0

    tool_names = [
        tool["name"]
        for tool in TOOL_DEFINITIONS
    ]

    assert "get_transaction" in tool_names


def test_get_transaction_returns_data():
    """Check that the transaction tool retrieves a known transaction."""
    result = get_transaction("TXN-10001")

    assert result is not None
    assert result.get("success") is True
    assert result.get("data") is not None
