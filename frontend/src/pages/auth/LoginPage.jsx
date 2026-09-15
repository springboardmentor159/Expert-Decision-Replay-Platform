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

  const fillDemo = (demoEmail) => {
    setEmail(demoEmail);
    setPassword('password123');
    setFormError('');
  };

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
      {/* LEFT SIDE: Fixed Enterprise Dark Showcase (Impeccable contrast in light & dark modes) */}
      <div style={{
        flex: '1.2',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '3rem 3.5rem',
        background: 'radial-gradient(ellipse at 20% 30%, rgba(59, 130, 246, 0.22), transparent 70%), linear-gradient(180deg, #090E1A 0%, #060A14 100%)',
        borderRight: '1px solid rgba(255, 255, 255, 0.08)',
        color: '#F8FAFC',
        position: 'relative',
        overflow: 'hidden',
      }}>
        {/* Ambient subtle grid pattern */}
        <div style={{
          position: 'absolute',
          inset: 0,
          backgroundImage: 'radial-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px)',
          backgroundSize: '24px 24px',
          opacity: 0.35,
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
              boxShadow: '0 8px 20px rgba(59, 130, 246, 0.4)',
            }}>
              ED
            </div>
            <div>
              <div style={{ fontFamily: 'Outfit, sans-serif', fontWeight: 800, fontSize: '1.35rem', letterSpacing: '-0.02em', lineHeight: 1.1, color: '#FFFFFF' }}>
                Expert Decision Replay
              </div>
              <div style={{ fontSize: '0.72rem', color: '#60A5FA', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', marginTop: '2px' }}>
                Audit-Grade Governance Platform
              </div>
            </div>
          </div>
        </div>

        {/* Center: High-Contrast Value Proposition & Realistic Photo */}
        <div style={{ position: 'relative', zIndex: 2, margin: '2rem 0' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '4px 12px',
            borderRadius: '20px',
            background: 'rgba(59, 130, 246, 0.15)',
            border: '1px solid rgba(59, 130, 246, 0.35)',
            color: '#60A5FA',
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
            background: 'linear-gradient(135deg, #FFFFFF 40%, #94A3B8 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Reconstruct, Deliberate &amp; Govern Technical Decisions
          </h1>

          <p style={{ fontSize: '0.975rem', color: '#94A3B8', lineHeight: 1.6, maxWidth: '560px', marginBottom: '1.75rem' }}>
            Capture engineering consensus, benchmark candidate trade-offs, and playback historical decision evolution step-by-step with interactive scrubbers.
          </p>

          {/* Realistic Photograph Banner */}
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
                <Users size={14} style={{ color: '#60A5FA' }} /> Architecture Review Board &amp; Engineering Deliberation
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
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#60A5FA', marginBottom: '4px' }}>
                <GitCommit size={16} />
                <strong style={{ fontSize: '0.85rem', color: '#FFFFFF' }}>Replay Scrubber</strong>
              </div>
              <p style={{ fontSize: '0.75rem', color: '#94A3B8', margin: 0, lineHeight: 1.4 }}>
                Animated playback showing consensus formation over time.
              </p>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#10B981', marginBottom: '4px' }}>
                <ShieldCheck size={16} />
                <strong style={{ fontSize: '0.85rem', color: '#FFFFFF' }}>Multi-Level ARB</strong>
              </div>
              <p style={{ fontSize: '0.75rem', color: '#94A3B8', margin: 0, lineHeight: 1.4 }}>
                Sequential Peer Lead &amp; Director approval gates.
              </p>
            </div>

            <div style={{
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              borderRadius: '10px',
              padding: '0.85rem 1rem',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#A78BFA', marginBottom: '4px' }}>
                <Layers size={16} />
                <strong style={{ fontSize: '0.85rem', color: '#FFFFFF' }}>Trade-Off Matrices</strong>
              </div>
              <p style={{ fontSize: '0.75rem', color: '#94A3B8', margin: 0, lineHeight: 1.4 }}>
                Benchmarking feasibility, cost (₹), and risk side-by-side.
              </p>
            </div>
          </div>
        </div>

        <div></div>
      </div>

      {/* RIGHT SIDE: Structured, Responsive Corporate Login Form */}
      <div style={{
        flex: '1',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '2.5rem 3.5rem',
        background: 'var(--bg-app)',
        maxWidth: '580px',
        width: '100%',
        overflowY: 'auto',
      }}>
        {/* Top bar with Theme Toggle */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <ThemeToggle />
        </div>

        {/* Center: Structured Card Container */}
        <div style={{
          margin: 'auto 0',
          width: '100%',
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: '16px',
          padding: '2.25rem 2.5rem',
          boxShadow: '0 12px 32px rgba(0, 0, 0, 0.06)',
        }}>
          <div style={{ marginBottom: '1.5rem' }}>
            <h2 style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.4rem', fontFamily: 'Outfit, sans-serif' }}>
              Sign In to Your Workspace
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.5 }}>
              Enter your corporate credentials to access architecture records, evaluations, and decision timelines.
            </p>
          </div>

          {/* Quick Demo Credentials Switcher */}
          <div style={{ marginBottom: '1.5rem' }}>
            <div style={{
              fontSize: '0.72rem',
              fontWeight: 700,
              color: 'var(--text-muted)',
              marginBottom: '0.5rem',
              textTransform: 'uppercase',
              letterSpacing: '0.06em',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}>
              <span>Quick Demo Access (1-Click Fill)</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
              {[
                { role: 'Admin', email: 'admin@example.com', color: '#3B82F6' },
                { role: 'Manager', email: 'manager@example.com', color: '#10B981' },
                { role: 'Reviewer', email: 'reviewer@example.com', color: '#8B5CF6' },
                { role: 'Employee', email: 'employee@example.com', color: '#F59E0B' },
              ].map((demo) => (
                <button
                  key={demo.role}
                  type="button"
                  onClick={() => fillDemo(demo.email)}
                  style={{
                    padding: '8px 4px',
                    background: 'var(--bg-app)',
                    border: email === demo.email ? `2px solid ${demo.color}` : '1px solid var(--border-color)',
                    borderRadius: '8px',
                    fontSize: '0.78rem',
                    fontWeight: 600,
                    color: 'var(--text-primary)',
                    cursor: 'pointer',
                    transition: 'all 0.15s ease',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '2px',
                  }}
                  title={`Fill credentials for ${demo.role} (${demo.email})`}
                >
                  <span style={{ fontSize: '0.78rem', fontWeight: 700 }}>{demo.role}</span>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>Demo</span>
                </button>
              ))}
            </div>
          </div>

          {formError && (
            <div style={{
              background: 'var(--danger-light, rgba(239, 68, 68, 0.12))',
              border: '1px solid var(--danger, #EF4444)',
              borderRadius: '8px',
              padding: '0.85rem 1rem',
              color: 'var(--danger, #EF4444)',
              fontSize: '0.875rem',
              marginBottom: '1.25rem',
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
              <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
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
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', margin: 0 }}>
                  Password
                </label>
                <span
                  style={{ fontSize: '0.78rem', color: 'var(--primary)', cursor: 'pointer', textDecoration: 'underline' }}
                  onClick={() => alert('For this demo platform, standard password is: password123')}
                >
                  Forgot password?
                </span>
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
          <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
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
