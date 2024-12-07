from dataclasses import dataclass
from datetime import date
from typing import List, Literal


@dataclass
class CountryRelationship:
    date: date
    country: str  # e.g., "China"
    event_description: str  # e.g., "Trade tensions escalate"
    event_impact: Literal["Positive", "Negative", "Neutral"]


@dataclass
class CountryRelationships:
    date: date
    relationships: List[CountryRelationship]


@dataclass
class PoliticalStability:
    date: date
    country: str
    political_stability_index: float  # Scale from -2.5 to 2.5


@dataclass
class GlobalEvent:
    date: date
    event_name: str  # e.g., "COVID-19 Pandemic"
    event_type: str  # e.g., "Pandemic", "War"
    event_impact: Literal["Positive", "Negative", "Neutral"]


@dataclass
class GlobalEvents:
    date: date
    events: List[GlobalEvent]
