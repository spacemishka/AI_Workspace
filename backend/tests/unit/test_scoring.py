import pytest
from src.analytics.scoring import (
    calculate_piotroski_f_score,
    calculate_altman_z_score,
    calculate_beneish_m_score,
)


def test_piotroski_f_score_perfect():
    res = calculate_piotroski_f_score(
        net_income_curr=100.0,
        operating_cf_curr=150.0,
        total_assets_curr=1000.0,
        current_assets_curr=400.0,
        current_liab_curr=200.0,
        long_term_debt_curr=100.0,
        gross_margin_curr=0.5,
        revenue_curr=800.0,
        shares_curr=10.0,
        total_assets_prior=950.0,
        current_assets_prior=350.0,
        current_liab_prior=250.0,
        long_term_debt_prior=120.0,
        gross_margin_prior=0.45,
        revenue_prior=700.0,
        shares_prior=10.0,
        net_income_prior=80.0,
    )

    assert res.score == 9
    assert res.positive_roa is True
    assert res.positive_cfo is True
    assert res.roa_increasing is True
    assert res.cfo_greater_than_net_income is True
    assert res.long_term_debt_decreasing is True
    assert res.current_ratio_increasing is True
    assert res.no_share_dilution is True
    assert res.gross_margin_increasing is True
    assert res.asset_turnover_increasing is True


def test_altman_z_score():
    res = calculate_altman_z_score(
        working_capital=200.0,
        retained_earnings=300.0,
        ebit=150.0,
        market_cap=1200.0,
        revenue=1000.0,
        total_assets=1000.0,
        total_liabilities=400.0,
    )

    assert res.score > 2.99
    assert res.zone == "Safe"


def test_beneish_m_score_normal():
    res = calculate_beneish_m_score(
        receivables_curr=100, revenue_curr=1000, gross_margin_curr=0.4,
        non_current_assets_curr=500, total_assets_curr=1000, depreciation_curr=50,
        sga_curr=150, net_income_curr=100, operating_cf_curr=120, total_debt_curr=200,
        receivables_prior=90, revenue_prior=900, gross_margin_prior=0.4,
        non_current_assets_prior=450, total_assets_prior=900, depreciation_prior=45,
        sga_prior=135, total_debt_prior=190,
    )

    assert res.score < -1.78
    assert res.is_manipulator_likely is False
