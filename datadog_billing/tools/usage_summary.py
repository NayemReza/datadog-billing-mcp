"""Get usage summary metrics."""

from datetime import datetime
from datadog_api_client.v1.api.usage_metering_api import UsageMeteringApi
from ..utils.client import get_api_client


def get_usage_summary(start_month: str, end_month: str | None = None) -> dict:
    """
    Get usage summary for a date range.

    Args:
        start_month: Start month in YYYY-MM format (required).
        end_month: End month in YYYY-MM format. Defaults to start_month.

    Returns:
        Dictionary containing usage metrics (logs, hosts, containers, etc.).
    """
    with get_api_client() as api_client:
        api = UsageMeteringApi(api_client)

        start_date = datetime.strptime(start_month, "%Y-%m")

        kwargs = {"start_month": start_date}
        if end_month:
            kwargs["end_month"] = datetime.strptime(end_month, "%Y-%m")

        response = api.get_usage_summary(**kwargs)

        results = []
        for usage in response.usage or []:
            metrics = {}

            # Logs - try multiple attribute names for compatibility
            for attr in ("logs_indexed_logs_usage_sum", "indexed_events_count_sum"):
                val = getattr(usage, attr, None)
                if val is not None:
                    metrics["logs_indexed_events"] = val
                    break

            if getattr(usage, "ingested_events_bytes_sum", None):
                metrics["logs_ingested_bytes"] = usage.ingested_events_bytes_sum

            # Infrastructure
            if getattr(usage, "infra_host_top99p", None):
                metrics["infra_hosts_p99"] = usage.infra_host_top99p
            if getattr(usage, "container_avg", None):
                metrics["containers_avg"] = usage.container_avg
            if getattr(usage, "container_excl_agent_avg", None):
                metrics["containers_excl_agent_avg"] = usage.container_excl_agent_avg

            # APM
            if getattr(usage, "apm_host_top99p", None):
                metrics["apm_hosts_p99"] = usage.apm_host_top99p
            if getattr(usage, "trace_search_indexed_events_count_sum", None):
                metrics["apm_indexed_spans"] = usage.trace_search_indexed_events_count_sum

            # RUM
            if getattr(usage, "rum_total_session_count_sum", None):
                metrics["rum_sessions"] = usage.rum_total_session_count_sum

            # Synthetics
            if getattr(usage, "synthetics_check_calls_count_sum", None):
                metrics["synthetics_api_calls"] = usage.synthetics_check_calls_count_sum
            if getattr(usage, "synthetics_browser_check_calls_count_sum", None):
                metrics["synthetics_browser_calls"] = usage.synthetics_browser_check_calls_count_sum

            # Custom metrics
            if getattr(usage, "custom_ts_avg", None):
                metrics["custom_metrics_avg"] = usage.custom_ts_avg

            results.append({
                "month": str(usage.date)[:7] if usage.date else None,
                "org_name": usage.org_name,
                "metrics": metrics,
            })

        return {"usage_summary": results}
