import React, { useEffect, useState } from 'react';
import { NewsResponse } from '../types';
import { fetchCompanyNews } from '../api';
import { Newspaper, ExternalLink } from 'lucide-react';

interface MarketNewsProps {
  ticker: string;
}

export const MarketNews: React.FC<MarketNewsProps> = ({ ticker }) => {
  const [data, setData] = useState<NewsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (ticker) {
      setLoading(true);
      fetchCompanyNews(ticker)
        .then(setData)
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [ticker]);

  if (loading) return <div style={{ color: 'var(--text-subtle)', padding: '16px' }}>Loading market news...</div>;
  if (!data || data.articles.length === 0) return null;

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <Newspaper size={22} color="var(--cyan)" />
        <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Live Financial Market News</h3>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {data.articles.map((item, idx) => (
          <div
            key={idx}
            style={{
              background: 'rgba(15, 23, 42, 0.5)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              gap: '8px'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px' }}>
              <a
                href={item.link}
                target="_blank"
                rel="noreferrer"
                style={{ fontSize: '0.95rem', fontWeight: 700, color: '#f8fafc', textDecoration: 'none', lineHeight: 1.4 }}
              >
                {item.title} <ExternalLink size={12} style={{ display: 'inline', color: 'var(--primary)' }} />
              </a>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)', whiteSpace: 'nowrap' }}>{item.pub_date}</span>
            </div>

            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5 }}>{item.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
