import enum

class InteractionType(enum.Enum):
    CALL = "call"
    EMAIL = "email"
    MEETING = "meeting"

class OpportunityStage(enum.Enum):
    LEAD = "lead"
    PROSPECT = "prospect"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"