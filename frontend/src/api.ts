import { CompanyAnalysis, CompanyProfile, ComparisonResponse, CIOReport } from './types';

const API_BASE =
  import.meta.env.VITE_API_BASE_URL && import.meta.env.VITE_API_BASE_URL !== 'http://localhost:8000'
    ? import.meta.env.VITE_API_BASE_URL
    : `${window.location.protocol}//${window.location.hostname}:8000`;

export async function fetchCompanyProfile(ticker: string): Promise<CompanyProfile> {
  const res = await fetch(`${API_BASE}/api/v1/financials/${ticker}/profile`);
  if (!res.ok) throw new Error(`Failed to fetch profile for ${ticker}`);
  return res.json();
}

export async function fetchCompanyAnalysis(
  ticker: string,
  wacc: number = 0.09,
  growthRate: number = 0.10
): Promise<CompanyAnalysis> {
  const res = await fetch(
    `${API_BASE}/api/v1/financials/${ticker}/analysis?wacc=${wacc}&growth_rate=${growthRate}`
  );
  if (!res.ok) throw new Error(`Failed to fetch analysis for ${ticker}`);
  return res.json();
}

export async function fetchCompanyComparison(tickers: string[]): Promise<ComparisonResponse> {
  const tickerQuery = tickers.join(',');
  const res = await fetch(`${API_BASE}/api/v1/financials/compare?tickers=${tickerQuery}`);
  if (!res.ok) throw new Error(`Failed to compare tickers: ${tickerQuery}`);
  return res.json();
}

export async function runAgentAnalysis(ticker: string, cloud: boolean = false): Promise<CIOReport> {
  const res = await fetch(`${API_BASE}/api/v1/analysis/company/${ticker}?cloud=${cloud}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
  });
  if (!res.ok) throw new Error(`Failed agent analysis for ${ticker}`);
  return res.json();
}
