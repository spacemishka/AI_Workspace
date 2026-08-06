import React from 'react';
import { TrendingUp, BarChart3, Bot, Activity } from 'lucide-react';

interface HeaderProps {
  activeTab: 'analysis' | 'compare' | 'agent';
  setActiveTab: (tab: 'analysis' | 'compare' | 'agent') => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  return (
    <header className="glass-panel" style={{ margin: '20px 24px 0', padding: '16px 24px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #6366f1 0%, #10b981 100%)',
            borderRadius: '12px',
            padding: '10px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)'
          }}>
            <TrendingUp size={24} color="#ffffff" />
          </div>
          <div>
            <h1 style={{ fontSize: '1.25rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(135deg, #ffffff 0%, #cbd5e1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Personal AI Investment Analyst
            </h1>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 500 }}>
              Fundamental Scoring • DCF Valuation • Multi-Agent Orchestration
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{ display: 'flex', background: 'rgba(15, 23, 42, 0.6)', padding: '4px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <button
            onClick={() => setActiveTab('analysis')}
            className={`btn-secondary ${activeTab === 'analysis' ? 'active-tab' : ''}`}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              border: 'none',
              background: activeTab === 'analysis' ? 'var(--primary)' : 'transparent',
              color: activeTab === 'analysis' ? '#fff' : 'var(--text-muted)',
              borderRadius: '8px',
              padding: '8px 16px',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <BarChart3 size={16} /> Single Analysis
          </button>

          <button
            onClick={() => setActiveTab('compare')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              border: 'none',
              background: activeTab === 'compare' ? 'var(--primary)' : 'transparent',
              color: activeTab === 'compare' ? '#fff' : 'var(--text-muted)',
              borderRadius: '8px',
              padding: '8px 16px',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <TrendingUp size={16} /> Compare Stocks
          </button>

          <button
            onClick={() => setActiveTab('agent')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              border: 'none',
              background: activeTab === 'agent' ? 'var(--primary)' : 'transparent',
              color: activeTab === 'agent' ? '#fff' : 'var(--text-muted)',
              borderRadius: '8px',
              padding: '8px 16px',
              fontSize: '0.875rem',
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            <Bot size={16} /> CIO Agent Hub
          </button>
        </div>

        {/* Live Service Indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--emerald)', background: 'rgba(16, 185, 129, 0.1)', padding: '6px 14px', borderRadius: '9999px', border: '1px solid rgba(16, 185, 129, 0.2)' }}>
          <Activity size={14} className="pulse" />
          <span>Local Backend Ready</span>
        </div>
      </div>
    </header>
  );
};
