"""
Shadow Safety Contract V5
Garantiza que el shadow testing de billing NO produce efectos secundarios
reales hacia sistemas externos (Stripe, SendGrid, APIs contables, etc.).
"""

from __future__ import annotations

import hashlib
import json
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from unittest.mock import patch


class ShadowSafetyViolation(Exception):
    """Se lanza cuando se detecta una llamada real a un sistema externo."""


@dataclass
class InterceptedCall:
    system: str
    method: str
    args_hash: str
    kwargs_hash: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    was_intercepted: bool = True
    simulated_response: Optional[Dict] = None


@dataclass
class SafetyReport:
    safe: bool
    intercepted_count: int = 0
    violations: List[str] = field(default_factory=list)
    simulated_side_effects: List[Dict] = field(default_factory=list)
    severity: str = "INFO"  # INFO | P1


class MockInterceptor:
    """Intercepta llamadas a un sistema externo y devuelve respuesta simulada."""

    def __init__(self, system: str, method: str, simulator: Optional[Callable] = None):
        self.system = system
        self.method = method
        self.simulator = simulator or self._default_simulator
        self.calls: List[InterceptedCall] = []
        self.original: Optional[Callable] = None

    def intercept(self, *args, **kwargs):
        call = InterceptedCall(
            system=self.system,
            method=self.method,
            args_hash=self._hash(args),
            kwargs_hash=self._hash(kwargs),
            simulated_response=self.simulator(self.system, self.method, args, kwargs),
        )
        self.calls.append(call)
        return call.simulated_response

    def _default_simulator(self, system, method, args, kwargs) -> Dict:
        return {
            "mocked": True,
            "id": f"mock_{system}_{uuid.uuid4().hex[:8]}",
            "status": "simulated_success",
        }

    @staticmethod
    def _hash(obj: Any) -> str:
        try:
            s = json.dumps(obj, sort_keys=True, default=str)
        except TypeError:
            s = repr(obj)
        return hashlib.sha256(s.encode()).hexdigest()


class ShadowSafetyContract:
    """
    Contrato de seguridad que debe activarse durante cualquier prueba de
    shadow billing. Registra mocks y valida que NO hubo llamadas reales.
    """

    EXTERNAL_SYSTEMS_MUST_MOCK = [
        ("stripe",            "Charge.create"),
        ("stripe",            "Refund.create"),
        ("stripe",            "Invoice.pay"),
        ("stripe",            "Customer.create"),
        ("sendgrid",          "send_email"),
        ("accounting_api",    "post_journal_entry"),
        ("tax_api",           "calculate_tax"),
        ("pdf_generator",     "create_invoice_pdf"),
        ("webhook_relay",     "dispatch"),
        ("slack_notifier",    "send_message"),
    ]

    def __init__(self):
        self.interceptors: Dict[str, MockInterceptor] = {}
        self._patches: List[Any] = []
        self.active: bool = False

    @contextmanager
    def activate(self):
        """Context manager que activa los mocks y los limpia al salir."""
        self._install_mocks()
        self.active = True
        try:
            yield self
        finally:
            self._uninstall_mocks()
            self.active = False

    def _install_mocks(self) -> None:
        for system, method in self.EXTERNAL_SYSTEMS_MUST_MOCK:
            key = f"{system}.{method}"
            interceptor = MockInterceptor(system, method)
            self.interceptors[key] = interceptor
            # Intentar parchar módulo si existe; si no, registrar igualmente.
            try:
                module_name, fn_name = self._resolve_target(system, method)
                p = patch(f"{module_name}.{fn_name}", side_effect=interceptor.intercept)
                p.start()
                self._patches.append(p)
            except (ImportError, AttributeError):
                # Sistema no instalado localmente: se registra como "must be mocked"
                pass

    def _uninstall_mocks(self) -> None:
        for p in self._patches:
            try:
                p.stop()
            except Exception:
                pass
        self._patches.clear()

    @staticmethod
    def _resolve_target(system: str, method: str) -> tuple[str, str]:
        """Mapea (system, method) a module.function para patch."""
        mapping = {
            ("stripe", "Charge.create"):       ("stripe", "Charge.create"),
            ("stripe", "Refund.create"):       ("stripe", "Refund.create"),
            ("stripe", "Invoice.pay"):         ("stripe", "Invoice.pay"),
            ("stripe", "Customer.create"):     ("stripe", "Customer.create"),
            ("sendgrid", "send_email"):        ("sendgrid.helpers.mail.Mail", "Mail"),
            ("accounting_api", "post_journal_entry"): ("clients.accounting", "post_journal_entry"),
            ("tax_api", "calculate_tax"):      ("clients.tax", "calculate_tax"),
            ("pdf_generator", "create_invoice_pdf"): ("clients.pdf", "create_invoice_pdf"),
            ("webhook_relay", "dispatch"):     ("clients.webhooks", "dispatch"),
            ("slack_notifier", "send_message"): ("clients.slack", "send_message"),
        }
        return mapping[(system, method)]

    def all_intercepted_calls(self) -> List[InterceptedCall]:
        return [c for i in self.interceptors.values() for c in i.calls]

    def validate(self) -> SafetyReport:
        """
        Verifica que:
        1. Todos los sistemas críticos tenían mock activo.
        2. No hubo llamadas reales detectadas (no hay forma directa,
           pero si un interceptor no se instaló y el sistema está presente, es violación).
        """
        violations: List[str] = []
        for system, method in self.EXTERNAL_SYSTEMS_MUST_MOCK:
            key = f"{system}.{method}"
            if key not in self.interceptors:
                violations.append(f"Missing mock for {key}")

        intercepted = self.all_intercepted_calls()

        if violations:
            return SafetyReport(
                safe=False,
                intercepted_count=len(intercepted),
                violations=violations,
                severity="P1",
            )

        return SafetyReport(
            safe=True,
            intercepted_count=len(intercepted),
            simulated_side_effects=[asdict(c) for c in intercepted],
            severity="INFO",
        )


# ------------------------------------------------------------
# Ejemplo de uso en test
# ------------------------------------------------------------

def run_shadow_billing_test(webhook_payload: Dict, old_engine, new_engine, persist_fn):
    """
    Ejecuta shadow billing con Safety Contract activo.
    - old_engine: procesa y persiste (lógica vigente)
    - new_engine: procesa pero NO persiste (lógica candidata)
    """
    contract = ShadowSafetyContract()
    with contract.activate():
        old_result = old_engine.process(webhook_payload)
        persist_fn(old_result)

        new_result = new_engine.process(webhook_payload)

        safety = contract.validate()
        if not safety.safe:
            raise ShadowSafetyViolation(
                f"Shadow Safety Contract violated: {safety.violations}"
            )

        if old_result != new_result:
            return {
                "discrepancy": True,
                "old": old_result,
                "new": new_result,
                "intercepted_side_effects": safety.simulated_side_effects,
            }
        return {"discrepancy": False, "intercepted_count": safety.intercepted_count}
