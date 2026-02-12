"""Get usage summary metrics."""

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

        from datetime import datetime
        start_date = datetime.strptime(start_month, "%Y-%m")

        kwargs = {"start_month": start_date}
        if end_month:
            kwargs["end_month"] = datetime.strptime(end_month, "%Y-%m")

        response = api.get_usage_summary(**kwargs)

        results = []
        for usage in response.usage or []:
            # Extract key metrics, filtering out None values
            metrics = {}

            # Logs
            if usage.logs_indexed_logs_usage_sum:
                metrics["logs_indexed_30day_events"] = usage.logs_indexed_logs_usage_sum
            if usage.ingested_events_bytes_sum:
                metrics["logs_ingested_bytes"] = usage.ingested_events_bytes_sum

            # Infrastructure
            if usage.infra_host_top99p:
                metrics["infra_hosts_p99"] = usage.infra_host_top99p
            if usage.container_avg:
                metrics["containers_avg"] = usage.container_avg
            if usage.container_excl_agent_avg:
                metrics["containers_excl_agent_avg"] = usage.container_excl_agent_avg

            # APM
            if usage.apm_host_top99p:
                metrics["apm_hosts_p99"] = usage.apm_host_top99p
            if usage.trace_search_indexed_events_count_sum:
                metrics["apm_indexed_spans"] = usage.trace_search_indexed_events_count_sum

            # RUM
            if usage.rum_total_session_count_sum:
                metrics["rum_sessions"] = usage.rum_total_session_count_sum

            # Synthetics
            if usage.synthetics_check_calls_count_sum:
                metrics["synthetics_api_calls"] = usage.synthetics_check_calls_count_sum
            if usage.synthetics_browser_check_calls_count_sum:
                metrics["synthetics_browser_calls"] = usage.synthetics_browser_check_calls_count_sum

            # Custom metrics
            if usage.custom_ts_avg:
                metrics["custom_metrics_avg"] = usage.custom_ts_avg

            results.append({
                "month": str(usage.date)[:7] if usage.date else None,
                "org_name": usage.org_name,
                "metrics": metrics,
            })

        return {"usage_summary": results}
