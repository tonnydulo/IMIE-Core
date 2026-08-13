from __future__ import annotations

from imie.models import (
    BrokerOrderSnapshot,
    BrokerOrderStatus,
    ExistingPositionProtectionResult,
    PositionProtectionReconciliationResult,
)


class PositionProtectionReconciliationEngine:
    """Compare accepted protective submissions with broker order truth."""

    _ACTIVE = {
        BrokerOrderStatus.PENDING_SUBMISSION,
        BrokerOrderStatus.SUBMITTED,
        BrokerOrderStatus.ACCEPTED,
        BrokerOrderStatus.PARTIALLY_FILLED,
        BrokerOrderStatus.PENDING_CANCEL,
    }
    _TERMINAL = {
        BrokerOrderStatus.CANCELED,
        BrokerOrderStatus.REJECTED,
        BrokerOrderStatus.EXPIRED,
        BrokerOrderStatus.REPLACED,
    }

    def reconcile(
        self,
        *,
        protection: ExistingPositionProtectionResult,
        snapshots: tuple[BrokerOrderSnapshot, ...],
    ) -> PositionProtectionReconciliationResult:
        if not isinstance(protection, ExistingPositionProtectionResult):
            raise TypeError(
                "protection must be an ExistingPositionProtectionResult."
            )
        if not protection.accepted:
            raise ValueError("protection must be an accepted result.")
        if not isinstance(snapshots, tuple) or not all(
            isinstance(item, BrokerOrderSnapshot) for item in snapshots
        ):
            raise TypeError("snapshots must be a tuple of BrokerOrderSnapshot.")

        by_id: dict[str, BrokerOrderSnapshot] = {}
        discrepancies: list[str] = []
        warnings: list[str] = list(protection.warnings)
        for snapshot in snapshots:
            if snapshot.broker_order_id in by_id:
                discrepancies.append(
                    f"Duplicate snapshot for order {snapshot.broker_order_id!r}."
                )
            by_id[snapshot.broker_order_id] = snapshot
            warnings.extend(snapshot.warnings)

        active_quantity = 0
        triggered_quantity = 0
        slice_states: list[str] = []
        expected_ids: set[str] = set()
        for submission in protection.submissions:
            order_ids = (submission.target_order_id, submission.stop_order_id)
            if any(order_id is None for order_id in order_ids):
                discrepancies.append(
                    f"Accepted {submission.label} submission lacks broker order IDs."
                )
                slice_states.append("indeterminate")
                continue
            expected_ids.update(order_ids)  # type: ignore[arg-type]
            pair = tuple(by_id.get(order_id) for order_id in order_ids)
            missing = [
                order_id
                for order_id, snapshot in zip(order_ids, pair)
                if snapshot is None
            ]
            if missing:
                discrepancies.append(
                    f"{submission.label} is missing broker snapshots: "
                    + ", ".join(missing)  # type: ignore[arg-type]
                    + "."
                )
                slice_states.append("indeterminate")
                continue
            valid_pair = True
            for snapshot in pair:
                assert snapshot is not None
                for label, expected, actual in (
                    ("broker", protection.broker, snapshot.broker),
                    ("symbol", protection.symbol, snapshot.symbol),
                    ("side", protection.exit_side, snapshot.side),
                    ("quantity", submission.quantity, snapshot.requested_quantity),
                ):
                    if expected != actual:
                        valid_pair = False
                        discrepancies.append(
                            f"{submission.label} {label} does not match broker truth: "
                            f"{expected!r} != {actual!r}."
                        )
            if not valid_pair:
                slice_states.append("indeterminate")
                continue
            statuses = {snapshot.status for snapshot in pair if snapshot is not None}
            if BrokerOrderStatus.FILLED in statuses:
                triggered_quantity += submission.quantity
                slice_states.append("triggered")
            elif statuses <= self._ACTIVE:
                active_quantity += submission.quantity
                slice_states.append("active")
            elif statuses <= self._TERMINAL:
                slice_states.append("terminal")
            elif statuses & self._ACTIVE and statuses & self._TERMINAL:
                slice_states.append("degraded")
            else:
                slice_states.append("indeterminate")

        unexpected = set(by_id) - expected_ids
        if unexpected:
            discrepancies.append(
                "Unexpected broker snapshots: " + ", ".join(sorted(unexpected)) + "."
            )
        state = self._state(slice_states, discrepancies)
        return PositionProtectionReconciliationResult(
            broker=protection.broker,
            symbol=protection.symbol,
            state=state,
            requested_quantity=protection.requested_quantity,
            active_quantity=active_quantity,
            triggered_quantity=triggered_quantity,
            reconciled=not discrepancies and state != "indeterminate",
            snapshots=snapshots,
            discrepancies=tuple(discrepancies),
            warnings=tuple(warnings),
        )

    @staticmethod
    def _state(slice_states: list[str], discrepancies: list[str]) -> str:
        if discrepancies or "indeterminate" in slice_states:
            return "indeterminate"
        if "triggered" in slice_states:
            return "triggered"
        if slice_states and all(state == "active" for state in slice_states):
            return "active"
        if slice_states and all(state == "terminal" for state in slice_states):
            return "terminal_unprotected"
        return "degraded"
