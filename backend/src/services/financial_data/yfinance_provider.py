from datetime import datetime
import asyncio
import yfinance as yf
from src.core.logging import get_logger
from src.services.financial_data.base import (
    CompanyProfile,
    FinancialDataProvider,
    FinancialStatementsData,
    StockPrice,
)

logger = get_logger(__name__)


class YFinanceProvider(FinancialDataProvider):
    @property
    def name(self) -> str:
        return "yfinance"

    async def get_company_profile(self, ticker: str) -> CompanyProfile:
        logger.info("Fetching company profile via yfinance", ticker=ticker)
        
        def _fetch():
            t = yf.Ticker(ticker)
            info = t.info or {}
            return CompanyProfile(
                ticker=ticker.upper(),
                name=info.get("longName") or info.get("shortName") or ticker.upper(),
                sector=info.get("sector"),
                industry=info.get("industry"),
                exchange=info.get("exchange"),
                currency=info.get("currency", "USD"),
                country=info.get("country"),
                description=info.get("longBusinessSummary"),
                website=info.get("website"),
                market_cap=info.get("marketCap"),
                pe_ratio=info.get("trailingPE"),
                dividend_yield=info.get("dividendYield"),
            )

        return await asyncio.to_thread(_fetch)

    async def get_price_history(
        self, ticker: str, period: str = "1y", interval: str = "1d"
    ) -> list[StockPrice]:
        logger.info("Fetching price history via yfinance", ticker=ticker, period=period)

        def _fetch():
            t = yf.Ticker(ticker)
            df = t.history(period=period, interval=interval)
            prices: list[StockPrice] = []
            for idx, row in df.iterrows():
                dt = idx.date() if isinstance(idx, datetime) else idx
                prices.append(
                    StockPrice(
                        date=dt,
                        open=float(row.get("Open", 0.0)),
                        high=float(row.get("High", 0.0)),
                        low=float(row.get("Low", 0.0)),
                        close=float(row.get("Close", 0.0)),
                        adj_close=float(row.get("Adj Close", row.get("Close", 0.0))),
                        volume=int(row.get("Volume", 0)),
                    )
                )
            return prices

        return await asyncio.to_thread(_fetch)

    async def get_financial_statements(
        self, ticker: str, period: str = "annual"
    ) -> FinancialStatementsData:
        logger.info("Fetching financial statements via yfinance", ticker=ticker, period=period)

        def _fetch():
            t = yf.Ticker(ticker)
            if period == "quarterly":
                inc = t.quarterly_incomestmt
                bal = t.quarterly_balance_sheet
                cf = t.quarterly_cashflow
            else:
                inc = t.incomestmt
                bal = t.balance_sheet
                cf = t.cashflow

            def _df_to_dict(df):
                if df is None or df.empty:
                    return {}
                # Convert timestamps/dates in column headers to strings
                cleaned = {}
                for col in df.columns:
                    col_str = str(col.date()) if hasattr(col, "date") else str(col)
                    cleaned[col_str] = {str(k): (None if str(v) == "nan" else v) for k, v in df[col].items()}
                return cleaned

            return FinancialStatementsData(
                ticker=ticker.upper(),
                income_statement=_df_to_dict(inc),
                balance_sheet=_df_to_dict(bal),
                cash_flow=_df_to_dict(cf),
            )

        return await asyncio.to_thread(_fetch)
