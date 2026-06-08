from dataclasses import dataclass, field
from typing import List
from heart_cuda import Token


@dataclass
class AuditResult:
    primary_token: Token
    confidence: float = 1.0
    mixed_valence_detected: bool = False
    reason: str = ""
    alternative_interpretations: List[Token] = field(default_factory=list)


class InterpretationAudit:
    """
    Layer 3 - Interpretation Audit
    Goal: Detect when the parser may have collapsed mixed emotional signals
    and provide clearer alternatives before the token reaches Heart CUDA.
    """

    def __init__(self):
        self.mixed_signals = {
            "cancer", "death", "suffering", "pain", "loss", "grief",
            "crisis", "trauma", "struggle", "terrible", "burned", "died"
        }

    def audit(self, token: Token, raw_text: str = "") -> AuditResult:
        text_lower = raw_text.lower()
        has_mixed_signal = any(word in text_lower for word in self.mixed_signals)

        if not has_mixed_signal:
            return AuditResult(
                primary_token=token,
                confidence=0.85,
                mixed_valence_detected=False,
                reason="Clean input - no mixed signals detected"
            )

        # Mixed signal detected
        mixed_valence_detected = True
        confidence = 0.4
        reason = "Mixed emotional signals detected. Parser may have flattened context."

        # Create a more positive alternative interpretation toward the concept
        # (This is still a heuristic, but more general than before)
        alternative_valence = max(token.valence, 0.5)

        alternative = Token(
            concept=token.concept,
            valence=alternative_valence,
            energy=token.energy,
            structural_value=token.structural_value
        )

        return AuditResult(
            primary_token=token,                    # Keep original by default
            confidence=confidence,
            mixed_valence_detected=mixed_valence_detected,
            reason=reason,
            alternative_interpretations=[alternative]
        )


def audit_token(token: Token, raw_text: str = "") -> AuditResult:
    auditor = InterpretationAudit()
    return auditor.audit(token, raw_text)