from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class InterestRate:
    country: str
    central_bank_interest_rate: float  # Percentage, e.g., 0.25


@dataclass
class InterestRates:
    date: date
    interest_rates: List[InterestRate]


@dataclass
class ExchangeRate:
    currency_pair: str  # e.g., "USD/EUR"
    exchange_rate: float  # e.g., 1.18


@dataclass
class CurrencyExchangeRates:
    date: date
    exchange_rates: List[ExchangeRate]


@dataclass
class CommodityPrice:
    commodity_name: str  # e.g., "Crude Oil"
    commodity_price: float  # Price per unit, e.g., 70.50


@dataclass
class CommodityPrices:
    date: date
    commodities: List[CommodityPrice]


@dataclass
class EconomicIndicators:
    date: date
    gdp_growth_rate: float
    unemployment_rate: float
    inflation_rate: float
    consumer_confidence_index: float
    manufacturing_index: float
    interest_rates: InterestRates
    exchange_rates: CurrencyExchangeRates
    commodity_prices: CommodityPrices
