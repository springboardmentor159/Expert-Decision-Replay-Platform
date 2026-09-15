import React, { useState, useEffect } from 'react';
import {
  User,
  Mail,
  Lock,
  Building,
  Briefcase,
  ArrowRight,
  Sparkles,
  Layers,
  GitCommit,
  ShieldCheck,
  Users,
  Eye,
  EyeOff,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { organizationsApi } from '../../api/organizations';
import { ThemeToggle } from '../../components/layout/ThemeToggle';

export function RegisterPage({ onNavigateLogin }) {
  const { register } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'Employee',
    organization_id: 1,
    department: 'Engineering',
    designation: 'Software Engineer',
    phone_number: '+1-555-0100',
    employee_id: `EMP-${Math.floor(1000 + Math.random() * 9000)}`,
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState({});

  useEffect(() => {
    async function loadOrgs() {
      try {
        const list = await organizationsApi.getPublicList();
        if (list && list.length > 0) {
          setOrganizations(list);
          setFormData((prev) => ({ ...prev, organization_id: list[0].id }));
        }
      } catch {
        setOrganizations([{ id: 1, name: 'Default Organization' }]);
      }
    }
    loadOrgs();
  }, []);

  const handleChange = (field, value) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => ({ ...prev, [field]: '' }));
    }
  };

  const validate = () => {
    const errs = {};
    if (!formData.full_name.trim()) errs.full_name = 'Full name is required';
    if (!formData.email.trim()) {
      errs.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email.trim())) {
      errs.email = 'Invalid email address format';
    }
    if (!formData.password) {
      errs.password = 'Password is required';
    } else if (formData.password.length < 8) {
      errs.password = 'Password must be at least 8 characters long';
    }
    if (formData.password !== formData.confirmPassword) {
      errs.confirmPassword = 'Passwords do not match';
    }
    if (!formData.organization_id) {
      errs.organization_id = 'Please select an organization';
    }
    setErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;

    try {
      setLoading(true);
      const payload = {
        full_name: formData.full_name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        role: formData.role,
        organization_id: Number(formData.organization_id),
        department: formData.department,
        designation: formData.designation,
        phone_number: formData.phone_number,
        employee_id: formData.employee_id,
      };

      await register(payload);
      onNavigateLogin();
    } catch (err) {
      setErrors({ global: err.message || 'Registration failed' });
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

      {/* RIGHT SIDE: Structured, Responsive Corporate Registration Form */}
      <div style={{
        flex: '1',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        padding: '2.5rem 3.5rem',
        background: 'var(--bg-app)',
        maxWidth: '640px',
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
              Create Your Workspace Account
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.5 }}>
              Join your organization's decision governance platform to participate in reviews, evaluations, and architecture deliberations.
            </p>
          </div>

          {errors.global && (
            <div style={{
              background: 'var(--danger-light, rgba(239, 68, 68, 0.12))',
              border: '1px solid var(--danger, #EF4444)',
              borderRadius: '8px',
              padding: '0.85rem 1rem',
              color: 'var(--danger, #EF4444)',
              fontSize: '0.875rem',
              marginBottom: '1.25rem',
            }}>
              {errors.global}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            {/* Full Name & Email */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
                  Full Name *
                </label>
                <div style={{ position: 'relative' }}>
                  <User size={16} style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-muted)',
                  }} />
                  <input
                    type="text"
                    className="form-input"
                    style={{ paddingLeft: '2.25rem', height: '42px', fontSize: '0.9rem', width: '100%' }}
                    placeholder="e.g. Jane Doe"
                    value={formData.full_name}
                    onChange={(e) => handleChange('full_name', e.target.value)}
                    disabled={loading}
                    required
                  />
                </div>
                {errors.full_name && <div className="form-error" style={{ fontSize: '0.75rem', marginTop: '4px', color: 'var(--danger)' }}>{errors.full_name}</div>}
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
                  Corporate Email *
                </label>
                <div style={{ position: 'relative' }}>
                  <Mail size={16} style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-muted)',
                  }} />
                  <input
                    type="email"
                    className="form-input"
                    style={{ paddingLeft: '2.25rem', height: '42px', fontSize: '0.9rem', width: '100%' }}
                    placeholder="jane@company.com"
                    value={formData.email}
                    onChange={(e) => handleChange('email', e.target.value)}
                    disabled={loading}
                    required
                  />
                </div>
                {errors.email && <div className="form-error" style={{ fontSize: '0.75rem', marginTop: '4px', color: 'var(--danger)' }}>{errors.email}</div>}
              </div>
            </div>

            {/* Password & Confirm Password */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
                  Password *
                </label>
                <div style={{ position: 'relative' }}>
                  <Lock size={16} style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-muted)',
                  }} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-input"
                    style={{ paddingLeft: '2.25rem', paddingRight: '2.25rem', height: '42px', fontSize: '0.9rem', width: '100%' }}
                    placeholder="Min 8 characters"
                    value={formData.password}
                    onChange={(e) => handleChange('password', e.target.value)}
                    disabled={loading}
                    required
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
                      padding: '2px',
                    }}
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
                {errors.password && <div className="form-error" style={{ fontSize: '0.75rem', marginTop: '4px', color: 'var(--danger)' }}>{errors.password}</div>}
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
                  Confirm Password *
                </label>
                <div style={{ position: 'relative' }}>
                  <Lock size={16} style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-muted)',
                  }} />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    className="form-input"
                    style={{ paddingLeft: '2.25rem', height: '42px', fontSize: '0.9rem', width: '100%' }}
                    placeholder="Repeat password"
                    value={formData.confirmPassword}
                    onChange={(e) => handleChange('confirmPassword', e.target.value)}
                    disabled={loading}
                    required
                  />
                </div>
                {errors.confirmPassword && <div className="form-error" style={{ fontSize: '0.75rem', marginTop: '4px', color: 'var(--danger)' }}>{errors.confirmPassword}</div>}
              </div>
            </div>

            {/* Role & Organization */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1rem' }}>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
                  Role *
                </label>
                <div style={{ position: 'relative' }}>
                  <Briefcase size={16} style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-muted)',
                  }} />
                  <select
                    className="form-select"
                    style={{ paddingLeft: '2.25rem', height: '42px', fontSize: '0.9rem', width: '100%' }}
                    value={formData.role}
                    onChange={(e) => handleChange('role', e.target.value)}
                    disabled={loading}
                  >
                    <option value="Employee">Employee</option>
                    <option value="Reviewer">Reviewer</option>
                    <option value="Manager">Manager</option>
                    <option value="Administrator">Administrator</option>
                  </select>
                </div>
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
                  Organization *
                </label>
                <div style={{ position: 'relative' }}>
                  <Building size={16} style={{
                    position: 'absolute',
                    left: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--text-muted)',
                  }} />
                  <select
                    className="form-select"
                    style={{ paddingLeft: '2.25rem', height: '42px', fontSize: '0.9rem', width: '100%' }}
                    value={formData.organization_id}
                    onChange={(e) => handleChange('organization_id', e.target.value)}
                    disabled={loading}
                  >
                    {organizations.map((org) => (
                      <option key={org.id} value={org.id}>
                        {org.name}
                      </option>
                    ))}
                  </select>
                </div>
                {errors.organization_id && <div className="form-error" style={{ fontSize: '0.75rem', marginTop: '4px', color: 'var(--danger)' }}>{errors.organization_id}</div>}
              </div>
            </div>

            {/* Department & Designation */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem' }}>
              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
                  Department
                </label>
                <input
                  type="text"
                  className="form-input"
                  style={{ height: '42px', fontSize: '0.9rem', width: '100%' }}
                  placeholder="e.g. Core Engineering"
                  value={formData.department}
                  onChange={(e) => handleChange('department', e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="form-group" style={{ margin: 0 }}>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem', marginBottom: '0.4rem', display: 'block' }}>
                  Designation
                </label>
                <input
                  type="text"
                  className="form-input"
                  style={{ height: '42px', fontSize: '0.9rem', width: '100%' }}
                  placeholder="e.g. Senior Architect"
                  value={formData.designation}
                  onChange={(e) => handleChange('designation', e.target.value)}
                  disabled={loading}
                />
              </div>
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
                  Create Account <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>

          {/* Navigation to Login */}
          <div style={{ textAlign: 'center', marginTop: '1.5rem', fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
            Already have an organizational account?{' '}
            <button
              onClick={onNavigateLogin}
              style={{
                background: 'transparent',
                border: 'none',
                color: 'var(--primary)',
                fontWeight: 600,
                cursor: 'pointer',
                textDecoration: 'underline',
              }}
            >
              Sign in here
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
