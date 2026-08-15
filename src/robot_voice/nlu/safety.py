from __future__ import annotations

from robot_voice.domain.models import ParsedIntent, RiskLevel, SafetyPolicyDecision


class SafetyPolicy:
    def __init__(self, min_confidence: float = 0.75) -> None:
        self._min_confidence = min_confidence

    def evaluate(self, intent: ParsedIntent) -> SafetyPolicyDecision:
        if intent.intent in {"robot.stop", "robot.emergency_stop"}:
            return SafetyPolicyDecision(allowed=True, reason="interrupt command", requires_confirmation=False)

        if intent.confidence < self._min_confidence:
            return SafetyPolicyDecision(
                allowed=False,
                reason="low confidence",
                requires_confirmation=True,
            )

        if intent.risk_level in {RiskLevel.MEDIUM, RiskLevel.HIGH}:
            return SafetyPolicyDecision(
                allowed=True,
                reason="risk requires confirmation",
                requires_confirmation=True,
            )

        return SafetyPolicyDecision(allowed=True, reason="safe", requires_confirmation=intent.needs_confirmation)
