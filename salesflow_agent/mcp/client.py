"""MCP Client - discovers and wraps MCP tools for the LangChain agent."""

import logging
from typing import Any

from langchain_core.tools import StructuredTool

logger = logging.getLogger(__name__)


class MCPClientWrapper:
    """Wraps FastMCP server tools as LangChain-compatible tools."""

    def __init__(self, server_url: str):
        self.server_url = server_url
        self._mcp_client = None
        self._session = None

    async def discover_tools(self) -> list[StructuredTool]:
        """Discover tools from FastMCP server and return as LangChain tools."""
        from fastmcp import Client

        self._mcp_client = Client(self.server_url)

        async with self._mcp_client as client:
            tools_response = await client.list_tools()

        langchain_tools = []
        for tool_info in tools_response:
            lc_tool = self._convert_to_langchain_tool(tool_info)
            langchain_tools.append(lc_tool)
            logger.info(f"Discovered MCP tool: {tool_info.name}")

        logger.info(f"Total MCP tools discovered: {len(langchain_tools)}")
        return langchain_tools

    def _convert_to_langchain_tool(self, tool_info: Any) -> StructuredTool:
        """Convert an MCP tool descriptor to a LangChain StructuredTool."""
        from pydantic import create_model

        # Build pydantic model from MCP tool input schema
        fields = {}
        schema = tool_info.inputSchema or {}
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        for param_name, param_schema in properties.items():
            param_type = _json_type_to_python(param_schema.get("type", "string"))
            default = ... if param_name in required else param_schema.get("default")
            fields[param_name] = (param_type, default)

        args_model = create_model(f"{tool_info.name}_args", **fields) if fields else None

        server_url = self.server_url
        tool_name = tool_info.name

        async def _invoke_tool(**kwargs) -> str:
            from fastmcp import Client

            async with Client(server_url) as client:
                result = await client.call_tool(tool_name, kwargs)
                # Extract text content from result
                if hasattr(result, "__iter__"):
                    texts = []
                    for item in result:
                        if hasattr(item, "text"):
                            texts.append(item.text)
                        else:
                            texts.append(str(item))
                    return "\n".join(texts)
                return str(result)

        tool = StructuredTool.from_function(
            coroutine=_invoke_tool,
            name=tool_info.name,
            description=tool_info.description or f"MCP tool: {tool_info.name}",
            args_schema=args_model,
        )
        return tool


def _json_type_to_python(json_type: str) -> type:
    """Map JSON schema type to Python type."""
    mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    return mapping.get(json_type, str)
