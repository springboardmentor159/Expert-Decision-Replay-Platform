import React from 'react';
import { Modal } from '../common/Modal';
import { RiskBadge } from '../common/StatusBadge';
import { Check, X, DollarSign, Star, AlertTriangle, Sparkles } from 'lucide-react';

export const CompareModal = ({ isOpen, onClose, alternatives = [] }) => {
  if (!isOpen) return null;

  // Find best feasibility score and lowest risk
  const highestFeasibility = Math.max(...alternatives.map((a) => a.feasibility_score || 0), 0);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Side-by-Side Alternative Analysis"
      size="xl"
      footer={
        <button className="btn btn-secondary" onClick={onClose}>
          Close Comparison
        </button>
      }
    >
      {alternatives.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '2rem' }}>
          <p className="text-muted">No alternatives available to compare.</p>
        </div>
      ) : (
        <div style={{ overflowX: 'auto', paddingBottom: '1rem' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: `repeat(${alternatives.length}, minmax(280px, 1fr))`,
              gap: '1.25rem',
            }}
          >
            {alternatives.map((alt) => {
              const isHighest = alt.feasibility_score === highestFeasibility && alternatives.length > 1;

              return (
                <div
                  key={alt.id}
                  className="card"
                  style={{
                    backgroundColor: 'var(--bg-elevated)',
                    border: isHighest ? '2px solid var(--primary)' : '1px solid var(--border-default)',
                    position: 'relative',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                >
                  {isHighest && (
                    <div
                      style={{
                        position: 'absolute',
                        top: '-12px',
                        right: '16px',
                        backgroundColor: 'var(--primary)',
                        color: 'white',
                        padding: '2px 10px',
                        borderRadius: 'var(--radius-full)',
                        fontSize: '0.72rem',
                        fontWeight: 700,
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px',
                        boxShadow: '0 2px 6px rgba(99, 102, 241, 0.5)',
                      }}
                    >
                      <Sparkles size={12} /> Top Feasibility
                    </div>
                  )}

                  <h4 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
                    {alt.name}
                  </h4>
                  <p className="text-muted" style={{ fontSize: '0.85rem', marginBottom: '1.25rem', flexGrow: 1 }}>
                    {alt.description}
                  </p>

                  <div
                    style={{
                      background: 'var(--bg-elevated)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.85rem',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '0.65rem',
                      marginBottom: '1.25rem',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="text-dim" style={{ fontSize: '0.8rem' }}>Feasibility Score</span>
                      <span style={{ fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '3px' }}>
                        <Star size={14} fill="#fbbf24" color="#fbbf24" />
                        {alt.feasibility_score} / 5
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="text-dim" style={{ fontSize: '0.8rem' }}>Estimated Cost</span>
                      <span style={{ fontWeight: 700, color: '#047857', fontFamily: 'var(--font-mono)' }}>
                        ${Number(alt.estimated_cost || 0).toLocaleString()}
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="text-dim" style={{ fontSize: '0.8rem' }}>Risk Assessment</span>
                      <RiskBadge risk={alt.risk_level} />
                    </div>
                  </div>

                  {/* Pros */}
                  <div style={{ marginBottom: '1rem' }}>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#047857', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '0.35rem' }}>
                      <Check size={14} /> Pros / Strengths
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
                      {alt.pros || 'None specified'}
                    </p>
                  </div>

                  {/* Cons */}
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700, color: '#b91c1c', display: 'flex', alignItems: 'center', gap: '4px', marginBottom: '0.35rem' }}>
                      <X size={14} /> Cons / Trade-offs
                    </div>
                    <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
                      {alt.cons || 'None specified'}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </Modal>
  );
};
