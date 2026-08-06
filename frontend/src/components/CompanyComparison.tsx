import React, { useState } from 'react';
import { CompanyAnalysis } from '../types';
import { fetchCompanyComparison } from '../api';
import { Columns, Sparkles, CheckCircle2 } from 'lucide-react';

export const CompanyComparison: React.FC = () => {
  const [tickersInput, setTickersInput] = useState('NVDA, AMD, INTC');
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<CompanyAnalysis[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const list = tickersInput.split(',').map((t) => t.trim()).filter(Boolean);
    if (list.length === 0) return;

    setLoading(true);
    setError(null);
    try {
      const res = await fetchCompanyComparison(list);
      setData(res.companies);
    } catch (err: any) {
      setError(err.message || 'Failed to compare companies');
    } finally {
      setLoading(false);
    }
  };

  const formatPct = (val?: number) => (val !== undefined && val !== null ? `${(val * 100).toFixed(1)}%` : 'N/A');
  const formatCurr = (val?: number) =>
    val !== undefined && val !== null
      ? val >= 1e12
        ? `$${(val / 1e12).toFixed(2)}T`
        : val >= 1e9
        ? `$${(val / 1e9).toFixed(2)}B`
        : `$${val.toFixed(2)}`
      : 'N/A';

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Search Bar */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <form onSubmit={handleCompare} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
          <div style={{ flex: 1, minWidth: '280px' }}>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 600, display: 'block', marginBottom: '6px' }}>
              Enter Comma-Separated Tickers to Compare:
            </label>
            <input
              type="text"
              className="glass-input"
              value={tickersInput}
              onChange={(e) => setTickersInput(e.target.value)}
              placeholder="e.g. NVDA, AMD, INTC, MSFT"
              style={{ width: '100%' }}
            />
          </div>

          <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '22px' }}>
            <Columns size={16} /> {loading ? 'Comparing...' : 'Run Side-by-Side Comparison'}
          </button>
        </form>
      </div>

      {error && (
        <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', color: 'var(--rose)' }}>
          {error}
        </div>
      )}

      {/* Comparison Grid */}
      {data && data.length > 0 && (
        <div className="glass-panel" style={{ padding: '24px', overflowX: 'auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
            <Sparkles size={20} color="var(--primary)" />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Financial Metrics Matrix</h3>
          </div>

          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', minWidth: '600px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                <th style={{ padding: '12px 16px', color: 'var(--text-subtle)', fontSize: '0.8rem', textTransform: 'uppercase' }}>Metric</th>
                {data.map((c) => (
                  <th key={c.ticker} style={{ padding: '12px 16px', fontSize: '1.1rem', fontWeight: 800, color: 'var(--primary)' }}>
                    {c.ticker}
                    <span style={{ display: 'block', fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-muted)' }}>{c.company_name}</span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Market Cap</td>
                {data.map((c) => (
                  <td key={c.ticker} style={{ padding: '14px 16px', fontWeight: 700, color: 'var(--emerald)' }}>{formatCurr(c.market_cap)}</td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>P/E Ratio</td>
                {data.map((c) => (
                  <td key={c.ticker} style={{ padding: '14px 16px', fontWeight: 700 }}>{c.pe_ratio ? c.pe_ratio.toFixed(2) : 'N/A'}</td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Gross Margin</td>
                {data.map((c) => (
                  <td key={c.ticker} style={{ padding: '14px 16px', fontWeight: 700 }}>{formatPct(c.ratios?.gross_margin)}</td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Operating Margin</td>
                {data.map((c) => (
                  <td key={c.ticker} style={{ padding: '14px 16px', fontWeight: 700, color: 'var(--primary)' }}>{formatPct(c.ratios?.operating_margin)}</td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>ROE</td>
                {data.map((c) => (
                  <td key={c.ticker} style={{ padding: '14px 16px', fontWeight: 700 }}>{formatPct(c.ratios?.roe)}</td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>ROIC</td>
                {data.map((c) => (
                  <td key={c.ticker} style={{ padding: '14px 16px', fontWeight: 700, color: 'var(--cyan)' }}>{formatPct(c.ratios?.roic)}</td>
                ))}
              </tr>

              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                <td style={{ padding: '14px 16px', fontWeight: 600, color: 'var(--text-muted)' }}>Altman Z-Score</td>
                {data.map((c) => (
                  <td key={c.ticker} style={{ padding: '14px 16px', fontWeight: 700 }}>
                    {c.altman_z_score ? `${c.altman_z_score.toFixed(2)} (${c.altman_z_zone})` : 'N/A'}
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      )}

    </div>
  );
};
