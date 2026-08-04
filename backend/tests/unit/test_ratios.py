import pytest
from src.analytics.ratios import calculate_ratios


def test_calculate_ratios_basic():
    res = calculate_ratios(
        revenue=1000.0,
        gross_profit=600.0,
        operating_income=300.0,
        net_income=200.0,
        operating_cash_flow=250.0,
        capex=50.0,
        total_assets=2000.0,
        total_equity=1000.0,
        total_debt=400.0,
        cash_and_equivalents=100.0,
        current_assets=500.0,
        current_liabilities=250.0,
        interest_expense=30.0,
        effective_tax_rate=0.20,
    )

    assert res.gross_margin == 0.6
    assert res.operating_margin == 0.3
    assert res.net_margin == 0.2
    assert res.fcf_margin == 0.2  # (250 - 50) / 1000
    assert res.roe == 0.2         # 200 / 1000
    assert res.roa == 0.1         # 200 / 2000
    assert res.current_ratio == 2.0  # 500 / 250
    assert res.debt_to_equity == 0.4 # 400 / 1000
    assert res.interest_coverage == 10.0 # 300 / 30


def test_calculate_ratios_zero_division_safety():
    res = calculate_ratios(
        revenue=0.0,
        current_liabilities=0.0,
        total_equity=0.0,
    )

    assert res.gross_margin is None
    assert res.current_ratio is None
    assert res.roe is None
