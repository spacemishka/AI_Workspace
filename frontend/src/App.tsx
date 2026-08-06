import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { MacroBar } from './components/MacroBar';
import { CompanySearch } from './components/CompanySearch';
import { FinancialMetrics } from './components/FinancialMetrics';
import { CompanyComparison } from './components/CompanyComparison';
import { AgentReport } from './components/AgentReport';
import { SecFilings } from './components/SecFilings';
import { MarketNews } from './components/MarketNews';
import { CompanyAnalysis } from './types';
import { fetchCompanyAnalysis } from './api';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'analysis' | 'compare' | 'agent'>('analysis');
  const [currentTicker, setCurrentTicker] = useState('NVDA');
  const [analysis, setAnalysis] = useState<CompanyAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadAnalysis = async (ticker: string, wacc = 0.09, growth = 0.10) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetchCompanyAnalysis(ticker, wacc, growth);
      setAnalysis(res);
      setCurrentTicker(ticker);
    } catch (err: any) {
      setError(err.message || `Failed to analyze ${ticker}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAnalysis('NVDA');
  }, []);

  return (
    <div style={{ minHeight: '100vh', paddingBottom: '60px' }}>
      <Header activeTab={activeTab} setActiveTab={setActiveTab} />
      <MacroBar />

      {activeTab === 'analysis' && (
        <>
          <CompanySearch onSearch={(t) => loadAnalysis(t)} loading={loading} />
          
          {error && (
            <div style={{ margin: '20px 24px 0', padding: '16px', borderRadius: '12px', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', color: 'var(--rose)' }}>
              {error}
            </div>
          )}

          {analysis && !loading && (
            <>
              <FinancialMetrics
                analysis={analysis}
                onRecalculateDCF={(wacc, growth) => loadAnalysis(currentTicker, wacc, growth)}
              />

              <div style={{ padding: '0 24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <SecFilings ticker={currentTicker} />
                <MarketNews ticker={currentTicker} />
              </div>
            </>
          )}
        </>
      )}

      {activeTab === 'compare' && <CompanyComparison />}

      {activeTab === 'agent' && <AgentReport currentTicker={currentTicker} />}
    </div>
  );
};
export default App;
