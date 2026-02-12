"""Get logs usage by index with hourly/daily breakdown."""

from datadog_api_client.v1.api.usage_metering_api import UsageMeteringApi
from ..utils.client import get_api_client
from collections import defaultdict


def get_logs_by_index(
    start_date: str,
    end_date: str,
    aggregate_by: str = "day"
) -> dict:
    """
    Get logs indexed usage broken down by index.

    Args:
        start_date: Start date in YYYY-MM-DD format (required).
        end_date: End date in YYYY-MM-DD format (required).
        aggregate_by: Aggregation level - "hour" or "day". Defaults to "day".

    Returns:
        Dictionary containing log event counts by date/hour and index.
    """
    with get_api_client() as api_client:
        api = UsageMeteringApi(api_client)

        from datetime import datetime
        start_hr = datetime.strptime(start_date, "%Y-%m-%d")
        end_hr = datetime.strptime(end_date + "T23", "%Y-%m-%dT%H")

        response = api.get_usage_logs_by_index(start_hr=start_hr, end_hr=end_hr)

        # Aggregate by day or hour
        aggregated = defaultdict(lambda: defaultdict(int))
        index_names = set()

        for item in response.usage or []:
            hour_str = str(item.hour)[:13] if item.hour else None  # YYYY-MM-DDTHH
            if not hour_str:
                continue

            if aggregate_by == "day":
                key = hour_str[:10]  # YYYY-MM-DD
            else:
                key = hour_str  # YYYY-MM-DDTHH

            index_name = item.index_name or "unknown"
            index_names.add(index_name)
            aggregated[key][index_name] += item.event_count or 0
            aggregated[key]["_total"] += item.event_count or 0

        # Format results
        results = []
        for date_key in sorted(aggregated.keys()):
            entry = {
                "date" if aggregate_by == "day" else "hour": date_key,
                "total_events": aggregated[date_key]["_total"],
                "by_index": {
                    idx: aggregated[date_key][idx]
                    for idx in index_names
                    if aggregated[date_key][idx] > 0
                },
            }
            results.append(entry)

        # Calculate summary
        total_events = sum(r["total_events"] for r in results)
        num_periods = len(results)

        return {
            "logs_by_index": results,
            "summary": {
                "total_events": total_events,
                "periods": num_periods,
                "average_per_period": total_events // num_periods if num_periods else 0,
                "indexes": list(index_names),
            }
        }
