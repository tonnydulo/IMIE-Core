from __future__ import annotations

import hashlib
import json

from imie.models import ExecutionCandidate, ExecutionOrderIntent


class ExecutionSubmissionFingerprint:
    """Create a stable digest from the exact candidate/intent submission pair."""

    @staticmethod
    def create(
        *, candidate: ExecutionCandidate, intent: ExecutionOrderIntent
    ) -> str:
        if not isinstance(candidate, ExecutionCandidate):
            raise TypeError("candidate must be an ExecutionCandidate.")
        if not isinstance(intent, ExecutionOrderIntent):
            raise TypeError("intent must be an ExecutionOrderIntent.")
        payload = {
            "candidate": {
                "symbol": candidate.symbol,
                "strategy": candidate.strategy,
                "direction": candidate.direction,
                "quantity": candidate.quantity,
                "entry": candidate.entry,
                "stop": candidate.stop,
                "target1": candidate.target1,
                "target2": candidate.target2,
                "position_notional": candidate.position_notional,
                "risk_amount": candidate.risk_amount,
                "valid": candidate.valid,
                "actionable": candidate.actionable,
            },
            "intent": {
                "symbol": intent.symbol,
                "side": intent.side,
                "quantity": intent.quantity,
                "order_type": intent.order_type,
                "entry_price": intent.entry_price,
                "stop_price": intent.stop_price,
                "target1_price": intent.target1_price,
                "target2_price": intent.target2_price,
                "time_in_force": intent.time_in_force,
                "valid": intent.valid,
                "actionable": intent.actionable,
            },
        }
        serialized = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
        return hashlib.sha256(serialized).hexdigest()
