import React, { useState } from 'react';
import { CIOReport } from '../types';
import { runAgentAnalysis } from '../api';
import { Bot, Cpu, Cloud, Target, TrendingUp, AlertTriangle, ShieldCheck } from 'lucide-react';

interface AgentReportProps {
  currentTicker: string;
}

export const AgentReport: React.FC<AgentReportProps> = ({ currentTicker }) => {
  const [ticker, setTicker] = useState(currentTicker || 'NVDA');
  const [cloud, setCloud] = useState(false);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState<CIOReport | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleRunAgent = async (overrideCloud?: boolean) => {
    const isCloud = overrideCloud !== undefined ? overrideCloud : cloud;
    setLoading(true);
    setError(null);
    try {
      const res = await runAgentAnalysis(ticker.toUpperCase(), isCloud);
      setReport(res);
    } catch (err: any) {
      setError(err.message || `Failed agent research analysis for ${ticker}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
      
      {/* Control Banner */}
      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Bot size={24} color="var(--primary)" />
              <h2 style={{ fontSize: '1.4rem', fontWeight: 800 }}>Chief Investment Officer Multi-Agent Hub</h2>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-subtle)', marginTop: '4px' }}>
              Synthesizes Fundamental, Financial Statement, and Valuation Analysts into a unified thesis.
            </p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            <input
              type="text"
              className="glass-input"
              value={ticker}
              onChange={(e) => setTicker(e.target.value)}
              placeholder="Ticker (e.g. NVDA)"
              style={{ width: '120px', textTransform: 'uppercase', fontWeight: 700 }}
            />

            {/* Cloud Toggle */}
            <button
              onClick={() => setCloud(!cloud)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '10px 16px',
                borderRadius: '12px',
                border: '1px solid var(--border-color)',
                background: cloud ? 'rgba(99, 102, 241, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                color: cloud ? 'var(--primary)' : 'var(--text-muted)',
                fontWeight: 600,
                cursor: 'pointer'
              }}
            >
              {cloud ? <Cloud size={16} color="var(--primary)" /> : <Cpu size={16} />}
              {cloud ? 'Cloud AI (OpenRouter)' : 'Local AI (Ollama)'}
            </button>

            <button className="btn-primary" onClick={() => handleRunAgent()} disabled={loading}>
              {loading ? 'Synthesizing...' : 'Run Multi-Agent Report'}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div style={{ padding: '16px', borderRadius: '12px', background: 'rgba(244, 63, 94, 0.15)', border: '1px solid rgba(244, 63, 94, 0.3)', color: 'var(--rose)' }}>
          {error}
        </div>
      )}

      {/* Report Display */}
      {report && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          
          {/* Header Card */}
          <div className="glass-panel" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
            <div>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600, textTransform: 'uppercase' }}>Investment Research Report</span>
              <h1 style={{ fontSize: '1.8rem', fontWeight: 800 }}>{report.ticker} — {report.company_name}</h1>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div style={{ textAlign: 'right' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', fontWeight: 600 }}>Conviction Score</span>
                <p style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--primary)' }}>{report.conviction_score} / 10</p>
              </div>

              <span className={`badge ${report.overall_rating === 'Bullish' ? 'badge-bullish' : report.overall_rating === 'Bearish' ? 'badge-bearish' : 'badge-neutral'}`} style={{ fontSize: '1rem', padding: '8px 16px' }}>
                {report.overall_rating}
              </span>
            </div>
          </div>

          {/* Verdict Banner */}
          <div style={{ background: 'rgba(99, 102, 241, 0.12)', border: '1px solid rgba(99, 102, 241, 0.3)', borderRadius: '16px', padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <Target size={22} color="var(--primary)" />
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#fff' }}>🎯 Valuation & "Is it Worth Buying?" Verdict</h3>
            </div>
            <p style={{ fontSize: '1.05rem', fontWeight: 600, color: '#e2e8f0', lineHeight: 1.6 }}>
              {report.is_worth_buying}
            </p>
          </div>

          {/* Grid for Catalysts & Executive Summary */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
            
            {/* Future Expectations */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                <TrendingUp size={20} color="var(--emerald)" />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>🔮 Future 3-5 Year Expectations & Catalysts</h3>
              </div>
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '10px', paddingLeft: '20px', color: '#cbd5e1' }}>
                {report.future_expectations?.map((item, idx) => (
                  <li key={idx} style={{ fontSize: '0.9rem' }}>{item}</li>
                ))}
              </ul>
            </div>

            {/* Key Risks */}
            <div className="glass-panel" style={{ padding: '24px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
                <AlertTriangle size={20} color="var(--rose)" />
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>⚠️ Key Investment Risks</h3>
              </div>
              <ul style={{ display: 'flex', flexDirection: 'column', gap: '10px', paddingLeft: '20px', color: '#cbd5e1' }}>
                {report.key_risks?.map((risk, idx) => (
                  <li key={idx} style={{ fontSize: '0.9rem' }}>{risk}</li>
                ))}
              </ul>
            </div>

          </div>

          {/* Executive Summary & Thesis */}
          <div className="glass-panel" style={{ padding: '24px' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '12px' }}>📋 Executive Summary</h3>
            <p style={{ fontSize: '0.95rem', color: '#cbd5e1', lineHeight: 1.7, marginBottom: '24px' }}>
              {report.executive_summary}
            </p>

            <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '12px' }}>💡 Investment Thesis Points</h3>
            <ul style={{ display: 'flex', flexDirection: 'column', gap: '10px', paddingLeft: '20px', color: '#cbd5e1' }}>
              {report.investment_thesis?.map((point, idx) => (
                <li key={idx} style={{ fontSize: '0.95rem' }}>{point}</li>
              ))}
            </ul>
          </div>

          {/* Cloud Deep Dive Prompt Banner */}
          {!cloud && (
            <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', borderRadius: '16px', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--emerald)' }}>⚡ Want a Deep-Dive Scenario Stress Test?</h4>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                  Run this research report through Cloud AI (OpenRouter) for extended reasoning and multi-scenario DCF stress testing.
                </p>
              </div>

              <button className="btn-primary" style={{ background: 'var(--emerald)' }} onClick={() => handleRunAgent(true)}>
                <Cloud size={16} /> Run Deep-Dive via Cloud AI
              </button>
            </div>
          )}

        </div>
      )}

    </div>
  );
};
