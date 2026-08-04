from dataclasses import dataclass, field
from typing import Optional


@dataclass
class PiotroskiBreakdown:
    score: int
    positive_roa: bool
    positive_cfo: bool
    roa_increasing: bool
    cfo_greater_than_net_income: bool
    long_term_debt_decreasing: bool
    current_ratio_increasing: bool
    no_share_dilution: bool
    gross_margin_increasing: bool
    asset_turnover_increasing: bool


@dataclass
class AltmanZScoreResult:
    score: float
    zone: str  # "Safe", "Grey", "Distress"


@dataclass
class BeneishMScoreResult:
    score: float
    is_manipulator_likely: bool  # True if M > -1.78


def calculate_piotroski_f_score(
    # Current Year
    net_income_curr: float,
    operating_cf_curr: float,
    total_assets_curr: float,
    current_assets_curr: float,
    current_liab_curr: float,
    long_term_debt_curr: float,
    gross_margin_curr: float,
    revenue_curr: float,
    shares_curr: float,
    # Prior Year
    total_assets_prior: float,
    current_assets_prior: float,
    current_liab_prior: float,
    long_term_debt_prior: float,
    gross_margin_prior: float,
    revenue_prior: float,
    shares_prior: float,
    net_income_prior: float,
) -> PiotroskiBreakdown:
    """Calculate 9-criterion Piotroski F-Score (0 to 9)."""
    roa_curr = net_income_curr / total_assets_curr if total_assets_curr > 0 else 0.0
    roa_prior = net_income_prior / total_assets_prior if total_assets_prior > 0 else 0.0

    cr_curr = current_assets_curr / current_liab_curr if current_liab_curr > 0 else 0.0
    cr_prior = current_assets_prior / current_liab_prior if current_liab_prior > 0 else 0.0

    at_curr = revenue_curr / total_assets_curr if total_assets_curr > 0 else 0.0
    at_prior = revenue_prior / total_assets_prior if total_assets_prior > 0 else 0.0

    # 9 Signals
    f_roa = net_income_curr > 0
    f_cfo = operating_cf_curr > 0
    f_droa = roa_curr > roa_prior
    f_accrual = operating_cf_curr > net_income_curr

    f_dlong = long_term_debt_curr <= long_term_debt_prior
    f_cr = cr_curr > cr_prior
    f_shares = shares_curr <= shares_prior

    f_gm = gross_margin_curr > gross_margin_prior
    f_at = at_curr > at_prior

    score = sum([
        f_roa, f_cfo, f_droa, f_accrual,
        f_dlong, f_cr, f_shares,
        f_gm, f_at
    ])

    return PiotroskiBreakdown(
        score=score,
        positive_roa=f_roa,
        positive_cfo=f_cfo,
        roa_increasing=f_droa,
        cfo_greater_than_net_income=f_accrual,
        long_term_debt_decreasing=f_dlong,
        current_ratio_increasing=f_cr,
        no_share_dilution=f_shares,
        gross_margin_increasing=f_gm,
        asset_turnover_increasing=f_at,
    )


def calculate_altman_z_score(
    working_capital: float,
    retained_earnings: float,
    ebit: float,
    market_cap: float,
    revenue: float,
    total_assets: float,
    total_liabilities: float,
) -> AltmanZScoreResult:
    """Calculate Altman Z-Score for public manufacturing/general companies."""
    if total_assets <= 0 or total_liabilities <= 0:
        return AltmanZScoreResult(score=0.0, zone="Distress")

    x1 = working_capital / total_assets
    x2 = retained_earnings / total_assets
    x3 = ebit / total_assets
    x4 = market_cap / total_liabilities
    x5 = revenue / total_assets

    z = (1.2 * x1) + (1.4 * x2) + (3.3 * x3) + (0.6 * x4) + (0.999 * x5)

    if z > 2.99:
        zone = "Safe"
    elif z >= 1.81:
        zone = "Grey"
    else:
        zone = "Distress"

    return AltmanZScoreResult(score=round(z, 2), zone=zone)


def calculate_beneish_m_score(
    # Current Year
    receivables_curr: float,
    revenue_curr: float,
    gross_margin_curr: float,
    non_current_assets_curr: float,
    total_assets_curr: float,
    depreciation_curr: float,
    sga_curr: float,
    net_income_curr: float,
    operating_cf_curr: float,
    total_debt_curr: float,
    # Prior Year
    receivables_prior: float,
    revenue_prior: float,
    gross_margin_prior: float,
    non_current_assets_prior: float,
    total_assets_prior: float,
    depreciation_prior: float,
    sga_prior: float,
    total_debt_prior: float,
) -> BeneishMScoreResult:
    """Calculate 8-parameter Beneish M-Score for earnings manipulation detection."""
    
    # 1. Days Sales in Receivables Index (DSRI)
    dsri_curr = (receivables_curr / revenue_curr) if revenue_curr > 0 else 1.0
    dsri_prior = (receivables_prior / revenue_prior) if revenue_prior > 0 else 1.0
    dsri = dsri_curr / dsri_prior if dsri_prior > 0 else 1.0

    # 2. Gross Margin Index (GMI)
    gmi = (gross_margin_prior / gross_margin_curr) if gross_margin_curr > 0 else 1.0

    # 3. Asset Quality Index (AQI)
    aq_curr = 1.0 - ((current_assets_curr := (total_assets_curr - non_current_assets_curr)) / total_assets_curr) if total_assets_curr > 0 else 0.0
    aq_prior = 1.0 - ((current_assets_prior := (total_assets_prior - non_current_assets_prior)) / total_assets_prior) if total_assets_prior > 0 else 0.0
    aqi = aq_curr / aq_prior if aq_prior > 0 else 1.0

    # 4. Sales Growth Index (SGI)
    sgi = revenue_curr / revenue_prior if revenue_prior > 0 else 1.0

    # 5. Depreciation Index (DEPI)
    depr_rate_prior = depreciation_prior / (depreciation_prior + non_current_assets_prior) if (depreciation_prior + non_current_assets_prior) > 0 else 0.1
    depr_rate_curr = depreciation_curr / (depreciation_curr + non_current_assets_curr) if (depreciation_curr + non_current_assets_curr) > 0 else 0.1
    depi = depr_rate_prior / depr_rate_curr if depr_rate_curr > 0 else 1.0

    # 6. Sales General & Administrative Expenses Index (SGAI)
    sgai_curr = sga_curr / revenue_curr if revenue_curr > 0 else 0.0
    sgai_prior = sga_prior / revenue_prior if revenue_prior > 0 else 0.0
    sgai = sgai_curr / sgai_prior if sgai_prior > 0 else 1.0

    # 7. Leverage Index (LVGI)
    lvgi_curr = total_debt_curr / total_assets_curr if total_assets_curr > 0 else 0.0
    lvgi_prior = total_debt_prior / total_assets_prior if total_assets_prior > 0 else 0.0
    lvgi = lvgi_curr / lvgi_prior if lvgi_prior > 0 else 1.0

    # 8. Total Accruals to Total Assets (TATA)
    tata = (net_income_curr - operating_cf_curr) / total_assets_curr if total_assets_curr > 0 else 0.0

    # Beneish M-Score Formula
    m = (-4.84) + (0.920 * dsri) + (0.528 * gmi) + (0.404 * aqi) + (0.892 * sgi) + (0.115 * depi) - (0.172 * sgai) + (4.679 * tata) - (0.327 * lvgi)

    return BeneishMScoreResult(
        score=round(m, 2),
        is_manipulator_likely=m > -1.78,
    )
