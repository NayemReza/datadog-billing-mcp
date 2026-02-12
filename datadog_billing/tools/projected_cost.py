"""Get projected cost for current billing period."""

from datadog_api_client.v2.api.usage_metering_api import UsageMeteringApi
from ..utils.client import get_api_client


def get_projected_cost(view: str = "sub-org") -> dict:
    """
    Get projected total cost for the current billing period.

    Args:
        view: Cost attribution view ("summary" or "sub-org"). Defaults to "sub-org".

    Returns:
        Dictionary containing projected cost breakdown by product.
    """
    with get_api_client() as api_client:
        api = UsageMeteringApi(api_client)

        response = api.get_projected_cost(view=view)

        results = []
        for item in response.data or []:
            attrs = item.attributes

            committed = []
            on_demand = []
            totals = []

            for charge in attrs.charges or []:
                entry = {
                    "product": charge.product_name,
                    "cost": charge.cost,
                }
                if charge.charge_type == "projected_committed":
                    committed.append(entry)
                elif charge.charge_type == "projected_on_demand":
                    on_demand.append(entry)
                elif charge.charge_type == "total":
                    totals.append(entry)

            results.append({
                "org_name": attrs.org_name,
                "date": str(attrs.date)[:10] if attrs.date else None,
                "projected_total_cost": attrs.projected_total_cost,
                "breakdown": sorted(totals, key=lambda x: x["cost"] or 0, reverse=True),
                "committed": sorted(committed, key=lambda x: x["cost"] or 0, reverse=True),
                "on_demand": sorted([c for c in on_demand if c["cost"]], key=lambda x: x["cost"] or 0, reverse=True),
            })

        return {"projected_costs": results}
