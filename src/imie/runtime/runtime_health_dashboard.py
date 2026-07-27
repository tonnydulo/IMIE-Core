from __future__ import annotations

import json

from http import HTTPStatus
from http.server import (
    BaseHTTPRequestHandler,
    ThreadingHTTPServer,
)
from pathlib import Path
from typing import Any


DEFAULT_DASHBOARD_HOST = "127.0.0.1"
DEFAULT_DASHBOARD_PORT = 8765
DEFAULT_REFRESH_SECONDS = 2.0


def read_health_status(
    path: str | Path,
) -> dict[str, Any]:
    if not isinstance(
        path,
        str | Path,
    ):
        raise TypeError(
            "path must be a string or Path."
        )

    resolved_path = Path(
        path
    )

    if not resolved_path.exists():
        raise FileNotFoundError(
            f"Health status file does not exist: "
            f"{resolved_path}"
        )

    if not resolved_path.is_file():
        raise ValueError(
            "Health status path must reference a file."
        )

    try:
        payload = json.loads(
            resolved_path.read_text(
                encoding="utf-8"
            )
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            "Health status file contains invalid JSON."
        ) from error

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Health status JSON must contain an object."
        )

    return payload


def build_dashboard_html(
    *,
    refresh_seconds: float = (
        DEFAULT_REFRESH_SECONDS
    ),
) -> str:
    if isinstance(
        refresh_seconds,
        bool,
    ) or not isinstance(
        refresh_seconds,
        int | float,
    ):
        raise TypeError(
            "refresh_seconds must be a number."
        )

    if refresh_seconds <= 0:
        raise ValueError(
            "refresh_seconds must be greater than zero."
        )

    refresh_milliseconds = int(
        float(
            refresh_seconds
        )
        * 1000
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >
    <title>IMIE Runtime Dashboard</title>

    <style>
        :root {{
            color-scheme: dark;
            font-family:
                Inter,
                Segoe UI,
                Arial,
                sans-serif;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            background: #0c111b;
            color: #edf2f7;
        }}

        .page {{
            max-width: 1180px;
            margin: 0 auto;
            padding: 28px;
        }}

        .header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 20px;
            margin-bottom: 24px;
        }}

        .title {{
            margin: 0;
            font-size: 28px;
            font-weight: 700;
        }}

        .subtitle {{
            margin-top: 6px;
            color: #93a4b8;
        }}

        .state-badge {{
            border-radius: 999px;
            padding: 10px 18px;
            font-weight: 700;
            letter-spacing: 0.04em;
            background: #374151;
        }}

        .state-running {{
            background: #126b46;
        }}

        .state-sleeping {{
            background: #735c0f;
        }}

        .state-failed {{
            background: #8f2635;
        }}

        .state-stopped {{
            background: #4b5563;
        }}

        .grid {{
            display: grid;
            grid-template-columns:
                repeat(
                    auto-fit,
                    minmax(220px, 1fr)
                );
            gap: 16px;
        }}

        .card {{
            min-height: 126px;
            padding: 18px;
            border: 1px solid #253044;
            border-radius: 14px;
            background: #141c29;
            box-shadow:
                0 8px 24px
                rgba(0, 0, 0, 0.18);
        }}

        .label {{
            color: #8fa1b6;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }}

        .value {{
            margin-top: 12px;
            font-size: 22px;
            font-weight: 650;
            word-break: break-word;
        }}

        .wide {{
            grid-column: 1 / -1;
        }}

        .error {{
            color: #ff7f8e;
        }}

        .muted {{
            color: #8fa1b6;
        }}

        .footer {{
            margin-top: 18px;
            color: #718096;
            font-size: 13px;
        }}

        .status-message {{
            margin-bottom: 18px;
            padding: 12px 16px;
            border: 1px solid #253044;
            border-radius: 10px;
            background: #101722;
            color: #9fb0c4;
        }}

        .cycle-completed {{
            color: #68d391;
        }}

        .cycle-skipped {{
            color: #f6c453;
        }}

        .cycle-failed {{
            color: #ff7f8e;
        }}

        .decision-ready {{
            color: #68d391;
        }}

        .decision-wait {{
            color: #f6c453;
        }}

        .decision-pass {{
            color: #8fa1b6;
        }}
        .actionable-yes {{
            color: #68d391;
        }}

        .actionable-no {{
            color: #f6c453;
        }}

        .direction-long {{
            color: #68d391;
        }}

        .direction-short {{
            color: #ff7f8e;
        }}

        .plan-valid {{
            color: #68d391;
        }}

        .plan-invalid {{
            color: #ff7f8e;
        }}

        .trade-price {{
            font-variant-numeric: tabular-nums;
        }}

        .trade-quality-high {{
            color: #68d391;
        }}

        .trade-quality-medium {{
            color: #f6c453;
        }}

        .trade-quality-low {{
            color: #ff7f8e;
        }}

        .institution-bullish {{
            color: #68d391;
        }}

        .institution-bearish {{
            color: #ff7f8e;
        }}

        .institution-neutral {{
            color: #f6c453;
        }}

        .institution-unknown {{
            color: #8fa1b6;
        }}

        .metric-good {{
            color: #68d391;
        }}

        .metric-medium {{
            color: #f6c453;
        }}

        .metric-low {{
            color: #ff7f8e;
        }}

        .conflict-clear {{
            color: #68d391;
        }}

        .conflict-present {{
            color: #ff7f8e;
        }}

        .recommendation {{
            font-size: 18px;
            line-height: 1.55;
            font-weight: 500;
        }}

        .explanation-list {{
            margin: 12px 0 0;
            padding-left: 22px;
            color: #c7d2df;
            line-height: 1.6;
        }}

        .explanation-list li + li {{
            margin-top: 8px;
        }}

        .warning-list {{
            color: #f6c453;
        }}

        .empty-list {{
            color: #8fa1b6;
            font-style: italic;
        }}

        .domain-list {{
            margin: 12px 0 0;
            padding-left: 22px;
            color: #c7d2df;
            line-height: 1.6;
        }}

        .domain-list li + li {{
            margin-top: 6px;
        }}

        .supporting-domain-list {{
            color: #68d391;
        }}

        .opposing-domain-list {{
            color: #ff7f8e;
        }}

        .analyst-summary {{
            display: grid;
            gap: 0.75rem;
            margin-top: 12px;
        }}

        .analyst-summary-row {{
            display: grid;
            grid-template-columns:
                minmax(7rem, 0.7fr)
                minmax(14rem, 2fr)
                minmax(6rem, 0.6fr)
                minmax(6rem, 0.6fr);
            gap: 0.75rem;
            align-items: start;
            padding: 0.75rem;
            border: 1px solid #253044;
            border-radius: 0.65rem;
            background: #101722;
        }}

        .analyst-summary-heading {{
            color: #8fa1b6;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}

        .analyst-summary-value {{
            margin-top: 0.2rem;
            overflow-wrap: anywhere;
        }}

        @media (max-width: 760px) {{
            .analyst-summary-row {{
                grid-template-columns: 1fr;
            }}
        }}

    </style>
</head>

<body>
    <main class="page">
        <header class="header">
            <div>
                <h1 class="title">
                    IMIE Runtime Dashboard
                </h1>

                <div class="subtitle">
                    Institutional Market Intelligence Engine
                </div>
            </div>

            <div
                id="stateBadge"
                class="state-badge"
            >
                LOADING
            </div>
        </header>

        <div
            id="statusMessage"
            class="status-message"
        >
            Loading runtime health...
        </div>

        <section class="grid">
            <article class="card">
                <div class="label">
                    Symbol
                </div>

                <div
                    id="symbol"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Timeframe
                </div>

                <div
                    id="timeframe"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Market Session
                </div>

                <div
                    id="marketSession"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Latest Decision
                </div>

                <div
                    id="latestDecision"
                    class="value"
                >
                    —
                </div>
            </article>

             <article class="card">
                <div class="label">
                    Decision Confidence
                </div>

                <div
                    id="decisionConfidence"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Actionable
                </div>

                <div
                    id="decisionActionable"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Trade Direction
                </div>

                <div
                    id="tradeDirection"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Recommendation
                </div>

                <div
                    id="decisionRecommendation"
                    class="value recommendation"
                >
                    —
                </div>
            </article>

             <article class="card wide">
                <div class="label">
                    Decision Reasons
                </div>

                <ul
                    id="decisionReasons"
                    class="explanation-list"
                >
                    <li class="empty-list">
                        No decision reasons available.
                    </li>
                </ul>
            </article>

            <article class="card wide">
                <div class="label">
                    Decision Warnings
                </div>

                <ul
                    id="decisionWarnings"
                    class="explanation-list warning-list"
                >
                    <li class="empty-list">
                        No decision warnings.
                    </li>
                </ul>
            </article>

            <article class="card">
                <div class="label">
                    Structure Analyst
                </div>

                <div
                    id="structureAnalyst"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Structure Opinion
                </div>

                <div
                    id="structureOpinion"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Structure Confidence
                </div>

                <div
                    id="structureConfidence"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Structure Enabled
                </div>

                <div
                    id="structureEnabled"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Liquidity Analyst
                </div>

                <div
                    id="liquidityAnalyst"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Liquidity Opinion
                </div>

                <div
                    id="liquidityOpinion"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Liquidity Confidence
                </div>

                <div
                    id="liquidityConfidence"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Liquidity Enabled
                </div>

                <div
                    id="liquidityEnabled"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Analyst Summary
                </div>

                <div
                    id="analystSummary"
                    class="analyst-summary"
                >
                    <div class="empty-list">
                        No analyst summary available.
                    </div>
                </div>
            </article>

             <article class="card">
                <div class="label">
                    Plan Valid
                </div>

                <div
                    id="tradePlanValid"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Entry
                </div>

                <div
                    id="tradeEntry"
                    class="value trade-price"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Stop
                </div>

                <div
                    id="tradeStop"
                    class="value trade-price"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Target 1
                </div>

                <div
                    id="tradeTarget1"
                    class="value trade-price"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Target 2
                </div>

                <div
                    id="tradeTarget2"
                    class="value trade-price"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    RR1
                </div>

                <div
                    id="tradeRR1"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    RR2
                </div>

                <div
                    id="tradeRR2"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Plan Quality
                </div>

                <div
                    id="tradeQuality"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Trade Narrative
                </div>

                <div
                    id="tradeNarrative"
                    class="value recommendation"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Trade Reasons
                </div>

                <ul
                    id="tradeReasons"
                    class="explanation-list"
                >
                    <li class="empty-list">
                        No trade reasons available.
                    </li>
                </ul>
            </article>

            <article class="card wide">
                <div class="label">
                    Trade Warnings
                </div>

                <ul
                    id="tradeWarnings"
                    class="explanation-list warning-list"
                >
                    <li class="empty-list">
                        No trade warnings.
                    </li>
                </ul>
            </article>

            <article class="card">
                <div class="label">
                    Institutional Bias
                </div>

                <div
                    id="institutionalBias"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Bias Confidence
                </div>

                <div
                    id="institutionalBiasConfidence"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Bias Strength
                </div>

                <div
                    id="institutionalBiasStrength"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Bullish Score
                </div>

                <div
                    id="institutionalBiasBullishScore"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Bearish Score
                </div>

                <div
                    id="institutionalBiasBearishScore"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Bias Agreement
                </div>

                <div
                    id="institutionalBiasAgreementCount"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Bias Conflict
                </div>

                <div
                    id="institutionalBiasConflictCount"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Supporting Bias Domains
                </div>

                <ul
                    id="institutionalBiasSupportingDomains"
                    class="domain-list supporting-domain-list"
                >
                    <li class="empty-list">
                        No supporting bias domains.
                    </li>
                </ul>
            </article>

            <article class="card wide">
                <div class="label">
                    Opposing Bias Domains
                </div>

                <ul
                    id="institutionalBiasOpposingDomains"
                    class="domain-list opposing-domain-list"
                >
                    <li class="empty-list">
                        No opposing bias domains.
                    </li>
                </ul>
            </article>    

            <article class="card">
                <div class="label">
                    Market Phase
                </div>

                <div
                    id="marketPhase"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Phase Confidence
                </div>

                <div
                    id="marketPhaseConfidence"
                    class="value"
                >
                    —
                </div>
            </article>

            <section class="panel">
                <h2>Confluence Detail</h2>

                <div class="metric-grid">
                    <div class="metric">
                        <span class="label">
                            Confidence Adjustment
                        </span>
                        <span
                            id="confluenceConfidenceAdjustment"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Structure Support
                        </span>
                        <span
                            id="confluenceStructureSupport"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Liquidity Support
                        </span>
                        <span
                            id="confluenceLiquiditySupport"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Order Block Support
                        </span>
                        <span
                            id="confluenceOrderBlockSupport"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Auction Support
                        </span>
                        <span
                            id="confluenceAuctionSupport"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Pressure Support
                        </span>
                        <span
                            id="confluencePressureSupport"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Participation Support
                        </span>
                        <span
                            id="confluenceParticipationSupport"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Value Support
                        </span>
                        <span
                            id="confluenceValueSupport"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Bullish Domains
                        </span>
                        <span
                            id="confluenceBullishCount"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Bearish Domains
                        </span>
                        <span
                            id="confluenceBearishCount"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Neutral Domains
                        </span>
                        <span
                            id="confluenceNeutralCount"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Unknown Domains
                        </span>
                        <span
                            id="confluenceUnknownCount"
                            class="value"
                        >
                            —
                        </span>
                    </div>

                    <div class="metric">
                        <span class="label">
                            Total Domains
                        </span>
                        <span
                            id="confluenceDomainCount"
                            class="value"
                        >
                            —
                        </span>
                    </div>
                </div>
            </section>

            <article class="card">
                <div class="label">
                    Confluence Direction
                </div>

                <div
                    id="confluenceDirection"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Confluence Score
                </div>

                <div
                    id="confluenceScore"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Institutional Agreement
                </div>

                <div
                    id="confluenceAgreementCount"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Institutional Conflict
                </div>

                <div
                    id="confluenceConflictCount"
                    class="value"
                >
                    —
                </div>
            </article>

             <article class="card">
                <div class="label">
                    Phase Strength
                </div>

                <div
                    id="marketPhaseStrength"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Phase Agreement
                </div>

                <div
                    id="marketPhaseAgreementCount"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Phase Conflict
                </div>

                <div
                    id="marketPhaseConflictCount"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Supporting Phase Domains
                </div>

                <ul
                    id="marketPhaseSupportingDomains"
                    class="domain-list supporting-domain-list"
                >
                    <li class="empty-list">
                        No supporting phase domains.
                    </li>
                </ul>
            </article>

            <article class="card wide">
                <div class="label">
                    Opposing Phase Domains
                </div>

                <ul
                    id="marketPhaseOpposingDomains"
                    class="domain-list opposing-domain-list"
                >
                    <li class="empty-list">
                        No opposing phase domains.
                    </li>
                </ul>
            </article>

            <article class="card">
                <div class="label">
                    Lifecycle State
                </div>

                <div
                    id="setupLifecycleState"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Lifecycle Direction
                </div>

                <div
                    id="setupLifecycleDirection"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Lifecycle Confidence
                </div>

                <div
                    id="setupLifecycleConfidence"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    ATR Distance
                </div>

                <div
                    id="setupLifecycleAtrDistance"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Lifecycle Action
                </div>

                <div
                    id="setupLifecycleAction"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Lifecycle Reason
                </div>

                <div
                    id="setupLifecycleReason"
                    class="value recommendation"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Acceptance Confirmed
                </div>

                <div
                    id="acceptanceConfirmed"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Acceptance Direction
                </div>

                <div
                    id="acceptanceDirection"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Acceptance Level
                </div>

                <div
                    id="acceptanceLevel"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Acceptance Score
                </div>

                <div
                    id="acceptanceScore"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Acceptance Confidence
                </div>

                <div
                    id="acceptanceConfidence"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Trigger Price
                </div>

                <div
                    id="acceptanceTriggerPrice"
                    class="value trade-price"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Previous Level
                </div>

                <div
                    id="acceptancePreviousLevel"
                    class="value trade-price"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Pullback Low
                </div>

                <div
                    id="acceptancePullbackLow"
                    class="value trade-price"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Pullback High
                </div>

                <div
                    id="acceptancePullbackHigh"
                    class="value trade-price"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Acceptance Reason
                </div>

                <div
                    id="acceptanceReason"
                    class="value recommendation"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Acceptance Evidence
                </div>

                <ul
                    id="acceptanceEvidence"
                    class="explanation-list"
                >
                    <li class="empty-list">
                        No acceptance evidence.
                    </li>
                </ul>
            </article>

            <article class="card wide">
                <div class="label">
                    Acceptance Warnings
                </div>

                <ul
                    id="acceptanceWarnings"
                    class="explanation-list warning-list"
                >
                    <li class="empty-list">
                        No acceptance warnings.
                    </li>
                </ul>
            </article>

             <article class="card">
                <div class="label">
                    Trend Analyst
                </div>

                <div
                    id="trendAnalyst"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Trend Opinion
                </div>

                <div
                    id="trendOpinion"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Trend Confidence
                </div>

                <div
                    id="trendConfidence"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Trend Enabled
                </div>

                <div
                    id="trendEnabled"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Trend Evidence
                </div>

                <ul
                    id="trendEvidence"
                    class="explanation-list"
                >
                    <li class="empty-list">
                        No trend evidence.
                    </li>
                </ul>
            </article>

            <article class="card wide">
                <div class="label">
                    Trend Warnings
                </div>

                <ul
                    id="trendWarnings"
                    class="explanation-list warning-list"
                >
                    <li class="empty-list">
                        No trend warnings.
                    </li>
                </ul>
            </article>

            <article class="card">
                <div class="label">
                    Current State
                </div>

                <div
                    id="state"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Uptime
                </div>

                <div
                    id="uptime"
                    class="value"
                >
                    —
                </div>
            </article>

             <article class="card">
                <div class="label">
                    Completed Cycles
                </div>

                <div
                    id="cycles"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Latest Cycle Status
                </div>

                <div
                    id="latestCycleStatus"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Cycle Started
                </div>

                <div
                    id="latestCycleStarted"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Cycle Completed
                </div>

                <div
                    id="latestCycleCompleted"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Running
                </div>

                <div
                    id="running"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Last Heartbeat
                </div>

                <div
                    id="heartbeat"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Last Successful Cycle
                </div>

                <div
                    id="successfulCycle"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Last Transition
                </div>

                <div
                    id="transition"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card">
                <div class="label">
                    Runtime Started
                </div>

                <div
                    id="started"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Latest Cycle Message
                </div>

                <div
                    id="latestCycleMessage"
                    class="value"
                >
                    —
                </div>
            </article>

            <article class="card wide">
                <div class="label">
                    Error
                </div>

                <div
                    id="error"
                    class="value"
                >
                    None
                </div>
            </article>
        </section>

        <div class="footer">
            Dashboard refresh interval:
            {float(refresh_seconds):g} seconds
        </div>
    </main>

    <script>
        const refreshMilliseconds = (
            {refresh_milliseconds}
        );

        function formatBoolean(value) {{
            if (value === true) {{
                return "YES";
            }}

            if (value === false) {{
                return "NO";
            }}

            return "—";
        }}

        function formatDate(value) {{
            if (!value) {{
                return "—";
            }}

            const parsed = new Date(value);

            if (Number.isNaN(parsed.getTime())) {{
                return value;
            }}

            return parsed.toLocaleString();
        }}

        function formatUptime(seconds) {{
            if (
                seconds === null
                || seconds === undefined
                || Number.isNaN(Number(seconds))
            ) {{
                return "—";
            }}

            let remaining = Math.max(
                0,
                Math.floor(
                    Number(seconds)
                )
            );

            const days = Math.floor(
                remaining / 86400
            );

            remaining %= 86400;

            const hours = Math.floor(
                remaining / 3600
            );

            remaining %= 3600;

            const minutes = Math.floor(
                remaining / 60
            );

            const secs = (
                remaining % 60
            );

            const parts = [];

            if (days > 0) {{
                parts.push(
                    `${{days}}d`
                );
            }}

            if (
                hours > 0
                || days > 0
            ) {{
                parts.push(
                    `${{hours}}h`
                );
            }}

            if (
                minutes > 0
                || hours > 0
                || days > 0
            ) {{
                parts.push(
                    `${{minutes}}m`
                );
            }}

            parts.push(
                `${{secs}}s`
            );

            return parts.join(
                " "
            );
        }}

        function setText(
            id,
            value
        ) {{
            document
                .getElementById(id)
                .textContent = value;
        }}

        function updateStateBadge(
            state
        ) {{
            const badge = document.getElementById(
                "stateBadge"
            );

            const normalized = (
                state || "UNKNOWN"
            ).toUpperCase();

            badge.textContent = normalized;
            badge.className = "state-badge";

            if (
                normalized === "RUNNING"
                || normalized === "CONNECTED"
                || normalized === "STARTING"
            ) {{
                badge.classList.add(
                    "state-running"
                );
            }} else if (
                normalized === "SLEEPING"
            ) {{
                badge.classList.add(
                    "state-sleeping"
                );
            }} else if (
                normalized === "FAILED"
            ) {{
                badge.classList.add(
                    "state-failed"
                );
            }} else if (
                normalized === "STOPPED"
                || normalized === "STOPPING"
            ) {{
                badge.classList.add(
                    "state-stopped"
                );
            }}
        }}

        function updateCycleStatus(
            status
        ) {{
            const element = document.getElementById(
                "latestCycleStatus"
            );

            const normalized = (
                status || "—"
            ).toUpperCase();

            element.textContent = normalized;
            element.className = "value";

            if (normalized === "COMPLETED") {{
                element.classList.add(
                    "cycle-completed"
                );
            }} else if (
                normalized.startsWith(
                    "SKIPPED"
                )
                || normalized === "STALE_DATA"
            ) {{
                element.classList.add(
                    "cycle-skipped"
                );
            }} else if (
                normalized === "FAILED"
            ) {{
                element.classList.add(
                    "cycle-failed"
                );
            }}
        }}

        function updateDecision(
            decision
        ) {{
            const element = document.getElementById(
                "latestDecision"
            );

            const normalized = (
                decision || "—"
            ).toUpperCase();

            element.textContent = normalized;
            element.className = "value";

            if (
                normalized === "READY"
                || normalized === "LONG"
                || normalized === "SHORT"
            ) {{
                element.classList.add(
                    "decision-ready"
                );
            }} else if (
                normalized === "WAIT"
                || normalized === "PREPARE"
            ) {{
                element.classList.add(
                    "decision-wait"
                );
            }} else if (
                normalized === "PASS"
            ) {{
                element.classList.add(
                    "decision-pass"
                );
            }}
        }}

        function formatConfidence(
            confidence
        ) {{
            if (
                confidence === null
                || confidence === undefined
                || Number.isNaN(
                    Number(confidence)
                )
            ) {{
                return "—";
            }}

            return (
                Number(confidence).toFixed(1)
                + "%"
            );
        }}

        function updateActionable(
            actionable
        ) {{
            const element = document.getElementById(
                "decisionActionable"
            );

            element.className = "value";

            if (actionable === true) {{
                element.textContent = "YES";
                element.classList.add(
                    "actionable-yes"
                );

                return;
            }}

            if (actionable === false) {{
                element.textContent = "NO";
                element.classList.add(
                    "actionable-no"
                );

                return;
            }}

            element.textContent = "—";
        }}

        function updateAcceptanceConfirmed(
            confirmed
        ) {{
            const element = document.getElementById(
                "acceptanceConfirmed"
            );

            element.className = "value";

            if (confirmed === true) {{
                element.textContent = "CONFIRMED";
                element.classList.add(
                    "plan-valid"
                );

                return;
            }}

            if (confirmed === false) {{
                element.textContent = "NOT CONFIRMED";
                element.classList.add(
                    "plan-invalid"
                );

                return;
            }}

            element.textContent = "—";
            element.classList.add(
                "institution-unknown"
            );
        }}

        function updateTrendEnabled(
            enabled
        ) {{
            const element = document.getElementById(
                "trendEnabled"
            );

            element.className = "value";

            if (enabled === true) {{
                element.textContent = "ENABLED";
                element.classList.add(
                    "plan-valid"
                );

                return;
            }}

            if (enabled === false) {{
                element.textContent = "DISABLED";
                element.classList.add(
                    "plan-invalid"
                );

                return;
            }}

            element.textContent = "—";
            element.classList.add(
                "institution-unknown"
            );
        }}

        function updateStructureEnabled(
            enabled
        ) {{
            const element = document.getElementById(
                "structureEnabled"
            );

            element.className = "value";

            if (enabled === true) {{
                element.textContent = "ENABLED";
                element.classList.add(
                    "plan-valid"
                );

                return;
            }}

            if (enabled === false) {{
                element.textContent = "DISABLED";
                element.classList.add(
                    "plan-invalid"
                );

                return;
            }}

            element.textContent = "—";
            element.classList.add(
                "institution-unknown"
            );
        }}

        function updateLiquidityEnabled(
            enabled
        ) {{
            const element = document.getElementById(
                "liquidityEnabled"
            );

            element.className = "value";

            if (enabled === true) {{
                element.textContent = "ENABLED";
                element.classList.add(
                    "plan-valid"
                );

                return;
            }}

            if (enabled === false) {{
                element.textContent = "DISABLED";
                element.classList.add(
                    "plan-invalid"
                );

                return;
            }}

            element.textContent = "—";
            element.classList.add(
                "institution-unknown"
            );
        }}

        function updateTradeDirection(
            direction
        ) {{
            const element = document.getElementById(
                "tradeDirection"
            );

            const normalized = (
                direction || "—"
            ).toUpperCase();

            element.textContent = normalized;
            element.className = "value";

            if (normalized === "LONG") {{
                element.classList.add(
                    "direction-long"
                );
            }} else if (
                normalized === "SHORT"
            ) {{
                element.classList.add(
                    "direction-short"
                );
            }}
        }}

        function formatTradePrice(
            value
        ) {{
            if (
                value === null
                || value === undefined
                || Number.isNaN(
                    Number(value)
                )
            ) {{
                return "—";
            }}

            return Number(value).toFixed(2);
        }}

        function formatRewardRisk(
            value
        ) {{
            if (
                value === null
                || value === undefined
                || Number.isNaN(
                    Number(value)
                )
            ) {{
                return "—";
            }}

            return (
                Number(value).toFixed(2)
                + "R"
            );
        }}

        function formatAtrDistance(
            value
        ) {{
            if (
                value === null
                || value === undefined
                || Number.isNaN(
                    Number(value)
                )
            ) {{
                return "—";
            }}

            return (
                Number(value).toFixed(2)
                + " ATR"
            );
        }}

        function updateTradePlanValid(
            valid
        ) {{
            const element = document.getElementById(
                "tradePlanValid"
            );

            element.className = "value";

            if (valid === true) {{
                element.textContent = "VALID";
                element.classList.add(
                    "plan-valid"
                );

                return;
            }}

            if (valid === false) {{
                element.textContent = "INVALID";
                element.classList.add(
                    "plan-invalid"
                );

                return;
            }}

            element.textContent = "—";
        }}

        function updateTradeQuality(
            quality
        ) {{
            const element = document.getElementById(
                "tradeQuality"
            );

            element.className = "value";

            if (
                quality === null
                || quality === undefined
                || Number.isNaN(
                    Number(quality)
                )
            ) {{
                element.textContent = "—";

                return;
            }}

            const normalized = Number(quality);

            element.textContent = (
                normalized.toFixed(0)
                + "/100"
            );

            if (normalized >= 80) {{
                element.classList.add(
                    "trade-quality-high"
                );
            }} else if (
                normalized >= 60
            ) {{
                element.classList.add(
                    "trade-quality-medium"
                );
            }} else {{
                element.classList.add(
                    "trade-quality-low"
                );
            }}
        }}

        function updateTextList(
            id,
            items,
            emptyMessage
        ) {{
            const element = document.getElementById(
                id
            );

            element.replaceChildren();

            if (
                !Array.isArray(items)
                || items.length === 0
            ) {{
                const emptyItem = document.createElement(
                    "li"
                );

                emptyItem.textContent = emptyMessage;

                emptyItem.className = "empty-list";

                element.appendChild(
                    emptyItem
                );

                return;
            }}

            for (const item of items) {{
                const normalized = String(
                    item ?? ""
                ).trim();

                if (!normalized) {{
                    continue;
                }}

                const listItem = document.createElement(
                    "li"
                );

                listItem.textContent = normalized;

                element.appendChild(
                    listItem
                );
            }}

            if (element.children.length === 0) {{
                const emptyItem = document.createElement(
                    "li"
                );

                emptyItem.textContent = emptyMessage;

                emptyItem.className = "empty-list";

                element.appendChild(
                    emptyItem
                );
            }}
        }}

        function updateAnalystSummary(summary) {{
            const container = document.getElementById(
                "analystSummary"
            );

            container.replaceChildren();

            if (
                !summary
                || typeof summary !== "object"
                || Array.isArray(summary)
                || Object.keys(summary).length === 0
            ) {{
                const empty = document.createElement(
                    "div"
                );

                empty.className = "empty-list";
                empty.textContent =
                    "No analyst summary available.";

                container.appendChild(empty);
                return;
            }}

            for (
                const [
                    analystId,
                    details,
                ] of Object.entries(summary)
            ) {{
                const row = document.createElement(
                    "div"
                );

                row.className =
                    "analyst-summary-row";

                const analystCell =
                    document.createElement("div");

                const analystHeading =
                    document.createElement("div");

                analystHeading.className =
                    "analyst-summary-heading";
                analystHeading.textContent =
                    "Analyst";

                const analystValue =
                    document.createElement("div");

                analystValue.className =
                    "analyst-summary-value";
                analystValue.textContent =
                    analystId;

                analystCell.append(
                    analystHeading,
                    analystValue
                );

                const opinionCell =
                    document.createElement("div");

                const opinionHeading =
                    document.createElement("div");

                opinionHeading.className =
                    "analyst-summary-heading";
                opinionHeading.textContent =
                    "Opinion";

                const opinionValue =
                    document.createElement("div");

                opinionValue.className =
                    "analyst-summary-value";
                opinionValue.textContent =
                    details?.opinion || "—";

                opinionCell.append(
                    opinionHeading,
                    opinionValue
                );

                const confidenceCell =
                    document.createElement("div");

                const confidenceHeading =
                    document.createElement("div");

                confidenceHeading.className =
                    "analyst-summary-heading";
                confidenceHeading.textContent =
                    "Confidence";

                const confidenceValue =
                    document.createElement("div");

                confidenceValue.className =
                    "analyst-summary-value";

                confidenceValue.textContent =
                    typeof details?.confidence
                        === "number"
                        ? (
                            details.confidence
                                .toFixed(1)
                            + "%"
                        )
                        : "—";

                confidenceCell.append(
                    confidenceHeading,
                    confidenceValue
                );

                const enabledCell =
                    document.createElement("div");

                const enabledHeading =
                    document.createElement("div");

                enabledHeading.className =
                    "analyst-summary-heading";
                enabledHeading.textContent =
                    "Status";

                const enabledValue =
                    document.createElement("div");

                enabledValue.className =
                    "analyst-summary-value";

                if (details?.enabled === true) {{
                    enabledValue.textContent =
                        "ENABLED";
                    enabledValue.classList.add(
                        "plan-valid"
                    );
                }} else if (
                    details?.enabled === false
                ) {{
                    enabledValue.textContent =
                        "DISABLED";
                    enabledValue.classList.add(
                        "plan-invalid"
                    );
                }} else {{
                    enabledValue.textContent = "—";
                    enabledValue.classList.add(
                        "institution-unknown"
                    );
                }}

                enabledCell.append(
                    enabledHeading,
                    enabledValue
                );

                row.append(
                    analystCell,
                    opinionCell,
                    confidenceCell,
                    enabledCell
                );

                container.appendChild(row);
            }}
        }}

        function updateInstitutionalDirection(
            id,
            direction
        ) {{
            const element = document.getElementById(
                id
            );

            element.className = "value";

            if (
                direction === null
                || direction === undefined
            ) {{
                element.textContent = "—";
                element.classList.add(
                    "institution-unknown"
                );

                return;
            }}

            const normalized = String(
                direction
            ).trim().toUpperCase();

            element.textContent = normalized || "—";

            if (normalized === "BULLISH") {{
                element.classList.add(
                    "institution-bullish"
                );
            }} else if (
                normalized === "BEARISH"
            ) {{
                element.classList.add(
                    "institution-bearish"
                );
            }} else if (
                normalized === "NEUTRAL"
            ) {{
                element.classList.add(
                    "institution-neutral"
                );
            }} else {{
                element.classList.add(
                    "institution-unknown"
                );
            }}
        }}

        function updatePercentageMetric(
            id,
            value
        ) {{
            const element = document.getElementById(
                id
            );

            element.className = "value";

            if (
                value === null
                || value === undefined
                || Number.isNaN(
                    Number(value)
                )
            ) {{
                element.textContent = "—";

                return;
            }}

            const normalized = Number(value);

            element.textContent = (
                normalized.toFixed(0)
                + "/100"
            );

            if (normalized >= 80) {{
                element.classList.add(
                    "metric-good"
                );
            }} else if (
                normalized >= 60
            ) {{
                element.classList.add(
                    "metric-medium"
                );
            }} else {{
                element.classList.add(
                    "metric-low"
                );
            }}
        }}

        function updateInstitutionalCount(
            id,
            value,
            conflict = false
        ) {{
            const element = document.getElementById(
                id
            );

            element.className = "value";

            if (
                value === null
                || value === undefined
                || Number.isNaN(
                    Number(value)
                )
            ) {{
                element.textContent = "—";

                return;
            }}

            const normalized = Number(value);

            element.textContent = (
                normalized.toFixed(0)
            );

            if (conflict) {{
                element.classList.add(
                    normalized === 0
                        ? "conflict-clear"
                        : "conflict-present"
                );

                return;
            }}

            if (normalized >= 5) {{
                element.classList.add(
                    "metric-good"
                );
            }} else if (
                normalized >= 3
            ) {{
                element.classList.add(
                    "metric-medium"
                );
            }} else {{
                element.classList.add(
                    "metric-low"
                );
            }}
        }}

        function updateSupportFlag(
            id,
            supported
        ) {{
            const element = document.getElementById(
                id
            );

            if (!element) {{
                return;
            }}

            element.className = "value";

            if (supported === true) {{
                element.textContent = "SUPPORT";
                element.classList.add(
                    "plan-valid"
                );

                return;
            }}

            if (supported === false) {{
                element.textContent = "NO SUPPORT";
                element.classList.add(
                    "institution-unknown"
                );

                return;
            }}

            element.textContent = "—";
            element.classList.add(
                "institution-unknown"
            );
        }}

        function updateConfidenceAdjustment(
            value
        ) {{
            const element = document.getElementById(
                "confluenceConfidenceAdjustment"
            );

            if (!element) {{
                return;
            }}

            element.className = "value";

            if (
                value === null
                || value === undefined
                || Number.isNaN(
                    Number(value)
                )
            ) {{
                element.textContent = "—";
                element.classList.add(
                    "institution-unknown"
                );

                return;
            }}

            const normalized = Number(value);

            element.textContent = (
                "+"
                + normalized.toFixed(0)
            );

            if (normalized >= 6) {{
                element.classList.add(
                    "metric-good"
                );

                return;
            }}

            if (normalized >= 3) {{
                element.classList.add(
                    "metric-medium"
                );

                return;
            }}

            element.classList.add(
                "metric-low"
            );
        }}
        
        async function loadHealth() {{
            const message = document.getElementById(
                "statusMessage"
            );

            try {{
                const response = await fetch(
                    "/api/health",
                    {{
                        cache: "no-store"
                    }}
                );

                if (!response.ok) {{
                    throw new Error(
                        `HTTP ${{response.status}}`
                    );
                }}

                const payload = await response.json();

                setText(
                    "symbol",
                    payload.symbol ?? "—"
                );

                setText(
                    "timeframe",
                    payload.timeframe ?? "—"
                );

                setText(
                    "marketSession",
                    payload.market_session ?? "—"
                );

                updateDecision(
                    payload.latest_decision
                );

                setText(
                    "decisionConfidence",
                    formatConfidence(
                        payload.decision_confidence
                    )
                );

                updateActionable(
                    payload.decision_actionable
                );

                updateTradeDirection(
                    payload.trade_direction
                );

                setText(
                    "decisionRecommendation",
                    payload.decision_recommendation
                        ?? "—"
                );

                updateTextList(
                    "decisionReasons",
                    payload.decision_reasons,
                    "No decision reasons available."
                );

                updateTextList(
                    "decisionWarnings",
                    payload.decision_warnings,
                    "No decision warnings."
                );

                updateAnalystSummary(
                    payload.analyst_summary
                );

                updateTradePlanValid(
                    payload.trade_plan_valid
                );

                setText(
                    "tradeEntry",
                    formatTradePrice(
                        payload.trade_entry
                    )
                );

                setText(
                    "tradeStop",
                    formatTradePrice(
                        payload.trade_stop
                    )
                );

                setText(
                    "tradeTarget1",
                    formatTradePrice(
                        payload.trade_target1
                    )
                );

                setText(
                    "tradeTarget2",
                    formatTradePrice(
                        payload.trade_target2
                    )
                );

                setText(
                    "tradeRR1",
                    formatRewardRisk(
                        payload.trade_rr1
                    )
                );

                setText(
                    "tradeRR2",
                    formatRewardRisk(
                        payload.trade_rr2
                    )
                );

                updateTradeQuality(
                    payload.trade_quality
                );

                setText(
                    "tradeNarrative",
                    payload.trade_narrative
                        ?? "—"
                );

                updateTextList(
                    "tradeReasons",
                    payload.trade_reasons,
                    "No trade reasons available."
                );

                updateTextList(
                    "tradeWarnings",
                    payload.trade_warnings,
                    "No trade warnings."
                );

                updateInstitutionalDirection(
                    "institutionalBias",
                    payload.institutional_bias
                );

                updatePercentageMetric(
                    "institutionalBiasConfidence",
                    payload.institutional_bias_confidence
                );

                updatePercentageMetric(
                    "institutionalBiasStrength",
                    payload.institutional_bias_strength
                );

                updatePercentageMetric(
                    "institutionalBiasBullishScore",
                    payload.institutional_bias_bullish_score
                );

                updatePercentageMetric(
                    "institutionalBiasBearishScore",
                    payload.institutional_bias_bearish_score
                );

                updateInstitutionalCount(
                    "institutionalBiasAgreementCount",
                    payload.institutional_bias_agreement_count
                );

                updateInstitutionalCount(
                    "institutionalBiasConflictCount",
                    payload.institutional_bias_conflict_count,
                    true
                );

                updateTextList(
                    "institutionalBiasSupportingDomains",
                    payload.institutional_bias_supporting_domains,
                    "No supporting bias domains."
                );

                updateTextList(
                    "institutionalBiasOpposingDomains",
                    payload.institutional_bias_opposing_domains,
                    "No opposing bias domains."
                );

                setText(
                    "marketPhase",
                    payload.market_phase
                        ?? "—"
                );

                updatePercentageMetric(
                    "marketPhaseConfidence",
                    payload.market_phase_confidence
                );

                updateInstitutionalDirection(
                    "confluenceDirection",
                    payload.confluence_direction
                );

                updatePercentageMetric(
                    "confluenceScore",
                    payload.confluence_score
                );

                updateInstitutionalCount(
                    "confluenceAgreementCount",
                    payload.confluence_agreement_count
                );

                updateInstitutionalCount(
                    "confluenceConflictCount",
                    payload.confluence_conflict_count,
                    true
                );

                //====================================================
                // CONFLUENCE DETAIL
                //====================================================

                updateConfidenceAdjustment(
                    payload.confluence_confidence_adjustment
                );

                updateSupportFlag(
                    "confluenceStructureSupport",
                    payload.confluence_structure_support
                );

                updateSupportFlag(
                    "confluenceLiquiditySupport",
                    payload.confluence_liquidity_support
                );

                updateSupportFlag(
                    "confluenceOrderBlockSupport",
                    payload.confluence_order_block_support
                );

                updateSupportFlag(
                    "confluenceAuctionSupport",
                    payload.confluence_auction_support
                );

                updateSupportFlag(
                    "confluencePressureSupport",
                    payload.confluence_pressure_support
                );

                updateSupportFlag(
                    "confluenceParticipationSupport",
                    payload.confluence_participation_support
                );

                updateSupportFlag(
                    "confluenceValueSupport",
                    payload.confluence_value_support
                );

                updateInstitutionalCount(
                    "confluenceBullishCount",
                    payload.confluence_bullish_count
                );

                updateInstitutionalCount(
                    "confluenceBearishCount",
                    payload.confluence_bearish_count,
                    true
                );

                updateInstitutionalCount(
                    "confluenceNeutralCount",
                    payload.confluence_neutral_count
                );

                updateInstitutionalCount(
                    "confluenceUnknownCount",
                    payload.confluence_unknown_count
                );

                updateInstitutionalCount(
                    "confluenceDomainCount",
                    payload.confluence_domain_count
                );

                //====================================================
                // MARKET PHASE DETAIL
                //====================================================

                updatePercentageMetric(
                    "marketPhaseStrength",
                    payload.market_phase_strength
                );

                updateInstitutionalCount(
                    "marketPhaseAgreementCount",
                    payload.market_phase_agreement_count
                );

                updateInstitutionalCount(
                    "marketPhaseConflictCount",
                    payload.market_phase_conflict_count,
                    true
                );

                updateTextList(
                    "marketPhaseSupportingDomains",
                    payload.market_phase_supporting_domains,
                    "No supporting phase domains."
                );

                updateTextList(
                    "marketPhaseOpposingDomains",
                    payload.market_phase_opposing_domains,
                    "No opposing phase domains."
                );

                 //====================================================
                // SETUP LIFECYCLE DETAIL
                //====================================================

                setText(
                    "setupLifecycleState",
                    payload.setup_lifecycle_state
                        ?? "—"
                );

                setText(
                    "setupLifecycleDirection",
                    payload.setup_lifecycle_direction
                        ?? "—"
                );

                updatePercentageMetric(
                    "setupLifecycleConfidence",
                    payload.setup_lifecycle_confidence
                );

                setText(
                    "setupLifecycleAtrDistance",
                    formatAtrDistance(
                        payload.setup_lifecycle_atr_distance
                    )
                );

                setText(
                    "setupLifecycleAction",
                    payload.setup_lifecycle_action
                        ?? "—"
                );

                setText(
                    "setupLifecycleReason",
                    payload.setup_lifecycle_reason
                        ?? "—"
                );

                //====================================================
                // ACCEPTANCE DETAIL
                //====================================================

                updateAcceptanceConfirmed(
                    payload.acceptance_confirmed
                );

                setText(
                    "acceptanceDirection",
                    payload.acceptance_direction
                        ?? "—"
                );

                setText(
                    "acceptanceLevel",
                    payload.acceptance_level
                        ?? "—"
                );

                updatePercentageMetric(
                    "acceptanceScore",
                    payload.acceptance_score
                );

                updatePercentageMetric(
                    "acceptanceConfidence",
                    payload.acceptance_confidence
                );

                setText(
                    "acceptanceTriggerPrice",
                    formatTradePrice(
                        payload.acceptance_trigger_price
                    )
                );

                setText(
                    "acceptancePreviousLevel",
                    formatTradePrice(
                        payload.acceptance_previous_level
                    )
                );

                setText(
                    "acceptancePullbackLow",
                    formatTradePrice(
                        payload.acceptance_pullback_low
                    )
                );

                setText(
                    "acceptancePullbackHigh",
                    formatTradePrice(
                        payload.acceptance_pullback_high
                    )
                );

                setText(
                    "acceptanceReason",
                    payload.acceptance_reason
                        ?? "—"
                );

                updateTextList(
                    "acceptanceEvidence",
                    payload.acceptance_evidence,
                    "No acceptance evidence."
                );

                updateTextList(
                    "acceptanceWarnings",
                    payload.acceptance_warnings,
                    "No acceptance warnings."
                );

                //====================================================
                // TREND DETAIL
                //====================================================

                setText(
                    "trendAnalyst",
                    payload.trend_analyst
                        ?? "—"
                );

                setText(
                    "trendOpinion",
                    payload.trend_opinion
                        ?? "—"
                );

                updatePercentageMetric(
                    "trendConfidence",
                    payload.trend_confidence
                );

                updateTrendEnabled(
                    payload.trend_enabled
                );

                updateTextList(
                    "trendEvidence",
                    payload.trend_evidence,
                    "No trend evidence."
                );

                updateTextList(
                    "trendWarnings",
                    payload.trend_warnings,
                    "No trend warnings."
                );

                setText(
                    "structureAnalyst",
                    payload.structure_analyst ?? "—"
                );

                setText(
                    "structureOpinion",
                    payload.structure_opinion ?? "—"
                );

                updatePercentageMetric(
                    "structureConfidence",
                    payload.structure_confidence
                );

                updateStructureEnabled(
                    payload.structure_enabled
                );

                setText(
                    "liquidityAnalyst",
                    payload.liquidity_analyst ?? "—"
                );

                setText(
                    "liquidityOpinion",
                    payload.liquidity_opinion ?? "—"
                );

                updatePercentageMetric(
                    "liquidityConfidence",
                    payload.liquidity_confidence
                );

                updateLiquidityEnabled(
                    payload.liquidity_enabled
                );

                //====================================================
                // RUNTIME DETAIL
                //====================================================

                setText(
                    "state",
                    payload.state ?? "UNKNOWN"
                );

                setText(
                    "uptime",
                    formatUptime(
                        payload.uptime_seconds
                    )
                );

                setText(
                    "cycles",
                    payload.completed_cycle_count
                        ?? 0
                );


                updateCycleStatus(
                    payload.latest_cycle_status
                );

                setText(
                    "latestCycleStarted",
                    formatDate(
                        payload.latest_cycle_started_at
                    )
                );

                setText(
                    "latestCycleCompleted",
                    formatDate(
                        payload.latest_cycle_completed_at
                    )
                );

                setText(
                    "latestCycleMessage",
                    payload.latest_cycle_message
                        ?? "—"
                );

                setText(
                    "running",
                    formatBoolean(
                        payload.running
                    )
                );

                setText(
                    "heartbeat",
                    formatDate(
                        payload.last_heartbeat_at
                    )
                );

                setText(
                    "successfulCycle",
                    formatDate(
                        payload.last_successful_cycle_at
                    )
                );

                setText(
                    "transition",
                    formatDate(
                        payload.last_transition_at
                    )
                );

                setText(
                    "started",
                    formatDate(
                        payload.started_at
                    )
                );

                const error = (
                    payload.latest_error_type
                    || payload.error_type
                    || "None"
                );

                setText(
                    "error",
                    error
                );

                document
                    .getElementById("error")
                    .className = (
                        payload.failed
                        ? "value error"
                        : "value"
                    );

                updateStateBadge(
                    payload.state
                );

                const cycleSummary = (
                    payload.latest_cycle_status
                    ? (
                        " Latest cycle: "
                        + payload.latest_cycle_status
                        + "."
                    )
                    : ""
                );

                message.textContent = (
                    "Dashboard connected."
                    + cycleSummary
                    + " Last refreshed: "
                    + new Date().toLocaleTimeString()
                );
            }} catch (error) {{
                message.textContent = (
                    "Unable to load runtime health: "
                    + error
                );

                updateStateBadge(
                    "FAILED"
                );
            }}
        }}

        loadHealth();

        window.setInterval(
            loadHealth,
            refreshMilliseconds
        );
    </script>
</body>
</html>
"""


def create_dashboard_handler(
    *,
    health_status_file: str | Path,
    refresh_seconds: float = (
        DEFAULT_REFRESH_SECONDS
    ),
) -> type[BaseHTTPRequestHandler]:
    resolved_health_status_file = Path(
        health_status_file
    )

    dashboard_html = build_dashboard_html(
        refresh_seconds=refresh_seconds
    )

    class RuntimeHealthDashboardHandler(
        BaseHTTPRequestHandler,
    ):
        def do_GET(
            self,
        ) -> None:
            if self.path in {
                "/",
                "/index.html",
            }:
                self._send_html(
                    dashboard_html
                )

                return

            if self.path == "/api/health":
                self._send_health()

                return

            self.send_error(
                HTTPStatus.NOT_FOUND,
                "Resource not found.",
            )

        def _send_html(
            self,
            html: str,
        ) -> None:
            encoded = html.encode(
                "utf-8"
            )

            self.send_response(
                HTTPStatus.OK
            )

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8",
            )

            self.send_header(
                "Content-Length",
                str(
                    len(
                        encoded
                    )
                ),
            )

            self.send_header(
                "Cache-Control",
                "no-store",
            )

            self.end_headers()

            self.wfile.write(
                encoded
            )

        def _send_health(
            self,
        ) -> None:
            try:
                payload = read_health_status(
                    resolved_health_status_file
                )

                status = HTTPStatus.OK
            except FileNotFoundError:
                payload = {
                    "state": "UNAVAILABLE",
                    "message": (
                        "Health status file has not "
                        "been created yet."
                    ),
                    "running": False,
                    "failed": False,
                    "terminal": False,
                    "completed_cycle_count": 0,
                }

                status = (
                    HTTPStatus.SERVICE_UNAVAILABLE
                )
            except ValueError as error:
                payload = {
                    "state": "FAILED",
                    "message": str(
                        error
                    ),
                    "running": False,
                    "failed": True,
                    "terminal": False,
                    "completed_cycle_count": 0,
                }

                status = (
                    HTTPStatus.INTERNAL_SERVER_ERROR
                )

            encoded = json.dumps(
                payload,
                separators=(
                    ",",
                    ":",
                ),
                sort_keys=True,
            ).encode(
                "utf-8"
            )

            self.send_response(
                status
            )

            self.send_header(
                "Content-Type",
                "application/json; charset=utf-8",
            )

            self.send_header(
                "Content-Length",
                str(
                    len(
                        encoded
                    )
                ),
            )

            self.send_header(
                "Cache-Control",
                "no-store",
            )

            self.end_headers()

            self.wfile.write(
                encoded
            )

        def log_message(
            self,
            format: str,
            *args: object,
        ) -> None:
            del format
            del args

    return RuntimeHealthDashboardHandler


def create_dashboard_server(
    *,
    health_status_file: str | Path,
    host: str = DEFAULT_DASHBOARD_HOST,
    port: int = DEFAULT_DASHBOARD_PORT,
    refresh_seconds: float = (
        DEFAULT_REFRESH_SECONDS
    ),
) -> ThreadingHTTPServer:
    if not isinstance(
        host,
        str,
    ):
        raise TypeError(
            "host must be a string."
        )

    resolved_host = host.strip()

    if not resolved_host:
        raise ValueError(
            "host cannot be empty."
        )

    if isinstance(
        port,
        bool,
    ) or not isinstance(
        port,
        int,
    ):
        raise TypeError(
            "port must be an int."
        )

    if not 1 <= port <= 65535:
        raise ValueError(
            "port must be between 1 and 65535."
        )

    handler = create_dashboard_handler(
        health_status_file=(
            health_status_file
        ),
        refresh_seconds=refresh_seconds,
    )

    return ThreadingHTTPServer(
        (
            resolved_host,
            port,
        ),
        handler,
    )


def run_dashboard(
    *,
    health_status_file: str | Path,
    host: str = DEFAULT_DASHBOARD_HOST,
    port: int = DEFAULT_DASHBOARD_PORT,
    refresh_seconds: float = (
        DEFAULT_REFRESH_SECONDS
    ),
) -> None:
    server = create_dashboard_server(
        health_status_file=(
            health_status_file
        ),
        host=host,
        port=port,
        refresh_seconds=refresh_seconds,
    )

    try:
        print(
            "IMIE Runtime Dashboard"
        )

        print(
            "Health file : "
            f"{Path(health_status_file)}"
        )

        print(
            "Dashboard   : "
            f"http://{host}:{port}"
        )

        print(
            "Press Ctrl+C to stop."
        )

        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()