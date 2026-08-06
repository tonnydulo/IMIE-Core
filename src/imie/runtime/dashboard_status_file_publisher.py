from __future__ import annotations

import os

import errno

import stat

import hmac

import hashlib

from collections.abc import Callable

from time import sleep

from enum import Enum

from dataclasses import dataclass

from uuid import uuid4

from typing import BinaryIO

from pathlib import Path
from threading import RLock

from imie.runtime.analysis_cycle_result import (
    AnalysisCycleResult,
)
from imie.runtime.runtime_dashboard_status import (
    RuntimeDashboardStatus,
)
from imie.runtime.runtime_health_summary import (
    RuntimeHealthSummary,
)

type TemporaryFileIdentity = tuple[
    int,
    int,
]

type TemporaryFileFingerprint = tuple[
    int,
    int,
    int,
    int,
]

_SHA256_READ_CHUNK_SIZE = 64 * 1024

_TEMPORARY_FILE_DISAPPEARED_MESSAGE = (
    "Dashboard temporary file disappeared "
    "before publication."
)

_TEMPORARY_FILE_CHANGED_AFTER_VALIDATION_MESSAGE = (
    "Dashboard temporary file changed "
    "after payload validation."
)

_TEMPORARY_FILE_CHANGED_BEFORE_VALIDATION_MESSAGE = (
    "Dashboard temporary file changed "
    "before payload validation."
)

_TEMPORARY_FILE_SIZE_MISMATCH_MESSAGE = (
    "Dashboard temporary file size does not "
    "match the serialized payload."
)

_TEMPORARY_FILE_DIGEST_MISMATCH_MESSAGE = (
    "Dashboard temporary file digest does not "
    "match the serialized payload."
)

_TEMPORARY_FILE_NOT_REGULAR_MESSAGE = (
    "Dashboard temporary file must be "
    "a regular file."
)

_TEMPORARY_FILE_HARD_LINK_MESSAGE = (
    "Dashboard temporary file must have "
    "exactly one hard link."
)

_EXISTING_DESTINATION_NOT_REGULAR_MESSAGE = (
    "Existing dashboard destination must be "
    "a regular file."
)

_GENERATED_TEMPORARY_PATH_NOT_OWNED_MESSAGE = (
    "Generated temporary path is not owned by "
    "this dashboard publisher."
)

_TEMPORARY_FILE_PATH_NOT_OWNED_MESSAGE = (
    "Dashboard temporary file path is not owned "
    "by this publisher."
)

_TEMPORARY_CLEANUP_PATH_NOT_OWNED_MESSAGE = (
    "temporary_path is not owned by this "
    "dashboard publisher."
)

def _temporary_file_identity(
    status: os.stat_result,
) -> TemporaryFileIdentity:
    return (
        status.st_dev,
        status.st_ino,
    )


def _temporary_file_fingerprint(
    status: os.stat_result,
) -> TemporaryFileFingerprint:
    identity = _temporary_file_identity(
        status
    )

    return (
        *identity,
        status.st_size,
        status.st_mtime_ns,
    )

def _normalize_temporary_file_fingerprint(
    value: object,
) -> TemporaryFileFingerprint:
    if not isinstance(
        value,
        tuple,
    ):
        raise TypeError(
            "Temporary file fingerprint must be "
            "a tuple."
        )

    if len(value) != 4:
        raise ValueError(
            "Temporary file fingerprint must contain "
            "exactly four values."
        )

    if any(
        (
            not isinstance(item, int)
            or isinstance(item, bool)
        )
        for item in value
    ):
        raise TypeError(
            "Temporary file fingerprint values must "
            "be integers."
        )

    if any(
        item < 0
        for item in value
    ):
        raise ValueError(
            "Temporary file fingerprint values must "
            "not be negative."
        )

    return value


def _validate_temporary_file_fingerprint(
    *,
    status: os.stat_result,
    expected_fingerprint: TemporaryFileFingerprint,
) -> None:
    current_fingerprint = (
        _temporary_file_fingerprint(
            status
        )
    )

    if current_fingerprint != expected_fingerprint:
        raise ValueError(
            _TEMPORARY_FILE_CHANGED_AFTER_VALIDATION_MESSAGE
        )

def _sha256_digest_value_error(
    *,
    field_name: str,
) -> ValueError:
    return ValueError(
        f"{field_name} must be a "
        "64-character SHA-256 hexadecimal value."
    )

def _normalize_sha256_digest(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            f"{field_name} must be a string."
        )

    normalized_digest = (
        value.lower()
    )

    if len(normalized_digest) != 64:
        raise _sha256_digest_value_error(
            field_name=field_name
        )

    try:
        digest_bytes = bytes.fromhex(
            normalized_digest
        )
    except ValueError as error:
        raise _sha256_digest_value_error(
            field_name=field_name
        ) from error

    if len(digest_bytes) != 32:
        raise _sha256_digest_value_error(
            field_name=field_name
        )

    return normalized_digest

def _normalize_non_negative_int(
    value: object,
    *,
    field_name: str,
) -> int:
    if (
        not isinstance(value, int)
        or isinstance(value, bool)
    ):
        raise TypeError(
            f"{field_name} must be an integer."
        )

    if value < 0:
        raise ValueError(
            f"{field_name} must not be negative."
        )

    return value

def _normalize_output_path(
    value: object,
) -> Path:
    if not isinstance(
        value,
        str | Path,
    ):
        raise TypeError(
            "path must be a string or Path."
        )

    if (
        isinstance(
            value,
            str,
        )
        and not value.strip()
    ):
        raise ValueError(
            "path cannot be empty."
        )

    return Path(
        value
    )

def _normalize_required_text(
    value: object,
    *,
    field_name: str,
) -> str:
    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            f"{field_name} must be a string."
        )

    normalized = value.strip()

    if not normalized:
        raise ValueError(
            f"{field_name} cannot be empty."
        )

    return normalized

def _normalize_optional_text(
    value: object,
    *,
    field_name: str,
) -> str | None:
    if value is None:
        return None

    if not isinstance(
        value,
        str,
    ):
        raise TypeError(
            f"{field_name} must be a string or None."
        )

    normalized = value.strip()

    return normalized or None

def _normalize_optional_non_negative_int(
    value: object,
    *,
    field_name: str,
) -> int | None:
    if value is None:
        return None

    if (
        not isinstance(
            value,
            int,
        )
        or isinstance(
            value,
            bool,
        )
    ):
        raise TypeError(
            f"{field_name} must be an int or None."
        )

    if value < 0:
        raise ValueError(
            f"{field_name} cannot be negative."
        )

    return value

def _require_instance(
    value: object,
    *,
    expected_type: type,
    field_name: str,
) -> None:
    if not isinstance(
        value,
        expected_type,
    ):
        raise TypeError(
            f"{field_name} must be a "
            f"{expected_type.__name__}."
        )


def _validate_temporary_file_identity(
    *,
    expected_status: os.stat_result,
    opened_status: os.stat_result,
) -> None:
    expected_identity = (
        _temporary_file_identity(
            expected_status
        )
    )
    opened_identity = (
        _temporary_file_identity(
            opened_status
        )
    )

    if opened_identity != expected_identity:
        raise ValueError(
            _TEMPORARY_FILE_CHANGED_BEFORE_VALIDATION_MESSAGE
        )


def _validate_temporary_file_size(
    *,
    status: os.stat_result,
    expected_size: int,
) -> None:
    if status.st_size != expected_size:
        raise ValueError(
            _TEMPORARY_FILE_SIZE_MISMATCH_MESSAGE
        )


def _calculate_open_file_sha256(
    file: BinaryIO,
) -> str:
    digest = hashlib.sha256()

    while True:
        chunk = file.read(
            _SHA256_READ_CHUNK_SIZE
        )

        if not chunk:
            break

        digest.update(
            chunk
        )

    return digest.hexdigest()


def _validate_sha256_digest_match(
    *,
    actual_digest: str,
    expected_digest: str,
    error_message: str,
) -> None:
    if not hmac.compare_digest(
        actual_digest,
        expected_digest,
    ):
        raise ValueError(
            error_message
        )


@dataclass(
    frozen=True,
    slots=True,
)
class TemporaryFileValidationSnapshot:
    fingerprint: TemporaryFileFingerprint
    digest: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "fingerprint",
            _normalize_temporary_file_fingerprint(
                self.fingerprint
            ),
        )

        object.__setattr__(
            self,
            "digest",
            _normalize_sha256_digest(
                self.digest,
                field_name=(
                    "Temporary file digest"
                ),
            ),
        )

@dataclass(
    frozen=True,
    slots=True,
)
class TemporaryFileExpectations:
    size: int
    digest: str

    def __post_init__(
        self,
    ) -> None:
        object.__setattr__(
            self,
            "size",
            _normalize_non_negative_int(
                self.size,
                field_name=(
                    "Expected temporary file size"
                ),
            ),
        )

        object.__setattr__(
            self,
            "digest",
            _normalize_sha256_digest(
                self.digest,
                field_name=(
                    "Expected temporary file digest"
                ),
            ),
        )

class DashboardStatusFilePublisher:
    """
    Maintains the latest unified runtime-dashboard payload.

    The publisher accepts both RuntimeHealthSummary and
    AnalysisCycleResult instances. Each accepted update rewrites
    the dashboard file atomically when a health summary is
    available.
    """

    _REPLACE_MAX_ATTEMPTS = 3
    _REPLACE_RETRY_DELAY_SECONDS = 0.01
    _TEMPORARY_PATH_MAX_ATTEMPTS = 3
    _TRANSIENT_REPLACE_WINERRORS = frozenset(
        {
            5,
            32,
            33,
        }
    )
    _UNSUPPORTED_DIRECTORY_FSYNC_ERRNOS = frozenset(
        {
            errno.EINVAL,
            errno.ENOTSUP,
            errno.EBADF,
            getattr(
                errno,
                "EOPNOTSUPP",
                errno.ENOTSUP,
            ),
        }
    )

    def __init__(
        self,
        path: str | Path,
        *,
        symbol: str,
        timeframe: str,
        indent: int | None = 2,
        create_parent_directories: bool = True,
    ) -> None:
        resolved_path = _normalize_output_path(
            path
        )

        self._symbol = _normalize_required_text(
            symbol,
            field_name="symbol",
        ).upper()

        self._timeframe = _normalize_required_text(
            timeframe,
            field_name="timeframe",
        ).lower()

        indent = _normalize_optional_non_negative_int(
            indent,
            field_name="indent",
        )

        if not isinstance(
            create_parent_directories,
            bool,
        ):
            raise TypeError(
                "create_parent_directories must be a bool."
            )

        self.path = resolved_path
        self.indent = indent
        self.create_parent_directories = (
            create_parent_directories
        )

        self._health: RuntimeHealthSummary | None = None
        self._latest_cycle: AnalysisCycleResult | None = None

        self._market_session: str | None = None
        self._latest_decision: str | None = None

        self._lock = RLock()

    @property
    def health(
        self,
    ) -> RuntimeHealthSummary | None:
        return self._health

    @property
    def latest_cycle(
        self,
    ) -> AnalysisCycleResult | None:
        return self._latest_cycle

    def __call__(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        self.publish_result(
            result
        )


    def publish(
        self,
        value: (
            RuntimeHealthSummary
            | AnalysisCycleResult
        ),
    ) -> None:
        if isinstance(
            value,
            RuntimeHealthSummary,
        ):
            self.publish_health(
                value
            )

            return

        if isinstance(
            value,
            AnalysisCycleResult,
        ):
            self.publish_result(
                value
            )

            return

        raise TypeError(
            "value must be a RuntimeHealthSummary "
            "or AnalysisCycleResult."
        )

    def publish_health(
        self,
        summary: RuntimeHealthSummary,
    ) -> None:
        _require_instance(
            summary,
            expected_type=RuntimeHealthSummary,
            field_name="summary",
        )

        with self._lock:
            self._health = summary
            self._write_if_ready()

    def publish_result(
        self,
        result: AnalysisCycleResult,
    ) -> None:
        _require_instance(
            result,
            expected_type=AnalysisCycleResult,
            field_name="result",
        )

        with self._lock:
            self._latest_cycle = result

            market_session = (
                self._market_session_from_result(
                    result
                )
            )

            if market_session is not None:
                self._market_session = market_session

            latest_decision = (
                self._decision_from_result(
                    result
                )
            )

            if latest_decision is not None:
                self._latest_decision = latest_decision

            self._write_if_ready()

    def update_market_session(
        self,
        market_session: str | None,
    ) -> None:
        def update(
            normalized: str | None,
        ) -> None:
            self._market_session = normalized

        self._update_optional_text(
            field_name="market_session",
            value=market_session,
            update=update,
        )

    def _update_optional_text(
        self,
        *,
        field_name: str,
        value: object,
        update: Callable[[str | None], None],
    ) -> None:
        normalized = _normalize_optional_text(
            value,
            field_name=field_name,
        )

        with self._lock:
            update(
                normalized
            )
            self._write_if_ready()

    def update_latest_decision(
        self,
        latest_decision: str | None,
    ) -> None:
        def update(
            normalized: str | None,
        ) -> None:
            self._latest_decision = normalized

        self._update_optional_text(
            field_name="latest_decision",
            value=latest_decision,
            update=update,
        )

    def build_status(
        self,
    ) -> RuntimeDashboardStatus:
        if self._health is None:
            raise RuntimeError(
                "A health summary is required before "
                "dashboard status can be built."
            )

        cycle = self._latest_cycle

        decision_result = (
            cycle.decision
            if cycle is not None
            else None
        )

        trade_plan = (
            decision_result.trade_plan
            if decision_result is not None
            else None
        )

        institutional_context = (
            decision_result.institutional_context
            if decision_result is not None
            else None
        )

        institutional_bias = (
            institutional_context.institutional_bias
            if institutional_context is not None
            else None
        )

        market_phase = (
            institutional_context.market_phase
            if institutional_context is not None
            else None
        )

        institutional_confluence = (
            institutional_context.institutional_confluence
            if institutional_context is not None
            else None
        )

        setup_lifecycle = (
            institutional_context.setup_lifecycle
            if institutional_context is not None
            else None
        )

        acceptance = (
            institutional_context.acceptance
            if institutional_context is not None
            else None
        )

        trend = (
            institutional_context.trend
            if institutional_context is not None
            else None
        )

        structure_summary = (
            decision_result.analyst_summary.get(
                "STRUCTURE"
            )
            if decision_result is not None
            else None
        )

        liquidity_summary = (
            decision_result.analyst_summary.get(
                "LIQUIDITY"
            )
            if decision_result is not None
            else None
        )

        order_block_summary = (
            decision_result.analyst_summary.get(
                "ORDER_BLOCK"
            )
            if decision_result is not None
            else None
        )

        auction_summary = (
            decision_result.analyst_summary.get(
                "AUCTION"
            )
            if decision_result is not None
            else None
        )

        pressure_summary = (
            decision_result.analyst_summary.get(
                "PRESSURE"
            )
            if decision_result is not None
            else None
        )

        participation_summary = (
            decision_result.analyst_summary.get(
                "PARTICIPATION"
            )
            if decision_result is not None
            else None
        )

        value_summary = (
            decision_result.analyst_summary.get(
                "VALUE"
            )
            if decision_result is not None
            else None
        )

        analyst_summary = (
            decision_result.analyst_summary
            if decision_result is not None
            else {}
        )

        analyst_domain_count = len(
            analyst_summary
        )

        analyst_enabled_count = sum(
            1
            for details in analyst_summary.values()
            if details.get("enabled") is True
        )

        analyst_resolved_count = sum(
            1
            for details in analyst_summary.values()
            if (
                isinstance(
                    details.get("opinion"),
                    str,
                )
                and bool(
                    details.get(
                        "opinion",
                        "",
                    ).strip()
                )
            )
        )

        analyst_enabled_resolved_count = sum(
            1
            for details in analyst_summary.values()
            if (
                details.get("enabled") is True
                and isinstance(
                    details.get("opinion"),
                    str,
                )
                and bool(
                    details.get(
                        "opinion",
                        "",
                    ).strip()
                )
            )
        )

        analyst_enabled_unresolved_count = (
            analyst_enabled_count
            - analyst_enabled_resolved_count
        )

        analyst_confidences: list[float] = []
        analyst_enabled_confidences: list[float] = []

        for details in analyst_summary.values():
            confidence = details.get(
                "confidence"
            )

            confidence_available = (
                details.get(
                    "confidence_available"
                )
                is True
            )

            if (
                confidence_available
                and isinstance(
                    confidence,
                    int | float,
                )
                and not isinstance(
                    confidence,
                    bool,
                )
            ):
                normalized_confidence = float(
                    confidence
                )

                analyst_confidences.append(
                    normalized_confidence
                )

                if details.get("enabled") is True:
                    analyst_enabled_confidences.append(
                        normalized_confidence
                    )

        analyst_confidence_count = len(
            analyst_confidences
        )

        analyst_enabled_confidence_count = len(
            analyst_enabled_confidences
        )

        analyst_missing_confidence_count = max(
            0,
            analyst_domain_count
            - analyst_confidence_count,
        )

        analyst_enabled_missing_confidence_count = max(
            0,
            analyst_enabled_count
            - analyst_enabled_confidence_count,
        )

        analyst_average_confidence = (
            sum(
                analyst_confidences
            )
            / len(
                analyst_confidences
            )
            if analyst_confidences
            else None
        )

        analyst_enabled_average_confidence = (
            sum(
                analyst_enabled_confidences
            )
            / len(
                analyst_enabled_confidences
            )
            if analyst_enabled_confidences
            else None
        )

        analyst_confidence_coverage_percentage = (
            (
                analyst_confidence_count
                / analyst_domain_count
            )
            * 100.0
            if analyst_domain_count > 0
            else 0.0
        )

        analyst_enabled_confidence_coverage_percentage = (
            (
                analyst_enabled_confidence_count
                / analyst_enabled_count
            )
            * 100.0
            if analyst_enabled_count > 0
            else 0.0
        )

        analyst_domain_label = (
            "analyst domain"
            if analyst_domain_count == 1
            else "analyst domains"
        )

        enabled_analyst_domain_label = (
            "enabled analyst domain"
            if analyst_enabled_count == 1
            else "enabled analyst domains"
        )

        if analyst_domain_count == 0:
            analyst_confidence_coverage_state = (
                "UNAVAILABLE"
            )
            analyst_confidence_coverage_message = (
                "No analyst domains are available."
            )

        elif analyst_confidence_count == 0:
            analyst_confidence_coverage_state = (
                "MISSING"
            )
            analyst_confidence_coverage_message = (
                "Confidence is unavailable for all "
                f"{analyst_domain_count} "
                f"{analyst_domain_label}."
            )

        elif (
            analyst_confidence_count
            < analyst_domain_count
        ):
            analyst_confidence_coverage_state = (
                "PARTIAL"
            )
            analyst_confidence_coverage_message = (
                "Confidence is available for "
                f"{analyst_confidence_count} of "
                f"{analyst_domain_count} "
                f"{analyst_domain_label}."
            )

        else:
            analyst_confidence_coverage_state = (
                "COMPLETE"
            )
            analyst_confidence_coverage_message = (
                "Confidence is available for all "
                f"{analyst_domain_count} "
                f"{analyst_domain_label}."
            )


        if analyst_domain_count == 0:
            analyst_enabled_confidence_coverage_state = (
                "UNAVAILABLE"
            )
            analyst_enabled_confidence_coverage_message = (
                "No analyst domains are available."
            )

        elif analyst_enabled_count == 0:
            analyst_enabled_confidence_coverage_state = (
                "DISABLED"
            )
            analyst_enabled_confidence_coverage_message = (
                "No analyst domains are enabled."
            )

        elif analyst_enabled_confidence_count == 0:
            analyst_enabled_confidence_coverage_state = (
                "MISSING"
            )
            analyst_enabled_confidence_coverage_message = (
                "Confidence is unavailable for all "
                f"{analyst_enabled_count} "
                f"{enabled_analyst_domain_label}."
            )

        elif (
            analyst_enabled_confidence_count
            < analyst_enabled_count
        ):
            analyst_enabled_confidence_coverage_state = (
                "PARTIAL"
            )
            analyst_enabled_confidence_coverage_message = (
                "Confidence is available for "
                f"{analyst_enabled_confidence_count} of "
                f"{analyst_enabled_count} "
                f"{enabled_analyst_domain_label}."
            )

        else:
            analyst_enabled_confidence_coverage_state = (
                "COMPLETE"
            )
            analyst_enabled_confidence_coverage_message = (
                "Confidence is available for all "
                f"{analyst_enabled_count} "
                f"{enabled_analyst_domain_label}."
            )

        analyst_coverage_percentage = (
            (
                analyst_resolved_count
                / analyst_domain_count
            )
            * 100.0
            if analyst_domain_count > 0
            else 0.0
        )

        analyst_operational_percentage = (
            (
                analyst_enabled_resolved_count
                / analyst_enabled_count
            )
            * 100.0
            if analyst_enabled_count > 0
            else 0.0
        )

        if analyst_domain_count == 0:
            analyst_coverage_state = "UNAVAILABLE"
            analyst_coverage_message = (
                "No analyst domains are available."
            )
        elif analyst_resolved_count == 0:
            analyst_coverage_state = "UNRESOLVED"
            analyst_coverage_message = (
                "Analyst domains are available, but none "
                "have produced an opinion."
            )
        elif analyst_resolved_count < analyst_domain_count:
            analyst_coverage_state = "PARTIAL"
            analyst_coverage_message = (
                f"{analyst_resolved_count} of "
                f"{analyst_domain_count} analyst domains "
                "have produced an opinion."
            )
        else:
            analyst_coverage_state = "COMPLETE"
            analyst_coverage_message = (
                f"All {analyst_domain_count} analyst domains "
                "have produced an opinion."
            )

        if analyst_domain_count == 0:
            analyst_operational_status = "UNAVAILABLE"
            analyst_operational_message = (
                "No analyst domains are available."
            )
        elif analyst_enabled_count == 0:
            analyst_operational_status = "DISABLED"
            analyst_operational_message = (
                "All analyst domains are disabled."
            )
        elif analyst_enabled_resolved_count == 0:
            analyst_operational_status = "UNRESOLVED"
            analyst_operational_message = (
                "Enabled analyst domains have not "
                "produced an opinion."
            )
        elif (
            analyst_enabled_resolved_count
            < analyst_enabled_count
        ):
            analyst_operational_status = "DEGRADED"
            analyst_operational_message = (
                f"{analyst_enabled_resolved_count} of "
                f"{analyst_enabled_count} enabled analyst "
                "domains have produced an opinion."
            )
        else:
            analyst_operational_status = "OPERATIONAL"
            analyst_operational_message = (
                f"All {analyst_enabled_count} enabled analyst "
                "domains have produced an opinion."
            )

        return RuntimeDashboardStatus(
            health=self._health,
            symbol=(
                cycle.symbol
                if cycle is not None
                else self._symbol
            ),
            timeframe=(
                cycle.timeframe
                if cycle is not None
                else self._timeframe
            ),
            latest_cycle_status=(
                cycle.status
                if cycle is not None
                else None
            ),
            latest_cycle_message=(
                cycle.message
                if cycle is not None
                else None
            ),
            latest_cycle_started_at=(
                cycle.started_at
                if cycle is not None
                else None
            ),
            latest_cycle_completed_at=(
                cycle.completed_at
                if cycle is not None
                else None
            ),
            market_session=self._market_session,
            latest_decision=self._latest_decision,
            decision_confidence=(
                float(
                    decision_result.confidence
                )
                if decision_result is not None
                else None
            ),
            decision_actionable=(
                decision_result.actionable
                if decision_result is not None
                else None
            ),
            decision_recommendation=(
                decision_result.recommendation
                if decision_result is not None
                else None
            ),
            decision_reasons=(
                tuple(
                    decision_result.reasons
                )
                if decision_result is not None
                else ()
            ),
            decision_warnings=(
                tuple(
                    decision_result.warnings
                )
                if decision_result is not None
                else ()
            ),
            analyst_summary=(
                {
                    analyst_id: dict(details)
                    for analyst_id, details
                    in decision_result.analyst_summary.items()
                }
                if decision_result is not None
                else {}
            ),
            trade_direction=(
                self._display_value(
                    trade_plan.direction
                )
                if trade_plan is not None
                else None
            ),

            trade_plan_valid=(
                trade_plan.valid
                if trade_plan is not None
                else None
            ),
            trade_entry=(
                trade_plan.entry
                if trade_plan is not None
                else None
            ),
            trade_stop=(
                trade_plan.stop
                if trade_plan is not None
                else None
            ),
            trade_target1=(
                trade_plan.target1
                if trade_plan is not None
                else None
            ),
            trade_target2=(
                trade_plan.target2
                if trade_plan is not None
                else None
            ),
            trade_rr1=(
                trade_plan.rr1
                if trade_plan is not None
                else None
            ),
            trade_rr2=(
                trade_plan.rr2
                if trade_plan is not None
                else None
            ),
            trade_quality=(
                trade_plan.quality
                if trade_plan is not None
                else None
            ),

            trade_narrative=(
                trade_plan.narrative
                if trade_plan is not None
                else None
            ),
            trade_reasons=(
                tuple(
                    trade_plan.reasons
                )
                if trade_plan is not None
                else ()
            ),
            trade_warnings=(
                tuple(
                    trade_plan.warnings
                )
                if trade_plan is not None
                else ()
            ),

            institutional_bias=(
                institutional_bias.direction.value
                if institutional_bias is not None
                else None
            ),
            institutional_bias_confidence=(
                institutional_bias.confidence
                if institutional_bias is not None
                else None
            ),
            institutional_bias_strength=(
                institutional_bias.strength
                if institutional_bias is not None
                else None
            ),
            institutional_bias_bullish_score=(
                institutional_bias.bullish_score
                if institutional_bias is not None
                else None
            ),
            institutional_bias_bearish_score=(
                institutional_bias.bearish_score
                if institutional_bias is not None
                else None
            ),
            institutional_bias_agreement_count=(
                institutional_bias.agreement_count
                if institutional_bias is not None
                else None
            ),
            institutional_bias_conflict_count=(
                institutional_bias.conflict_count
                if institutional_bias is not None
                else None
            ),
            institutional_bias_supporting_domains=(
                tuple(
                    institutional_bias.supporting_domains
                )
                if institutional_bias is not None
                else ()
            ),
            institutional_bias_opposing_domains=(
                tuple(
                    institutional_bias.opposing_domains
                )
                if institutional_bias is not None
                else ()
            ),
            market_phase=(
                market_phase.phase.value
                if market_phase is not None
                else None
            ),
            market_phase_confidence=(
                market_phase.confidence
                if market_phase is not None
                else None
            ),
            confluence_direction=(
                institutional_confluence
                .dominant_direction
                .value
                if institutional_confluence is not None
                else None
            ),
            confluence_score=(
                institutional_confluence.score
                if institutional_confluence is not None
                else None
            ),
            confluence_agreement_count=(
                institutional_confluence.agreement_count
                if institutional_confluence is not None
                else None
            ),
            confluence_conflict_count=(
                institutional_confluence.conflict_count
                if institutional_confluence is not None
                else None
            ),
            confluence_confidence_adjustment=(
                institutional_confluence.confidence_adjustment
                if institutional_confluence is not None
                else None
            ),
            confluence_structure_support=(
                institutional_confluence.structure_support
                if institutional_confluence is not None
                else None
            ),
            confluence_liquidity_support=(
                institutional_confluence.liquidity_support
                if institutional_confluence is not None
                else None
            ),
            confluence_order_block_support=(
                institutional_confluence.order_block_support
                if institutional_confluence is not None
                else None
            ),
            confluence_auction_support=(
                institutional_confluence.auction_support
                if institutional_confluence is not None
                else None
            ),
            confluence_pressure_support=(
                institutional_confluence.pressure_support
                if institutional_confluence is not None
                else None
            ),
            confluence_participation_support=(
                institutional_confluence.participation_support
                if institutional_confluence is not None
                else None
            ),
            confluence_value_support=(
                institutional_confluence.value_support
                if institutional_confluence is not None
                else None
            ),
            confluence_bullish_count=(
                institutional_confluence.bullish_count
                if institutional_confluence is not None
                else None
            ),
            confluence_bearish_count=(
                institutional_confluence.bearish_count
                if institutional_confluence is not None
                else None
            ),
            confluence_neutral_count=(
                institutional_confluence.neutral_count
                if institutional_confluence is not None
                else None
            ),
            confluence_unknown_count=(
                institutional_confluence.unknown_count
                if institutional_confluence is not None
                else None
            ),
            confluence_domain_count=(
                institutional_confluence.domain_count
                if institutional_confluence is not None
                else None
            ),
            market_phase_strength=(
                market_phase.strength
                if market_phase is not None
                else None
            ),
            market_phase_agreement_count=(
                market_phase.agreement_count
                if market_phase is not None
                else None
            ),
            market_phase_conflict_count=(
                market_phase.conflict_count
                if market_phase is not None
                else None
            ),
            market_phase_supporting_domains=(
                tuple(
                    market_phase.supporting_domains
                )
                if market_phase is not None
                else ()
            ),
            market_phase_opposing_domains=(
                tuple(
                    market_phase.opposing_domains
                )
                if market_phase is not None
                else ()
            ),

            setup_lifecycle_state=(
                setup_lifecycle.state
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_direction=(
                setup_lifecycle.direction
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_confidence=(
                setup_lifecycle.confidence
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_atr_distance=(
                setup_lifecycle.atr_distance
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_action=(
                setup_lifecycle.action
                if setup_lifecycle is not None
                else None
            ),
            setup_lifecycle_reason=(
                setup_lifecycle.reason
                if setup_lifecycle is not None
                else None
            ),
            acceptance_confirmed=(
                acceptance.accepted
                if acceptance is not None
                else None
            ),
            acceptance_direction=(
                acceptance.direction
                if acceptance is not None
                else None
            ),
            acceptance_level=(
                acceptance.level
                if acceptance is not None
                else None
            ),
            acceptance_score=(
                acceptance.score
                if acceptance is not None
                else None
            ),
            acceptance_confidence=(
                acceptance.confidence
                if acceptance is not None
                else None
            ),
            acceptance_trigger_price=(
                acceptance.trigger_price
                if acceptance is not None
                else None
            ),
            acceptance_previous_level=(
                acceptance.previous_level
                if acceptance is not None
                else None
            ),
            acceptance_pullback_low=(
                acceptance.pullback_low
                if acceptance is not None
                else None
            ),
            acceptance_pullback_high=(
                acceptance.pullback_high
                if acceptance is not None
                else None
            ),
            acceptance_reason=(
                acceptance.reason
                if acceptance is not None
                else None
            ),
            acceptance_evidence=(
                tuple(
                    acceptance.evidence
                )
                if acceptance is not None
                else ()
            ),
            acceptance_warnings=(
                tuple(
                    acceptance.warnings
                )
                if acceptance is not None
                else ()
            ),

            trend_analyst=(
                trend.analyst
                if trend is not None
                else None
            ),
            trend_opinion=(
                trend.opinion
                if trend is not None
                else None
            ),
            trend_confidence=(
                trend.confidence
                if trend is not None
                else None
            ),
            trend_enabled=(
                trend.enabled
                if trend is not None
                else None
            ),
            trend_evidence=(
                tuple(
                    trend.evidence
                )
                if trend is not None
                else ()
            ),
            trend_warnings=(
                tuple(
                    trend.warnings
                )
                if trend is not None
                else ()
            ),

            structure_analyst=(
                "STRUCTURE"
                if structure_summary is not None
                else None
            ),
            structure_opinion=(
                structure_summary.get(
                    "opinion"
                )
                if structure_summary is not None
                else None
            ),
            structure_confidence=(
                structure_summary.get(
                    "confidence"
                )
                if structure_summary is not None
                else None
            ),
            structure_enabled=(
                structure_summary.get(
                    "enabled"
                )
                if structure_summary is not None
                else None
            ),

            liquidity_analyst=(
                "LIQUIDITY"
                if liquidity_summary is not None
                else None
            ),
            liquidity_opinion=(
                liquidity_summary.get(
                    "opinion"
                )
                if liquidity_summary is not None
                else None
            ),
            liquidity_confidence=(
                liquidity_summary.get(
                    "confidence"
                )
                if liquidity_summary is not None
                else None
            ),
            liquidity_enabled=(
                liquidity_summary.get(
                    "enabled"
                )
                if liquidity_summary is not None
                else None
            ),

            order_block_analyst=(
                "ORDER_BLOCK"
                if order_block_summary is not None
                else None
            ),
            order_block_opinion=(
                order_block_summary.get(
                    "opinion"
                )
                if order_block_summary is not None
                else None
            ),
            order_block_confidence=(
                order_block_summary.get(
                    "confidence"
                )
                if order_block_summary is not None
                else None
            ),
            order_block_enabled=(
                order_block_summary.get(
                    "enabled"
                )
                if order_block_summary is not None
                else None
            ),
            auction_analyst=(
                "AUCTION"
                if auction_summary is not None
                else None
            ),
            auction_opinion=(
                auction_summary.get(
                    "opinion"
                )
                if auction_summary is not None
                else None
            ),
            auction_confidence=(
                auction_summary.get(
                    "confidence"
                )
                if auction_summary is not None
                else None
            ),
            auction_enabled=(
                auction_summary.get(
                    "enabled"
                )
                if auction_summary is not None
                else None
            ),
            pressure_analyst=(
                "PRESSURE"
                if pressure_summary is not None
                else None
            ),
            pressure_opinion=(
                pressure_summary.get(
                    "opinion"
                )
                if pressure_summary is not None
                else None
            ),
            pressure_confidence=(
                pressure_summary.get(
                    "confidence"
                )
                if pressure_summary is not None
                else None
            ),
            pressure_enabled=(
                pressure_summary.get(
                    "enabled"
                )
                if pressure_summary is not None
                else None
            ),
            participation_analyst=(
                "PARTICIPATION"
                if participation_summary is not None
                else None
            ),
            participation_opinion=(
                participation_summary.get(
                    "opinion"
                )
                if participation_summary is not None
                else None
            ),
            participation_confidence=(
                participation_summary.get(
                    "confidence"
                )
                if participation_summary is not None
                else None
            ),
            participation_enabled=(
                participation_summary.get(
                    "enabled"
                )
                if participation_summary is not None
                else None
            ),

            value_analyst=(
                "VALUE"
                if value_summary is not None
                else None
            ),
            value_opinion=(
                value_summary.get(
                    "opinion"
                )
                if value_summary is not None
                else None
            ),
            value_confidence=(
                value_summary.get(
                    "confidence"
                )
                if value_summary is not None
                else None
            ),
            value_enabled=(
                value_summary.get(
                    "enabled"
                )
                if value_summary is not None
                else None
            ),

            analyst_domain_count=(
                analyst_domain_count
            ),
            analyst_enabled_count=(
                analyst_enabled_count
            ),
            analyst_resolved_count=(
                analyst_resolved_count
            ),
            analyst_enabled_resolved_count=(
                analyst_enabled_resolved_count
            ),
            analyst_enabled_unresolved_count=(
                analyst_enabled_unresolved_count
            ),
            analyst_confidence_count=(
                analyst_confidence_count
            ),
            analyst_enabled_confidence_count=(
                analyst_enabled_confidence_count
            ),
            analyst_missing_confidence_count=(
                analyst_missing_confidence_count
            ),
            analyst_enabled_missing_confidence_count=(
                analyst_enabled_missing_confidence_count
            ),
            analyst_average_confidence=(
                analyst_average_confidence
            ),
            analyst_confidence_coverage_percentage=(
                analyst_confidence_coverage_percentage
            ),
            analyst_enabled_confidence_coverage_percentage=(
                analyst_enabled_confidence_coverage_percentage
            ),
            analyst_confidence_coverage_state=(
                analyst_confidence_coverage_state
            ),
            analyst_confidence_coverage_message=(
                analyst_confidence_coverage_message
            ),
            analyst_enabled_confidence_coverage_state=(
                analyst_enabled_confidence_coverage_state
            ),
            analyst_enabled_confidence_coverage_message=(
                analyst_enabled_confidence_coverage_message
            ),
            analyst_coverage_percentage=(
                analyst_coverage_percentage
            ),
            analyst_coverage_state=(
                analyst_coverage_state
            ),
            analyst_coverage_message=(
                analyst_coverage_message
            ),
            analyst_operational_status=(
                analyst_operational_status
            ),
            analyst_operational_message=(
                analyst_operational_message
            ),
            analyst_operational_percentage=(
                analyst_operational_percentage
            ),
            analyst_enabled_average_confidence=(
                analyst_enabled_average_confidence
            ),
            latest_error_type=(
                cycle.error_type
                if cycle is not None
                else None
            ),
        )

    def _apply_existing_destination_mode(
        self,
        temporary_path: Path,
    ) -> None:
        destination_status = (
            _existing_destination_status(
                self.path
            )
        )

        if destination_status is None:
            return

        destination_mode = stat.S_IMODE(
            destination_status.st_mode
        )

        temporary_path.chmod(
            destination_mode
        )

    def _write_if_ready(
        self,
    ) -> None:
        if self._health is None:
            return

        if self.create_parent_directories:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        status = self.build_status()

        payload = status.to_json(
            indent=self.indent
        )

        serialized_payload = (
            payload + "\n"
        )

        serialized_payload_bytes = (
            serialized_payload.encode(
                "utf-8"
            )
        )

        expectations = TemporaryFileExpectations(
            size=len(
                serialized_payload_bytes
            ),
            digest=hashlib.sha256(
                serialized_payload_bytes
            ).hexdigest(),
        )

        temporary_path = (
            self._write_temporary_payload(
                payload=payload,
            )
        )

        try:
            self._apply_existing_destination_mode(
                temporary_path
            )

            validation_snapshot = (
                self._validate_temporary_file(
                    temporary_path,
                    expectations=expectations,
                )
            )

            self._replace_atomically(
                temporary_path=temporary_path,
                expected_snapshot=validation_snapshot,
            )

        except Exception:
            self._remove_temporary_file(
                temporary_path,
                suppress_errors=True,
            )

            raise

        else:
            self._remove_temporary_file(
                temporary_path,
                suppress_errors=False,
            )

    def _build_temporary_path(
        self,
    ) -> Path:
        return self.path.with_name(
            f".{self.path.name}.{uuid4().hex}.tmp"
        )

    def _replace_atomically(
        self,
        *,
        temporary_path: Path,
        expected_snapshot: TemporaryFileValidationSnapshot,
    ) -> None:
        for attempt in range(
            1,
            self._REPLACE_MAX_ATTEMPTS + 1,
        ):
            self._validate_temporary_file_snapshot(
                temporary_path,
                expected_snapshot=expected_snapshot,
            )

            try:
                os.replace(
                    temporary_path,
                    self.path,
                )

            except PermissionError as error:
                if not self._is_transient_replace_error(
                    error
                ):
                    raise

                if _is_final_attempt(
                    attempt=attempt,
                    maximum_attempts=(
                        self._REPLACE_MAX_ATTEMPTS
                    ),
                ):
                    raise

                sleep(
                    self._REPLACE_RETRY_DELAY_SECONDS
                )

                continue

            self._sync_parent_directory()
            return


    def _is_owned_temporary_path(
        self,
        path: Path,
    ) -> bool:
        return _is_owned_temporary_path(
            path=path,
            destination_path=self.path,
        )

    def _validate_owned_temporary_path(
        self,
        path: Path,
        *,
        error_message: str,
    ) -> None:
        _validate_owned_temporary_path_for_destination(
            path=path,
            destination_path=self.path,
            error_message=error_message,
        )


    def _validate_temporary_file(
        self,
        temporary_path: Path,
        *,
        expectations: TemporaryFileExpectations,
    ) -> TemporaryFileValidationSnapshot:
        self._validate_owned_temporary_path(
            temporary_path,
            error_message=(
                _TEMPORARY_FILE_PATH_NOT_OWNED_MESSAGE
            ),
        )

        temporary_status = (
            _validated_temporary_path_status(
                temporary_path
            )
        )

        with _open_temporary_file(
            temporary_path
        ) as temporary_file:
            opened_status = (
                _validated_open_file_status(
                    temporary_file
                )
            )

            _validate_temporary_file_identity(
                expected_status=temporary_status,
                opened_status=opened_status,
            )

            _validate_temporary_file_size(
                status=opened_status,
                expected_size=expectations.size,
            )

            actual_digest = (
                _calculate_open_file_sha256(
                    temporary_file
                )
            )

        _validate_sha256_digest_match(
            actual_digest=actual_digest,
            expected_digest=expectations.digest,
            error_message=(
                _TEMPORARY_FILE_DIGEST_MISMATCH_MESSAGE
            ),
        )

        return TemporaryFileValidationSnapshot(
            fingerprint=(
                _temporary_file_fingerprint(
                    opened_status
                )
            ),
            digest=actual_digest,
        )


    @staticmethod
    def _directory_open_flags(
    ) -> int:
        return (
            os.O_RDONLY
            | getattr(
                os,
                "O_DIRECTORY",
                0,
            )
            | getattr(
                os,
                "O_CLOEXEC",
                0,
            )
        )

    @staticmethod
    def _supports_directory_fsync(
    ) -> bool:
        return os.name == "posix"

    def _sync_parent_directory(
        self,
    ) -> None:
        if not self._supports_directory_fsync():
            return

        try:
            directory_descriptor = os.open(
                self.path.parent,
                self._directory_open_flags(),
            )

        except OSError as error:
            if self._is_unsupported_directory_fsync_error(
                error
            ):
                return

            raise

        sync_error: OSError | None = None

        try:
            try:
                os.fsync(
                    directory_descriptor
                )

            except OSError as error:
                if self._is_unsupported_directory_fsync_error(
                    error
                ):
                    return

                sync_error = error
                raise

        finally:
            try:
                os.close(
                    directory_descriptor
                )

            except OSError:
                if sync_error is None:
                    raise

    def _write_temporary_payload(
        self,
        *,
        payload: str,
    ) -> Path:
        for attempt in range(
            1,
            self._TEMPORARY_PATH_MAX_ATTEMPTS + 1,
        ):
            temporary_path = (
                self._build_temporary_path()
            )

            self._validate_owned_temporary_path(
                temporary_path,
                error_message=(
                    _GENERATED_TEMPORARY_PATH_NOT_OWNED_MESSAGE
                ),
            )

            try:
                with temporary_path.open(
                    mode="x",
                    encoding="utf-8",
                    newline="",
                ) as temporary_file:
                    temporary_file.write(
                        payload + "\n"
                    )
                    temporary_file.flush()
                    os.fsync(
                        temporary_file.fileno()
                    )

            except FileExistsError:
                if _is_final_attempt(
                    attempt=attempt,
                    maximum_attempts=(
                        self._TEMPORARY_PATH_MAX_ATTEMPTS
                    ),
                ):
                    raise

                continue

            except Exception:
                self._remove_temporary_file(
                    temporary_path,
                    suppress_errors=True,
                )

                raise

            return temporary_path


    @classmethod
    def _is_transient_replace_error(
        cls,
        error: PermissionError,
    ) -> bool:
        return (
            getattr(
                error,
                "winerror",
                None,
            )
            in cls._TRANSIENT_REPLACE_WINERRORS
        )

    @classmethod
    def _is_unsupported_directory_fsync_error(
        cls,
        error: OSError,
    ) -> bool:
        return (
            error.errno
            in cls._UNSUPPORTED_DIRECTORY_FSYNC_ERRNOS
        )

    def _remove_temporary_file(
        self,
        temporary_path: Path,
        *,
        suppress_errors: bool,
    ) -> None:
        self._validate_owned_temporary_path(
            temporary_path,
            error_message=(
                _TEMPORARY_CLEANUP_PATH_NOT_OWNED_MESSAGE
            ),
        )

        try:
            temporary_path.unlink(
                missing_ok=True
            )

        except OSError:
            if not suppress_errors:
                raise

    @staticmethod
    def _display_value(
        value: object | None,
    ) -> str | None:
        if value is None:
            return None

        if isinstance(
            value,
            Enum,
        ):
            value = value.value

        normalized = str(
            value
        ).strip()

        return normalized or None

    @classmethod
    def _market_session_from_result(
        cls,
        result: AnalysisCycleResult,
    ) -> str | None:
        if result.market_session is None:
            return None

        return cls._display_value(
            result.market_session.state
        )

    @classmethod
    def _decision_from_result(
        cls,
        result: AnalysisCycleResult,
    ) -> str | None:
        if result.decision is None:
            return None

        return cls._display_value(
            result.decision.decision
        )

    def _validate_temporary_file_snapshot(
        self,
        temporary_path: Path,
        *,
        expected_snapshot: TemporaryFileValidationSnapshot,
    ) -> None:
        with _open_temporary_file(
            temporary_path
        ) as temporary_file:
            current_status = (
                _validated_open_file_status(
                    temporary_file
                )
            )

            _validate_temporary_file_fingerprint(
                status=current_status,
                expected_fingerprint=(
                    expected_snapshot.fingerprint
                ),
            )

            current_digest = (
                _calculate_open_file_sha256(
                    temporary_file
                )
            )

        _validate_sha256_digest_match(
            actual_digest=current_digest,
            expected_digest=expected_snapshot.digest,
            error_message=(
                _TEMPORARY_FILE_CHANGED_AFTER_VALIDATION_MESSAGE
            ),
        )

def _validate_temporary_file_status(
    status: os.stat_result,
) -> None:
    if not stat.S_ISREG(
        status.st_mode
    ):
        raise ValueError(
            _TEMPORARY_FILE_NOT_REGULAR_MESSAGE
        )

    if status.st_nlink != 1:
        raise ValueError(
            _TEMPORARY_FILE_HARD_LINK_MESSAGE
        )

def _validated_open_file_status(
    file: BinaryIO,
) -> os.stat_result:
    status = os.fstat(
        file.fileno()
    )

    _validate_temporary_file_status(
        status
    )

    return status

def _validated_temporary_path_status(
    path: Path,
) -> os.stat_result:
    try:
        status = path.lstat()
    except FileNotFoundError as error:
        raise FileNotFoundError(
            _TEMPORARY_FILE_DISAPPEARED_MESSAGE
        ) from error

    _validate_temporary_file_status(
        status
    )

    return status

def _existing_destination_status(
    path: Path,
) -> os.stat_result | None:
    try:
        status = path.lstat()
    except FileNotFoundError:
        return None

    if not stat.S_ISREG(
        status.st_mode
    ):
        raise ValueError(
            _EXISTING_DESTINATION_NOT_REGULAR_MESSAGE
        )

    return status

def _is_final_attempt(
    *,
    attempt: int,
    maximum_attempts: int,
) -> bool:
    return attempt >= maximum_attempts

def _open_temporary_file(
    path: Path,
) -> BinaryIO:
    try:
        return open(
            path,
            "rb",
            buffering=0,
        )
    except FileNotFoundError as error:
        raise FileNotFoundError(
            _TEMPORARY_FILE_DISAPPEARED_MESSAGE
        ) from error

def _validate_owned_temporary_path_for_destination(
    *,
    path: Path,
    destination_path: Path,
    error_message: str,
) -> None:
    if not _is_owned_temporary_path(
        path=path,
        destination_path=destination_path,
    ):
        raise ValueError(
            error_message
        )

def _is_owned_temporary_path(
    *,
    path: Path,
    destination_path: Path,
) -> bool:
    prefix = (
        f".{destination_path.name}."
    )
    suffix = ".tmp"

    if (
        path.parent != destination_path.parent
        or path == destination_path
        or not path.name.startswith(
            prefix
        )
        or not path.name.endswith(
            suffix
        )
    ):
        return False

    token = path.name[
        len(prefix):
        -len(suffix)
    ]

    return (
        len(token) == 32
        and all(
            character in "0123456789abcdef"
            for character in token
        )
    )
