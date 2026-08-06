export interface CompanyProfile {
  ticker: str;
  name: str;
  sector?: str;
  industry?: str;
  exchange?: str;
  currency?: str;
  country?: str;
  description?: str;
  website?: str;
  market_cap?: number;
  pe_ratio?: number;
  dividend_yield?: number;
}

export interface FinancialRatios {
  gross_margin?: number;
  operating_margin?: number;
  net_margin?: number;
  fcf_margin?: number;
  roe?: number;
  roa?: number;
  roic?: number;
  current_ratio?: number;
  quick_ratio?: number;
  debt_to_equity?: number;
  asset_turnover?: number;
}

export interface CompanyAnalysis {
  ticker: string;
  company_name: string;
  sector?: string;
  industry?: string;
  market_cap?: number;
  pe_ratio?: number;
  ratios: FinancialRatios;
  piotroski_score?: number;
  altman_z_score?: number;
  altman_z_zone?: string;
  dcf_intrinsic_value?: number;
}

export interface ComparisonResponse {
  comparison_count: number;
  companies: CompanyAnalysis[];
}

export interface AgentResult {
  agent_name: string;
  summary: string;
  findings: Record<string, any>;
  confidence_score: number;
}

export interface CIOReport {
  ticker: string;
  company_name: string;
  overall_rating: string;
  conviction_score: number;
  executive_summary: string;
  is_worth_buying: string;
  investment_thesis: string[];
  future_expectations: string[];
  key_risks: string[];
  cloud_deep_dive_prompt?: string;
  fundamental_analysis?: AgentResult;
  financial_statement_analysis?: AgentResult;
  valuation_analysis?: AgentResult;
}
