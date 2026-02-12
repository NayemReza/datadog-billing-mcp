"""Datadog API client configuration."""

import os
from datadog_api_client import Configuration, ApiClient

VALID_DD_SITES = {
    "datadoghq.com",      # US1
    "us3.datadoghq.com",  # US3
    "us5.datadoghq.com",  # US5
    "datadoghq.eu",       # EU
    "ap1.datadoghq.com",  # AP1
    "ddog-gov.com",       # US1-FED
}

DEFAULT_DD_SITE = "datadoghq.com"


def get_configuration() -> Configuration:
    """Create Datadog API configuration from environment variables."""
    api_key = os.getenv("DD_API_KEY")
    app_key = os.getenv("DD_APP_KEY")
    site = os.getenv("DD_SITE", DEFAULT_DD_SITE)

    if not api_key:
        raise ValueError("DD_API_KEY environment variable is required")
    if not app_key:
        raise ValueError("DD_APP_KEY environment variable is required")

    if site not in VALID_DD_SITES:
        import warnings
        warnings.warn(f"Unknown DD_SITE '{site}'. Valid sites: {VALID_DD_SITES}")

    configuration = Configuration()
    configuration.api_key["apiKeyAuth"] = api_key
    configuration.api_key["appKeyAuth"] = app_key
    configuration.server_variables["site"] = site

    return configuration


def get_api_client() -> ApiClient:
    """Create a configured Datadog API client."""
    return ApiClient(get_configuration())
