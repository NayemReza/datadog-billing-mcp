"""Get estimated cost for current billing period."""

from datetime import datetime
from datadog_api_client.v2.api.usage_metering_api import UsageMeteringApi
from ..utils.client import get_api_client


def get_estimated_cost(view: str = "sub-org", start_month: str | None = None) -> dict:
    """
    Get estimated cost for the current billing period.

    Args:
        view: Cost attribution view ("summary" or "sub-org"). Defaults to "sub-org".
        start_month: Start month in YYYY-MM format. Defaults to current month.

    Returns:
        Dictionary containing estimated cost breakdown by product.
    """
    with get_api_client() as api_client:
        api = UsageMeteringApi(api_client)

        kwargs = {"view": view}
        if start_month:
            for fmt in ("%Y-%m", "%Y-%m-%d"):
                try:
                    kwargs["start_month"] = datetime.strptime(start_month, fmt)
                    break
                except ValueError:
                    continue

        response = api.get_estimated_cost_by_org(**kwargs)

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
                "date": str(attrs.date)[:10] if attrs.date else None,
                "total_cost": attrs.total_cost,
                "charges": sorted(charges, key=lambda x: x["cost"] or 0, reverse=True),
            })

        return {"estimated_costs": results}
