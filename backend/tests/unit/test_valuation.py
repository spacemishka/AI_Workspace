import pytest
from src.analytics.valuation import calculate_dcf


def test_calculate_dcf_valuation():
    res = calculate_dcf(
        current_fcf=100.0,
        shares_outstanding=10.0,
        total_debt=50.0,
        cash_and_equivalents=20.0,
        growth_rate_5yr=0.10,
        terminal_growth_rate=0.025,
        discount_rate_wacc=0.09,
        projection_years=5,
    )

    assert len(res.projected_fcf) == 5
    assert res.projected_fcf[0] == 110.0  # 100 * 1.10
    assert res.present_value_fcf > 0.0
    assert res.present_value_terminal_value > 0.0
    assert res.intrinsic_value_per_share > 0.0


def test_dcf_invalid_shares():
    with pytest.raises(ValueError):
        calculate_dcf(current_fcf=100.0, shares_outstanding=0.0)
