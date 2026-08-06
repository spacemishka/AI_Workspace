import React, { useState } from 'react';
import { Search, Sparkles } from 'lucide-react';

interface CompanySearchProps {
  onSearch: (ticker: string) => void;
  loading?: boolean;
}

const POPULAR_TICKERS = ['NVDA', 'AAPL', 'MSFT', 'AMD', 'TSLA', 'AMZN', 'GOOGL', 'META'];

export const CompanySearch: React.FC<CompanySearchProps> = ({ onSearch, loading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSearch(input.trim().toUpperCase());
    }
  };

  return (
    <div className="glass-panel" style={{ padding: '24px', margin: '20px 24px 0' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '280px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '16px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-subtle)' }} />
          <input
            type="text"
            className="glass-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Enter ticker symbol (e.g. NVDA, AAPL, MSFT)..."
            style={{ width: '100%', paddingLeft: '44px' }}
          />
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          <Sparkles size={16} /> {loading ? 'Analyzing...' : 'Run Financial Analysis'}
        </button>
      </form>

      {/* Popular Tickers Quick Selection */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '16px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)', fontWeight: 600 }}>Quick Select:</span>
        {POPULAR_TICKERS.map((ticker) => (
          <button
            key={ticker}
            onClick={() => {
              setInput(ticker);
              onSearch(ticker);
            }}
            style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-muted)',
              borderRadius: '6px',
              padding: '4px 10px',
              fontSize: '0.75rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            {ticker}
          </button>
        ))}
      </div>
    </div>
  );
};
