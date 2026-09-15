import React, { useState } from 'react';
import {
  Lock,
  Mail,
  ArrowRight,
  Eye,
  EyeOff,
  Sparkles,
  Layers,
  GitCommit,
  ShieldCheck,
  Users,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { ThemeToggle } from '../../components/layout/ThemeToggle';

export function LoginPage({ onNavigateRegister }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setFormError('');

    if (!email.trim()) {
      setFormError('Please enter your corporate email address');
      return;
    }
    if (!password) {
      setFormError('Please enter your password');
      return;
    }

    try {
      setLoading(true);
      await login(email.trim(), password);
    } catch (err) {
      setFormError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      background: 'var(--bg-app)',
      color: 'var(--text-primary)',
      fontFamily: 'Inter, system-ui, sans-serif',
    }}>
      {/* LEFT SIDE: Showcase & Visual Brand Experience */}
      <div style={{
        flex: '1.2',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '3rem 3.5rem',
        background: 'radial-gradient(ellipse at 20% 30%, rgba(59, 130, 246, 0.18), transparent 70%), linear-gradient(180deg, var(--bg-card) 0%, rgba(15, 23, 42, 0.95) 100%)',
        borderRight: '1px solid var(--border-color)',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Subtle background ambient grid pattern */}
        <div style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: 'radial-gradient(var(--border-color) 1px, transparent 1px)',
          backgroundSize: '24px 24px',
          opacity: 0.25,
          pointerEvents: 'none',
        }} />

        {/* Top Branding */}
        <div style={{ position: 'relative', zIndex: 2 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
            <div style={{
              width: '44px',
              height: '44px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              fontWeight: 800,
              fontSize: '1.2rem',
              boxShadow: '0 8px 20px rgba(59, 130, 246, 0.35)',
            }}>
              ED
            </div>
            <div>
              <div style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: '1.35rem', letterSpacing: '-0.02em', lineHeight: 1.1 }}>
                Expert Decision Replay
              </div>
              <div style={{ fontSize: '0.72rem', color: 'var(--primary)', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: '2px' }}>
                Audit-Grade Governance Platform
              </div>
            </div>
          </div>
        </div>

        {/* Center: Realistic Photography & Value Proposition */}
        <div style={{ position: 'relative', zIndex: 2, margin: '2rem 0' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 12px',
            borderRadius: '20px',
            background: 'rgba(59, 130, 246, 0.12)',
            border: '1px solid rgba(59, 130, 246, 0.35)',
            color: 'var(--primary)',
            fontSize: '0.78rem',
            fontWeight: 600,
            marginBottom: '1rem',
          }}>
            <Sparkles size={14} /> Zero Tribal Knowledge Loss
          </div>

          <h1 style={{
            fontSize: '2.35rem',
            fontWeight: 800,
            lineHeight: 1.2,
            letterSpacing: '-0.03em',
            marginBottom: '1rem',
            background: 'linear-gradient(135deg, #FFFFFF 30%, #94A3B8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Reconstruct, Deliberate & Govern Technical Decisions
          </h1>

          <p style={{ fontSize: '0.975rem', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '560px', marginBottom: '1.75rem' }}>
            Capture engineering consensus, benchmark candidate trade-offs, and playback historical decision evolution step-by-step with interactive scrubbers.
          </p>

          {/* Embedded Realistic Architecture Team Photograph */}
          <div style={{
            borderRadius: '16px',
            overflow: 'hidden',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.6), 0 0 25px rgba(59, 130, 246, 0.18)',
            position: 'relative',
            background: '#0B1120',
          }}>
            <img
              src="/architecture_team_realistic.jpg"
              alt="Architecture Review Board and Engineering Team Collaboration"
              style={{
                width: '100%',
                height: 'auto',
                display: 'block',
                maxHeight: '340px',
                objectFit: 'cover',
                objectPosition: 'center',
              }}
            />
            <div style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              padding: '0.85rem 1.25rem',
              background: 'linear-gradient(180deg, transparent 0%, rgba(11, 17, 32, 0.95) 100%)',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}>
              <span style={{ fontSize: '0.78rem', color: '#E2E8F0', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Users size={14} style={{ color: 'var(--primary)' }} /> Architecture Review Board & Engineering Deliberation
              </span>
              <span style={{
                fontSize: '0.68rem',
                background: 'rgba(16, 185, 129, 0.2)',
                color: '#10B981',
                border: '1px solid rgba(16, 185, 129, 0.4)',
                padding: '2px 8px',
                borderRadius: '10px',
                fontWeight: 700,
              }}>
                SOC-2 CERTIFIED
              </span>
            </div>
          </div>

          {/* Three Feature Highlights */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginTop: '1.75rem' }}>
            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-color)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--primary)', marginBottom: '4px' }}>
                <GitCommit size={16} />
                <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>Replay Scrubber</strong>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
                Animated playback showing consensus formation over time.
              </p>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-color)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--success)', marginBottom: '4px' }}>
                <ShieldCheck size={16} />
                <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>Multi-Level ARB</strong>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
                Sequential Peer Lead & Director approval gates.
              </p>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.03)',
              border: '1px solid var(--border-color)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--purple)', marginBottom: '4px' }}>
                <Layers size={16} />
                <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>Trade-Off Matrices</strong>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0, lineHeight: 1.4 }}>
                Benchmarking feasibility, cost (₹), and risk side-by-side.
              </p>
            </div>
          </div>
        </div>

        </div>
      </div>

      {/* RIGHT SIDE: Clean, Focused Corporate Login Form */}
      <div style={{
        flex: '1',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '3rem 4rem',
        background: 'var(--bg-app)',
        maxWidth: '560px',
        width: '100%',
      }}>
        {/* Top bar with Theme Toggle */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <ThemeToggle />
        </div>

        {/* Center: Sleek Form Card */}
        <div style={{ margin: 'auto 0', width: '100%' }}>
          <div style={{ marginBottom: '2rem' }}>
            <h2 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '0.5rem', fontFamily: 'Outfit, sans-serif' }}>
              Sign In to Your Workspace
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.925rem', lineHeight: 1.5 }}>
              Enter your corporate credentials to access architecture records, evaluations, and decision timelines.
            </p>
          </div>

          {formError && (
            <div style={{
              background: 'var(--danger-light, rgba(239, 68, 68, 0.12))',
              border: '1px solid var(--danger, #EF4444)',
              borderRadius: '8px',
              padding: '0.85rem 1rem',
              color: 'var(--danger, #EF4444)',
              fontSize: '0.875rem',
              marginBottom: '1.5rem',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <span>{formError}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Email Field */}
            <div className="form-group" style={{ marginBottom: '1.25rem' }}>
              <label className="form-label" style={{ fontWeight: 600, fontSize: '0.875rem', marginBottom: '0.5rem', display: 'block' }}>
                Corporate Email Address
              </label>
              <div style={{ position: 'relative' }}>
                <Mail size={18} style={{
                  position: 'absolute',
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)',
                }} />
                <input
                  type="email"
                  className="form-input"
                  style={{ paddingLeft: '2.5rem', height: '44px', fontSize: '0.925rem', width: '100%' }}
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  autoComplete="email"
                  required
                />
              </div>
            </div>

            {/* Password Field with Show/Hide Toggle */}
            <div className="form-group" style={{ marginBottom: '1.25rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.875rem', margin: 0 }}>
                  Password
                </label>
              </div>
              <div style={{ position: 'relative' }}>
                <Lock size={18} style={{
                  position: 'absolute',
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)',
                }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  style={{ paddingLeft: '2.5rem', paddingRight: '2.75rem', height: '44px', fontSize: '0.925rem', width: '100%' }}
                  placeholder="Enter your security credentials"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  autoComplete="current-password"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'transparent',
                    border: 'none',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    padding: '4px',
                  }}
                  title={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
                </button>
              </div>
            </div>

            {/* Remember Me */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.85rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  style={{ accentColor: 'var(--primary)' }}
                />
                Remember me on this device
              </label>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="btn btn-primary"
              style={{
                width: '100%',
                padding: '0.85rem',
                fontSize: '1rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                borderRadius: '8px',
                boxShadow: '0 4px 14px rgba(59, 130, 246, 0.4)',
              }}
              disabled={loading}
            >
              {loading ? (
                <span className="spinner" />
              ) : (
                <>
                  Sign In <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          {/* Registration Link */}
          <div style={{ textAlign: 'center', marginTop: '2rem', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>
            Need a new organizational account?{' '}
            <button
              onClick={onNavigateRegister}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--primary)',
                fontWeight: 600,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Register here
            </button>
          </div>
        </div>

        {/* Bottom footer */}
        <div style={{
          textAlign: 'center',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          paddingTop: '1.5rem',
          borderTop: '1px solid var(--border-color)',
        }}>
          <span>Expert Decision Replay</span>
        </div>
      </div>
    </div>
  );
}
