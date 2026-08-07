from __future__ import annotations

import os

import errno

import stat

import hmac

import hashlib

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


def _directory_open_flags() -> int:
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


def _is_transient_replace_error(
    error: PermissionError,
) -> bool:
    return (
        getattr(
            error,
            "winerror",
            None,
        )
        in _TRANSIENT_REPLACE_WINERRORS
    )


def _is_unsupported_directory_fsync_error(
    error: OSError,
) -> bool:
    return (
        error.errno
        in _UNSUPPORTED_DIRECTORY_FSYNC_ERRNOS
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

def _has_resolved_analyst_opinion(
    details: dict[str, object],
) -> bool:
    opinion = details.get(
        "opinion"
    )

    return (
        isinstance(
            opinion,
            str,
        )
        and bool(
            opinion.strip()
        )
    )

def _analyst_confidence_value(
    details: dict[str, object],
) -> float | None:
    confidence = details.get(
        "confidence"
    )

    if (
        details.get(
            "confidence_available"
        )
        is not True
    ):
        return None

    if (
        not isinstance(
            confidence,
            int | float,
        )
        or isinstance(
            confidence,
            bool,
        )
    ):
        return None

    return float(
        confidence
    )

def _analyst_confidence_values(
    analyst_summary: dict[str, dict[str, object]],
) -> tuple[
    tuple[float, ...],
    tuple[float, ...],
]:
    confidences: list[float] = []
    enabled_confidences: list[float] = []

    for details in analyst_summary.values():
        confidence = _analyst_confidence_value(
            details
        )

        if confidence is None:
            continue

        confidences.append(
            confidence
        )

        if details.get("enabled") is True:
            enabled_confidences.append(
                confidence
            )

    return (
        tuple(confidences),
        tuple(enabled_confidences),
    )

def _analyst_confidence_metrics(
    *,
    analyst_domain_count: int,
    analyst_enabled_count: int,
    analyst_confidences: tuple[float, ...],
    analyst_enabled_confidences: tuple[float, ...],
) -> tuple[
    int,
    int,
    int,
    int,
    float | None,
    float | None,
]:
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
        / analyst_confidence_count
        if analyst_confidences
        else None
    )

    analyst_enabled_average_confidence = (
        sum(
            analyst_enabled_confidences
        )
        / analyst_enabled_confidence_count
        if analyst_enabled_confidences
        else None
    )

    return (
        analyst_confidence_count,
        analyst_enabled_confidence_count,
        analyst_missing_confidence_count,
        analyst_enabled_missing_confidence_count,
        analyst_average_confidence,
        analyst_enabled_average_confidence,
    )

def _analyst_coverage_percentages(
    *,
    analyst_domain_count: int,
    analyst_enabled_count: int,
    analyst_resolved_count: int,
    analyst_enabled_resolved_count: int,
    analyst_confidence_count: int,
    analyst_enabled_confidence_count: int,
) -> tuple[
    float,
    float,
    float,
    float,
]:
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

    return (
        analyst_confidence_coverage_percentage,
        analyst_enabled_confidence_coverage_percentage,
        analyst_coverage_percentage,
        analyst_operational_percentage,
    )

def _analyst_confidence_coverage_status(
    *,
    analyst_domain_count: int,
    analyst_confidence_count: int,
) -> tuple[str, str]:
    analyst_domain_label = (
        "analyst domain"
        if analyst_domain_count == 1
        else "analyst domains"
    )

    if analyst_domain_count == 0:
        return (
            "UNAVAILABLE",
            "No analyst domains are available.",
        )

    if analyst_confidence_count == 0:
        return (
            "MISSING",
            (
                "Confidence is unavailable for all "
                f"{analyst_domain_count} "
                f"{analyst_domain_label}."
            ),
        )

    if analyst_confidence_count < analyst_domain_count:
        return (
            "PARTIAL",
            (
                "Confidence is available for "
                f"{analyst_confidence_count} of "
                f"{analyst_domain_count} "
                f"{analyst_domain_label}."
            ),
        )

    return (
        "COMPLETE",
        (
            "Confidence is available for all "
            f"{analyst_domain_count} "
            f"{analyst_domain_label}."
        ),
    )

def _enabled_analyst_confidence_coverage_status(
    *,
    analyst_domain_count: int,
    analyst_enabled_count: int,
    analyst_enabled_confidence_count: int,
) -> tuple[str, str]:
    enabled_analyst_domain_label = (
        "enabled analyst domain"
        if analyst_enabled_count == 1
        else "enabled analyst domains"
    )

    if analyst_domain_count == 0:
        return (
            "UNAVAILABLE",
            "No analyst domains are available.",
        )

    if analyst_enabled_count == 0:
        return (
            "DISABLED",
            "No analyst domains are enabled.",
        )

    if analyst_enabled_confidence_count == 0:
        return (
            "MISSING",
            (
                "Confidence is unavailable for all "
                f"{analyst_enabled_count} "
                f"{enabled_analyst_domain_label}."
            ),
        )

    if (
        analyst_enabled_confidence_count
        < analyst_enabled_count
    ):
        return (
            "PARTIAL",
            (
                "Confidence is available for "
                f"{analyst_enabled_confidence_count} of "
                f"{analyst_enabled_count} "
                f"{enabled_analyst_domain_label}."
            ),
        )

    return (
        "COMPLETE",
        (
            "Confidence is available for all "
            f"{analyst_enabled_count} "
            f"{enabled_analyst_domain_label}."
        ),
    )

def _analyst_resolution_coverage_status(
    *,
    analyst_domain_count: int,
    analyst_resolved_count: int,
) -> tuple[str, str]:
    if analyst_domain_count == 0:
        return (
            "UNAVAILABLE",
            "No analyst domains are available.",
        )

    if analyst_resolved_count == 0:
        return (
            "UNRESOLVED",
            (
                "Analyst domains are available, but none "
                "have produced an opinion."
            ),
        )

    if analyst_resolved_count < analyst_domain_count:
        return (
            "PARTIAL",
            (
                f"{analyst_resolved_count} of "
                f"{analyst_domain_count} analyst domains "
                "have produced an opinion."
            ),
        )

    return (
        "COMPLETE",
        (
            f"All {analyst_domain_count} analyst domains "
            "have produced an opinion."
        ),
    )

def _analyst_operational_status(
    *,
    analyst_domain_count: int,
    analyst_enabled_count: int,
    analyst_enabled_resolved_count: int,
) -> tuple[str, str]:
    if analyst_domain_count == 0:
        return (
            "UNAVAILABLE",
            "No analyst domains are available.",
        )

    if analyst_enabled_count == 0:
        return (
            "DISABLED",
            "All analyst domains are disabled.",
        )

    if analyst_enabled_resolved_count == 0:
        return (
            "UNRESOLVED",
            (
                "Enabled analyst domains have not "
                "produced an opinion."
            ),
        )

    if (
        analyst_enabled_resolved_count
        < analyst_enabled_count
    ):
        return (
            "DEGRADED",
            (
                f"{analyst_enabled_resolved_count} of "
                f"{analyst_enabled_count} enabled analyst "
                "domains have produced an opinion."
            ),
        )

    return (
        "OPERATIONAL",
        (
            f"All {analyst_enabled_count} enabled analyst "
            "domains have produced an opinion."
        ),
    )

def _analyst_resolution_counts(
    analyst_summary: dict[str, dict[str, object]],
) -> tuple[
    int,
    int,
    int,
    int,
    int,
]:
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
        if _has_resolved_analyst_opinion(
            details
        )
    )

    analyst_enabled_resolved_count = sum(
        1
        for details in analyst_summary.values()
        if (
            details.get("enabled") is True
            and _has_resolved_analyst_opinion(
                details
            )
        )
    )

    analyst_enabled_unresolved_count = (
        analyst_enabled_count
        - analyst_enabled_resolved_count
    )

    return (
        analyst_domain_count,
        analyst_enabled_count,
        analyst_resolved_count,
        analyst_enabled_resolved_count,
        analyst_enabled_unresolved_count,
    )

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


@dataclass(
    frozen=True,
    slots=True,
)
class _AnalystDashboardMetrics:
    domain_count: int
    enabled_count: int
    resolved_count: int
    enabled_resolved_count: int
    enabled_unresolved_count: int

    confidence_count: int
    enabled_confidence_count: int
    missing_confidence_count: int
    enabled_missing_confidence_count: int

    average_confidence: float | None
    enabled_average_confidence: float | None

    confidence_coverage_percentage: float
    enabled_confidence_coverage_percentage: float
    coverage_percentage: float
    operational_percentage: float

    confidence_coverage_state: str
    confidence_coverage_message: str

    enabled_confidence_coverage_state: str
    enabled_confidence_coverage_message: str

    coverage_state: str
    coverage_message: str

    operational_status: str
    operational_message: str


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

            if result.market_session is not None:
                market_session = _display_value(
                    result.market_session.state
                )

                if market_session is not None:
                    self._market_session = market_session

            if result.decision is not None:
                latest_decision = _display_value(
                    result.decision.decision
                )

                if latest_decision is not None:
                    self._latest_decision = latest_decision

            self._write_if_ready()


    def update_market_session(
        self,
        market_session: str | None,
    ) -> None:
        normalized = _normalize_optional_text(
            market_session,
            field_name="market_session",
        )

        with self._lock:
            self._market_session = normalized
            self._write_if_ready()

    def update_latest_decision(
        self,
        latest_decision: str | None,
    ) -> None:
        normalized = _normalize_optional_text(
            latest_decision,
            field_name="latest_decision",
        )

        with self._lock:
            self._latest_decision = normalized
            self._write_if_ready()

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

        analyst_metrics = _build_analyst_dashboard_metrics(
            analyst_summary
        )

        (
            structure_analyst,
            structure_opinion,
            structure_confidence,
            structure_enabled,
        ) = _analyst_domain_dashboard_values(
            analyst_id="STRUCTURE",
            analyst_summary=structure_summary,
        )

        (
            liquidity_analyst,
            liquidity_opinion,
            liquidity_confidence,
            liquidity_enabled,
        ) = _analyst_domain_dashboard_values(
            analyst_id="LIQUIDITY",
            analyst_summary=liquidity_summary,
        )

        (
            order_block_analyst,
            order_block_opinion,
            order_block_confidence,
            order_block_enabled,
        ) = _analyst_domain_dashboard_values(
            analyst_id="ORDER_BLOCK",
            analyst_summary=order_block_summary,
        )

        (
            auction_analyst,
            auction_opinion,
            auction_confidence,
            auction_enabled,
        ) = _analyst_domain_dashboard_values(
            analyst_id="AUCTION",
            analyst_summary=auction_summary,
        )

        (
            pressure_analyst,
            pressure_opinion,
            pressure_confidence,
            pressure_enabled,
        ) = _analyst_domain_dashboard_values(
            analyst_id="PRESSURE",
            analyst_summary=pressure_summary,
        )

        (
            participation_analyst,
            participation_opinion,
            participation_confidence,
            participation_enabled,
        ) = _analyst_domain_dashboard_values(
            analyst_id="PARTICIPATION",
            analyst_summary=participation_summary,
        )

        (
            value_analyst,
            value_opinion,
            value_confidence,
            value_enabled,
        ) = _analyst_domain_dashboard_values(
            analyst_id="VALUE",
            analyst_summary=value_summary,
        )

        (
            setup_lifecycle_state,
            setup_lifecycle_direction,
            setup_lifecycle_confidence,
            setup_lifecycle_atr_distance,
            setup_lifecycle_action,
            setup_lifecycle_reason,
        ) = _setup_lifecycle_dashboard_values(
            setup_lifecycle
        )

        (
            acceptance_confirmed,
            acceptance_direction,
            acceptance_level,
            acceptance_score,
            acceptance_confidence,
            acceptance_trigger_price,
            acceptance_previous_level,
            acceptance_pullback_low,
            acceptance_pullback_high,
            acceptance_reason,
            acceptance_evidence,
            acceptance_warnings,
        ) = _acceptance_dashboard_values(
            acceptance
        )

        (
            trend_analyst,
            trend_opinion,
            trend_confidence,
            trend_enabled,
            trend_evidence,
            trend_warnings,
        ) = _trend_dashboard_values(
            trend
        )

        (
            institutional_bias_direction,
            institutional_bias_confidence,
            institutional_bias_strength,
            institutional_bias_bullish_score,
            institutional_bias_bearish_score,
            institutional_bias_agreement_count,
            institutional_bias_conflict_count,
            institutional_bias_supporting_domains,
            institutional_bias_opposing_domains,
        ) = _institutional_bias_dashboard_values(
            institutional_bias
        )

        (
            market_phase_value,
            market_phase_confidence,
            market_phase_strength,
            market_phase_agreement_count,
            market_phase_conflict_count,
            market_phase_supporting_domains,
            market_phase_opposing_domains,
        ) = _market_phase_dashboard_values(
            market_phase
        )

        (
            confluence_direction,
            confluence_score,
            confluence_agreement_count,
            confluence_conflict_count,
            confluence_confidence_adjustment,
            confluence_structure_support,
            confluence_liquidity_support,
            confluence_order_block_support,
            confluence_auction_support,
            confluence_pressure_support,
            confluence_participation_support,
            confluence_value_support,
            confluence_bullish_count,
            confluence_bearish_count,
            confluence_neutral_count,
            confluence_unknown_count,
            confluence_domain_count,
        ) = _institutional_confluence_dashboard_values(
            institutional_confluence
        )

        (
            trade_direction,
            trade_plan_valid,
            trade_entry,
            trade_stop,
            trade_target1,
            trade_target2,
            trade_rr1,
            trade_rr2,
            trade_quality,
            trade_narrative,
            trade_reasons,
            trade_warnings,
        ) = _trade_plan_dashboard_values(
            trade_plan
        )

        (
            decision_confidence,
            decision_actionable,
            decision_recommendation,
            decision_reasons,
            decision_warnings,
            decision_analyst_summary,
        ) = _decision_result_dashboard_values(
            decision_result
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

            structure_analyst=structure_analyst,
            structure_opinion=structure_opinion,
            structure_confidence=structure_confidence,
            structure_enabled=structure_enabled,

            liquidity_analyst=liquidity_analyst,
            liquidity_opinion=liquidity_opinion,
            liquidity_confidence=liquidity_confidence,
            liquidity_enabled=liquidity_enabled,

            order_block_analyst=order_block_analyst,
            order_block_opinion=order_block_opinion,
            order_block_confidence=order_block_confidence,
            order_block_enabled=order_block_enabled,

            auction_analyst=auction_analyst,
            auction_opinion=auction_opinion,
            auction_confidence=auction_confidence,
            auction_enabled=auction_enabled,

            pressure_analyst=pressure_analyst,
            pressure_opinion=pressure_opinion,
            pressure_confidence=pressure_confidence,
            pressure_enabled=pressure_enabled,

            participation_analyst=participation_analyst,
            participation_opinion=participation_opinion,
            participation_confidence=participation_confidence,
            participation_enabled=participation_enabled,

            value_analyst=value_analyst,
            value_opinion=value_opinion,
            value_confidence=value_confidence,
            value_enabled=value_enabled,

            setup_lifecycle_state=setup_lifecycle_state,
            setup_lifecycle_direction=setup_lifecycle_direction,
            setup_lifecycle_confidence=setup_lifecycle_confidence,
            setup_lifecycle_atr_distance=setup_lifecycle_atr_distance,
            setup_lifecycle_action=setup_lifecycle_action,
            setup_lifecycle_reason=setup_lifecycle_reason,

            acceptance_confirmed=acceptance_confirmed,
            acceptance_direction=acceptance_direction,
            acceptance_level=acceptance_level,
            acceptance_score=acceptance_score,
            acceptance_confidence=acceptance_confidence,
            acceptance_trigger_price=acceptance_trigger_price,
            acceptance_previous_level=acceptance_previous_level,
            acceptance_pullback_low=acceptance_pullback_low,
            acceptance_pullback_high=acceptance_pullback_high,
            acceptance_reason=acceptance_reason,
            acceptance_evidence=acceptance_evidence,
            acceptance_warnings=acceptance_warnings,

            trend_analyst=trend_analyst,
            trend_opinion=trend_opinion,
            trend_confidence=trend_confidence,
            trend_enabled=trend_enabled,
            trend_evidence=trend_evidence,
            trend_warnings=trend_warnings,

            institutional_bias=institutional_bias_direction,
            institutional_bias_confidence=institutional_bias_confidence,
            institutional_bias_strength=institutional_bias_strength,
            institutional_bias_bullish_score=institutional_bias_bullish_score,
            institutional_bias_bearish_score=institutional_bias_bearish_score,
            institutional_bias_agreement_count=institutional_bias_agreement_count,
            institutional_bias_conflict_count=institutional_bias_conflict_count,
            institutional_bias_supporting_domains=(
                institutional_bias_supporting_domains
            ),
            institutional_bias_opposing_domains=(
                institutional_bias_opposing_domains
            ),

            market_phase=market_phase_value,
            market_phase_confidence=market_phase_confidence,
            market_phase_strength=market_phase_strength,
            market_phase_agreement_count=market_phase_agreement_count,
            market_phase_conflict_count=market_phase_conflict_count,
            market_phase_supporting_domains=(
                market_phase_supporting_domains
            ),
            market_phase_opposing_domains=(
                market_phase_opposing_domains
            ),

            confluence_direction=confluence_direction,
            confluence_score=confluence_score,
            confluence_agreement_count=confluence_agreement_count,
            confluence_conflict_count=confluence_conflict_count,
            confluence_confidence_adjustment=(
                confluence_confidence_adjustment
            ),
            confluence_structure_support=confluence_structure_support,
            confluence_liquidity_support=confluence_liquidity_support,
            confluence_order_block_support=confluence_order_block_support,
            confluence_auction_support=confluence_auction_support,
            confluence_pressure_support=confluence_pressure_support,
            confluence_participation_support=(
                confluence_participation_support
            ),
            confluence_value_support=confluence_value_support,
            confluence_bullish_count=confluence_bullish_count,
            confluence_bearish_count=confluence_bearish_count,
            confluence_neutral_count=confluence_neutral_count,
            confluence_unknown_count=confluence_unknown_count,
            confluence_domain_count=confluence_domain_count,

            trade_direction=trade_direction,
            trade_plan_valid=trade_plan_valid,
            trade_entry=trade_entry,
            trade_stop=trade_stop,
            trade_target1=trade_target1,
            trade_target2=trade_target2,
            trade_rr1=trade_rr1,
            trade_rr2=trade_rr2,
            trade_quality=trade_quality,
            trade_narrative=trade_narrative,
            trade_reasons=trade_reasons,
            trade_warnings=trade_warnings,

            decision_confidence=decision_confidence,
            decision_actionable=decision_actionable,
            decision_recommendation=decision_recommendation,
            decision_reasons=decision_reasons,
            decision_warnings=decision_warnings,
            analyst_summary=decision_analyst_summary,


            analyst_domain_count=(
                analyst_metrics.domain_count
            ),
            analyst_enabled_count=(
                analyst_metrics.enabled_count
            ),
            analyst_resolved_count=(
                analyst_metrics.resolved_count
            ),
            analyst_enabled_resolved_count=(
                analyst_metrics.enabled_resolved_count
            ),
            analyst_enabled_unresolved_count=(
                analyst_metrics.enabled_unresolved_count
            ),
            analyst_confidence_count=(
                analyst_metrics.confidence_count
            ),
            analyst_enabled_confidence_count=(
                analyst_metrics.enabled_confidence_count
            ),
            analyst_missing_confidence_count=(
                analyst_metrics.missing_confidence_count
            ),
            analyst_enabled_missing_confidence_count=(
                analyst_metrics.enabled_missing_confidence_count
            ),
            analyst_average_confidence=(
                analyst_metrics.average_confidence
            ),
            analyst_confidence_coverage_percentage=(
                analyst_metrics.confidence_coverage_percentage
            ),
            analyst_enabled_confidence_coverage_percentage=(
                analyst_metrics.enabled_confidence_coverage_percentage
            ),
            analyst_confidence_coverage_state=(
                analyst_metrics.confidence_coverage_state
            ),
            analyst_confidence_coverage_message=(
                analyst_metrics.confidence_coverage_message
            ),
            analyst_enabled_confidence_coverage_state=(
                analyst_metrics.enabled_confidence_coverage_state
            ),
            analyst_enabled_confidence_coverage_message=(
                analyst_metrics.enabled_confidence_coverage_message
            ),
            analyst_coverage_percentage=(
                analyst_metrics.coverage_percentage
            ),
            analyst_coverage_state=(
                analyst_metrics.coverage_state
            ),
            analyst_coverage_message=(
                analyst_metrics.coverage_message
            ),
            analyst_operational_status=(
                analyst_metrics.operational_status
            ),
            analyst_operational_message=(
                analyst_metrics.operational_message
            ),
            analyst_operational_percentage=(
                analyst_metrics.operational_percentage
            ),
            analyst_enabled_average_confidence=(
                analyst_metrics.enabled_average_confidence
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

        serialized_payload_bytes = (
            (payload + "\n").encode(
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
                if not _is_transient_replace_error(
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
                _directory_open_flags(),
            )

        except OSError as error:
            if _is_unsupported_directory_fsync_error(
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
                if _is_unsupported_directory_fsync_error(
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

def _build_analyst_dashboard_metrics(
    analyst_summary: dict[str, dict[str, object]],
) -> _AnalystDashboardMetrics:
    (
        analyst_domain_count,
        analyst_enabled_count,
        analyst_resolved_count,
        analyst_enabled_resolved_count,
        analyst_enabled_unresolved_count,
    ) = _analyst_resolution_counts(
        analyst_summary
    )

    (
        analyst_confidences,
        analyst_enabled_confidences,
    ) = _analyst_confidence_values(
        analyst_summary
    )

    (
        analyst_confidence_count,
        analyst_enabled_confidence_count,
        analyst_missing_confidence_count,
        analyst_enabled_missing_confidence_count,
        analyst_average_confidence,
        analyst_enabled_average_confidence,
    ) = _analyst_confidence_metrics(
        analyst_domain_count=analyst_domain_count,
        analyst_enabled_count=analyst_enabled_count,
        analyst_confidences=analyst_confidences,
        analyst_enabled_confidences=(
            analyst_enabled_confidences
        ),
    )

    (
        analyst_confidence_coverage_percentage,
        analyst_enabled_confidence_coverage_percentage,
        analyst_coverage_percentage,
        analyst_operational_percentage,
    ) = _analyst_coverage_percentages(
        analyst_domain_count=analyst_domain_count,
        analyst_enabled_count=analyst_enabled_count,
        analyst_resolved_count=analyst_resolved_count,
        analyst_enabled_resolved_count=(
            analyst_enabled_resolved_count
        ),
        analyst_confidence_count=analyst_confidence_count,
        analyst_enabled_confidence_count=(
            analyst_enabled_confidence_count
        ),
    )

    (
        analyst_confidence_coverage_state,
        analyst_confidence_coverage_message,
    ) = _analyst_confidence_coverage_status(
        analyst_domain_count=analyst_domain_count,
        analyst_confidence_count=analyst_confidence_count,
    )

    (
        analyst_enabled_confidence_coverage_state,
        analyst_enabled_confidence_coverage_message,
    ) = _enabled_analyst_confidence_coverage_status(
        analyst_domain_count=analyst_domain_count,
        analyst_enabled_count=analyst_enabled_count,
        analyst_enabled_confidence_count=(
            analyst_enabled_confidence_count
        ),
    )

    (
        analyst_coverage_state,
        analyst_coverage_message,
    ) = _analyst_resolution_coverage_status(
        analyst_domain_count=analyst_domain_count,
        analyst_resolved_count=analyst_resolved_count,
    )

    (
        analyst_operational_status,
        analyst_operational_message,
    ) = _analyst_operational_status(
        analyst_domain_count=analyst_domain_count,
        analyst_enabled_count=analyst_enabled_count,
        analyst_enabled_resolved_count=(
            analyst_enabled_resolved_count
        ),
    )

    return _AnalystDashboardMetrics(
        domain_count=analyst_domain_count,
        enabled_count=analyst_enabled_count,
        resolved_count=analyst_resolved_count,
        enabled_resolved_count=(
            analyst_enabled_resolved_count
        ),
        enabled_unresolved_count=(
            analyst_enabled_unresolved_count
        ),
        confidence_count=analyst_confidence_count,
        enabled_confidence_count=(
            analyst_enabled_confidence_count
        ),
        missing_confidence_count=(
            analyst_missing_confidence_count
        ),
        enabled_missing_confidence_count=(
            analyst_enabled_missing_confidence_count
        ),
        average_confidence=analyst_average_confidence,
        enabled_average_confidence=(
            analyst_enabled_average_confidence
        ),
        confidence_coverage_percentage=(
            analyst_confidence_coverage_percentage
        ),
        enabled_confidence_coverage_percentage=(
            analyst_enabled_confidence_coverage_percentage
        ),
        coverage_percentage=analyst_coverage_percentage,
        operational_percentage=analyst_operational_percentage,
        confidence_coverage_state=(
            analyst_confidence_coverage_state
        ),
        confidence_coverage_message=(
            analyst_confidence_coverage_message
        ),
        enabled_confidence_coverage_state=(
            analyst_enabled_confidence_coverage_state
        ),
        enabled_confidence_coverage_message=(
            analyst_enabled_confidence_coverage_message
        ),
        coverage_state=analyst_coverage_state,
        coverage_message=analyst_coverage_message,
        operational_status=analyst_operational_status,
        operational_message=analyst_operational_message,
    )

def _analyst_domain_dashboard_values(
    *,
    analyst_id: str,
    analyst_summary: dict[str, object] | None,
) -> tuple[
    str | None,
    object | None,
    object | None,
    object | None,
]:
    if analyst_summary is None:
        return (
            None,
            None,
            None,
            None,
        )

    return (
        analyst_id,
        analyst_summary.get("opinion"),
        analyst_summary.get("confidence"),
        analyst_summary.get("enabled"),
    )

def _setup_lifecycle_dashboard_values(
    setup_lifecycle: object | None,
) -> tuple[
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
]:
    if setup_lifecycle is None:
        return (
            None,
            None,
            None,
            None,
            None,
            None,
        )

    return (
        setup_lifecycle.state,
        setup_lifecycle.direction,
        setup_lifecycle.confidence,
        setup_lifecycle.atr_distance,
        setup_lifecycle.action,
        setup_lifecycle.reason,
    )

def _acceptance_dashboard_values(
    acceptance: object | None,
) -> tuple[
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    tuple[object, ...],
    tuple[object, ...],
]:
    if acceptance is None:
        return (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            (),
            (),
        )

    return (
        acceptance.accepted,
        acceptance.direction,
        acceptance.level,
        acceptance.score,
        acceptance.confidence,
        acceptance.trigger_price,
        acceptance.previous_level,
        acceptance.pullback_low,
        acceptance.pullback_high,
        acceptance.reason,
        tuple(acceptance.evidence),
        tuple(acceptance.warnings),
    )

def _trend_dashboard_values(
    trend: object | None,
) -> tuple[
    object | None,
    object | None,
    object | None,
    object | None,
    tuple[object, ...],
    tuple[object, ...],
]:
    if trend is None:
        return (
            None,
            None,
            None,
            None,
            (),
            (),
        )

    return (
        trend.analyst,
        trend.opinion,
        trend.confidence,
        trend.enabled,
        tuple(trend.evidence),
        tuple(trend.warnings),
    )

def _institutional_bias_dashboard_values(
    institutional_bias: object | None,
) -> tuple[
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    tuple[object, ...],
    tuple[object, ...],
]:
    if institutional_bias is None:
        return (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            (),
            (),
        )

    return (
        institutional_bias.direction.value,
        institutional_bias.confidence,
        institutional_bias.strength,
        institutional_bias.bullish_score,
        institutional_bias.bearish_score,
        institutional_bias.agreement_count,
        institutional_bias.conflict_count,
        tuple(institutional_bias.supporting_domains),
        tuple(institutional_bias.opposing_domains),
    )

def _market_phase_dashboard_values(
    market_phase: object | None,
) -> tuple[
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    tuple[object, ...],
    tuple[object, ...],
]:
    if market_phase is None:
        return (
            None,
            None,
            None,
            None,
            None,
            (),
            (),
        )

    return (
        market_phase.phase.value,
        market_phase.confidence,
        market_phase.strength,
        market_phase.agreement_count,
        market_phase.conflict_count,
        tuple(market_phase.supporting_domains),
        tuple(market_phase.opposing_domains),
    )

def _institutional_confluence_dashboard_values(
    institutional_confluence: object | None,
) -> tuple[
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
]:
    if institutional_confluence is None:
        return (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
        )

    return (
        institutional_confluence.dominant_direction.value,
        institutional_confluence.score,
        institutional_confluence.agreement_count,
        institutional_confluence.conflict_count,
        institutional_confluence.confidence_adjustment,
        institutional_confluence.structure_support,
        institutional_confluence.liquidity_support,
        institutional_confluence.order_block_support,
        institutional_confluence.auction_support,
        institutional_confluence.pressure_support,
        institutional_confluence.participation_support,
        institutional_confluence.value_support,
        institutional_confluence.bullish_count,
        institutional_confluence.bearish_count,
        institutional_confluence.neutral_count,
        institutional_confluence.unknown_count,
        institutional_confluence.domain_count,
    )

def _trade_plan_dashboard_values(
    trade_plan: object | None,
) -> tuple[
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    object | None,
    tuple[object, ...],
    tuple[object, ...],
]:
    if trade_plan is None:
        return (
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            (),
            (),
        )

    return (
        _display_value(trade_plan.direction),
        trade_plan.valid,
        trade_plan.entry,
        trade_plan.stop,
        trade_plan.target1,
        trade_plan.target2,
        trade_plan.rr1,
        trade_plan.rr2,
        trade_plan.quality,
        trade_plan.narrative,
        tuple(trade_plan.reasons),
        tuple(trade_plan.warnings),
    )

def _decision_result_dashboard_values(
    decision_result: object | None,
) -> tuple[
    object | None,
    object | None,
    object | None,
    tuple[object, ...],
    tuple[object, ...],
    dict[str, dict[str, object]],
]:
    if decision_result is None:
        return (
            None,
            None,
            None,
            (),
            (),
            {},
        )

    return (
        float(decision_result.confidence),
        decision_result.actionable,
        decision_result.recommendation,
        tuple(decision_result.reasons),
        tuple(decision_result.warnings),
        {
            analyst_id: dict(details)
            for analyst_id, details
            in decision_result.analyst_summary.items()
        },
    )
