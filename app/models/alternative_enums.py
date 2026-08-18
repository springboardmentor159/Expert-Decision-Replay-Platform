import enum


class FeasibilityScore(int, enum.Enum):
    VERY_DIFFICULT = 1
    DIFFICULT = 2
    MODERATE = 3
    GOOD = 4
    VERY_FEASIBLE = 5


class RiskLevel(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"
    