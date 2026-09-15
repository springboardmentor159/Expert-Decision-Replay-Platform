import React, { useState } from 'react';
import {
  Lock,
  Mail,
  Shield,
  ArrowRight,
  Eye,
  EyeOff,
  Sparkles,
  Layers,
  GitCommit,
  CheckCircle2,
  Clock,
  User,
  ShieldCheck,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { ThemeToggle } from '../../components/layout/ThemeToggle';

export function LoginPage({ onNavigateRegister }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [selectedPersona, setSelectedPersona] = useState(null);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState('');

  const demoPersonas = [
    {
      id: 'employee',
      name: 'Alex Chen',
      role: 'Employee',
      designation: 'Staff Software Engineer',
      email: 'employee@example.com',
      password: 'password123',
      color: 'var(--primary, #3B82F6)',
      badgeClass: 'badge-role',
    },
    {
      id: 'reviewer',
      name: 'Raftaar Singh',
      role: 'Reviewer',
      designation: 'Principal Architect (Stage 1)',
      email: 'reviewer@example.com',
      password: 'password123',
      color: 'var(--info, #06B6D4)',
      badgeClass: 'badge-info',
    },
    {
      id: 'manager',
      name: 'Sarah Jenkins',
      role: 'Manager',
      designation: 'Engineering Director (Stage 2)',
      email: 'manager@example.com',
      password: 'password123',
      color: 'var(--purple, #8B5CF6)',
      badgeClass: 'badge-purple',
    },
    {
      id: 'admin',
      name: 'John Doe',
      role: 'Admin',
      designation: 'Platform Administrator',
      email: 'admin@example.com',
      password: 'password123',
      color: 'var(--warning, #F59E0B)',
      badgeClass: 'badge-warning',
    },
  ];

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setFormError('');

    if (!email.trim()) {
      setFormError('Please enter your email address');
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

  const handleSelectPersona = (persona) => {
    setSelectedPersona(persona.id);
    setEmail(persona.email);
    setPassword(persona.password);
    setFormError('');
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
        flex: '1.15',
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

        {/* Center: Showcase Illustration & Value Proposition */}
        <div style={{ position: 'relative', zIndex: 2, margin: '2.5rem 0' }}>
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
            fontSize: '2.4rem',
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

          <p style={{ fontSize: '1rem', color: 'var(--text-secondary)', lineHeight: 1.6, maxWidth: '580px', marginBottom: '1.75rem' }}>
            Capture engineering consensus, benchmark candidate trade-offs, and playback historical decision evolution step-by-step with interactive scrubbers.
          </p>

          {/* Embedded Visual 3D Showcase Image */}
          <div style={{
            borderRadius: '16px',
            overflow: 'hidden',
            border: '1px solid rgba(255, 255, 255, 0.12)',
            boxShadow: '0 20px 40px -15px rgba(0, 0, 0, 0.6), 0 0 25px rgba(59, 130, 246, 0.18)',
            position: 'relative',
            background: '#0B1120',
          }}>
            <img
              src="/decision_replay_showcase.jpg"
              alt="Decision Evolution Replay Engine"
              style={{
                width: '100%',
                height: 'auto',
                display: 'block',
                transform: 'scale(1.01)',
                transition: 'transform 0.5s ease',
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
                <Clock size={13} style={{ color: 'var(--primary)' }} /> Live Evolution Timeline & Consensus Scrubber
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
                16 MILESTONES ACTIVE
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

        {/* Bottom Status / Trust Badges */}
        <div style={{
          position: 'relative',
          zIndex: 2,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: '0.75rem',
          color: 'var(--text-muted)',
          paddingTop: '1rem',
          borderTop: '1px solid var(--border-color)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10B981', display: 'inline-block', boxShadow: '0 0 8px #10B981' }} />
            <span>All Governance Services Operational</span>
          </div>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <span>SOC-2 Type II Certified</span>
            <span>•</span>
            <span>Argon2id Encrypted</span>
            <span>•</span>
            <span>v2.4 Enterprise</span>
          </div>
        </div>
      </div>

      {/* RIGHT SIDE: Authentication Form & 1-Click Persona Cards */}
      <div style={{
        flex: '1',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '2.5rem 3.5rem',
        background: 'var(--bg-app)',
        maxWidth: '620px',
        width: '100%',
      }}>
        {/* Top bar with Theme Toggle */}
        <div style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <ThemeToggle />
        </div>

        {/* Center: Login Card */}
        <div style={{ margin: 'auto 0', width: '100%' }}>
          <div style={{ marginBottom: '1.75rem' }}>
            <h2 style={{ fontSize: '1.85rem', fontWeight: 800, marginBottom: '0.4rem', fontFamily: 'Outfit, sans-serif' }}>
              Sign In to Your Workspace
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Access architectural proposals, evaluations, and decision timelines.
            </p>
          </div>

          {formError && (
            <div style={{
              background: 'var(--danger-light, rgba(239, 68, 68, 0.12))',
              border: '1px solid var(--danger, #EF4444)',
              borderRadius: '8px',
              padding: '0.75rem 1rem',
              color: 'var(--danger, #EF4444)',
              fontSize: '0.85rem',
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
            <div className="form-group" style={{ marginBottom: '1.1rem' }}>
              <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                Corporate Email Address
              </label>
              <div style={{ position: 'relative' }}>
                <Mail size={18} style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)',
                }} />
                <input
                  type="email"
                  className="form-input"
                  style={{ paddingLeft: '2.4rem', height: '42px', fontSize: '0.9rem' }}
                  placeholder="name@example.com"
                  value={email}
                  onChange={(e) => {
                    setEmail(e.target.value);
                    setSelectedPersona(null);
                  }}
                  disabled={loading}
                  autoComplete="email"
                />
              </div>
            </div>

            {/* Password Field with Show/Hide Toggle */}
            <div className="form-group" style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', margin: 0 }}>
                  Password
                </label>
              </div>
              <div style={{ position: 'relative' }}>
                <Lock size={18} style={{
                  position: 'absolute',
                  left: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)',
                }} />
                <input
                  type={showPassword ? 'text' : 'password'}
                  className="form-input"
                  style={{ paddingLeft: '2.4rem', paddingRight: '2.5rem', height: '42px', fontSize: '0.9rem' }}
                  placeholder="Enter your security credentials"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value);
                    setSelectedPersona(null);
                  }}
                  disabled={loading}
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: 'absolute',
                    right: '10px',
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.825rem', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  style={{ accentColor: 'var(--primary)' }}
                />
                Remember me on this browser
              </label>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Demo Password: <code style={{ color: 'var(--primary)' }}>password123</code>
              </span>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              className="btn btn-primary"
              style={{
                width: '100%',
                padding: '0.8rem',
                fontSize: '0.95rem',
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                borderRadius: '8px',
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

          {/* QUICK DEMO PERSONAS CARDS */}
          <div style={{ marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.08em',
              }}>
                Instant Demo Access (1-Click Fill)
              </span>
              <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                Select persona to inspect role
              </span>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
              {demoPersonas.map((persona) => {
                const isSelected = selectedPersona === persona.id;

                return (
                  <div
                    key={persona.id}
                    onClick={() => handleSelectPersona(persona)}
                    style={{
                      padding: '0.75rem 0.85rem',
                      borderRadius: '10px',
                      background: isSelected ? 'var(--bg-active, rgba(59, 130, 246, 0.12))' : 'var(--bg-card)',
                      border: isSelected ? `2px solid ${persona.color}` : '1px solid var(--border-color)',
                      boxShadow: isSelected ? `0 0 12px ${persona.color}33` : 'none',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      display: 'flex',
                      flexDirection: 'column',
                      gap: '4px',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <span style={{
                          width: '24px',
                          height: '24px',
                          borderRadius: '50%',
                          background: persona.color,
                          color: '#fff',
                          fontSize: '0.7rem',
                          fontWeight: 700,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                        }}>
                          {persona.name.charAt(0)}
                        </span>
                        <strong style={{ fontSize: '0.85rem', color: 'var(--text-primary)' }}>
                          {persona.name}
                        </strong>
                      </div>
                      <span className={`badge ${persona.badgeClass}`} style={{ fontSize: '0.65rem', textTransform: 'uppercase', padding: '1px 6px' }}>
                        {persona.role}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginLeft: '30px' }}>
                      {persona.designation}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Registration Link */}
          <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
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

        {/* Bottom copyright / security footer */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '0.72rem',
          color: 'var(--text-muted)',
          paddingTop: '1.25rem',
          borderTop: '1px solid var(--border-color)',
        }}>
          <span>© 2026 Expert Decision Replay Platform</span>
          <span>Security Verified</span>
        </div>
      </div>
    </div>
  );
}
