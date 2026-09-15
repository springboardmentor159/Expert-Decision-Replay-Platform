import React, { useState, useEffect } from 'react';
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  CheckCircle2,
  AlertCircle,
  FileText,
  Clock,
  User,
  Layers,
  Sparkles,
  Paperclip,
} from 'lucide-react';
import { replayApi } from '../../api/replay';
import { LoadingSpinner } from '../common/LoadingSpinner';

export function DecisionReplayTimeline({ decisionId }) {
  const [replayData, setReplayData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeIndex, setActiveIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    let isMounted = true;
    async function loadReplay() {
      setLoading(true);
      try {
        const data = await replayApi.getDecisionReplay(decisionId);
        if (isMounted) {
          setReplayData(data);
          setActiveIndex((data.milestones?.length || 1) - 1); // default to latest
        }
      } catch (err) {
        console.error('Failed to load decision replay', err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }
    loadReplay();
    return () => {
      isMounted = false;
    };
  }, [decisionId]);

  // Autoplay effect
  useEffect(() => {
    let interval = null;
    if (isPlaying && replayData?.milestones?.length) {
      interval = setInterval(() => {
        setActiveIndex(prev => {
          if (prev >= replayData.milestones.length - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 2000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isPlaying, replayData]);

  if (loading) {
    return <LoadingSpinner message="Reconstructing decision timeline..." size="small" />;
  }

  if (!replayData || !replayData.milestones || replayData.milestones.length === 0) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--text-muted)' }}>
        No replay events captured for this decision yet.
      </div>
    );
  }

  const milestones = replayData.milestones;
  const currentMilestone = milestones[activeIndex] || milestones[0];

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: '12px',
      padding: '1.5rem',
      display: 'flex',
      flexDirection: 'column',
      gap: '1.25rem',
    }}>
      {/* Replay Controls Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
            <Sparkles size={18} style={{ color: 'var(--primary)' }} />
            Decision Evolution Replay
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '0.2rem 0 0' }}>
            Interactive historical playback showing consensus formation, review stages, and revisions.
          </p>
        </div>

        {/* Playback Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => {
              setIsPlaying(false);
              setActiveIndex(Math.max(0, activeIndex - 1));
            }}
            disabled={activeIndex === 0}
            title="Previous Milestone"
          >
            <SkipBack size={15} />
          </button>
          <button
            className="btn btn-primary btn-sm"
            onClick={() => setIsPlaying(!isPlaying)}
            title={isPlaying ? "Pause Playback" : "Play Evolution"}
            style={{ minWidth: '90px', display: 'flex', alignItems: 'center', gap: '4px', justifyContent: 'center' }}
          >
            {isPlaying ? <Pause size={15} /> : <Play size={15} />}
            <span>{isPlaying ? 'Pause' : 'Replay'}</span>
          </button>
          <button
            className="btn btn-secondary btn-sm"
            onClick={() => {
              setIsPlaying(false);
              setActiveIndex(Math.min(milestones.length - 1, activeIndex + 1));
            }}
            disabled={activeIndex === milestones.length - 1}
            title="Next Milestone"
          >
            <SkipForward size={15} />
          </button>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '0.4rem' }}>
            {activeIndex + 1} of {milestones.length}
          </span>
        </div>
      </div>

      {/* Scrubber Track */}
      <div style={{ position: 'relative', padding: '1rem 0 0.5rem' }}>
        {/* Horizontal line */}
        <div style={{
          position: 'absolute',
          top: '25px',
          left: '10px',
          right: '10px',
          height: '4px',
          background: 'var(--border-color)',
          borderRadius: '2px',
          zIndex: 1,
        }} />
        {/* Active progress line */}
        <div style={{
          position: 'absolute',
          top: '25px',
          left: '10px',
          width: `${(activeIndex / Math.max(1, milestones.length - 1)) * 96}%`,
          height: '4px',
          background: 'var(--primary)',
          borderRadius: '2px',
          zIndex: 2,
          transition: 'width 0.25s ease',
        }} />

        {/* Milestone Dots */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          position: 'relative',
          zIndex: 3,
        }}>
          {milestones.map((m, idx) => {
            const isActive = idx === activeIndex;
            const isPassed = idx < activeIndex;

            return (
              <button
                key={m.id}
                onClick={() => {
                  setIsPlaying(false);
                  setActiveIndex(idx);
                }}
                style={{
                  width: isActive ? '32px' : '22px',
                  height: isActive ? '32px' : '22px',
                  borderRadius: '50%',
                  background: isActive ? 'var(--primary)' : isPassed ? 'var(--primary-dark, #4338CA)' : 'var(--bg-card)',
                  border: `2px solid ${isActive ? '#fff' : isPassed ? 'var(--primary)' : 'var(--border-color)'}`,
                  boxShadow: isActive ? '0 0 0 4px var(--primary-light)' : 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#fff',
                  fontSize: '0.65rem',
                  fontWeight: 700,
                  transform: isActive ? 'scale(1.1)' : 'none',
                  transition: 'all 0.2s',
                  padding: 0,
                }}
                title={`${m.title} (${new Date(m.timestamp).toLocaleDateString()})`}
              >
                {idx + 1}
              </button>
            );
          })}
        </div>
      </div>

      {/* Selected Milestone Spotlight Card */}
      <div style={{
        background: 'var(--bg-card-solid, var(--bg-card))',
        border: '1px solid var(--border-color)',
        borderRadius: '10px',
        padding: '1.25rem',
        boxShadow: 'var(--shadow-sm)',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
        animation: 'fadeIn 0.2s ease-out',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '0.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <span className={`badge badge-${currentMilestone.badge_color || 'primary'}`} style={{ textTransform: 'uppercase', fontSize: '0.7rem' }}>
              {currentMilestone.event_type.replace('_', ' ')}
            </span>
            <h4 style={{ margin: 0, fontSize: '1rem', fontWeight: 700 }}>
              {currentMilestone.title}
            </h4>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <Clock size={14} />
            {new Date(currentMilestone.timestamp).toLocaleString()}
          </div>
        </div>

        <p style={{ margin: 0, fontSize: '0.9rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          {currentMilestone.description}
        </p>

        {currentMilestone.actor_name && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.78rem', color: 'var(--text-muted)', paddingTop: '0.25rem' }}>
            <User size={13} />
            <span>Action by: <strong>{currentMilestone.actor_name}</strong> {currentMilestone.actor_role ? `(${currentMilestone.actor_role})` : ''}</span>
          </div>
        )}
      </div>
    </div>
  );
}
