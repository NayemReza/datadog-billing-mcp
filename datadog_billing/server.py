"""Datadog Billing MCP Server."""

import asyncio
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .tools import (
    get_estimated_cost,
    get_historical_cost,
    get_projected_cost,
    get_usage_summary,
    get_logs_by_index,
)

server = Server("datadog-billing-mcp")


TOOLS = [
    Tool(
        name="get_estimated_cost",
        description="Get estimated cost for the current billing period, broken down by product. Shows committed vs on-demand costs.",
        inputSchema={
            "type": "object",
            "properties": {
                "view": {
                    "type": "string",
                    "description": "Cost attribution view: 'summary' or 'sub-org'",
                    "default": "sub-org",
                },
                "start_month": {
                    "type": "string",
                    "description": "Start month in YYYY-MM format (optional, defaults to current month)",
                },
            },
        },
    ),
    Tool(
        name="get_historical_cost",
        description="Get historical cost data for a date range, showing monthly costs broken down by product.",
        inputSchema={
            "type": "object",
            "properties": {
                "start_month": {
                    "type": "string",
                    "description": "Start month in YYYY-MM format (required)",
                },
                "end_month": {
                    "type": "string",
                    "description": "End month in YYYY-MM format (optional, defaults to start_month)",
                },
                "view": {
                    "type": "string",
                    "description": "Cost attribution view: 'summary' or 'sub-org'",
                    "default": "sub-org",
                },
            },
            "required": ["start_month"],
        },
    ),
    Tool(
        name="get_projected_cost",
        description="Get projected total cost for the current billing period, showing expected end-of-month costs by product with committed vs on-demand breakdown.",
        inputSchema={
            "type": "object",
            "properties": {
                "view": {
                    "type": "string",
                    "description": "Cost attribution view: 'summary' or 'sub-org'",
                    "default": "sub-org",
                },
            },
        },
    ),
    Tool(
        name="get_usage_summary",
        description="Get usage metrics summary including logs indexed/ingested, hosts, containers, APM, RUM, and custom metrics.",
        inputSchema={
            "type": "object",
            "properties": {
                "start_month": {
                    "type": "string",
                    "description": "Start month in YYYY-MM format (required)",
                },
                "end_month": {
                    "type": "string",
                    "description": "End month in YYYY-MM format (optional)",
                },
            },
            "required": ["start_month"],
        },
    ),
    Tool(
        name="get_logs_by_index",
        description="Get logs indexed usage broken down by index with hourly or daily aggregation. Useful for identifying log volume spikes and trends.",
        inputSchema={
            "type": "object",
            "properties": {
                "start_date": {
                    "type": "string",
                    "description": "Start date in YYYY-MM-DD format (required)",
                },
                "end_date": {
                    "type": "string",
                    "description": "End date in YYYY-MM-DD format (required)",
                },
                "aggregate_by": {
                    "type": "string",
                    "description": "Aggregation level: 'hour' or 'day'",
                    "default": "day",
                    "enum": ["hour", "day"],
                },
            },
            "required": ["start_date", "end_date"],
        },
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available billing tools."""
    return TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Execute a billing tool."""
    try:
        if name == "get_estimated_cost":
            result = get_estimated_cost(
                view=arguments.get("view", "sub-org"),
                start_month=arguments.get("start_month"),
            )
        elif name == "get_historical_cost":
            result = get_historical_cost(
                start_month=arguments["start_month"],
                end_month=arguments.get("end_month"),
                view=arguments.get("view", "sub-org"),
            )
        elif name == "get_projected_cost":
            result = get_projected_cost(
                view=arguments.get("view", "sub-org"),
            )
        elif name == "get_usage_summary":
            result = get_usage_summary(
                start_month=arguments["start_month"],
                end_month=arguments.get("end_month"),
            )
        elif name == "get_logs_by_index":
            result = get_logs_by_index(
                start_date=arguments["start_date"],
                end_date=arguments["end_date"],
                aggregate_by=arguments.get("aggregate_by", "day"),
            )
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {str(e)}")]


def main():
    """Run the MCP server."""

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
