import React, { useState, useEffect, useCallback } from 'react';
import {
  User,
  Mail,
  Building,
  Briefcase,
  Phone,
  Shield,
  KeyRound,
  CheckCircle2,
  Clock,
  XCircle,
  BarChart3,
  TrendingUp,
  FileText,
  Layers,
  MessageSquare,
  Award,
  Save,
  Lock,
  Calendar,
  AlertCircle,
  Plus,
} from 'lucide-react';
import { usersApi } from '../../api/users';
import { organizationsApi } from '../../api/organizations';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { RoleBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

export function ProfilePage({ onNavigateCreate, onNavigateMyDecisions }) {
  const { user, role, isEmployee, isReviewer, isManager, isAdmin } = useAuth();
  const { success, error, info } = useNotification();

  const [activeTab, setActiveTab] = useState('overview'); // 'overview' | 'edit' | 'security'
  const [profileData, setProfileData] = useState(user || null);
  const [statistics, setStatistics] = useState(null);
  const [orgName, setOrgName] = useState('');
  const [loading, setLoading] = useState(true);

  // Edit profile form state
  const [editForm, setEditForm] = useState({
    full_name: user?.full_name || '',
    department: user?.department || '',
    designation: user?.designation || '',
    phone_number: user?.phone_number || '',
  });
  const [savingProfile, setSavingProfile] = useState(false);

  // Password change form state
  const [passwordForm, setPasswordForm] = useState({
    password: '',
    confirm_password: '',
  });
  const [savingPassword, setSavingPassword] = useState(false);

  const loadProfileAndStats = useCallback(async () => {
    setLoading(true);
    try {
      const [profileRes, statsRes, orgsRes] = await Promise.all([
        usersApi.getMyProfile().catch(() => user),
        usersApi.getMyStatistics().catch(() => null),
        organizationsApi.getPublicList().catch(() => []),
      ]);

      if (profileRes) {
        setProfileData(profileRes);
        setEditForm({
          full_name: profileRes.full_name || '',
          department: profileRes.department || '',
          designation: profileRes.designation || '',
          phone_number: profileRes.phone_number || '',
        });

        if (profileRes.organization_id && Array.isArray(orgsRes)) {
          const matched = orgsRes.find((o) => o.id === profileRes.organization_id);
          if (matched) setOrgName(matched.name);
        }
      }

      if (statsRes) {
        setStatistics(statsRes);
      }
    } catch (err) {
      error(err.message || 'Failed to load profile details');
    } finally {
      setLoading(false);
    }
  }, [user, error]);

  useEffect(() => {
    loadProfileAndStats();
  }, [loadProfileAndStats]);

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    if (!profileData?.id) return;
    if (!editForm.full_name.trim()) {
      error('Full Name cannot be empty');
      return;
    }

    setSavingProfile(true);
    try {
      const updated = await usersApi.updateUser(profileData.id, {
        full_name: editForm.full_name.trim(),
        department: editForm.department.trim() || null,
        designation: editForm.designation.trim() || null,
        phone_number: editForm.phone_number.trim() || null,
      });

      setProfileData(updated);
      localStorage.setItem('user', JSON.stringify(updated));
      success('Profile updated successfully!');
      setActiveTab('overview');
    } catch (err) {
      error(err.message || 'Failed to update profile');
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (e) => {
    e.preventDefault();
    if (!profileData?.id) return;

    if (passwordForm.password.length < 8) {
      error('Password must be at least 8 characters long');
      return;
    }
    if (passwordForm.password !== passwordForm.confirm_password) {
      error('Password confirmation does not match');
      return;
    }

    setSavingPassword(true);
    try {
      await usersApi.updateUser(profileData.id, {
        password: passwordForm.password,
      });
      setPasswordForm({ password: '', confirm_password: '' });
      success('Password changed successfully!');
      setActiveTab('overview');
    } catch (err) {
      error(err.message || 'Failed to change password');
    } finally {
      setSavingPassword(false);
    }
  };

  if (loading && !profileData) {
    return <LoadingSpinner message="Loading your profile & performance analytics..." size="large" />;
  }

  const currentUser = profileData || user;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem', maxWidth: '1100px', margin: '0 auto' }}>
      {/* Profile Header Hero Card */}
      <div className="card" style={{
        padding: '2rem',
        background: 'linear-gradient(135deg, var(--bg-card), var(--bg-hover))',
        border: '1px solid var(--border-color)',
        borderRadius: '16px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '1.5rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', flexWrap: 'wrap' }}>
            {/* Avatar Badge */}
            <div style={{
              width: '76px',
              height: '76px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, var(--primary), var(--purple))',
              color: '#fff',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '2rem',
              fontWeight: 700,
              boxShadow: '0 8px 24px rgba(99, 102, 241, 0.25)',
              border: '3px solid var(--bg-card)',
            }}>
              {currentUser?.full_name ? currentUser.full_name.charAt(0).toUpperCase() : <User size={36} />}
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap', marginBottom: '0.35rem' }}>
                <h1 style={{ fontSize: '1.65rem', margin: 0, fontWeight: 700 }}>
                  {currentUser?.full_name || 'My Profile'}
                </h1>
                <RoleBadge role={currentUser?.role} />
                {currentUser?.employee_id && (
                  <span className="badge badge-role" style={{ fontSize: '0.75rem' }}>
                    ID: {currentUser.employee_id}
                  </span>
                )}
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem', flexWrap: 'wrap', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Mail size={15} style={{ color: 'var(--primary)' }} />
                  {currentUser?.email}
                </span>
                {currentUser?.department && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Briefcase size={15} style={{ color: 'var(--primary)' }} />
                    {currentUser.department} {currentUser?.designation ? `(${currentUser.designation})` : ''}
                  </span>
                )}
                {orgName && (
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <Building size={15} style={{ color: 'var(--primary)' }} />
                    {orgName}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Quick Actions */}
          <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
            <button
              className={`btn btn-sm ${activeTab === 'overview' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('overview')}
            >
              <BarChart3 size={15} /> Overview & Stats
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'edit' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('edit')}
            >
              <User size={15} /> Edit Profile
            </button>
            <button
              className={`btn btn-sm ${activeTab === 'security' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveTab('security')}
            >
              <KeyRound size={15} /> Security
            </button>
          </div>
        </div>
      </div>

      {/* TAB 1: OVERVIEW & STATISTICS */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
          {/* Section Title */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h2 style={{ fontSize: '1.25rem', margin: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                <TrendingUp size={20} style={{ color: 'var(--primary)' }} />
                {isReviewer ? 'Reviewer Governance & Workload Statistics' : 'Personal Activity & Platform Statistics'}
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginTop: '2px' }}>
                {isReviewer
                  ? 'Overview of assigned decisions, pending evaluations, review completion, and audit discussions.'
                  : 'Comprehensive metric breakdown of your architectural decisions, approvals, and collaboration impact.'}
              </p>
            </div>
            {!isReviewer && onNavigateCreate && (
              <button onClick={onNavigateCreate} className="btn btn-primary btn-sm">
                <Plus size={15} /> New Decision
              </button>
            )}
          </div>

          {/* Primary Metrics Grid */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.15rem',
          }}>
            {isReviewer ? (
              <>
                {/* Assigned Decisions for Review */}
                <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Assigned Reviews
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--text-primary)', marginTop: '4px' }}>
                        {statistics?.assigned_reviews ?? 0}
                      </div>
                    </div>
                    <div style={{ padding: '8px', borderRadius: '8px', background: 'var(--primary-light)', color: 'var(--primary)' }}>
                      <Shield size={22} />
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    Decisions assigned for your evaluation
                  </div>
                </div>

                {/* Pending Reviews */}
                <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Pending Reviews
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Outfit', color: '#f59e0b', marginTop: '4px' }}>
                        {statistics?.pending_reviews ?? 0}
                      </div>
                    </div>
                    <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b' }}>
                      <Clock size={22} />
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    Awaiting your vote or review feedback
                  </div>
                </div>

                {/* Completed Reviews */}
                <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Completed Reviews
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--success)', marginTop: '4px' }}>
                        {statistics?.completed_reviews ?? 0}
                      </div>
                    </div>
                    <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(34, 197, 94, 0.12)', color: 'var(--success)' }}>
                      <CheckCircle2 size={22} />
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    Evaluations cast and finalized
                  </div>
                </div>

                {/* Discussion Comments */}
                <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Discussion Notes
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--primary)', marginTop: '4px' }}>
                        {statistics?.total_comments_posted ?? 0}
                      </div>
                    </div>
                    <div style={{ padding: '8px', borderRadius: '8px', background: 'var(--primary-light)', color: 'var(--primary)' }}>
                      <MessageSquare size={22} />
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    Comments contributed to discussions
                  </div>
                </div>
              </>
            ) : (
              <>
                {/* Total Authored */}
                <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Authored Decisions
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--text-primary)', marginTop: '4px' }}>
                        {statistics?.total_decisions ?? 0}
                      </div>
                    </div>
                    <div style={{ padding: '8px', borderRadius: '8px', background: 'var(--primary-light)', color: 'var(--primary)' }}>
                      <FileText size={22} />
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    Total architectural records created
                  </div>
                </div>

                {/* Approved Decisions */}
                <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Approved Decisions
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--success)', marginTop: '4px' }}>
                        {statistics?.approved_decisions ?? 0}
                      </div>
                    </div>
                    <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(34, 197, 94, 0.12)', color: 'var(--success)' }}>
                      <CheckCircle2 size={22} />
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    Approved & ratified ADRs
                  </div>
                </div>

                {/* In Review */}
                <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Under Review
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Outfit', color: '#f59e0b', marginTop: '4px' }}>
                        {statistics?.under_review_decisions ?? 0}
                      </div>
                    </div>
                    <div style={{ padding: '8px', borderRadius: '8px', background: 'rgba(245, 158, 11, 0.12)', color: '#f59e0b' }}>
                      <Clock size={22} />
                    </div>
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                    Awaiting reviewer deliberation
                  </div>
                </div>

                {/* Approval Success Rate */}
                <div className="card" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontSize: '0.78rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 600 }}>
                        Approval Rate
                      </div>
                      <div style={{ fontSize: '2rem', fontWeight: 700, fontFamily: 'Outfit', color: 'var(--primary)', marginTop: '4px' }}>
                        {statistics?.approval_rate ?? 0}%
                      </div>
                    </div>
                    <div style={{ padding: '8px', borderRadius: '8px', background: 'var(--primary-light)', color: 'var(--primary)' }}>
                      <Award size={22} />
                    </div>
                  </div>
                  <div style={{
                    height: '4px',
                    width: '100%',
                    background: 'var(--bg-hover)',
                    borderRadius: '2px',
                    marginTop: '0.75rem',
                    overflow: 'hidden',
                  }}>
                    <div style={{
                      height: '100%',
                      width: `${Math.min(statistics?.approval_rate || 0, 100)}%`,
                      background: 'var(--primary)',
                      borderRadius: '2px',
                    }} />
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Secondary Metrics */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: isReviewer ? '1fr' : 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.25rem',
          }}>
            {!isReviewer && (
              /* Decision Lifecycle Breakdown */
              <div className="card" style={{ padding: '1.5rem' }}>
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Layers size={18} style={{ color: 'var(--primary)' }} />
                  Decision Status Distribution
                </h3>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--text-muted)' }} />
                      Draft Records
                    </span>
                    <span style={{ fontWeight: 600 }}>{statistics?.draft_decisions ?? 0}</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }} />
                      Under Active Review
                    </span>
                    <span style={{ fontWeight: 600 }}>{statistics?.under_review_decisions ?? 0}</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)' }} />
                      Approved & Enacted
                    </span>
                    <span style={{ fontWeight: 600 }}>{statistics?.approved_decisions ?? 0}</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--danger)' }} />
                      Rejected / Needs Revision
                    </span>
                    <span style={{ fontWeight: 600 }}>{statistics?.rejected_decisions ?? 0}</span>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--text-secondary)' }} />
                      Archived ADRs
                    </span>
                    <span style={{ fontWeight: 600 }}>{statistics?.archived_decisions ?? 0}</span>
                  </div>
                </div>
              </div>
            )}

            {/* Collaboration & Review Workload */}
            <div className="card" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Shield size={18} style={{ color: 'var(--primary)' }} />
                {isReviewer ? 'Reviewer Workload & Compliance Breakdown' : 'Collaboration & Governance'}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {!isReviewer && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Layers size={15} style={{ color: 'var(--primary)' }} />
                      Alternative Options Evaluated
                    </span>
                    <span style={{ fontWeight: 600 }}>{statistics?.total_alternatives_created ?? 0}</span>
                  </div>
                )}

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <MessageSquare size={15} style={{ color: 'var(--primary)' }} />
                    Discussion Comments Posted
                  </span>
                  <span style={{ fontWeight: 600 }}>{statistics?.total_comments_posted ?? 0}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <CheckCircle2 size={15} style={{ color: 'var(--primary)' }} />
                    Assigned Review Tasks
                  </span>
                  <span style={{ fontWeight: 600 }}>{statistics?.assigned_reviews ?? 0}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Clock size={15} style={{ color: '#f59e0b' }} />
                    Pending Reviews Awaiting Vote
                  </span>
                  <span style={{ fontWeight: 600, color: '#f59e0b' }}>{statistics?.pending_reviews ?? 0}</span>
                </div>

                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.875rem' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Award size={15} style={{ color: 'var(--success)' }} />
                    Reviews Completed & Finalized
                  </span>
                  <span style={{ fontWeight: 600, color: 'var(--success)' }}>{statistics?.completed_reviews ?? 0}</span>
                </div>
              </div>
            </div>
          </div>

          {/* User Profile Summary Details */}
          <div className="card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <User size={18} style={{ color: 'var(--primary)' }} />
              Employment & Account Information
            </h3>

            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '1.25rem',
              fontSize: '0.875rem',
            }}>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Full Name
                </div>
                <div style={{ fontWeight: 600, marginTop: '3px' }}>{currentUser?.full_name}</div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Email Address
                </div>
                <div style={{ fontWeight: 600, marginTop: '3px' }}>{currentUser?.email}</div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Assigned Role
                </div>
                <div style={{ marginTop: '3px' }}><RoleBadge role={currentUser?.role} /></div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Organization
                </div>
                <div style={{ fontWeight: 600, marginTop: '3px' }}>{orgName || `Organization #${currentUser?.organization_id}`}</div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Department
                </div>
                <div style={{ fontWeight: 600, marginTop: '3px' }}>{currentUser?.department || '—'}</div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Designation
                </div>
                <div style={{ fontWeight: 600, marginTop: '3px' }}>{currentUser?.designation || '—'}</div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Employee ID
                </div>
                <div style={{ fontWeight: 600, marginTop: '3px' }}>{currentUser?.employee_id || '—'}</div>
              </div>

              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem', textTransform: 'uppercase', fontWeight: 600 }}>
                  Phone Number
                </div>
                <div style={{ fontWeight: 600, marginTop: '3px' }}>{currentUser?.phone_number || '—'}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: EDIT PROFILE */}
      {activeTab === 'edit' && (
        <div className="card" style={{ padding: '2rem' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <User size={20} style={{ color: 'var(--primary)' }} /> Edit Profile Details
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Update your professional profile information across the platform.
          </p>

          <form onSubmit={handleUpdateProfile} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.25rem' }}>
              <div>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  Full Name *
                </label>
                <input
                  type="text"
                  className="form-input"
                  required
                  value={editForm.full_name}
                  onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                  placeholder="Your full name"
                />
              </div>

              <div>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  Email Address
                </label>
                <input
                  type="email"
                  className="form-input"
                  disabled
                  value={currentUser?.email || ''}
                  style={{ opacity: 0.7, cursor: 'not-allowed' }}
                />
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Email is system-bound. Contact an Administrator to modify.
                </div>
              </div>

              <div>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  Department
                </label>
                <input
                  type="text"
                  className="form-input"
                  value={editForm.department}
                  onChange={(e) => setEditForm({ ...editForm, department: e.target.value })}
                  placeholder="e.g. Engineering, Architecture, QA"
                />
              </div>

              <div>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  Designation / Job Title
                </label>
                <input
                  type="text"
                  className="form-input"
                  value={editForm.designation}
                  onChange={(e) => setEditForm({ ...editForm, designation: e.target.value })}
                  placeholder="e.g. Principal Architect, Senior Engineer"
                />
              </div>

              <div>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  Phone Number
                </label>
                <input
                  type="tel"
                  className="form-input"
                  value={editForm.phone_number}
                  onChange={(e) => setEditForm({ ...editForm, phone_number: e.target.value })}
                  placeholder="e.g. +1 (555) 000-0000"
                />
              </div>

              <div>
                <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  Assigned Organization
                </label>
                <input
                  type="text"
                  className="form-input"
                  disabled
                  value={orgName || `Organization #${currentUser?.organization_id}`}
                  style={{ opacity: 0.7, cursor: 'not-allowed' }}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setActiveTab('overview')}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={savingProfile}
              >
                <Save size={16} />
                {savingProfile ? 'Saving Changes...' : 'Save Profile Changes'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* TAB 3: SECURITY & PASSWORD */}
      {activeTab === 'security' && (
        <div className="card" style={{ padding: '2rem' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '0.35rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Lock size={20} style={{ color: 'var(--primary)' }} /> Security & Password Settings
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Ensure your account is protected with a secure password.
          </p>

          <form onSubmit={handleChangePassword} style={{ maxWidth: '480px', display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div>
              <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                New Password *
              </label>
              <input
                type="password"
                className="form-input"
                required
                minLength={8}
                value={passwordForm.password}
                onChange={(e) => setPasswordForm({ ...passwordForm, password: e.target.value })}
                placeholder="At least 8 characters"
              />
            </div>

            <div>
              <label className="form-label" style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                Confirm New Password *
              </label>
              <input
                type="password"
                className="form-input"
                required
                minLength={8}
                value={passwordForm.confirm_password}
                onChange={(e) => setPasswordForm({ ...passwordForm, confirm_password: e.target.value })}
                placeholder="Confirm your new password"
              />
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-start', gap: '0.75rem', marginTop: '0.5rem' }}>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={savingPassword}
              >
                <KeyRound size={16} />
                {savingPassword ? 'Updating Password...' : 'Update Password'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}
