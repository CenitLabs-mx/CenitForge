"""
API Deprecation Headers Middleware V5
Añade headers estándar (Deprecation, Sunset, Link) a respuestas de
versiones deprecadas según la política documentada.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Callable, Dict, Optional

import yaml


DEFAULT_SCHEDULE_PATH = Path("docs/architecture/api-deprecation-schedule.yaml")


class DeprecationHeadersMiddleware:
    """
    Middleware compatible con FastAPI / Flask / Django.
    Detecta la versión de API de la request y añade headers si está deprecada.
    """

    def __init__(self, schedule_path: Path = DEFAULT_SCHEDULE_PATH):
        self.schedule = self._load_schedule(schedule_path)

    @staticmethod
    def _load_schedule(path: Path) -> Dict:
        if not path.exists():
            return {"deprecated": {}, "successor_url": ""}
        return yaml.safe_load(path.read_text()) or {}

    def __call__(self, request, call_next: Callable):
        api_version = self._extract_version(request)
        response = call_next(request)
        return self._apply_headers(response, api_version)

    # ------------------------------
    # API pública para frameworks
    # ------------------------------

    def apply(self, response, api_version: str):
        """Para frameworks que no usan WSGI/ASGI estándar."""
        return self._apply_headers(response, api_version)

    # ------------------------------
    # Internals
    # ------------------------------

    def _extract_version(self, request) -> str:
        path = getattr(request, "path", "") or getattr(request, "url", "")
        # /v1/..., /v2/...
        import re
        m = re.search(r"/v(\d+)/", str(path))
        if m:
            return f"v{m.group(1)}"
        # Header fallback
        headers = getattr(request, "headers", {}) or {}
        return headers.get("X-API-Version", "v1")

    def _apply_headers(self, response, api_version: str):
        deprecated = self.schedule.get("deprecated", {})
        if api_version not in deprecated:
            return response

        cfg = deprecated[api_version]
        sunset_raw = cfg.get("sunset_date")
        if isinstance(sunset_raw, datetime):
            sunset_dt = sunset_raw
        else:
            sunset_dt = datetime.fromisoformat(str(sunset_raw))

        sunset_str = sunset_dt.strftime("%a, %d %b %Y %H:%M:%S GMT")
        successor = self.schedule.get("successor_url", "")

        self._set_header(response, "Deprecation", "true")
        self._set_header(response, "Sunset", sunset_str)
        if successor:
            self._set_header(response, "Link", f'<{successor}>; rel="successor-version"')
        self._set_header(response, "X-API-Deprecation-Notice", cfg.get("notice", ""))
        return response

    @staticmethod
    def _set_header(response, name: str, value: str):
        if hasattr(response, "headers"):
            if isinstance(response.headers, dict):
                response.headers[name] = value
            else:
                response.headers[name] = value  # Starlette / FastAPI
        elif hasattr(response, "set_header"):
            response.set_header(name, value)


# ------------------------------------------------------------
# Integración FastAPI
# ------------------------------------------------------------

def install_fastapi(app, schedule_path: Path = DEFAULT_SCHEDULE_PATH):
    """
    from api.middleware.deprecation_headers import install_fastapi
    install_fastapi(app)
    """
    middleware = DeprecationHeadersMiddleware(schedule_path)

    @app.middleware("http")
    async def _mw(request, call_next):
        return middleware(request, call_next)

    return middleware
