import React, { useState } from 'react';
import {
  PieChart,
  BarChart3,
  TrendingUp,
  Users,
  CheckCircle2,
  Clock,
  XCircle,
  Shield,
  Layers,
  Award,
  Activity,
} from 'lucide-react';
import { StatusBadge } from '../common/StatusBadge';

// Helper to compute SVG donut path coordinates
function getCoordinatesForPercent(percent) {
  const x = Math.cos(2 * Math.PI * percent);
  const y = Math.sin(2 * Math.PI * percent);
  return [x, y];
}

function DonutChart({ slices, size = 200, innerRadiusRatio = 0.65, totalCount = 0 }) {
  const [hoveredSlice, setHoveredSlice] = useState(null);

  if (!slices || slices.length === 0 || totalCount === 0) {
    return (
      <div style={{ height: size, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
        No decision data to chart
      </div>
    );
  }

  let cumulativePercent = 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
      <svg
        width={size}
        height={size}
        viewBox="-1.1 -1.1 2.2 2.2"
        style={{ transform: 'rotate(-90deg)', overflow: 'visible' }}
      >
        {slices.map((slice, idx) => {
          if (slice.value <= 0) return null;
          const percent = slice.value / totalCount;
          const [startX, startY] = getCoordinatesForPercent(cumulativePercent);
          cumulativePercent += percent;
          const [endX, endY] = getCoordinatesForPercent(cumulativePercent);
          const largeArcFlag = percent > 0.5 ? 1 : 0;

          // If 100% of a single slice
          if (percent >= 0.9999) {
            return (
              <circle
                key={idx}
                cx="0"
                cy="0"
                r="0.85"
                fill="none"
                stroke={slice.color}
                strokeWidth={1 - innerRadiusRatio}
                style={{
                  transition: 'stroke-width 0.2s',
                  cursor: 'pointer',
                  filter: hoveredSlice === slice.label ? 'drop-shadow(0 0 6px ' + slice.color + ')' : 'none',
                }}
                onMouseEnter={() => setHoveredSlice(slice.label)}
                onMouseLeave={() => setHoveredSlice(null)}
              />
            );
          }

          const innerR = innerRadiusRatio;
          const outerR = 0.95;
          const isHovered = hoveredSlice === slice.label;
          const currentOuterR = isHovered ? outerR + 0.05 : outerR;

          // Donut segment SVG path
          const pathData = [
            `M ${startX * currentOuterR} ${startY * currentOuterR}`,
            `A ${currentOuterR} ${currentOuterR} 0 ${largeArcFlag} 1 ${endX * currentOuterR} ${endY * currentOuterR}`,
            `L ${endX * innerR} ${endY * innerR}`,
            `A ${innerR} ${innerR} 0 ${largeArcFlag} 0 ${startX * innerR} ${startY * innerR}`,
            'Z',
          ].join(' ');

          return (
            <path
              key={idx}
              d={pathData}
              fill={slice.color}
              style={{
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                opacity: hoveredSlice && !isHovered ? 0.6 : 1,
                filter: isHovered ? `drop-shadow(0 0 6px ${slice.color})` : 'none',
              }}
              onMouseEnter={() => setHoveredSlice(slice.label)}
              onMouseLeave={() => setHoveredSlice(null)}
            />
          );
        })}
      </svg>

      {/* Center Label */}
      <div
        style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
          pointerEvents: 'none',
        }}
      >
        <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
          {hoveredSlice
            ? slices.find((s) => s.label === hoveredSlice)?.value ?? totalCount
            : totalCount}
        </div>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '3px' }}>
          {hoveredSlice || 'Total'}
        </div>
      </div>
    </div>
  );
}

// Semi-circle speedometer / gauge for Governance Approval Rate
function RadialGauge({ percentage = 0, label = 'Approval Rate', size = 160 }) {
  const clamped = Math.max(0, Math.min(100, percentage));
  const radius = 60;
  const circumference = Math.PI * radius;
  const strokeDashoffset = circumference - (clamped / 100) * circumference;

  const color =
    clamped >= 75 ? 'var(--success)' : clamped >= 50 ? 'var(--warning)' : 'var(--danger)';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', position: 'relative' }}>
      <svg width={size} height={size * 0.65} viewBox="0 0 160 100" style={{ overflow: 'visible' }}>
        {/* Track */}
        <path
          d="M 20 85 A 60 60 0 0 1 140 85"
          fill="none"
          stroke="var(--border-color)"
          strokeWidth="14"
          strokeLinecap="round"
        />
        {/* Fill */}
        <path
          d="M 20 85 A 60 60 0 0 1 140 85"
          fill="none"
          stroke={color}
          strokeWidth="14"
          strokeDasharray={circumference}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease-out' }}
        />
      </svg>
      <div style={{ position: 'absolute', bottom: '6px', textAlign: 'center' }}>
        <div style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
          {Math.round(clamped)}%
        </div>
        <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '2px' }}>{label}</div>
      </div>
    </div>
  );
}

export function AdminAnalyticsCharts({ data = {}, categoryStats = [], statusStats = [] }) {
  const [activeChartTab, setActiveChartTab] = useState('all'); // 'all' | 'governance' | 'categories'

  const totalDecisions = data?.total_decisions || 0;
  const approvedCount = data?.approved_decisions || 0;
  const underReviewCount = data?.under_review || 0;
  const draftCount = data?.draft_decisions || 0;
  const rejectedCount = data?.rejected_decisions || 0;
  const archivedCount = data?.archived_decisions || 0;

  // Status donut slices
  const statusSlices = [
    { label: 'Approved', value: approvedCount, color: '#10B981' },
    { label: 'Under Review', value: underReviewCount, color: '#3B82F6' },
    { label: 'Draft', value: draftCount, color: '#F59E0B' },
    { label: 'Rejected', value: rejectedCount, color: '#EF4444' },
    { label: 'Archived', value: archivedCount, color: '#6B7280' },
  ].filter((s) => s.value > 0);

  // Approval Rate
  const totalApprovals = data?.total_approvals || 0;
  const approvedApprovals = data?.approved_approvals || 0;
  const pendingApprovals = data?.pending_approvals || 0;
  const rejectedApprovals = data?.rejected_approvals || 0;
  const approvalRate =
    totalApprovals > 0 ? Math.round((approvedApprovals / totalApprovals) * 100) : 0;

  // Max category count for bar scaling
  const maxCategoryCount = Math.max(...categoryStats.map((c) => c.count), 1);

  // User Demographics
  const totalUsers = data?.total_users || 0;
  const employees = data?.employees || 0;
  const reviewers = data?.reviewers || 0;
  const managers = data?.managers || 0;
  const admins = data?.administrators || 0;

  const roleSegments = [
    { role: 'Employees', count: employees, color: '#3B82F6' },
    { role: 'Reviewers', count: reviewers, color: '#8B5CF6' },
    { role: 'Managers', count: managers, color: '#F59E0B' },
    { role: 'Admins', count: admins, color: '#10B981' },
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {/* Visual Analytics Header with View Filters */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 700, margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
            <BarChart3 size={20} style={{ color: 'var(--primary)' }} />
            Executive Governance & Analytics Intelligence
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0' }}>
            Real-time visual telemetry across architectural health, consensus pipelines, and role demographics.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '0.4rem', background: 'var(--bg-card)', padding: '4px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <button
            className={`btn btn-sm ${activeChartTab === 'all' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveChartTab('all')}
            style={{ fontSize: '0.78rem' }}
          >
            All Charts
          </button>
          <button
            className={`btn btn-sm ${activeChartTab === 'governance' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveChartTab('governance')}
            style={{ fontSize: '0.78rem' }}
          >
            Decisions & Approvals
          </button>
          <button
            className={`btn btn-sm ${activeChartTab === 'categories' ? 'btn-primary' : 'btn-ghost'}`}
            onClick={() => setActiveChartTab('categories')}
            style={{ fontSize: '0.78rem' }}
          >
            Domains & Workforce
          </button>
        </div>
      </div>

      {/* Grid of Visual Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '1.5rem' }}>
        {/* Chart 1: Donut Chart - Status Breakdown */}
        {(activeChartTab === 'all' || activeChartTab === 'governance') && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.05rem', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <PieChart size={17} style={{ color: 'var(--primary)' }} />
                Decision Status Breakdown
              </h3>
              <span className="badge badge-secondary" style={{ fontSize: '0.72rem' }}>
                {totalDecisions} Decisions
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', flexWrap: 'wrap', gap: '1rem', padding: '0.5rem 0' }}>
              <DonutChart slices={statusSlices} size={180} totalCount={totalDecisions} />

              {/* Legend with Interactive Percentages */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.45rem', minWidth: '140px' }}>
                {statusSlices.map((s) => {
                  const pct = totalDecisions > 0 ? Math.round((s.value / totalDecisions) * 100) : 0;
                  return (
                    <div key={s.label} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem', fontSize: '0.82rem' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: s.color }} />
                        <span style={{ color: 'var(--text-secondary)' }}>{s.label}</span>
                      </div>
                      <span style={{ fontWeight: 600 }}>
                        {s.value} <span style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>({pct}%)</span>
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Chart 2: Governance Velocity & Speedometer Gauge */}
        {(activeChartTab === 'all' || activeChartTab === 'governance') && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.05rem', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingUp size={17} style={{ color: 'var(--success)' }} />
                Approval Velocity & Consensus Rate
              </h3>
              <span className="badge badge-success" style={{ fontSize: '0.72rem' }}>
                {totalApprovals} Total Reviews
              </span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-around', flexWrap: 'wrap', gap: '1rem', padding: '0.5rem 0' }}>
              <RadialGauge percentage={approvalRate} label="Sign-Off Rate" size={170} />

              {/* Breakdown metrics */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem', minWidth: '140px' }}>
                <div style={{
                  background: 'var(--bg-hover)',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: '0.8rem',
                }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--success)' }}>
                    <CheckCircle2 size={13} /> Approved
                  </span>
                  <strong>{approvedApprovals}</strong>
                </div>

                <div style={{
                  background: 'var(--bg-hover)',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: '0.8rem',
                }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--warning)' }}>
                    <Clock size={13} /> In Progress
                  </span>
                  <strong>{pendingApprovals}</strong>
                </div>

                <div style={{
                  background: 'var(--bg-hover)',
                  padding: '6px 12px',
                  borderRadius: '6px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: '0.8rem',
                }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--danger)' }}>
                    <XCircle size={13} /> Rejected
                  </span>
                  <strong>{rejectedApprovals}</strong>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Chart 3: Horizontal Bar Chart - Category Architecture Distribution */}
        {(activeChartTab === 'all' || activeChartTab === 'categories') && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.05rem', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Layers size={17} style={{ color: 'var(--purple)' }} />
                Architectural Domains & Categories
              </h3>
              <span className="badge badge-secondary" style={{ fontSize: '0.72rem' }}>
                {categoryStats.length} Domains
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
              {categoryStats.length === 0 ? (
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>No architectural categories recorded yet.</div>
              ) : (
                categoryStats.map((cat, idx) => {
                  const pct = Math.round((cat.count / maxCategoryCount) * 100);
                  const colors = ['#6366F1', '#8B5CF6', '#EC4899', '#3B82F6', '#10B981', '#F59E0B'];
                  const barColor = colors[idx % colors.length];

                  return (
                    <div key={cat.category || idx}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{cat.category || 'General'}</span>
                        <span style={{ color: 'var(--text-secondary)' }}>
                          <strong>{cat.count}</strong> {cat.count === 1 ? 'decision' : 'decisions'}
                        </span>
                      </div>
                      <div style={{
                        height: '8px',
                        background: 'var(--border-color)',
                        borderRadius: '4px',
                        overflow: 'hidden',
                      }}>
                        <div style={{
                          height: '100%',
                          width: `${pct}%`,
                          background: `linear-gradient(90deg, ${barColor}, var(--primary))`,
                          borderRadius: '4px',
                          transition: 'width 0.6s ease',
                        }} />
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        )}

        {/* Chart 4: Workforce & Governance Role Composition */}
        {(activeChartTab === 'all' || activeChartTab === 'categories') && (
          <div className="card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <h3 style={{ fontSize: '1.05rem', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Users size={17} style={{ color: 'var(--primary)' }} />
                Workforce Persona Distribution
              </h3>
              <span className="badge badge-role" style={{ fontSize: '0.72rem' }}>
                {totalUsers} Members
              </span>
            </div>

            {/* Segmented Progress Bar */}
            <div style={{ marginBottom: '1.25rem' }}>
              <div style={{
                height: '12px',
                display: 'flex',
                borderRadius: '6px',
                overflow: 'hidden',
                background: 'var(--border-color)',
              }}>
                {roleSegments.map((seg) => {
                  if (seg.count <= 0) return null;
                  const pct = totalUsers > 0 ? (seg.count / totalUsers) * 100 : 0;
                  return (
                    <div
                      key={seg.role}
                      title={`${seg.role}: ${seg.count} (${Math.round(pct)}%)`}
                      style={{
                        width: `${pct}%`,
                        background: seg.color,
                        transition: 'width 0.5s ease',
                      }}
                    />
                  );
                })}
              </div>
            </div>

            {/* Role Cards Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              {roleSegments.map((seg) => (
                <div
                  key={seg.role}
                  style={{
                    background: 'var(--bg-hover)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '8px',
                    padding: '0.65rem 0.85rem',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '2px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: seg.color }} />
                    {seg.role}
                  </div>
                  <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {seg.count}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
