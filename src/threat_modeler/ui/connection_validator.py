"""SCR-014 — Model connection validation logic.

Provides a thin, synchronous connectivity check for each provider type.
The validator does NOT send any prompt or consume tokens — it only checks
that the endpoint is reachable and (where applicable) that the API key
is non-empty.  Actual prompt functionality is verified by the llm_live
test suite.

Return type: ValidationResult (named tuple)
  - ok: bool         — True when the check passed
  - message: str     — Human-readable result message shown in the UI
  - detail: str      — Technical detail for error cases (empty string on success)
"""

from __future__ import annotations

from typing import NamedTuple

from threat_modeler.config import PROVIDER_MATRIX, ModelSelection


class ValidationResult(NamedTuple):
    ok: bool
    message: str
    detail: str = ""


def validate_connection(model: ModelSelection, api_key: str = "") -> ValidationResult:
    """Run the appropriate connectivity check for the given model selection.

    Args:
        model:    ModelSelection from session state.
        api_key:  API key string (may be empty; validated only structurally here).

    Returns:
        ValidationResult with ok, message, and detail fields.
    """
    provider = model.provider
    provider_info = PROVIDER_MATRIX.get(provider)

    # ── Fixture / offline mode: always valid ────────────────────────────
    if model.offline_only or provider == "fixture":
        return ValidationResult(
            ok=True,
            message="Offline/Fixture mode active — no connection required.",
        )

    if provider_info is None:
        return ValidationResult(
            ok=False,
            message=f"Unknown provider '{provider}'.",
            detail="Provider is not listed in PROVIDER_MATRIX. Select a supported provider.",
        )

    # ── API-key check for providers that require one ─────────────────────
    if provider_info["requires_api_key"] and not api_key.strip():
        return ValidationResult(
            ok=False,
            message=f"{provider_info['label']} requires an API key.",
            detail=(
                "Set the appropriate environment variable before validating:\n"
                + _env_var_hint(provider)
            ),
        )

    # ── URL check for providers that require a connection URL ─────────────
    if provider_info["requires_url"]:
        if not model.connection_url.strip():
            return ValidationResult(
                ok=False,
                message=f"{provider_info['label']} requires a Connection URL.",
                detail="Enter the endpoint URL in the Connection Details field.",
            )
        url_result = _check_url_reachable(model.connection_url.strip())
        if not url_result.ok:
            return url_result

    # ── Cloud providers without a custom URL: check via HTTP HEAD ────────
    else:
        base_url = _provider_base_url(provider)
        if base_url:
            url_result = _check_url_reachable(base_url)
            if not url_result.ok:
                return url_result

    return ValidationResult(
        ok=True,
        message=(
            f"Connection to {provider_info['label']} verified. "
            f"Model: {model.model_name}. Ready to run."
        ),
    )


def _check_url_reachable(url: str) -> ValidationResult:
    """Attempt an HTTP HEAD request to verify the URL is reachable."""
    try:
        import urllib.request  # stdlib — no extra deps required
        from urllib.error import HTTPError

        req = urllib.request.Request(url, method="HEAD")  # noqa: S310
        req.add_header("User-Agent", "ThreatModeler/1.0 connection-check")
        with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
            status = resp.status
            if 200 <= status < 500:
                return ValidationResult(ok=True, message="Endpoint reachable.")
            return ValidationResult(
                ok=False,
                message=f"Endpoint returned HTTP {status}.",
                detail=f"URL: {url}",
            )
    except HTTPError as exc:
        if 400 <= exc.code < 500:
            return ValidationResult(
                ok=True,
                message=f"Endpoint reachable (HTTP {exc.code}).",
                detail=f"URL: {url}",
            )
        return ValidationResult(
            ok=False,
            message=f"Could not reach endpoint: HTTPError",
            detail=str(exc),
        )
    except Exception as exc:  # noqa: BLE001
        return ValidationResult(
            ok=False,
            message=f"Could not reach endpoint: {type(exc).__name__}",
            detail=str(exc),
        )


def _provider_base_url(provider: str) -> str:
    """Return a ping-able base URL for known cloud providers."""
    _BASE_URLS: dict[str, str] = {
        "openai": "https://api.openai.com",
        "anthropic": "https://api.anthropic.com",
        "xai": "https://api.x.ai",
    }
    return _BASE_URLS.get(provider, "")


def _env_var_hint(provider: str) -> str:
    """Return guidance for where to supply provider API keys."""
    _ENV_VARS: dict[str, str] = {
        "openai": "Provide API key in Pipeline Configuration (SCR-013).",
        "anthropic": "Provide API key in Pipeline Configuration (SCR-013).",
        "xai": "Provide GROK_API value in Pipeline Configuration (SCR-013).",
        "azure": "Provide API key in Pipeline Configuration (SCR-013).",
        "custom": "Provide API key in Pipeline Configuration (SCR-013).",
    }
    return _ENV_VARS.get(provider, "Provide API key in Pipeline Configuration (SCR-013).")
