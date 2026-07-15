from __future__ import annotations

from dataclasses import dataclass

from imie.models.liquidity_finding import LiquidityFinding
from imie.models.liquidity_pool import LiquidityPool
from imie.models.liquidity_types import (
    LiquidityImportance,
    LiquiditySide,
)


_IMPORTANCE_RANK: dict[LiquidityImportance, int] = {
    LiquidityImportance.MINOR: 1,
    LiquidityImportance.INTERMEDIATE: 2,
    LiquidityImportance.MAJOR: 3,
}


@dataclass(frozen=True, slots=True)
class LiquidityPoolBuilder:
    """
    Builds institutional liquidity pools from detector findings.

    The builder does not inspect market bars or detect liquidity.
    It receives existing LiquidityFinding objects and consolidates
    nearby findings into side-specific LiquidityPool objects.

    Buy-side and sell-side findings are never merged together.
    """

    cluster_tolerance: float = 0.10
    min_findings: int = 1
    confluence_bonus: float = 3.0

    def __post_init__(self) -> None:
        if self.cluster_tolerance < 0.0:
            raise ValueError(
                "LiquidityPoolBuilder cluster_tolerance "
                "cannot be negative."
            )

        if self.min_findings < 1:
            raise ValueError(
                "LiquidityPoolBuilder min_findings must be "
                "at least 1."
            )

        if self.confluence_bonus < 0.0:
            raise ValueError(
                "LiquidityPoolBuilder confluence_bonus "
                "cannot be negative."
            )

    def build(
        self,
        findings: tuple[LiquidityFinding, ...],
    ) -> tuple[LiquidityPool, ...]:
        """
        Consolidate active liquidity findings into pools.

        Exact duplicate findings are removed before clustering.
        Inactive findings are excluded.

        A cluster remains valid only when its complete price span
        stays within cluster_tolerance. This prevents nearby levels
        from chaining together into an excessively wide pool.
        """
        self._validate_findings(findings)

        eligible_findings = tuple(
            finding
            for finding in self._deduplicate(findings)
            if finding.is_active
        )

        if not eligible_findings:
            return ()

        pools: list[LiquidityPool] = []

        for side in (
            LiquiditySide.BUY_SIDE,
            LiquiditySide.SELL_SIDE,
        ):
            side_findings = tuple(
                sorted(
                    (
                        finding
                        for finding in eligible_findings
                        if finding.point.side is side
                    ),
                    key=lambda finding: finding.point.price,
                )
            )

            clusters = self._cluster_findings(side_findings)

            for cluster in clusters:
                if len(cluster) < self.min_findings:
                    continue

                pools.append(
                    self._build_pool(cluster)
                )

        return tuple(
            sorted(
                pools,
                key=lambda pool: (
                    pool.side.value,
                    pool.price,
                ),
            )
        )

    @staticmethod
    def _validate_findings(
        findings: tuple[LiquidityFinding, ...],
    ) -> None:
        for finding in findings:
            if not isinstance(finding, LiquidityFinding):
                raise TypeError(
                    "LiquidityPoolBuilder requires "
                    "LiquidityFinding objects."
                )

    @staticmethod
    def _deduplicate(
        findings: tuple[LiquidityFinding, ...],
    ) -> tuple[LiquidityFinding, ...]:
        unique: list[LiquidityFinding] = []

        for finding in findings:
            if finding not in unique:
                unique.append(finding)

        return tuple(unique)

    def _cluster_findings(
        self,
        findings: tuple[LiquidityFinding, ...],
    ) -> tuple[tuple[LiquidityFinding, ...], ...]:
        if not findings:
            return ()

        clusters: list[list[LiquidityFinding]] = []
        current_cluster: list[LiquidityFinding] = [
            findings[0],
        ]

        for finding in findings[1:]:
            cluster_lower = current_cluster[0].point.price
            candidate_upper = finding.point.price

            complete_span = (
                candidate_upper - cluster_lower
            )

            if complete_span <= self.cluster_tolerance:
                current_cluster.append(finding)
                continue

            clusters.append(current_cluster)
            current_cluster = [finding]

        clusters.append(current_cluster)

        return tuple(
            tuple(cluster)
            for cluster in clusters
        )

    def _build_pool(
        self,
        findings: tuple[LiquidityFinding, ...],
    ) -> LiquidityPool:
        side = findings[0].point.side

        lower = min(
            finding.point.price
            for finding in findings
        )

        upper = max(
            finding.point.price
            for finding in findings
        )

        price = self._calculate_weighted_price(
            findings
        )

        importance = max(
            (
                finding.importance
                for finding in findings
            ),
            key=lambda value: _IMPORTANCE_RANK[value],
        )

        confidence = self._calculate_pool_confidence(
            findings
        )

        strength = float(
            sum(
                finding.point.strength
                for finding in findings
            )
        )

        evidence = self._collect_evidence(
            findings
        )

        side_label = (
            "buy-side"
            if side is LiquiditySide.BUY_SIDE
            else "sell-side"
        )

        source_count = len(
            {
                finding.source
                for finding in findings
            }
        )

        reason = (
            f"{len(findings)} active liquidity finding"
            f"{'' if len(findings) == 1 else 's'} from "
            f"{source_count} detector source"
            f"{'' if source_count == 1 else 's'} formed one "
            f"{side_label} liquidity pool between "
            f"{lower:.4f} and {upper:.4f}."
        )

        return LiquidityPool(
            price=price,
            upper=upper,
            lower=lower,
            side=side,
            importance=importance,
            confidence=confidence,
            strength=strength,
            findings=findings,
            reason=reason,
            evidence=evidence,
        )

    @staticmethod
    def _calculate_weighted_price(
        findings: tuple[LiquidityFinding, ...],
    ) -> float:
        weighted_total = 0.0
        total_weight = 0.0

        for finding in findings:
            weight = (
                finding.confidence
                * finding.point.strength
            )

            weighted_total += (
                finding.point.price * weight
            )

            total_weight += weight

        if total_weight == 0.0:
            return round(
                sum(
                    finding.point.price
                    for finding in findings
                )
                / len(findings),
                6,
            )

        return round(
            weighted_total / total_weight,
            6,
        )

    def _calculate_pool_confidence(
        self,
        findings: tuple[LiquidityFinding, ...],
    ) -> float:
        total_strength = sum(
            finding.point.strength
            for finding in findings
        )

        if total_strength == 0:
            base_confidence = (
                sum(
                    finding.confidence
                    for finding in findings
                )
                / len(findings)
            )
        else:
            base_confidence = (
                sum(
                    finding.confidence
                    * finding.point.strength
                    for finding in findings
                )
                / total_strength
            )

        bonus = (
            max(0, len(findings) - 1)
            * self.confluence_bonus
        )

        return round(
            min(100.0, base_confidence + bonus),
            2,
        )

    @staticmethod
    def _collect_evidence(
        findings: tuple[LiquidityFinding, ...],
    ) -> tuple[str, ...]:
        evidence: list[str] = []

        for finding in findings:
            source_evidence = (
                f"{finding.source}: {finding.reason}"
            )

            if source_evidence not in evidence:
                evidence.append(source_evidence)

            for item in finding.evidence:
                if item not in evidence:
                    evidence.append(item)

        return tuple(evidence)