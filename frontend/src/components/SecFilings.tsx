import React, { useEffect, useState } from 'react';
import { SECFilingsResponse } from '../types';
import { fetchSecFilings } from '../api';
import { FileText, ExternalLink, ShieldCheck } from 'lucide-react';

interface SecFilingsProps {
  ticker: string;
}

export const SecFilings: React.FC<SecFilingsProps> = ({ ticker }) => {
  const [data, setData] = useState<SECFilingsResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (ticker) {
      setLoading(true);
      fetchSecFilings(ticker)
        .then(setData)
        .catch(() => {})
        .finally(() => setLoading(false));
    }
  }, [ticker]);

  if (loading) return <div style={{ color: 'var(--text-subtle)', padding: '16px' }}>Loading SEC EDGAR filings...</div>;
  if (!data || data.filings.length === 0) return null;

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <FileText size={22} color="var(--primary)" />
          <div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 700 }}>Official SEC EDGAR Filings</h3>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-subtle)' }}>
              CIK: {data.cik} • {data.company_name} ({data.sic_description})
            </span>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(16, 185, 129, 0.12)', padding: '4px 12px', borderRadius: '9999px', fontSize: '0.75rem', color: 'var(--emerald)', fontWeight: 600 }}>
          <ShieldCheck size={14} /> Official Public SEC API
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '16px' }}>
        {data.filings.map((item, idx) => (
          <div
            key={idx}
            style={{
              background: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid var(--border-color)',
              borderRadius: '12px',
              padding: '16px',
              display: 'flex',
              flexDirection: 'column',
              justify: 'space-between',
              gap: '12px'
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                <span className="badge badge-bullish" style={{ background: 'rgba(99, 102, 241, 0.15)', color: 'var(--primary)', border: '1px solid rgba(99, 102, 241, 0.3)' }}>
                  Form {item.form}
                </span>
                <span style={{ fontSize: '0.75rem', color: 'var(--text-subtle)' }}>{item.filing_date}</span>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#e2e8f0', fontWeight: 500 }}>{item.description || `Form ${item.form} Filing`}</p>
            </div>

            {item.document_url && (
              <a
                href={item.document_url}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.8rem',
                  color: 'var(--primary)',
                  fontWeight: 600,
                  textDecoration: 'none'
                }}
              >
                View Filing on SEC.gov <ExternalLink size={12} />
              </a>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
