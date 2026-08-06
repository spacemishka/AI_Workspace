import React, { useEffect, useState } from 'react';
import { MacroResponse } from '../types';
import { fetchMacroIndicators } from '../api';
import { Landmark, TrendingUp, DollarSign, Percent } from 'lucide-react';

export const MacroBar: React.FC = () => {
  const [macro, setMacro] = useState<MacroResponse | null>(null);

  useEffect(() => {
    fetchMacroIndicators()
      .then(setMacro)
      .catch(() => {});
  }, []);

  if (!macro || !macro.indicators) return null;

  const ind = macro.indicators;

  return (
    <div className="glass-panel" style={{ margin: '20px 24px 0', padding: '14px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Landmark size={18} color="var(--primary)" />
        <span style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-main)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
          FRED Macro Benchmarks:
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '24px', flexWrap: 'wrap' }}>
        {ind.fed_funds_rate && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--text-subtle)' }}>Fed Rate:</span>
            <span style={{ fontWeight: 700, color: 'var(--amber)' }}>{ind.fed_funds_rate.value}%</span>
          </div>
        )}

        {ind.treasury_10yr_yield && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--text-subtle)' }}>10Y Treasury:</span>
            <span style={{ fontWeight: 700, color: 'var(--cyan)' }}>{ind.treasury_10yr_yield.value}%</span>
          </div>
        )}

        {ind.cpi_inflation_rate && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--text-subtle)' }}>CPI Inflation:</span>
            <span style={{ fontWeight: 700, color: 'var(--rose)' }}>{ind.cpi_inflation_rate.value}%</span>
          </div>
        )}

        {ind.us_gdp_growth && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
            <span style={{ color: 'var(--text-subtle)' }}>GDP Growth:</span>
            <span style={{ fontWeight: 700, color: 'var(--emerald)' }}>{ind.us_gdp_growth.value}%</span>
          </div>
        )}
      </div>
    </div>
  );
};
