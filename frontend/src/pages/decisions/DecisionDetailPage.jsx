import React, { useState, useEffect, useCallback } from 'react';
import {
  ArrowLeft,
  Calendar,
  User,
  Building,
  Tag,
  Plus,
  Trash2,
  Edit2,
  CheckCircle2,
  XCircle,
  Clock,
  Send,
  MessageSquare,
  FileSpreadsheet,
  GitCommit,
  Shield,
  Layers,
  FileText,
  AlertTriangle,
  Scale,
  Sparkles,
  Download,
  Check,
  Award,
} from 'lucide-react';
import { decisionsApi } from '../../api/decisions';
import { alternativesApi } from '../../api/alternatives';
import { approvalsApi } from '../../api/approvals';
import { discussionsApi } from '../../api/discussions';
import { usersApi } from '../../api/users';
import { useAuth } from '../../context/AuthContext';
import { useNotification } from '../../context/NotificationContext';
import { StatusBadge, RiskBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { Modal } from '../../components/common/Modal';
import { EmptyState } from '../../components/common/EmptyState';

export function DecisionDetailPage({ decisionId, onBack }) {
  const { user, role, isEmployee, isReviewer, isManager, isAdmin } = useAuth();
  const { success, error } = useNotification();

  const [decision, setDecision] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);

  // Alternatives state
  const [alternatives, setAlternatives] = useState([]);
  const [comparisonData, setComparisonData] = useState(null);
  const [showAddAlternativeModal, setShowAddAlternativeModal] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [selectedAltId, setSelectedAltId] = useState(() => {
    const saved = localStorage.getItem(`selected_alt_${decisionId}`);
    return saved ? Number(saved) : null;
  });

  const handleSelectAlternative = (altId) => {
    if (selectedAltId === altId) {
      setSelectedAltId(null);
      localStorage.removeItem(`selected_alt_${decisionId}`);
      success('Deselected candidate option');
    } else {
      setSelectedAltId(altId);
      localStorage.setItem(`selected_alt_${decisionId}`, altId);
      success('Marked alternative as the chosen / recommended option');
    }
  };
  const [altForm, setAltForm] = useState({
    name: '',
    description: '',
    estimated_cost: '',
    feasibility_score: 3,
    risk_level: 'Medium',
    pros: '',
    cons: '',
  });

  // Approvals state
  const [approvals, setApprovals] = useState([]);
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [orgUsers, setOrgUsers] = useState([]);
  const [selectedReviewerId, setSelectedReviewerId] = useState('');

  // Discussions state
  const [threads, setThreads] = useState([]);
  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadContent, setNewThreadContent] = useState('');
  const [meetingNotes, setMeetingNotes] = useState([]);
  const [showNoteModal, setShowNoteModal] = useState(false);
  const [noteForm, setNoteForm] = useState({ title: '', attendees: '', notes: '' });

  // Timeline & Versions
  const [timeline, setTimeline] = useState([]);
  const [versions, setVersions] = useState([]);

  // Tag input
  const [newTag, setNewTag] = useState('');

  const loadAllDetails = useCallback(async () => {
    try {
      setLoading(true);
      const [detail, alts, apps, thrs, notes, tline, vers] = await Promise.all([
        decisionsApi.getDecisionDetail(decisionId).catch(() => decisionsApi.getDecision(decisionId)),
        alternativesApi.getByDecisionId(decisionId).catch(() => []),
        approvalsApi.getByDecisionId(decisionId).catch(() => []),
        discussionsApi.getThreads(decisionId).catch(() => []),
        discussionsApi.getMeetingNotes(decisionId).catch(() => []),
        decisionsApi.getTimeline(decisionId).catch(() => []),
        decisionsApi.getVersions(decisionId).catch(() => []),
      ]);

      setDecision(detail);
      setAlternatives(alts || []);
      setApprovals(apps || []);
      setThreads(thrs || []);
      setMeetingNotes(notes || []);
      setTimeline(tline || []);
      setVersions(vers || []);
    } catch (err) {
      error(err.message || 'Failed to load complete decision data');
    } finally {
      setLoading(false);
    }
  }, [decisionId, error]);

  useEffect(() => {
    loadAllDetails();
  }, [loadAllDetails]);

  // Load org users for reviewer assignment if Manager or Admin
  useEffect(() => {
    if (isManager || isAdmin) {
      usersApi.getUsers().then((res) => {
        if (res) {
          const reviewers = res.filter((u) => u.role === 'Reviewer' || u.role === 'Manager');
          setOrgUsers(reviewers);
          if (reviewers.length > 0) setSelectedReviewerId(reviewers[0].id);
        }
      }).catch(() => {});
    }
  }, [isManager, isAdmin]);

  // Actions
  const handleAddTag = async (e) => {
    e.preventDefault();
    if (!newTag.trim()) return;
    try {
      await decisionsApi.addTag(decisionId, newTag.trim());
      setNewTag('');
      success('Tag added');
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Failed to add tag');
    }
  };

  const handleRemoveTag = async (tagId) => {
    try {
      await decisionsApi.removeTag(decisionId, tagId);
      success('Tag removed');
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Failed to remove tag');
    }
  };

  const handleCreateAlternative = async (e) => {
    e.preventDefault();
    if (!altForm.name.trim()) {
      error('Alternative name is required');
      return;
    }
    const score = Number(altForm.feasibility_score);
    if (isNaN(score) || score < 1 || score > 5) {
      error('Feasibility score must be between 1 and 5');
      return;
    }

    try {
      await alternativesApi.create(decisionId, {
        name: altForm.name.trim(),
        description: altForm.description.trim() || `${altForm.name.trim()} candidate alternative`,
        estimated_cost: altForm.estimated_cost ? Number(altForm.estimated_cost) : 0,
        feasibility_score: score,
        risk_level: altForm.risk_level,
        pros: altForm.pros.trim() || 'Provides required architectural capabilities',
        cons: altForm.cons.trim() || 'Requires operational maintenance and monitoring',
      });
      success('Alternative added successfully');
      setShowAddAlternativeModal(false);
      setAltForm({
        name: '',
        description: '',
        estimated_cost: '',
        feasibility_score: 3,
        risk_level: 'Medium',
        pros: '',
        cons: '',
      });
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Failed to add alternative');
    }
  };

  const handleDeleteAlternative = async (altId) => {
    try {
      await alternativesApi.delete(altId);
      success('Alternative deleted');
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Failed to delete alternative');
    }
  };

  const handleOpenComparison = async () => {
    try {
      const cmp = await alternativesApi.compare(decisionId);
      setComparisonData(cmp);
      setShowCompareModal(true);
    } catch (err) {
      error(err.message || 'Failed to load alternative comparison matrix');
    }
  };

  const handleSubmitForReview = async () => {
    try {
      await decisionsApi.submitDecision(decisionId);
      success('Decision submitted for review!');
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Submit failed');
    }
  };

  const handleAssignReviewer = async (e) => {
    e.preventDefault();
    if (!selectedReviewerId) {
      error('Please select a reviewer');
      return;
    }
    try {
      await approvalsApi.create(decisionId, Number(selectedReviewerId));
      success('Reviewer assigned successfully');
      setShowAssignModal(false);
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Failed to assign reviewer');
    }
  };

  const handleApprovalAction = async (approvalId, newStatus) => {
    try {
      await approvalsApi.updateStatus(approvalId, newStatus);
      success(`Decision marked as ${newStatus}!`);
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Failed to update approval');
    }
  };

  const handleCreateThread = async (e) => {
    e.preventDefault();
    if (!newThreadTitle.trim() || !newThreadContent.trim()) {
      error('Thread title and initial message are required');
      return;
    }
    try {
      await discussionsApi.createThread(decisionId, {
        title: newThreadTitle.trim(),
        content: newThreadContent.trim(),
      });
      setNewThreadTitle('');
      setNewThreadContent('');
      success('Discussion thread created');
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Failed to create discussion thread');
    }
  };

  const handleCreateNote = async (e) => {
    e.preventDefault();
    if (!noteForm.title.trim() || !noteForm.notes.trim()) {
      error('Title and notes are required');
      return;
    }
    try {
      await discussionsApi.createMeetingNote(decisionId, {
        title: noteForm.title.trim(),
        notes: noteForm.notes.trim(),
        attendees: noteForm.attendees.trim() || undefined,
      });
      setShowNoteModal(false);
      setNoteForm({ title: '', attendees: '', notes: '' });
      success('Meeting note recorded');
      loadAllDetails();
    } catch (err) {
      error(err.message || 'Failed to save meeting note');
    }
  };

  if (loading) {
    return <LoadingSpinner message="Loading complete decision file and governance records..." size="large" />;
  }

  if (!decision) {
    return (
      <EmptyState
        title="Decision Not Found"
        description="The decision may have been deleted or belongs to another organization."
        action={
          <button className="btn btn-primary" onClick={onBack}>
            Return to List
          </button>
        }
      />
    );
  }

  const canModify =
    decision.created_by === user?.id || user?.role === 'Manager' || user?.role === 'Administrator';
  const canSubmit = canModify && (decision.status === 'Draft' || decision.status === 'Rejected');

  // Check if current user is an assigned reviewer with pending approval
  const myPendingApproval = approvals.find(
    (a) => a.reviewer_id === user?.id && a.status === 'Pending'
  );

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Top Bar Navigation */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '1rem',
      }}>
        <button className="btn btn-secondary btn-sm" onClick={onBack}>
          <ArrowLeft size={16} /> Back to Decisions
        </button>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <StatusBadge status={decision.status} />
          {canSubmit && (
            <button className="btn btn-primary btn-sm" onClick={handleSubmitForReview}>
              <Send size={15} /> Submit for Review
            </button>
          )}
          {(isManager || isAdmin || decision.created_by === user?.id) && (
            <button className="btn btn-secondary btn-sm" onClick={() => setShowAssignModal(true)}>
              <User size={15} /> Assign Reviewer
            </button>
          )}
        </div>
      </div>

      {/* Decision Hero Header */}
      <div className="card" style={{ padding: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
              <span className="badge badge-role">{decision.category || 'General'}</span>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                Decision #{decision.id}
              </span>
            </div>
            <h1 style={{ fontSize: '1.85rem', marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
              {decision.title}
            </h1>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.25rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Calendar size={15} />
                Created {new Date(decision.created_at).toLocaleDateString()}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Building size={15} />
                Org #{decision.organization_id}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <User size={15} />
                Author: {decision.creator?.full_name || `User #${decision.created_by}`}
              </div>
            </div>
          </div>
        </div>

        {/* Tags row */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1.25rem', paddingTop: '1rem', borderTop: '1px solid var(--border-color)' }}>
          <Tag size={15} style={{ color: 'var(--text-muted)' }} />
          {decision.tags && decision.tags.length > 0 ? (
            decision.tags.map((t) => (
              <span key={t.id} style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.75rem',
                background: 'var(--bg-hover)',
                border: '1px solid var(--border-color)',
                padding: '2px 8px',
                borderRadius: '6px',
                color: 'var(--text-secondary)',
              }}>
                #{t.name}
                {canModify && (
                  <button
                    onClick={() => handleRemoveTag(t.id)}
                    style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', display: 'flex' }}
                  >
                    ×
                  </button>
                )}
              </span>
            ))
          ) : (
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>No tags assigned</span>
          )}

          {canModify && (
            <form onSubmit={handleAddTag} style={{ display: 'inline-flex', gap: '4px', marginLeft: '0.5rem' }}>
              <input
                type="text"
                placeholder="+ tag"
                value={newTag}
                onChange={(e) => setNewTag(e.target.value)}
                style={{
                  background: 'var(--bg-input)',
                  border: '1px solid var(--border-color)',
                  borderRadius: '4px',
                  padding: '2px 6px',
                  fontSize: '0.75rem',
                  color: 'var(--text-primary)',
                  width: '70px',
                }}
              />
            </form>
          )}
        </div>
      </div>

      {/* Reviewer Action Callout Banner if user has pending review */}
      {myPendingApproval && (
        <div className="card" style={{
          borderColor: 'var(--primary)',
          background: 'linear-gradient(135deg, var(--bg-card), var(--primary-light))',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '1rem',
        }}>
          <div>
            <h3 style={{ fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Shield size={20} style={{ color: 'var(--primary)' }} />
              You are assigned to review this decision
            </h3>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Evaluate problem statement, proposed alternatives, feasibility scores, and cast your vote.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button
              className="btn btn-success"
              onClick={() => handleApprovalAction(myPendingApproval.id, 'Approved')}
            >
              <CheckCircle2 size={16} /> Approve Decision
            </button>
            <button
              className="btn btn-danger"
              onClick={() => handleApprovalAction(myPendingApproval.id, 'Rejected')}
            >
              <XCircle size={16} /> Reject Decision
            </button>
          </div>
        </div>
      )}

      {/* Navigation Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border-color)',
        gap: '0.5rem',
        overflowX: 'auto',
      }}>
        {[
          { id: 'overview', label: 'Overview & Criteria', icon: FileText },
          { id: 'alternatives', label: `Alternatives (${alternatives.length})`, icon: Scale },
          { id: 'discussions', label: `Discussions & Notes (${threads.length + meetingNotes.length})`, icon: MessageSquare },
          { id: 'approvals', label: `Approval Workflow (${approvals.length})`, icon: CheckCircle2 },
          { id: 'timeline', label: `Timeline & Versions (${versions.length})`, icon: GitCommit },
        ].map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.75rem 1.25rem',
                border: 'none',
                background: 'transparent',
                borderBottom: `2px solid ${isActive ? 'var(--primary)' : 'transparent'}`,
                color: isActive ? 'var(--primary)' : 'var(--text-secondary)',
                fontWeight: isActive ? 600 : 500,
                fontSize: '0.9rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.15s ease',
              }}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab 1: Overview */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card">
            <h2 style={{ fontSize: '1.15rem', marginBottom: '0.75rem' }}>Problem Statement</h2>
            <p style={{ color: 'var(--text-primary)', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
              {decision.problem_statement}
            </p>
          </div>

          {decision.rationale && (
            <div className="card">
              <h2 style={{ fontSize: '1.15rem', marginBottom: '0.75rem' }}>Objectives & Business Rationale</h2>
              <p style={{ color: 'var(--text-primary)', lineHeight: 1.6, whiteSpace: 'pre-line' }}>
                {decision.rationale}
              </p>
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
            <div className="card">
              <h3 style={{ fontSize: '1.05rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Scale size={17} style={{ color: 'var(--primary)' }} /> Evaluation Criteria
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {decision.evaluation_criteria || 'Alternatives are benchmarked on Feasibility Score (1-5), Estimated Total Cost, and Implementation Risk Level.'}
              </p>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.05rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertTriangle size={17} style={{ color: 'var(--warning)' }} /> Identified Risks
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {decision.risks || 'Potential operational downtime, vendor lock-in, latency SLAs, and compliance auditing.'}
              </p>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.05rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <User size={17} style={{ color: 'var(--purple)' }} /> Key Stakeholders
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {decision.stakeholders || 'Engineering Leadership, Quality Assurance, Product Governance, Security Architecture.'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Alternatives & Comparison */}
      {activeTab === 'alternatives' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h2 style={{ fontSize: '1.25rem', marginBottom: '0.2rem' }}>Alternative Options</h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                Formally evaluate and compare technological or architectural candidates.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {alternatives.length >= 2 && (
                <button className="btn btn-secondary" onClick={handleOpenComparison}>
                  <Scale size={16} /> Compare Matrix
                </button>
              )}
              {canModify && (
                <button className="btn btn-primary" onClick={() => setShowAddAlternativeModal(true)}>
                  <Plus size={16} /> Add Alternative
                </button>
              )}
            </div>
          </div>

          {alternatives.length === 0 ? (
            <EmptyState
              title="No alternatives added yet"
              description="Add at least 2 alternatives to enable comparative trade-off analysis."
              action={
                canModify && (
                  <button className="btn btn-primary btn-sm" onClick={() => setShowAddAlternativeModal(true)}>
                    <Plus size={15} /> Add Alternative
                  </button>
                )
              }
            />
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1.25rem' }}>
              {alternatives.map((alt) => {
                const isSelected = selectedAltId === alt.id;
                return (
                  <div
                    key={alt.id}
                    className="card"
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'space-between',
                      border: isSelected ? '2px solid var(--success)' : '1px solid var(--border-color)',
                      background: isSelected ? 'linear-gradient(180deg, var(--bg-card), var(--bg-hover))' : 'var(--bg-card)',
                      boxShadow: isSelected ? '0 0 16px rgba(16, 185, 129, 0.18)' : 'none',
                      transition: 'all 0.2s ease',
                      position: 'relative',
                    }}
                  >
                    <div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem', gap: '0.5rem' }}>
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-primary)', margin: 0 }}>{alt.name}</h3>
                            {isSelected && (
                              <span
                                className="badge"
                                style={{
                                  background: 'var(--success-light)',
                                  color: 'var(--success)',
                                  border: '1px solid var(--success)',
                                  fontSize: '0.72rem',
                                  display: 'inline-flex',
                                  alignItems: 'center',
                                  gap: '3px',
                                  padding: '2px 6px',
                                  fontWeight: 600,
                                }}
                              >
                                <Award size={12} /> Selected Option
                              </span>
                            )}
                          </div>
                        </div>
                        <RiskBadge level={alt.risk_level} />
                      </div>
                      {alt.description && (
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
                          {alt.description}
                        </p>
                      )}

                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem', marginBottom: '1rem', background: 'var(--bg-hover)', padding: '0.75rem', borderRadius: '8px' }}>
                        <div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Feasibility Score</div>
                          <div style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--primary)' }}>
                            {alt.feasibility_score} / 5
                          </div>
                        </div>
                        <div>
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Estimated Cost</div>
                          <div style={{ fontSize: '1.25rem', fontWeight: 700 }}>
                            ${alt.estimated_cost != null ? alt.estimated_cost.toLocaleString() : 'N/A'}
                          </div>
                        </div>
                      </div>

                      {alt.pros && (
                        <div style={{ marginBottom: '0.5rem', fontSize: '0.825rem' }}>
                          <strong style={{ color: 'var(--success)' }}>Pros:</strong> {alt.pros}
                        </div>
                      )}
                      {alt.cons && (
                        <div style={{ marginBottom: '0.5rem', fontSize: '0.825rem' }}>
                          <strong style={{ color: 'var(--danger)' }}>Cons:</strong> {alt.cons}
                        </div>
                      )}
                    </div>

                    <div style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      gap: '0.5rem',
                      borderTop: '1px solid var(--border-color)',
                      paddingTop: '0.75rem',
                      marginTop: '1rem'
                    }}>
                      <button
                        type="button"
                        className={`btn btn-sm ${isSelected ? 'btn-success' : 'btn-secondary'}`}
                        style={{ display: 'inline-flex', alignItems: 'center', gap: '5px' }}
                        onClick={() => handleSelectAlternative(alt.id)}
                      >
                        {isSelected ? (
                          <>
                            <Check size={14} /> Selected Option
                          </>
                        ) : (
                          <>
                            <Award size={14} /> Select as Choice
                          </>
                        )}
                      </button>

                      {canModify && (
                        <button
                          className="btn btn-secondary btn-sm"
                          style={{ color: 'var(--danger)' }}
                          onClick={() => handleDeleteAlternative(alt.id)}
                        >
                          <Trash2 size={14} /> Remove
                        </button>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Discussions & Notes */}
      {activeTab === 'discussions' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ fontSize: '1.25rem' }}>Decision Discussions & Deliberations</h2>
            <button className="btn btn-secondary btn-sm" onClick={() => setShowNoteModal(true)}>
              <Plus size={15} /> Add Meeting Note
            </button>
          </div>

          {/* New Thread Input Box */}
          <div className="card">
            <h3 style={{ fontSize: '1rem', marginBottom: '0.75rem' }}>Start a New Discussion Thread</h3>
            <form onSubmit={handleCreateThread}>
              <div className="form-group">
                <input
                  type="text"
                  className="form-input"
                  placeholder="Thread topic / title..."
                  value={newThreadTitle}
                  onChange={(e) => setNewThreadTitle(e.target.value)}
                />
              </div>
              <div className="form-group">
                <textarea
                  className="form-textarea"
                  rows={3}
                  placeholder="Share feedback, architectural concerns, or questions..."
                  value={newThreadContent}
                  onChange={(e) => setNewThreadContent(e.target.value)}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button type="submit" className="btn btn-primary btn-sm">
                  <MessageSquare size={14} /> Post Thread
                </button>
              </div>
            </form>
          </div>

          {/* Meeting Notes section */}
          {meetingNotes.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: '1.05rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <FileText size={18} style={{ color: 'var(--primary)' }} /> Formal Meeting Notes
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {meetingNotes.map((note) => (
                  <div key={note.id} style={{ background: 'var(--bg-hover)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                      <strong style={{ fontSize: '0.95rem' }}>{note.title}</strong>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {new Date(note.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    {note.attendees && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                        <strong>Attendees:</strong> {note.attendees}
                      </div>
                    )}
                    <p style={{ fontSize: '0.85rem', whiteSpace: 'pre-line', color: 'var(--text-primary)' }}>
                      {note.notes}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Threads List */}
          {threads.length === 0 ? (
            <EmptyState
              title="No discussion threads yet"
              description="Be the first to start a conversation about this decision proposal."
            />
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              {threads.map((thr) => (
                <div key={thr.id} className="card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                    <h4 style={{ fontSize: '1.05rem' }}>{thr.title}</h4>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      {new Date(thr.created_at).toLocaleString()}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.75rem' }}>
                    {thr.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Approval Workflow */}
      {activeTab === 'approvals' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Approval Workflow Governance</h2>

            {/* Visual Workflow Pipeline */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-around',
              padding: '1.5rem',
              background: 'var(--bg-hover)',
              borderRadius: '12px',
              border: '1px solid var(--border-color)',
              marginBottom: '1.5rem',
            }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: 'var(--warning-light)',
                  color: 'var(--warning)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 0.5rem',
                  border: '2px solid var(--warning)',
                }}>
                  1
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>Draft</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Authoring</div>
              </div>

              <div style={{ flex: 1, height: '2px', background: 'var(--border-color)', margin: '0 1rem' }} />

              <div style={{ textAlign: 'center' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: decision.status === 'Under Review' ? 'var(--info-light)' : 'var(--bg-card)',
                  color: decision.status === 'Under Review' ? 'var(--info)' : 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 0.5rem',
                  border: `2px solid ${decision.status === 'Under Review' ? 'var(--info)' : 'var(--border-color)'}`,
                }}>
                  2
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>Under Review</div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Peer Assessment</div>
              </div>

              <div style={{ flex: 1, height: '2px', background: 'var(--border-color)', margin: '0 1rem' }} />

              <div style={{ textAlign: 'center' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '50%',
                  background: decision.status === 'Approved' ? 'var(--success-light)' : decision.status === 'Rejected' ? 'var(--danger-light)' : 'var(--bg-card)',
                  color: decision.status === 'Approved' ? 'var(--success)' : decision.status === 'Rejected' ? 'var(--danger)' : 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  margin: '0 auto 0.5rem',
                  border: `2px solid ${decision.status === 'Approved' ? 'var(--success)' : decision.status === 'Rejected' ? 'var(--danger)' : 'var(--border-color)'}`,
                }}>
                  3
                </div>
                <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>
                  {decision.status === 'Approved' ? 'Approved' : decision.status === 'Rejected' ? 'Rejected' : 'Verdict'}
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Final Determination</div>
              </div>
            </div>

            {/* Approvals Table */}
            <h3 style={{ fontSize: '1.05rem', marginBottom: '0.75rem' }}>Assigned Approvals & Reviews</h3>
            {approvals.length === 0 ? (
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                No reviewer currently assigned. (Click "Assign Reviewer" above to assign an evaluator)
              </div>
            ) : (
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Reviewer ID</th>
                      <th>Status</th>
                      <th>Requested Date</th>
                      <th>Decision Date</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {approvals.map((app) => {
                      const isCurrentUserReviewer = app.reviewer_id === user?.id;
                      const isPending = app.status === 'Pending';

                      return (
                        <tr key={app.id}>
                          <td>
                            <strong>Reviewer #{app.reviewer_id}</strong>
                            {isCurrentUserReviewer && (
                              <span className="badge badge-role" style={{ marginLeft: '6px' }}>
                                You
                              </span>
                            )}
                          </td>
                          <td><StatusBadge status={app.status} /></td>
                          <td>{new Date(app.created_at).toLocaleString()}</td>
                          <td>{app.completed_at ? new Date(app.completed_at).toLocaleString() : '—'}</td>
                          <td>
                            {isPending && isCurrentUserReviewer && (
                              <div style={{ display: 'flex', gap: '0.5rem' }}>
                                <button
                                  className="btn btn-success btn-sm"
                                  onClick={() => handleApprovalAction(app.id, 'Approved')}
                                >
                                  Approve
                                </button>
                                <button
                                  className="btn btn-danger btn-sm"
                                  onClick={() => handleApprovalAction(app.id, 'Rejected')}
                                >
                                  Reject
                                </button>
                              </div>
                            )}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 5: Timeline & Versions */}
      {activeTab === 'timeline' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.25rem' }}>
              Decision Evolution & Audit Timeline
            </h2>

            {timeline.length === 0 ? (
              <div style={{ color: 'var(--text-secondary)' }}>No timeline audit records found.</div>
            ) : (
              <div style={{ position: 'relative', paddingLeft: '1.75rem' }}>
                <div style={{
                  position: 'absolute',
                  left: '7px',
                  top: '8px',
                  bottom: '8px',
                  width: '2px',
                  background: 'var(--border-color)',
                }} />

                {timeline.map((event) => (
                  <div key={event.id} style={{ position: 'relative', marginBottom: '1.5rem' }}>
                    <div style={{
                      position: 'absolute',
                      left: '-1.75rem',
                      top: '2px',
                      width: '16px',
                      height: '16px',
                      borderRadius: '50%',
                      background: 'var(--primary)',
                      border: '3px solid var(--bg-card)',
                      boxShadow: '0 0 0 2px var(--primary-light)',
                    }} />
                    <div style={{ background: 'var(--bg-hover)', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                        <span style={{ fontWeight: 600, fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                          {event.description || `${event.action} event`}
                        </span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          {new Date(event.created_at).toLocaleString()}
                        </span>
                      </div>
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                        Action: <strong>{event.action}</strong> • Performed by User #{event.user_id}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Versions Snapshot List */}
          {versions.length > 0 && (
            <div className="card">
              <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>Archived Snapshot Versions</h3>
              <div className="table-container">
                <table className="table">
                  <thead>
                    <tr>
                      <th>Version</th>
                      <th>Title</th>
                      <th>Problem Statement Snapshot</th>
                      <th>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {versions.map((ver) => (
                      <tr key={ver.id}>
                        <td><span className="badge badge-role">v{ver.version_number}</span></td>
                        <td><strong>{ver.title}</strong></td>
                        <td style={{ maxWidth: '360px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {ver.problem_statement}
                        </td>
                        <td>{new Date(ver.created_at).toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Add Alternative Modal */}
      <Modal
        isOpen={showAddAlternativeModal}
        onClose={() => setShowAddAlternativeModal(false)}
        title="Add Candidate Alternative"
      >
        <form onSubmit={handleCreateAlternative}>
          <div className="form-group">
            <label className="form-label">Alternative Name *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Apache Kafka with Schema Registry"
              value={altForm.name}
              onChange={(e) => setAltForm({ ...altForm, name: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Description</label>
            <textarea
              className="form-textarea"
              rows={2}
              placeholder="Summary of this alternative..."
              value={altForm.description}
              onChange={(e) => setAltForm({ ...altForm, description: e.target.value })}
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Estimated Cost ($)</label>
              <input
                type="number"
                className="form-input"
                placeholder="e.g. 15000"
                value={altForm.estimated_cost}
                onChange={(e) => setAltForm({ ...altForm, estimated_cost: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Feasibility Score (1 - 5) *</label>
              <input
                type="number"
                min="1"
                max="5"
                className="form-input"
                value={altForm.feasibility_score}
                onChange={(e) => setAltForm({ ...altForm, feasibility_score: e.target.value })}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label">Risk Level *</label>
            <select
              className="form-select"
              value={altForm.risk_level}
              onChange={(e) => setAltForm({ ...altForm, risk_level: e.target.value })}
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div className="form-group">
              <label className="form-label">Key Pros</label>
              <textarea
                className="form-textarea"
                rows={2}
                placeholder="Strengths, benefits..."
                value={altForm.pros}
                onChange={(e) => setAltForm({ ...altForm, pros: e.target.value })}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Key Cons</label>
              <textarea
                className="form-textarea"
                rows={2}
                placeholder="Trade-offs, drawbacks..."
                value={altForm.cons}
                onChange={(e) => setAltForm({ ...altForm, cons: e.target.value })}
              />
            </div>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowAddAlternativeModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save Alternative
            </button>
          </div>
        </form>
      </Modal>

      {/* Side-by-Side Alternative Comparison Modal */}
      <Modal
        isOpen={showCompareModal}
        onClose={() => setShowCompareModal(false)}
        title="Side-by-Side Alternative Comparison Matrix"
        maxWidth="840px"
      >
        {comparisonData && comparisonData.alternatives && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Benchmarking trade-offs across cost, feasibility, and risk for Decision #{decisionId}.
            </p>
            <div className="table-container">
              <table className="table">
                <thead>
                  <tr>
                    <th>Alternative</th>
                    <th>Feasibility (1-5)</th>
                    <th>Estimated Cost</th>
                    <th>Risk Level</th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonData.alternatives.map((alt, idx) => {
                    const isSelected = selectedAltId === alt.id;
                    return (
                      <tr
                        key={idx}
                        style={{
                          background: isSelected ? 'var(--primary-light)' : 'transparent',
                        }}
                      >
                        <td>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <strong style={{ fontSize: '0.95rem' }}>{alt.name}</strong>
                            {isSelected && (
                              <span className="badge" style={{ background: 'var(--success-light)', color: 'var(--success)', border: '1px solid var(--success)', fontSize: '0.7rem' }}>
                                Selected
                              </span>
                            )}
                          </div>
                        </td>
                        <td>
                          <span style={{
                            fontWeight: 700,
                            color: alt.feasibility_score >= 4 ? 'var(--success)' : alt.feasibility_score <= 2 ? 'var(--danger)' : 'var(--warning)',
                          }}>
                            {alt.feasibility_score} / 5
                          </span>
                        </td>
                        <td>
                          {alt.estimated_cost != null ? `$${alt.estimated_cost.toLocaleString()}` : 'N/A'}
                        </td>
                        <td><RiskBadge level={alt.risk_level} /></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </Modal>

      {/* Assign Reviewer Modal */}
      <Modal
        isOpen={showAssignModal}
        onClose={() => setShowAssignModal(false)}
        title="Assign Peer Reviewer"
      >
        <form onSubmit={handleAssignReviewer}>
          <div className="form-group">
            <label className="form-label">Select Qualified Reviewer / Manager</label>
            <select
              className="form-select"
              value={selectedReviewerId}
              onChange={(e) => setSelectedReviewerId(e.target.value)}
              required
            >
              {orgUsers.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.full_name} ({u.role} - {u.email})
                </option>
              ))}
            </select>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowAssignModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Confirm Assignment
            </button>
          </div>
        </form>
      </Modal>

      {/* Add Meeting Note Modal */}
      <Modal
        isOpen={showNoteModal}
        onClose={() => setShowNoteModal(false)}
        title="Record Meeting Note"
      >
        <form onSubmit={handleCreateNote}>
          <div className="form-group">
            <label className="form-label">Meeting Title *</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. Architecture Review Board Deliberation"
              value={noteForm.title}
              onChange={(e) => setNoteForm({ ...noteForm, title: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Attendees</label>
            <input
              type="text"
              className="form-input"
              placeholder="e.g. John Doe, Jane Smith, Alex Wong"
              value={noteForm.attendees}
              onChange={(e) => setNoteForm({ ...noteForm, attendees: e.target.value })}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Deliberation Notes & Minutes *</label>
            <textarea
              className="form-textarea"
              rows={4}
              placeholder="Record consensus, dissent, and architectural trade-offs discussed..."
              value={noteForm.notes}
              onChange={(e) => setNoteForm({ ...noteForm, notes: e.target.value })}
              required
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <button type="button" className="btn btn-secondary" onClick={() => setShowNoteModal(false)}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary">
              Save Meeting Note
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
