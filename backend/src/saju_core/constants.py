from __future__ import annotations

from typing import Final

SUPPORTED_YEAR_MIN: Final = 1900
SUPPORTED_YEAR_MAX: Final = 2050
DEFAULT_TIMEZONE: Final = "Asia/Seoul"

STEMS: Final = [
    "Gap",
    "Eul",
    "Byeong",
    "Jeong",
    "Mu",
    "Gi",
    "Gyeong",
    "Sin",
    "Im",
    "Gye",
]
BRANCHES: Final = [
    "Ja",
    "Chuk",
    "In",
    "Myo",
    "Jin",
    "Sa",
    "O",
    "Mi",
    "Sin",
    "Yu",
    "Sul",
    "Hae",
]

STEM_ELEMENTS: Final = {
    "Gap": "wood",
    "Eul": "wood",
    "Byeong": "fire",
    "Jeong": "fire",
    "Mu": "earth",
    "Gi": "earth",
    "Gyeong": "metal",
    "Sin": "metal",
    "Im": "water",
    "Gye": "water",
}
STEM_YIN_YANG: Final = {
    "Gap": "yang",
    "Eul": "yin",
    "Byeong": "yang",
    "Jeong": "yin",
    "Mu": "yang",
    "Gi": "yin",
    "Gyeong": "yang",
    "Sin": "yin",
    "Im": "yang",
    "Gye": "yin",
}
BRANCH_ELEMENTS: Final = {
    "Ja": "water",
    "Chuk": "earth",
    "In": "wood",
    "Myo": "wood",
    "Jin": "earth",
    "Sa": "fire",
    "O": "fire",
    "Mi": "earth",
    "Sin": "metal",
    "Yu": "metal",
    "Sul": "earth",
    "Hae": "water",
}
HIDDEN_STEMS: Final = {
    "Ja": ["Im"],
    "Chuk": ["Gi", "Gye", "Sin"],
    "In": ["Mu", "Byeong", "Gap"],
    "Myo": ["Eul"],
    "Jin": ["Mu", "Eul", "Gye"],
    "Sa": ["Mu", "Gyeong", "Byeong"],
    "O": ["Jeong", "Gi"],
    "Mi": ["Gi", "Jeong", "Eul"],
    "Sin": ["Mu", "Im", "Gyeong"],
    "Yu": ["Sin"],
    "Sul": ["Mu", "Sin", "Jeong"],
    "Hae": ["Mu", "Gap", "Im"],
}
HIDDEN_STEM_WEIGHTS: Final = (0.6, 0.3, 0.1)

ELEMENTS: Final = ["wood", "fire", "earth", "metal", "water"]
GENERATES: Final = {
    "wood": "fire",
    "fire": "earth",
    "earth": "metal",
    "metal": "water",
    "water": "wood",
}
CONTROLS: Final = {
    "wood": "earth",
    "fire": "metal",
    "earth": "water",
    "metal": "wood",
    "water": "fire",
}

TEN_GODS: Final = [
    "friend",
    "rob_wealth",
    "eating_god",
    "hurting_officer",
    "indirect_wealth",
    "direct_wealth",
    "seven_killings",
    "direct_officer",
    "indirect_resource",
    "direct_resource",
]

BRANCH_RELATIONS: Final = {
    frozenset({"Ja", "O"}): ("clash", 1.0),
    frozenset({"Chuk", "Mi"}): ("clash", 1.0),
    frozenset({"In", "Sin"}): ("clash", 1.0),
    frozenset({"Myo", "Yu"}): ("clash", 1.0),
    frozenset({"Jin", "Sul"}): ("clash", 1.0),
    frozenset({"Sa", "Hae"}): ("clash", 1.0),
    frozenset({"Ja", "Chuk"}): ("combine", 0.8),
    frozenset({"In", "Hae"}): ("combine", 0.8),
    frozenset({"Myo", "Sul"}): ("combine", 0.8),
    frozenset({"Jin", "Yu"}): ("combine", 0.8),
    frozenset({"Sa", "Sin"}): ("combine", 0.8),
    frozenset({"O", "Mi"}): ("combine", 0.8),
}
STEM_RELATIONS: Final = {
    frozenset({"Gap", "Gi"}): ("combine", 0.6),
    frozenset({"Eul", "Gyeong"}): ("combine", 0.6),
    frozenset({"Byeong", "Sin"}): ("combine", 0.6),
    frozenset({"Jeong", "Im"}): ("combine", 0.6),
    frozenset({"Mu", "Gye"}): ("combine", 0.6),
}

GOAL_DOMAIN_MAP: Final = {
    "career": ("career", "wealth"),
    "relationship": ("relationship", "health"),
    "wealth": ("wealth", "career"),
    "health": ("health", "relationship"),
}

STATE_DEFAULTS: Final = {
    "career": 50.0,
    "relationship": 50.0,
    "wealth": 50.0,
    "health": 50.0,
    "stress": 35.0,
    "momentum": 50.0,
    "support": 50.0,
    "risk_exposure": 40.0,
}

SOLAR_TERM_BOUNDARIES: Final = [
    ("In", 315.0, "Ipchun"),
    ("Myo", 345.0, "Gyeongchip"),
    ("Jin", 15.0, "Cheongmyeong"),
    ("Sa", 45.0, "Ipha"),
    ("O", 75.0, "Mangjong"),
    ("Mi", 105.0, "Soseo"),
    ("Sin", 135.0, "Ipchu"),
    ("Yu", 165.0, "Baekro"),
    ("Sul", 195.0, "Hanro"),
    ("Hae", 225.0, "Ipdong"),
    ("Ja", 255.0, "Daeseol"),
    ("Chuk", 285.0, "Sohan"),
]

RULE_IMPACTS: Final = {
    "CAREER_MOVE": {"career": 12, "momentum": 8, "stress": 4},
    "CAREER_STALL": {"career": -10, "momentum": -8, "stress": 6},
    "AUTHORITY_PRESSURE": {"career": 2, "stress": 12, "health": -4},
    "SKILL_GAIN": {"career": 8, "momentum": 6, "support": 3},
    "RELATIONSHIP_BOND": {"relationship": 12, "support": 6, "stress": -3},
    "RELATIONSHIP_CONFLICT": {"relationship": -14, "stress": 10, "health": -3},
    "RECONCILIATION_WINDOW": {"relationship": 9, "support": 5, "stress": -2},
    "SOCIAL_FATIGUE": {"relationship": -6, "stress": 8, "health": -4},
    "WEALTH_GAIN": {"wealth": 14, "risk_exposure": 4, "momentum": 4},
    "WEALTH_LEAK": {"wealth": -15, "stress": 6, "relationship": -3},
    "INVESTMENT_VOLATILITY": {"wealth": 4, "risk_exposure": 12, "stress": 5},
    "ASSET_LOCK": {"wealth": 2, "momentum": -4, "risk_exposure": 3},
    "HEALTH_RECOVERY": {"health": 12, "stress": -8, "momentum": 3},
    "HEALTH_ALERT": {"health": -12, "stress": 7, "momentum": -4},
    "BURNOUT_RISK": {"health": -10, "stress": 12, "career": -3},
    "ENERGY_DROP": {"health": -7, "momentum": -7, "stress": 4},
}

RULE_POSTURES: Final = {
    "CAREER_MOVE": "move with preparation",
    "CAREER_STALL": "conserve and wait",
    "AUTHORITY_PRESSURE": "reduce exposure",
    "SKILL_GAIN": "invest in learning",
    "RELATIONSHIP_BOND": "lean in gently",
    "RELATIONSHIP_CONFLICT": "avoid escalation",
    "RECONCILIATION_WINDOW": "reopen dialogue carefully",
    "SOCIAL_FATIGUE": "reduce social load",
    "WEALTH_GAIN": "capture upside carefully",
    "WEALTH_LEAK": "pause commitments",
    "INVESTMENT_VOLATILITY": "limit position size",
    "ASSET_LOCK": "preserve optionality",
    "HEALTH_RECOVERY": "recover deliberately",
    "HEALTH_ALERT": "reduce load",
    "BURNOUT_RISK": "stop compounding pressure",
    "ENERGY_DROP": "slow the pace",
}

EVENT_DOMAIN: Final = {
    "CAREER_MOVE": "career",
    "CAREER_STALL": "career",
    "AUTHORITY_PRESSURE": "career",
    "SKILL_GAIN": "career",
    "RELATIONSHIP_BOND": "relationship",
    "RELATIONSHIP_CONFLICT": "relationship",
    "RECONCILIATION_WINDOW": "relationship",
    "SOCIAL_FATIGUE": "relationship",
    "WEALTH_GAIN": "wealth",
    "WEALTH_LEAK": "wealth",
    "INVESTMENT_VOLATILITY": "wealth",
    "ASSET_LOCK": "wealth",
    "HEALTH_RECOVERY": "health",
    "HEALTH_ALERT": "health",
    "BURNOUT_RISK": "health",
    "ENERGY_DROP": "health",
}
