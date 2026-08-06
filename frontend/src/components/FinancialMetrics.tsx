import React, { useState } from 'react';
import { CompanyAnalysis } from '../types';
import { ShieldCheck, DollarSign, Percent, PieChart, Calculator } from 'lucide-react';

interface FinancialMetricsProps {
  analysis: CompanyAnalysis;
  onRecalculateDCF: (wacc: number, growthRate: number) => void;
}

export const FinancialMetrics: React.FC<FinancialMetricsProps> = ({ analysis, onRecalculateDCF }) => {
  const [wacc, setWacc] = useState(0.09);
  const [growthRate, setGrowthRate] = useState(0.10);

  const formatPct = (val?: number) => (val !== undefined && val !== null ? `${(val * 100).toFixed(1)}%` : 'N/A');
  const formatCurr = (val?: number) =>
    val !== undefined && val !== null
      ? val >= 1e12
        ? `$${(val / 1e12).toFixed(2)}T`
        : val >= 1e9
        ? `$${(val / 1e9).toFixed(2)}B`
        : `$${val.toFixed(2)}`
      : 'N/A';

  const r = analysis.ratios || {};

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Header Profile Summary */}
      <div className="glass-panel" style={{ padding: '24px', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px' }}>
        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600, textTransform: 'uppercase' }}>Company</span>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>{analysis.company_name}</h2>
          <span style={{ fontSize: '0.85rem', color: 'var(--primary)', fontWeight: 600 }}>{analysis.ticker}</span>
        </div>

        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600, textTransform: 'uppercase' }}>Sector & Industry</span>
          <p style={{ fontSize: '0.95rem', fontWeight: 600, color: '#e2e8f0' }}>{analysis.sector || 'N/A'}</p>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{analysis.industry || 'N/A'}</p>
        </div>

        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600, textTransform: 'uppercase' }}>Market Capitalization</span>
          <p style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--emerald)' }}>{formatCurr(analysis.market_cap)}</p>
        </div>

        <div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600, textTransform: 'uppercase' }}>P/E Ratio</span>
          <p style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--cyan)' }}>{analysis.pe_ratio ? analysis.pe_ratio.toFixed(2) : 'N/A'}</p>
        </div>
      </div>

      {/* Grid Layout for Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
        
        {/* Profitability & Margins */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
            <Percent size={20} color="var(--primary)" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Profitability Margins</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Gross Margin</span>
                <span style={{ fontWeight: 700, color: '#fff' }}>{formatPct(r.gross_margin)}</span>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.06)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                <div style={{ background: 'var(--primary)', width: `${Math.min(100, Math.max(0, (r.gross_margin || 0) * 100))}%`, height: '100%' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Operating Margin</span>
                <span style={{ fontWeight: 700, color: 'var(--emerald)' }}>{formatPct(r.operating_margin)}</span>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.06)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                <div style={{ background: 'var(--emerald)', width: `${Math.min(100, Math.max(0, (r.operating_margin || 0) * 100))}%`, height: '100%' }} />
              </div>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '6px' }}>
                <span style={{ color: 'var(--text-muted)' }}>Net Profit Margin</span>
                <span style={{ fontWeight: 700, color: 'var(--cyan)' }}>{formatPct(r.net_margin)}</span>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.06)', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                <div style={{ background: 'var(--cyan)', width: `${Math.min(100, Math.max(0, (r.net_margin || 0) * 100))}%`, height: '100%' }} />
              </div>
            </div>
          </div>
        </div>

        {/* Returns & Capital Efficiency */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
            <PieChart size={20} color="var(--emerald)" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Return & Capital Efficiency</h3>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600 }}>ROE (Return on Equity)</span>
              <p style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--emerald)', marginTop: '4px' }}>{formatPct(r.roe)}</p>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600 }}>ROIC (Invested Capital)</span>
              <p style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--primary)', marginTop: '4px' }}>{formatPct(r.roic)}</p>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600 }}>ROA (Assets)</span>
              <p style={{ fontSize: '1.2rem', fontWeight: 700, color: '#e2e8f0', marginTop: '4px' }}>{formatPct(r.roa)}</p>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600 }}>Asset Turnover</span>
              <p style={{ fontSize: '1.2rem', fontWeight: 700, color: '#e2e8f0', marginTop: '4px' }}>{r.asset_turnover ? r.asset_turnover.toFixed(2) : 'N/A'}</p>
            </div>
          </div>
        </div>

        {/* Financial Safety & Risk */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
            <ShieldCheck size={20} color="var(--amber)" />
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Financial Safety & Solvency</h3>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '12px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 600 }}>Altman Z-Score</span>
                <p style={{ fontSize: '1.5rem', fontWeight: 800, color: '#fff' }}>{analysis.altman_z_score ? analysis.altman_z_score.toFixed(2) : 'N/A'}</p>
              </div>
              <span className={`badge ${analysis.altman_z_zone === 'Safe' ? 'badge-bullish' : analysis.altman_z_zone === 'Distress' ? 'badge-bearish' : 'badge-neutral'}`}>
                {analysis.altman_z_zone || 'Unknown'} Zone
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
              <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '12px', borderRadius: '8px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>Current Ratio</span>
                <p style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>{r.current_ratio ? r.current_ratio.toFixed(2) : 'N/A'}</p>
              </div>
              <div style={{ background: 'rgba(15, 23, 42, 0.4)', padding: '12px', borderRadius: '8px' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>Debt to Equity</span>
                <p style={{ fontSize: '1.1rem', fontWeight: 700, color: '#fff' }}>{r.debt_to_equity ? r.debt_to_equity.toFixed(2) : 'N/A'}</p>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* DCF Valuation Calculator */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Calculator size={22} color="var(--primary)" />
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>Gordon Growth DCF Intrinsic Valuation</h3>
          </div>

          <div style={{ background: 'rgba(99, 102, 241, 0.15)', padding: '8px 20px', borderRadius: '12px', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600 }}>Estimated Intrinsic Value / Share</span>
            <p style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--emerald)' }}>
              {analysis.dcf_intrinsic_value ? `$${analysis.dcf_intrinsic_value.toFixed(2)}` : 'N/A'}
            </p>
          </div>
        </div>

        {/* Sliders */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '24px' }}>
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.85rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Discount Rate (WACC):</span>
              <span style={{ fontWeight: 700, color: 'var(--primary)' }}>{(wacc * 100).toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="0.04"
              max="0.20"
              step="0.005"
              value={wacc}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setWacc(val);
                onRecalculateDCF(val, growthRate);
              }}
              style={{ width: '100%', accentColor: 'var(--primary)' }}
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', fontSize: '0.85rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>5-Yr FCF Growth Rate:</span>
              <span style={{ fontWeight: 700, color: 'var(--emerald)' }}>{(growthRate * 100).toFixed(1)}%</span>
            </div>
            <input
              type="range"
              min="0.01"
              max="0.40"
              step="0.01"
              value={growthRate}
              onChange={(e) => {
                const val = parseFloat(e.target.value);
                setGrowthRate(val);
                onRecalculateDCF(wacc, val);
              }}
              style={{ width: '100%', accentColor: 'var(--emerald)' }}
            />
          </div>
        </div>
      </div>

    </div>
  );
};
