"""
Emergency Budget Tracker V5
Limita el uso de modo emergencia a 3 por trimestre, registra deuda técnica
y bloquea nuevas features si la deuda no se paga.
"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional


class EmergencyDenied(Exception):
    pass


class TechDebtBlockError(Exception):
    pass


@dataclass
class Emergency:
    id: str
    timestamp: str
    reason: str
    quarter: str
    tech_debt_credits: int
    adr_required: bool = True
    adr_deadline: str = ""
    adr_completed: bool = False


@dataclass
class EmergencyApproval:
    approved: bool
    emergency_id: Optional[str] = None
    remaining_emergencies: int = 0
    tech_debt_credits_consumed: int = 0
    adr_deadline: str = ""
    reason: str = ""
    escalation_required: bool = False
    escalate_to: Optional[str] = None


class EmergencyBudgetTracker:
    MAX_EMERGENCIES_PER_QUARTER = 3
    TECH_DEBT_CREDITS_PER_EMERGENCY = 5
    MAX_UNPAID_CREDITS_BEFORE_BLOCK = 10

    def __init__(self, state_path: Path = Path(".emergency_budget.json")):
        self.state_path = state_path
        self.state = self._load_state()

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def can_use_emergency_mode(self, reason: str) -> EmergencyApproval:
        quarter = self._current_quarter()
        emergencies = self.state.get("quarters", {}).get(quarter, [])
        used = len(emergencies)
        remaining = self.MAX_EMERGENCIES_PER_QUARTER - used

        if remaining <= 0:
            return EmergencyApproval(
                approved=False,
                reason=f"Emergency budget agotado: {used}/{self.MAX_EMERGENCIES_PER_QUARTER} este trimestre",
                escalation_required=True,
                escalate_to="CTO",
            )

        if remaining == 1:
            return EmergencyApproval(
                approved=False,
                reason="Última emergencia del trimestre. Requiere aprobación de VP Engineering.",
                escalation_required=True,
                escalate_to="VP_Engineering",
            )

        # Aprobar
        emergency = Emergency(
            id=f"EM-{uuid.uuid4().hex[:8].upper()}",
            timestamp=datetime.utcnow().isoformat(),
            reason=reason,
            quarter=quarter,
            tech_debt_credits=self.TECH_DEBT_CREDITS_PER_EMERGENCY,
            adr_deadline=(datetime.utcnow() + timedelta(hours=24)).isoformat(),
        )

        self.state.setdefault("quarters", {}).setdefault(quarter, []).append(asdict(emergency))
        self._save_state()

        return EmergencyApproval(
            approved=True,
            emergency_id=emergency.id,
            remaining_emergencies=remaining - 1,
            tech_debt_credits_consumed=self.TECH_DEBT_CREDITS_PER_EMERGENCY,
            adr_deadline=emergency.adr_deadline,
        )

    def mark_adr_completed(self, emergency_id: str) -> None:
        quarter = self._current_quarter()
        for e in self.state.get("quarters", {}).get(quarter, []):
            if e["id"] == emergency_id:
                e["adr_completed"] = True
                break
        self._save_state()

    def get_tech_debt_balance(self) -> int:
        total = 0
        paid = 0
        for quarter_emergencies in self.state.get("quarters", {}).values():
            for e in quarter_emergencies:
                total += e.get("tech_debt_credits", 0)
                if e.get("adr_completed"):
                    paid += e.get("tech_debt_credits", 0)
        # Plus credits pagados manualmente
        paid += sum(self.state.get("manual_payments", []))
        return total - paid

    def check_feature_block(self, feature_name: str) -> None:
        balance = self.get_tech_debt_balance()
        if balance > self.MAX_UNPAID_CREDITS_BEFORE_BLOCK:
            raise TechDebtBlockError(
                f"Cannot start feature '{feature_name}' with unpaid tech debt.\n"
                f"Balance: {balance} credits (threshold: {self.MAX_UNPAID_CREDITS_BEFORE_BLOCK})\n"
                f"Complete ADRs de emergencias previas o paga créditos manualmente."
            )

    def pay_credits(self, credits: int, reason: str) -> None:
        self.state.setdefault("manual_payments", []).append(credits)
        self.state.setdefault("payment_log", []).append({
            "credits": credits,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat(),
        })
        self._save_state()

    # ------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------

    @staticmethod
    def _current_quarter() -> str:
        now = datetime.utcnow()
        q = (now.month - 1) // 3 + 1
        return f"{now.year}-Q{q}"

    def _load_state(self) -> dict:
        if self.state_path.exists():
            return json.loads(self.state_path.read_text())
        return {"quarters": {}, "manual_payments": [], "payment_log": []}

    def _save_state(self) -> None:
        self.state_path.write_text(json.dumps(self.state, indent=2))


# ------------------------------------------------------------
# CLI
# ------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_req = sub.add_parser("request")
    p_req.add_argument("--reason", required=True)

    p_bal = sub.add_parser("balance")

    p_pay = sub.add_parser("pay")
    p_pay.add_argument("--credits", type=int, required=True)
    p_pay.add_argument("--reason", required=True)

    p_check = sub.add_parser("check")
    p_check.add_argument("--feature", required=True)

    args = parser.parse_args()
    tracker = EmergencyBudgetTracker()

    if args.cmd == "request":
        approval = tracker.can_use_emergency_mode(args.reason)
        print(json.dumps(asdict(approval), indent=2))
    elif args.cmd == "balance":
        print(f"Tech debt balance: {tracker.get_tech_debt_balance()} credits")
    elif args.cmd == "pay":
        tracker.pay_credits(args.credits, args.reason)
        print(f"Pagados {args.credits} créditos")
    elif args.cmd == "check":
        try:
            tracker.check_feature_block(args.feature)
            print(f"✅ Feature '{args.feature}' puede iniciarse")
        except TechDebtBlockError as exc:
            print(f"❌ {exc}")
