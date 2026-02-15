"""Get historical cost data."""

from datetime import datetime
from datadog_api_client.v2.api.usage_metering_api import UsageMeteringApi
from ..utils.client import get_api_client


def _parse_month(month_str: str) -> datetime:
    """Parse YYYY-MM or YYYY-MM-DD string to datetime."""
    for fmt in ("%Y-%m", "%Y-%m-%d"):
        try:
            return datetime.strptime(month_str, fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse '{month_str}' as date. Use YYYY-MM format.")


def get_historical_cost(start_month: str, end_month: str | None = None, view: str = "sub-org") -> dict:
    """
    Get historical cost data for a date range.

    Args:
        start_month: Start month in YYYY-MM format (required).
        end_month: End month in YYYY-MM format. Defaults to start_month.
        view: Cost attribution view ("summary" or "sub-org"). Defaults to "sub-org".

    Returns:
        Dictionary containing monthly cost breakdown.
    """
    with get_api_client() as api_client:
        api = UsageMeteringApi(api_client)

        kwargs = {
            "start_month": _parse_month(start_month),
            "view": view,
        }
        if end_month:
            kwargs["end_month"] = _parse_month(end_month)

        response = api.get_historical_cost_by_org(**kwargs)

        results = []
        for item in response.data or []:
            attrs = item.attributes
            charges = []
            for charge in attrs.charges or []:
                if charge.charge_type == "total":
                    charges.append({
                        "product": charge.product_name,
                        "cost": charge.cost,
                    })

            results.append({
                "org_name": attrs.org_name,
                "date": str(attrs.date)[:7] if attrs.date else None,
                "total_cost": attrs.total_cost,
                "charges": sorted(charges, key=lambda x: x["cost"] or 0, reverse=True),
            })

        return {
            "historical_costs": sorted(results, key=lambda x: x["date"] or ""),
            "summary": {
                "total": sum(r["total_cost"] or 0 for r in results),
                "months": len(results),
            }
        }
