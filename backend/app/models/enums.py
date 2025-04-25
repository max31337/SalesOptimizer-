import enum
from typing import List

class InteractionType(str, enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"

class OpportunityStage(enum.Enum):
    LEAD = "LEAD"
    PROSPECT = "PROSPECT"
    NEGOTIATION = "NEGOTIATION"
    CLOSED_WON = "CLOSED_WON"
    CLOSED_LOST = "CLOSED_LOST"

class OpportunityStageGroup:
    """Helper class to group opportunity stages by category."""
    
    ACTIVE: List[OpportunityStage] = [
        OpportunityStage.LEAD,
        OpportunityStage.PROSPECT,
        OpportunityStage.NEGOTIATION,
    ]

    CLOSED: List[OpportunityStage] = [
        OpportunityStage.CLOSED_WON,
        OpportunityStage.CLOSED_LOST,
    ]

    WON: List[OpportunityStage] = [
        OpportunityStage.CLOSED_WON,
    ]

    LOST: List[OpportunityStage] = [
        OpportunityStage.CLOSED_LOST,
    ]