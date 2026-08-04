from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Any


@dataclass
class CompanyProfile:
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    exchange: Optional[str] = None
    currency: str = "USD"
    country: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None


@dataclass
class StockPrice:
    date: date
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int


@dataclass
class FinancialStatementsData:
    ticker: str
    income_statement: dict[str, Any] = field(default_factory=dict)
    balance_sheet: dict[str, Any] = field(default_factory=dict)
    cash_flow: dict[str, Any] = field(default_factory=dict)


class FinancialDataProvider(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g. 'yfinance', 'sec_edgar', 'fmp')."""
        pass

    @abstractmethod
    async def get_company_profile(self, ticker: str) -> CompanyProfile:
        """Fetch company profile and high-level metrics."""
        pass

    @abstractmethod
    async def get_price_history(
        self, ticker: str, period: str = "1y", interval: str = "1d"
    ) -> list[StockPrice]:
        """Fetch historical price data."""
        pass

    @abstractmethod
    async def get_financial_statements(
        self, ticker: str, period: str = "annual"
    ) -> FinancialStatementsData:
        """Fetch Income Statement, Balance Sheet, and Cash Flow."""
        pass
