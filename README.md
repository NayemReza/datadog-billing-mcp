# Datadog Billing MCP Server

A Model Context Protocol (MCP) server that provides Datadog billing and usage analytics tools for AI assistants like Claude.

## Features

- **Cost Analysis**: Estimated, historical, and projected costs
- **Usage Metrics**: Logs, hosts, containers, APM, RUM breakdown
- **Log Volume Tracking**: Hourly/daily log indexing trends by index

## Tools

| Tool | Description |
|------|-------------|
| `get_estimated_cost` | Current billing period estimated cost by product |
| `get_historical_cost` | Monthly cost history for a date range |
| `get_projected_cost` | End-of-month projected cost with committed/on-demand split |
| `get_usage_summary` | Usage metrics (logs, hosts, containers, APM, RUM) |
| `get_logs_by_index` | Log event counts by index with hourly/daily aggregation |

## Installation

### Prerequisites

- Python 3.11+
- [uv](https://github.com/astral-sh/uv) package manager
- Datadog API Key and Application Key

### Setup

1. Clone the repository:
```bash
git clone https://github.com/NayemReza/datadog-billing-mcp.git
cd datadog-billing-mcp
```

2. Install dependencies:
```bash
uv sync
```

## Configuration

### Claude Code

Add the MCP server using the CLI:

```bash
claude mcp add --scope local --transport stdio datadog-billing \
  -- uv --directory /path/to/datadog-billing-mcp run datadog-billing-mcp
```

Then set the environment variables in `~/.claude.json` under your project's `mcpServers` entry:

```json
{
  "projects": {
    "/path/to/your-project": {
      "mcpServers": {
        "datadog-billing": {
          "type": "stdio",
          "command": "uv",
          "args": ["--directory", "/path/to/datadog-billing-mcp", "run", "datadog-billing-mcp"],
          "env": {
            "DD_API_KEY": "your-api-key",
            "DD_APP_KEY": "your-app-key",
            "DD_SITE": "datadoghq.eu"
          }
        }
      }
    }
  }
}
```

> **Note:** Do not add MCP servers to `.claude/settings.local.json` — they are silently ignored there. Use `~/.claude.json` for local/personal servers, or `.mcp.json` for team-shared servers (but avoid committing API keys).

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DD_API_KEY` | Yes | Datadog API Key |
| `DD_APP_KEY` | Yes | Datadog Application Key |
| `DD_SITE` | No | Datadog region (default: `datadoghq.com`) |

**Valid DD_SITE values:**
- `datadoghq.com` (US1)
- `us3.datadoghq.com` (US3)
- `us5.datadoghq.com` (US5)
- `datadoghq.eu` (EU)
- `ap1.datadoghq.com` (AP1)
- `ddog-gov.com` (US1-FED)

## Usage Examples

Once configured, Claude can use these tools:

```
"What's our projected Datadog cost this month?"
→ Uses get_projected_cost

"Show me historical costs from January to now"
→ Uses get_historical_cost with start_month="2025-01"

"Break down our log usage by day for the last week"
→ Uses get_logs_by_index with daily aggregation

"What's driving our cost increase?"
→ Combines multiple tools to analyze trends
```

## API Key Permissions

The Application Key needs these scopes:
- `usage_read` - Required for all billing/usage endpoints

## Security

- Credentials are passed via environment variables only
- Keys are never logged or exposed in responses
- All requests go directly to official Datadog API endpoints

## License

MIT
