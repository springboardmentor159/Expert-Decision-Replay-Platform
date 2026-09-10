import React, { useState, useEffect } from 'react';
import { decisionService } from '../../api/decisionService';
import { alternativeService } from '../../api/alternativeService';
import { approvalService } from '../../api/approvalService';
import { discussionService } from '../../api/discussionService';
import { userService } from '../../api/authService';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Input, TextArea, Select } from '../../components/common/Input';
import { Modal } from '../../components/common/Modal';
import { StatusBadge, RiskBadge } from '../../components/common/Badge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { useToast } from '../../context/ToastContext';
import { useAuth } from '../../context/AuthContext';
import {
  ArrowLeft,
  Edit,
  Trash2,
  Send,
  PlusCircle,
  Scale,
  MessageSquare,
  CheckCircle2,
  XCircle,
  History,
  FileText,
  Clock,
  Tag,
  AlertTriangle,
  UserCheck,
  Calendar,
  Layers,
  ChevronRight,
} from 'lucide-react';

export const DecisionDetailPage = ({ decisionId, onNavigate, initialTab = 'overview', initialOpenEdit = false }) => {
  const [activeTab, setActiveTab] = useState(initialTab);
  const [decision, setDecision] = useState(null);
  const [loading, setLoading] = useState(true);

  // Alternatives state
  const [alternatives, setAlternatives] = useState([]);
  const [comparison, setComparison] = useState(null);
  const [showAltModal, setShowAltModal] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [altForm, setAltForm] = useState({
    name: '',
    description: '',
    pros: '',
    cons: '',
    estimated_cost: '',
    feasibility_score: 3,
    risk_level: 'Medium',
  });

  // Approvals state
  const [approvals, setApprovals] = useState([]);
  const [showSubmitApprovalModal, setShowSubmitApprovalModal] = useState(false);
  const [reviewersList, setReviewersList] = useState([]);
  const [selectedReviewerId, setSelectedReviewerId] = useState('');
  const [approvalComments, setApprovalComments] = useState('');
  const [actionComments, setActionComments] = useState('');
  const [processingAction, setProcessingAction] = useState(false);

  // Discussions state
  const [threads, setThreads] = useState([]);
  const [comments, setComments] = useState([]);
  const [meetingNotes, setMeetingNotes] = useState([]);
  const [newComment, setNewComment] = useState('');
  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadDesc, setNewThreadDesc] = useState('');
  const [showNewThreadModal, setShowNewThreadModal] = useState(false);
  const [newNoteTitle, setNewNoteTitle] = useState('');
  const [newNoteContent, setNewNoteContent] = useState('');
  const [showNewNoteModal, setShowNewNoteModal] = useState(false);

  // Timeline & History state
  const [versions, setVersions] = useState([]);
  const [timeline, setTimeline] = useState([]);

  // Edit rationale modal
  const [showRationaleModal, setShowRationaleModal] = useState(false);
  const [editRationale, setEditRationale] = useState('');

  // Edit decision modal
  const [showEditDecisionModal, setShowEditDecisionModal] = useState(false);
  const [editDecisionForm, setEditDecisionForm] = useState({
    title: '',
    category: 'Architecture',
    problem_statement: '',
  });

  // Edit alternative modal
  const [showEditAltModal, setShowEditAltModal] = useState(false);
  const [editingAlt, setEditingAlt] = useState(null);
  const [editAltForm, setEditAltForm] = useState({
    name: '',
    description: '',
    pros: '',
    cons: '',
    estimated_cost: '',
    feasibility_score: 3,
    risk_level: 'Medium',
  });

  const { success, error } = useToast();
  const { user } = useAuth();

  const fetchAllData = async () => {
    try {
      setLoading(true);
      const dec = await decisionService.getDecision(decisionId);
      setDecision(dec);
      setEditRationale(dec.rationale || '');
      if (initialOpenEdit && dec) {
        setEditDecisionForm({
          title: dec.title || '',
          category: dec.category || 'Architecture',
          problem_statement: dec.problem_statement || '',
        });
        setShowEditDecisionModal(true);
      }

      // Load supporting data concurrently
      const [alts, apprList, threadList, commentList, notesList, versionList, timelineData] =
        await Promise.all([
          alternativeService.getAlternatives(decisionId).catch(() => []),
          approvalService.getApprovals({ decision_id: decisionId }).catch(() => []),
          discussionService.getThreads(decisionId).catch(() => []),
          discussionService.getComments(decisionId).catch(() => []),
          discussionService.getMeetingNotes(decisionId).catch(() => []),
          decisionService.getVersions(decisionId).catch(() => []),
          decisionService.getTimeline(decisionId).catch(() => null),
        ]);

      setAlternatives(alts || []);
      setApprovals(apprList || []);
      setThreads(threadList || []);
      setComments(commentList || []);
      setMeetingNotes(notesList || []);
      setVersions(versionList || []);
      setTimeline(timelineData?.events || []);
    } catch (err) {
      error(err.message || 'Failed to load decision detail');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAllData();
  }, [decisionId]);

  // Open Edit Decision Modal
  const handleOpenEditDecision = () => {
    if (!decision) return;
    setEditDecisionForm({
      title: decision.title,
      category: decision.category,
      problem_statement: decision.problem_statement,
    });
    setShowEditDecisionModal(true);
  };

  // Save Edit Decision
  const handleSaveEditDecision = async (e) => {
    e.preventDefault();
    if (!editDecisionForm.title.trim() || !editDecisionForm.problem_statement.trim()) {
      error('Title and problem statement are required.');
      return;
    }
    try {
      setProcessingAction(true);
      const updated = await decisionService.updateDecision(decisionId, {
        title: editDecisionForm.title.trim(),
        category: editDecisionForm.category.trim(),
        problem_statement: editDecisionForm.problem_statement.trim(),
      });
      setDecision(updated);
      setShowEditDecisionModal(false);
      success('Decision updated successfully! Version history incremented.');
      fetchAllData();
    } catch (err) {
      error(err.message || 'Failed to update decision');
    } finally {
      setProcessingAction(false);
    }
  };

  // Open Edit Alternative Modal
  const handleOpenEditAlt = (alt) => {
    setEditingAlt(alt);
    setEditAltForm({
      name: alt.name || '',
      description: alt.description || '',
      pros: alt.pros || '',
      cons: alt.cons || '',
      estimated_cost: alt.estimated_cost ?? '',
      feasibility_score: alt.feasibility_score || 3,
      risk_level: alt.risk_level || 'Medium',
    });
    setShowEditAltModal(true);
  };

  // Save Edit Alternative
  const handleSaveEditAlt = async (e) => {
    e.preventDefault();
    if (!editAltForm.name.trim()) {
      error('Alternative name is required.');
      return;
    }
    const score = Number(editAltForm.feasibility_score);
    if (isNaN(score) || score < 1 || score > 5) {
      error('Feasibility score must be between 1 and 5');
      return;
    }
    try {
      setProcessingAction(true);
      await alternativeService.updateAlternative(editingAlt.id, {
        name: editAltForm.name.trim(),
        description: editAltForm.description.trim(),
        pros: editAltForm.pros.trim(),
        cons: editAltForm.cons.trim(),
        estimated_cost: editAltForm.estimated_cost ? Number(editAltForm.estimated_cost) : 0,
        feasibility_score: score,
        risk_level: editAltForm.risk_level,
      });
      success(`Alternative "${editAltForm.name}" updated!`);
      setShowEditAltModal(false);
      const updatedAlts = await alternativeService.getAlternatives(decisionId);
      setAlternatives(updatedAlts);
    } catch (err) {
      error(err.message || 'Failed to update alternative');
    } finally {
      setProcessingAction(false);
    }
  };

  // Load potential reviewers for approval submission
  const loadReviewers = async () => {
    try {
      const allUsers = await userService.getUsers();
      const filtered = allUsers.filter((u) => u.role === 'Reviewer' || u.role === 'Manager' || u.role === 'Administrator');
      setReviewersList(filtered);
      if (filtered.length > 0) setSelectedReviewerId(filtered[0].id);
      setShowSubmitApprovalModal(true);
    } catch (err) {
      error('Failed to load reviewers');
    }
  };

  // Submit decision for approval
  const handleSubmitApproval = async (e) => {
    e.preventDefault();
    if (!selectedReviewerId) {
      error('Please select a reviewer.');
      return;
    }

    try {
      setProcessingAction(true);
      await approvalService.createApproval({
        decision_id: Number(decisionId),
        reviewer_id: Number(selectedReviewerId),
        approval_level: 1,
        comments: approvalComments.trim() || 'Submitted for architectural review',
      });
      success('Decision submitted for review successfully!');
      setShowSubmitApprovalModal(false);
      fetchAllData();
    } catch (err) {
      error(err.message || 'Failed to submit decision for review');
    } finally {
      setProcessingAction(false);
    }
  };

  // Process Approval / Rejection
  const handleApprovalAction = async (approvalId, action) => {
    try {
      setProcessingAction(true);
      if (action === 'approve') {
        await approvalService.approveDecision(approvalId, actionComments);
        success('Decision approved successfully!');
      } else {
        await approvalService.rejectDecision(approvalId, actionComments);
        success('Decision rejected.');
      }
      setActionComments('');
      fetchAllData();
    } catch (err) {
      error(err.message || `Failed to ${action} decision`);
    } finally {
      setProcessingAction(false);
    }
  };

  // Add Alternative
  const handleAddAlternative = async (e) => {
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
      await alternativeService.createAlternative(decisionId, {
        name: altForm.name.trim(),
        description: altForm.description.trim(),
        pros: altForm.pros.trim(),
        cons: altForm.cons.trim(),
        estimated_cost: altForm.estimated_cost ? Number(altForm.estimated_cost) : 0,
        feasibility_score: score,
        risk_level: altForm.risk_level,
      });
      success(`Alternative "${altForm.name}" added successfully!`);
      setShowAltModal(false);
      setAltForm({
        name: '',
        description: '',
        pros: '',
        cons: '',
        estimated_cost: '',
        feasibility_score: 3,
        risk_level: 'Medium',
      });
      const updatedAlts = await alternativeService.getAlternatives(decisionId);
      setAlternatives(updatedAlts);
    } catch (err) {
      error(err.message || 'Failed to add alternative');
    }
  };

  // Delete Alternative
  const handleDeleteAlternative = async (altId, altName) => {
    if (!window.confirm(`Delete alternative "${altName}"?`)) return;
    try {
      await alternativeService.deleteAlternative(altId);
      success('Alternative removed.');
      const updatedAlts = await alternativeService.getAlternatives(decisionId);
      setAlternatives(updatedAlts);
    } catch (err) {
      error(err.message || 'Failed to remove alternative');
    }
  };

  // Compare Alternatives
  const handleOpenCompare = async () => {
    try {
      const cmp = await alternativeService.compareAlternatives(decisionId);
      setComparison(cmp);
      setShowCompareModal(true);
    } catch (err) {
      error(err.message || 'Failed to generate comparison matrix');
    }
  };

  // Add Direct Comment
  const handleAddComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) return;

    try {
      await discussionService.addComment(decisionId, newComment.trim());
      setNewComment('');
      success('Comment posted!');
      const updatedComments = await discussionService.getComments(decisionId);
      setComments(updatedComments);
    } catch (err) {
      error(err.message || 'Failed to post comment');
    }
  };

  // Create Discussion Thread
  const handleCreateThread = async (e) => {
    e.preventDefault();
    if (!newThreadTitle.trim()) return;

    try {
      await discussionService.createThread(decisionId, {
        title: newThreadTitle.trim(),
        description: newThreadDesc.trim(),
      });
      setNewThreadTitle('');
      setNewThreadDesc('');
      setShowNewThreadModal(false);
      success('Discussion thread initiated!');
      const updatedThreads = await discussionService.getThreads(decisionId);
      setThreads(updatedThreads);
    } catch (err) {
      error(err.message || 'Failed to create discussion thread');
    }
  };

  // Save Rationale
  const handleSaveRationale = async () => {
    try {
      await decisionService.updateRationale(decisionId, editRationale);
      setDecision((prev) => ({ ...prev, rationale: editRationale }));
      setShowRationaleModal(false);
      success('Decision rationale updated!');
      fetchAllData();
    } catch (err) {
      error(err.message || 'Failed to update rationale');
    }
  };

  if (loading) return <LoadingSpinner message="Loading decision details and history..." />;
  if (!decision) return <EmptyState title="Decision not found" />;

  // Permission checks
  const isCreator = user?.id === decision.created_by;
  const isAdmin = user?.role === 'Administrator';
  const isManager = user?.role === 'Manager';
  const isReviewer = user?.role === 'Reviewer';

  // Check if current user is an assigned reviewer for any pending approval
  const pendingApprovalForUser = approvals.find(
    (a) => a.status === 'Pending' && (a.reviewer_id === user?.id || isAdmin || isManager)
  );

  return (
    <div>
      {/* Top Breadcrumb & Actions */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Button
            variant="outline"
            size="sm"
            icon={ArrowLeft}
            onClick={() => onNavigate('decisions')}
          >
            Back
          </Button>
          <span style={{ color: 'var(--text-muted)' }}>/</span>
          <span style={{ color: 'var(--accent-cyan)', fontSize: '0.85rem', fontWeight: 600 }}>
            {decision.category}
          </span>
          <span style={{ color: 'var(--text-muted)' }}>/</span>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
            Decision #{decision.id}
          </span>
        </div>

        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <StatusBadge status={decision.status} />

          {/* Edit Decision button (if isCreator or Admin) */}
          {(isCreator || isAdmin) && (
            <Button
              variant="outline"
              size="sm"
              icon={Edit}
              onClick={handleOpenEditDecision}
            >
              Edit Decision
            </Button>
          )}

          {/* Submit for review button (if Draft and isCreator or Admin) */}
          {(decision.status === 'Draft' || decision.status === 'Rejected') && (isCreator || isAdmin) && (
            <Button
              variant="primary"
              size="sm"
              icon={Send}
              onClick={loadReviewers}
            >
              Submit for Review
            </Button>
          )}
        </div>
      </div>

      {/* Decision Hero Title Card */}
      <Card style={{ marginBottom: '1.5rem', position: 'relative' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#ffffff', marginBottom: '0.5rem' }}>
          {decision.title}
        </h1>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
          <div>
            Created by: <strong style={{ color: '#ffffff' }}>User #{decision.created_by}</strong>
          </div>
          <div>
            Created: <strong style={{ color: '#ffffff' }}>{new Date(decision.created_at).toLocaleDateString()}</strong>
          </div>
          <div>
            Last Updated: <strong style={{ color: '#ffffff' }}>{new Date(decision.updated_at).toLocaleDateString()}</strong>
          </div>
          <div>
            Category: <strong style={{ color: '#60a5fa' }}>{decision.category}</strong>
          </div>
        </div>
      </Card>

      {/* Navigation Tabs */}
      <div className="tabs-header">
        <button
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <FileText size={16} /> Overview
        </button>
        <button
          className={`tab-btn ${activeTab === 'alternatives' ? 'active' : ''}`}
          onClick={() => setActiveTab('alternatives')}
        >
          <Scale size={16} /> Alternatives ({alternatives.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'discussions' ? 'active' : ''}`}
          onClick={() => setActiveTab('discussions')}
        >
          <MessageSquare size={16} /> Discussions ({comments.length + threads.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'approvals' ? 'active' : ''}`}
          onClick={() => setActiveTab('approvals')}
        >
          <CheckCircle2 size={16} /> Approvals & Workflow ({approvals.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'timeline' ? 'active' : ''}`}
          onClick={() => setActiveTab('timeline')}
        >
          <History size={16} /> Timeline & Versions ({versions.length})
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <Card>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.75rem' }}>
              Problem Statement & Architectural Context
            </h3>
            <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, fontSize: '0.95rem', whiteSpace: 'pre-wrap' }}>
              {decision.problem_statement}
            </p>
          </Card>

          <Card>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff' }}>
                Decision Rationale
              </h3>
              {(isCreator || isAdmin || isManager) && (
                <Button
                  variant="outline"
                  size="sm"
                  icon={Edit}
                  onClick={() => setShowRationaleModal(true)}
                >
                  Edit Rationale
                </Button>
              )}
            </div>
            {decision.rationale ? (
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.7, fontSize: '0.95rem', whiteSpace: 'pre-wrap' }}>
                {decision.rationale}
              </p>
            ) : (
              <p style={{ color: 'var(--text-muted)', fontStyle: 'italic', fontSize: '0.9rem' }}>
                No final decision rationale has been recorded yet. Update the rationale after evaluating alternatives.
              </p>
            )}
          </Card>

          {/* Tags */}
          <Card>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.75rem' }}>
              Taxonomy & Tags
            </h3>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
              {decision.tags && decision.tags.length > 0 ? (
                decision.tags.map((t, idx) => (
                  <span
                    key={idx}
                    style={{
                      background: 'rgba(59, 130, 246, 0.15)',
                      color: '#93c5fd',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: 'var(--radius-full)',
                      padding: '0.3rem 0.8rem',
                      fontSize: '0.85rem',
                      fontWeight: 600,
                    }}
                  >
                    #{typeof t === 'string' ? t : t.name}
                  </span>
                ))
              ) : (
                <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                  No tags associated.
                </span>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* TAB 2: ALTERNATIVES & COMPARISON */}
      {activeTab === 'alternatives' && (
        <div>
          <div
            style={{
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              marginBottom: '1.5rem',
              flexWrap: 'wrap',
              gap: '1rem',
            }}
          >
            <div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#ffffff' }}>
                Architectural Alternatives Under Evaluation
              </h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                Quantify pros, cons, costs, risk profiles, and feasibility scores.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {alternatives.length >= 2 && (
                <Button
                  variant="outline"
                  icon={Scale}
                  onClick={handleOpenCompare}
                >
                  Side-by-Side Comparison
                </Button>
              )}
              {(isCreator || isAdmin || isManager) && (
                <Button
                  variant="primary"
                  icon={PlusCircle}
                  onClick={() => setShowAltModal(true)}
                >
                  Add Alternative
                </Button>
              )}
            </div>
          </div>

          {alternatives.length === 0 ? (
            <EmptyState
              icon={Scale}
              title="No alternatives added yet"
              description="Add two or more architectural candidates to evaluate feasibility and trade-offs."
              actionLabel="Add First Alternative"
              onAction={() => setShowAltModal(true)}
            />
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.25rem' }}>
              {alternatives.map((alt) => (
                <Card key={alt.id} style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
                    <h4 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>{alt.name}</h4>
                    <RiskBadge risk={alt.risk_level} />
                  </div>

                  <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem', flex: 1 }}>
                    {alt.description || 'No description provided.'}
                  </p>

                  {/* Metrics Bar */}
                  <div
                    style={{
                      background: 'rgba(255, 255, 255, 0.03)',
                      borderRadius: 'var(--radius-md)',
                      padding: '0.75rem',
                      display: 'grid',
                      gridTemplateColumns: '1fr 1fr',
                      gap: '0.5rem',
                      marginBottom: '1rem',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>
                        Feasibility (1-5)
                      </span>
                      <strong style={{ fontSize: '1.1rem', color: '#60a5fa' }}>
                        {alt.feasibility_score}/5
                      </strong>
                    </div>
                    <div>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block' }}>
                        Estimated Cost
                      </span>
                      <strong style={{ fontSize: '1.1rem', color: '#ffffff' }}>
                        ${Number(alt.estimated_cost).toLocaleString()}
                      </strong>
                    </div>
                  </div>

                  {/* Pros & Cons */}
                  <div style={{ fontSize: '0.85rem', marginBottom: '1rem' }}>
                    {alt.pros && (
                      <div style={{ marginBottom: '0.5rem' }}>
                        <span style={{ color: '#34d399', fontWeight: 700 }}>+ Pros: </span>
                        <span style={{ color: 'var(--text-secondary)' }}>{alt.pros}</span>
                      </div>
                    )}
                    {alt.cons && (
                      <div>
                        <span style={{ color: '#fb7185', fontWeight: 700 }}>- Cons: </span>
                        <span style={{ color: 'var(--text-secondary)' }}>{alt.cons}</span>
                      </div>
                    )}
                  </div>

                  {(isCreator || isAdmin) && (
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem' }}>
                      <Button
                        variant="outline"
                        size="sm"
                        icon={Edit}
                        onClick={() => handleOpenEditAlt(alt)}
                      >
                        Edit
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        icon={Trash2}
                        onClick={() => handleDeleteAlternative(alt.id, alt.name)}
                      >
                        Remove
                      </Button>
                    </div>
                  )}
                </Card>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: DISCUSSIONS & COMMENTS */}
      {activeTab === 'discussions' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          {/* Discussion Threads & Meeting Notes Column */}
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff' }}>
                Discussion Threads & Topics
              </h3>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <Button variant="outline" size="sm" onClick={() => setShowNewNoteModal(true)}>
                  + Meeting Note
                </Button>
                <Button variant="primary" size="sm" onClick={() => setShowNewThreadModal(true)}>
                  + New Thread
                </Button>
              </div>
            </div>

            {threads.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', padding: '1rem 0' }}>
                No active discussion threads. Click '+ New Thread' to start a deliberation.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {threads.map((th) => (
                  <Card key={th.id} style={{ padding: '1rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                      <strong style={{ color: '#ffffff', fontSize: '0.95rem' }}>{th.title}</strong>
                      <span className="badge badge-role" style={{ fontSize: '0.7rem' }}>
                        {th.status}
                      </span>
                    </div>
                    {th.description && (
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', marginBottom: '0.5rem' }}>
                        {th.description}
                      </p>
                    )}
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Started by User #{th.created_by} • {new Date(th.created_at).toLocaleDateString()}
                    </span>
                  </Card>
                ))}
              </div>
            )}

            {/* Meeting Notes */}
            {meetingNotes.length > 0 && (
              <div style={{ marginTop: '1.5rem' }}>
                <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#ffffff', marginBottom: '0.75rem' }}>
                  Recorded Meeting Notes ({meetingNotes.length})
                </h4>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {meetingNotes.map((mn) => (
                    <div
                      key={mn.id}
                      style={{
                        padding: '0.85rem',
                        background: 'rgba(255, 255, 255, 0.02)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: 'var(--radius-md)',
                      }}
                    >
                      <strong style={{ color: '#a5b4fc', fontSize: '0.9rem' }}>{mn.title}</strong>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', margin: '0.35rem 0' }}>
                        {mn.content}
                      </p>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        Date: {new Date(mn.meeting_date || mn.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Direct Comments Feed Column */}
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', marginBottom: '1rem' }}>
              Comments & Peer Feedback
            </h3>

            {/* Comment Post Box */}
            <Card style={{ marginBottom: '1.25rem', padding: '1rem' }}>
              <form onSubmit={handleAddComment}>
                <TextArea
                  placeholder="Share feedback, ask architectural questions, or raise concerns..."
                  rows={3}
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  required
                />
                <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '0.5rem' }}>
                  <Button type="submit" variant="primary" size="sm" icon={Send}>
                    Post Comment
                  </Button>
                </div>
              </form>
            </Card>

            {/* Comments List */}
            {comments.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                No comments on this decision yet.
              </p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {comments.map((c) => (
                  <div
                    key={c.id}
                    style={{
                      padding: '0.85rem 1rem',
                      background: 'rgba(17, 24, 39, 0.7)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-md)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                      <span style={{ fontWeight: 600, fontSize: '0.85rem', color: '#60a5fa' }}>
                        User #{c.user_id}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {new Date(c.created_at).toLocaleString()}
                      </span>
                    </div>
                    <p style={{ color: 'var(--text-primary)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                      {c.content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 4: APPROVALS & WORKFLOW */}
      {activeTab === 'approvals' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Action Box for Authorized Reviewers */}
          {pendingApprovalForUser && (
            <Card
              style={{
                border: '1px solid var(--accent-blue)',
                boxShadow: 'var(--shadow-glow-blue)',
                background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(17, 24, 39, 0.9))',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <UserCheck size={20} color="#60a5fa" />
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff' }}>
                  Reviewer Action Required
                </h3>
              </div>
              <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
                You are authorized to review and cast a verdict on this decision proposal (Level{' '}
                {pendingApprovalForUser.approval_level}).
              </p>

              <TextArea
                label="Review Comments / Conditions (Optional)"
                placeholder="Add approval notes, mitigation requests, or justification for rejection..."
                rows={2}
                value={actionComments}
                onChange={(e) => setActionComments(e.target.value)}
              />

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <Button
                  variant="success"
                  icon={CheckCircle2}
                  loading={processingAction}
                  onClick={() => handleApprovalAction(pendingApprovalForUser.id, 'approve')}
                >
                  Approve Decision
                </Button>
                <Button
                  variant="danger"
                  icon={XCircle}
                  loading={processingAction}
                  onClick={() => handleApprovalAction(pendingApprovalForUser.id, 'reject')}
                >
                  Reject Decision
                </Button>
              </div>
            </Card>
          )}

          {/* Approvals History Table */}
          <Card>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#ffffff', marginBottom: '1rem' }}>
              Multi-Level Approval Workflow Audit
            </h3>

            {approvals.length === 0 ? (
              <EmptyState
                icon={CheckCircle2}
                title="No approvals recorded"
                description="This decision has not been submitted for approval yet."
                actionLabel={isCreator || isAdmin ? 'Submit for Review' : undefined}
                onAction={loadReviewers}
              />
            ) : (
              <div className="table-container">
                <table className="custom-table">
                  <thead>
                    <tr>
                      <th>Level</th>
                      <th>Assigned Reviewer</th>
                      <th>Status</th>
                      <th>Submitted</th>
                      <th>Completed</th>
                      <th>Reviewer Comments</th>
                    </tr>
                  </thead>
                  <tbody>
                    {approvals.map((appr) => (
                      <tr key={appr.id}>
                        <td>Level {appr.approval_level}</td>
                        <td style={{ fontWeight: 600, color: '#ffffff' }}>
                          Reviewer #{appr.reviewer_id}
                        </td>
                        <td>
                          <StatusBadge status={appr.status} />
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                          {new Date(appr.created_at).toLocaleDateString()}
                        </td>
                        <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                          {appr.completed_at
                            ? new Date(appr.completed_at).toLocaleDateString()
                            : 'Pending'}
                        </td>
                        <td style={{ color: 'var(--text-secondary)', fontSize: '0.85rem' }}>
                          {appr.comments || '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </Card>
        </div>
      )}

      {/* TAB 5: TIMELINE & VERSION HISTORY */}
      {activeTab === 'timeline' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          {/* Sequential Version History */}
          <Card>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', marginBottom: '1rem' }}>
              Sequential Version History
            </h3>
            {versions.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No version records.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                {versions.map((ver) => (
                  <div
                    key={ver.id}
                    style={{
                      padding: '0.85rem 1rem',
                      background: 'rgba(255, 255, 255, 0.02)',
                      borderRadius: 'var(--radius-md)',
                      border: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <span style={{ fontWeight: 700, color: '#60a5fa' }}>
                        Version {ver.version_number}
                      </span>
                      <StatusBadge status={ver.status} />
                    </div>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                      Saved by User #{ver.created_by} on {new Date(ver.created_at).toLocaleString()}
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                      <strong>Title:</strong> {ver.title}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>

          {/* Chronological Event Timeline */}
          <Card>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#ffffff', marginBottom: '1rem' }}>
              Audit Event Timeline
            </h3>
            {timeline.length === 0 ? (
              <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>No events logged.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', position: 'relative' }}>
                {timeline.map((evt, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      padding: '0.65rem 0',
                      borderBottom: '1px solid var(--border-subtle)',
                    }}
                  >
                    <div
                      style={{
                        width: '8px',
                        height: '8px',
                        borderRadius: '50%',
                        background: 'var(--accent-cyan)',
                        marginTop: '6px',
                        boxShadow: 'var(--shadow-glow-cyan)',
                      }}
                    />
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <strong style={{ fontSize: '0.85rem', color: '#ffffff' }}>
                          {evt.event_type}
                        </strong>
                        <span style={{ fontSize: '0.725rem', color: 'var(--text-muted)' }}>
                          {new Date(evt.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                        Actor: {evt.actor_name || `User #${evt.actor_id || 'System'}`}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      )}

      {/* MODAL: ADD ALTERNATIVE */}
      <Modal
        isOpen={showAltModal}
        onClose={() => setShowAltModal(false)}
        title="Add Architectural Alternative"
      >
        <form onSubmit={handleAddAlternative}>
          <Input
            id="alt-name"
            label="Alternative Option Name"
            placeholder="e.g. Apache Pulsar, Redis Streams, Cloud Pub/Sub"
            value={altForm.name}
            onChange={(e) => setAltForm({ ...altForm, name: e.target.value })}
            required
          />

          <TextArea
            id="alt-desc"
            label="Description & Architectural Fit"
            placeholder="Outline how this alternative satisfies the technical requirements..."
            rows={2}
            value={altForm.description}
            onChange={(e) => setAltForm({ ...altForm, description: e.target.value })}
          />

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Input
              id="alt-cost"
              label="Estimated Cost ($)"
              type="number"
              placeholder="e.g. 5000"
              value={altForm.estimated_cost}
              onChange={(e) => setAltForm({ ...altForm, estimated_cost: e.target.value })}
            />

            <Select
              id="alt-feasibility"
              label="Feasibility Score (1-5)"
              value={altForm.feasibility_score}
              onChange={(e) => setAltForm({ ...altForm, feasibility_score: Number(e.target.value) })}
              options={[
                { value: 1, label: '1 - Very Low Feasibility' },
                { value: 2, label: '2 - Low Feasibility' },
                { value: 3, label: '3 - Moderate Feasibility' },
                { value: 4, label: '4 - High Feasibility' },
                { value: 5, label: '5 - Optimal Feasibility' },
              ]}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <Select
              id="alt-risk"
              label="Risk Level"
              value={altForm.risk_level}
              onChange={(e) => setAltForm({ ...altForm, risk_level: e.target.value })}
              options={[
                { value: 'Low', label: 'Low Risk' },
                { value: 'Medium', label: 'Medium Risk' },
                { value: 'High', label: 'High Risk' },
              ]}
              required
            />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '0.5rem' }}>
            <TextArea
              id="alt-pros"
              label="Pros"
              placeholder="e.g. Native tiered storage, active community..."
              rows={2}
              value={altForm.pros}
              onChange={(e) => setAltForm({ ...altForm, pros: e.target.value })}
            />
            <TextArea
              id="alt-cons"
              label="Cons"
              placeholder="e.g. Requires BookKeeper ZooKeeper cluster..."
              rows={2}
              value={altForm.cons}
              onChange={(e) => setAltForm({ ...altForm, cons: e.target.value })}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <Button variant="secondary" onClick={() => setShowAltModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Save Alternative
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: SIDE-BY-SIDE COMPARISON */}
      <Modal
        isOpen={showCompareModal}
        onClose={() => setShowCompareModal(false)}
        title="Side-by-Side Alternatives Comparison"
        maxWidth="900px"
      >
        {comparison && comparison.alternatives ? (
          <div>
            <div className="table-container">
              <table className="custom-table">
                <thead>
                  <tr>
                    <th>Metric / Attribute</th>
                    {comparison.alternatives.map((alt) => (
                      <th key={alt.id} style={{ color: '#ffffff', fontSize: '0.9rem' }}>
                        {alt.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Feasibility (1-5)</td>
                    {comparison.alternatives.map((alt) => (
                      <td key={alt.id}>
                        <strong style={{ color: '#60a5fa', fontSize: '1.05rem' }}>
                          {alt.feasibility_score} / 5
                        </strong>
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Risk Level</td>
                    {comparison.alternatives.map((alt) => (
                      <td key={alt.id}>
                        <RiskBadge risk={alt.risk_level} />
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Estimated Cost</td>
                    {comparison.alternatives.map((alt) => (
                      <td key={alt.id}>${Number(alt.estimated_cost).toLocaleString()}</td>
                    ))}
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Pros</td>
                    {comparison.alternatives.map((alt) => (
                      <td key={alt.id} style={{ color: '#34d399', fontSize: '0.85rem' }}>
                        {alt.pros || '-'}
                      </td>
                    ))}
                  </tr>
                  <tr>
                    <td style={{ fontWeight: 600 }}>Cons</td>
                    {comparison.alternatives.map((alt) => (
                      <td key={alt.id} style={{ color: '#fb7185', fontSize: '0.85rem' }}>
                        {alt.cons || '-'}
                      </td>
                    ))}
                  </tr>
                </tbody>
              </table>
            </div>

            {comparison.recommendation && (
              <div
                style={{
                  marginTop: '1.25rem',
                  padding: '1rem',
                  background: 'rgba(59, 130, 246, 0.1)',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                }}
              >
                <span style={{ fontWeight: 700, color: '#60a5fa' }}>Analytical Recommendation: </span>
                <span style={{ color: 'var(--text-secondary)' }}>{comparison.recommendation}</span>
              </div>
            )}
          </div>
        ) : (
          <p>No comparison data available.</p>
        )}
      </Modal>

      {/* MODAL: SUBMIT FOR APPROVAL */}
      <Modal
        isOpen={showSubmitApprovalModal}
        onClose={() => setShowSubmitApprovalModal(false)}
        title="Submit Decision for Formal Review"
      >
        <form onSubmit={handleSubmitApproval}>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1rem' }}>
            Routing this decision will update its status to <strong>Under Review</strong> and notify the assigned reviewer.
          </p>

          <Select
            label="Assign Reviewer"
            value={selectedReviewerId}
            onChange={(e) => setSelectedReviewerId(e.target.value)}
            options={reviewersList.map((r) => ({
              value: r.id,
              label: `${r.full_name} (${r.role} - ${r.department || 'General'})`,
            }))}
            required
          />

          <TextArea
            label="Submission Message & Instructions"
            placeholder="Specify what aspects require particular attention..."
            rows={3}
            value={approvalComments}
            onChange={(e) => setApprovalComments(e.target.value)}
          />

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <Button variant="secondary" onClick={() => setShowSubmitApprovalModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" loading={processingAction} icon={Send}>
              Submit for Review
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: EDIT RATIONALE */}
      <Modal
        isOpen={showRationaleModal}
        onClose={() => setShowRationaleModal(false)}
        title="Update Decision Rationale"
      >
        <div>
          <TextArea
            label="Architectural Rationale"
            rows={5}
            value={editRationale}
            onChange={(e) => setEditRationale(e.target.value)}
            placeholder="Document why this choice was selected over other alternatives..."
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
            <Button variant="secondary" onClick={() => setShowRationaleModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSaveRationale}>
              Save Rationale
            </Button>
          </div>
        </div>
      </Modal>

      {/* MODAL: NEW DISCUSSION THREAD */}
      <Modal
        isOpen={showNewThreadModal}
        onClose={() => setShowNewThreadModal(false)}
        title="Start Discussion Thread"
      >
        <form onSubmit={handleCreateThread}>
          <Input
            label="Thread Topic / Title"
            placeholder="e.g. Clarification on ZooKeeper quorum requirements"
            value={newThreadTitle}
            onChange={(e) => setNewThreadTitle(e.target.value)}
            required
          />
          <TextArea
            label="Topic Details"
            rows={3}
            value={newThreadDesc}
            onChange={(e) => setNewThreadDesc(e.target.value)}
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
            <Button variant="secondary" onClick={() => setShowNewThreadModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Create Thread
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: NEW MEETING NOTE */}
      <Modal
        isOpen={showNewNoteModal}
        onClose={() => setShowNewNoteModal(false)}
        title="Record Architecture Meeting Note"
      >
        <form
          onSubmit={async (e) => {
            e.preventDefault();
            if (!newNoteTitle.trim() || !newNoteContent.trim()) return;
            try {
              await discussionService.createMeetingNote(decisionId, {
                title: newNoteTitle.trim(),
                content: newNoteContent.trim(),
              });
              setNewNoteTitle('');
              setNewNoteContent('');
              setShowNewNoteModal(false);
              success('Meeting note recorded!');
              const updatedNotes = await discussionService.getMeetingNotes(decisionId);
              setMeetingNotes(updatedNotes);
            } catch (err) {
              error(err.message || 'Failed to record note');
            }
          }}
        >
          <Input
            label="Meeting Subject / Title"
            placeholder="e.g. Architecture Review Board - Session 4"
            value={newNoteTitle}
            onChange={(e) => setNewNoteTitle(e.target.value)}
            required
          />
          <TextArea
            label="Minutes & Outcomes"
            rows={4}
            value={newNoteContent}
            onChange={(e) => setNewNoteContent(e.target.value)}
            required
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1rem' }}>
            <Button variant="secondary" onClick={() => setShowNewNoteModal(false)}>
              Cancel
            </Button>
            <Button type="submit" variant="primary">
              Save Meeting Note
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: EDIT DECISION */}
      <Modal
        isOpen={showEditDecisionModal}
        onClose={() => setShowEditDecisionModal(false)}
        title="Edit Decision Details"
      >
        <form onSubmit={handleSaveEditDecision}>
          <Input
            label="Decision Title"
            value={editDecisionForm.title}
            onChange={(e) => setEditDecisionForm({ ...editDecisionForm, title: e.target.value })}
            required
          />
          <Input
            label="Category"
            value={editDecisionForm.category}
            onChange={(e) => setEditDecisionForm({ ...editDecisionForm, category: e.target.value })}
          />
          <TextArea
            label="Problem Statement"
            rows={5}
            value={editDecisionForm.problem_statement}
            onChange={(e) => setEditDecisionForm({ ...editDecisionForm, problem_statement: e.target.value })}
            required
          />
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <Button variant="secondary" onClick={() => setShowEditDecisionModal(false)} disabled={processingAction}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={processingAction}>
              {processingAction ? 'Saving...' : 'Update Decision'}
            </Button>
          </div>
        </form>
      </Modal>

      {/* MODAL: EDIT ALTERNATIVE */}
      <Modal
        isOpen={showEditAltModal}
        onClose={() => setShowEditAltModal(false)}
        title={`Edit Alternative: ${editingAlt?.name || ''}`}
      >
        <form onSubmit={handleSaveEditAlt}>
          <Input
            label="Alternative Name"
            value={editAltForm.name}
            onChange={(e) => setEditAltForm({ ...editAltForm, name: e.target.value })}
            required
          />
          <TextArea
            label="Description / Architecture Specs"
            rows={3}
            value={editAltForm.description}
            onChange={(e) => setEditAltForm({ ...editAltForm, description: e.target.value })}
          />
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <TextArea
              label="Pros / Advantages"
              rows={2}
              value={editAltForm.pros}
              onChange={(e) => setEditAltForm({ ...editAltForm, pros: e.target.value })}
            />
            <TextArea
              label="Cons / Trade-offs"
              rows={2}
              value={editAltForm.cons}
              onChange={(e) => setEditAltForm({ ...editAltForm, cons: e.target.value })}
            />
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginTop: '0.75rem' }}>
            <Input
              label="Estimated Cost ($)"
              type="number"
              min="0"
              value={editAltForm.estimated_cost}
              onChange={(e) => setEditAltForm({ ...editAltForm, estimated_cost: e.target.value })}
            />
            <Select
              label="Feasibility (1-5)"
              value={editAltForm.feasibility_score}
              onChange={(e) => setEditAltForm({ ...editAltForm, feasibility_score: e.target.value })}
              options={[
                { value: 1, label: '1 - Very Low' },
                { value: 2, label: '2 - Low' },
                { value: 3, label: '3 - Moderate' },
                { value: 4, label: '4 - High' },
                { value: 5, label: '5 - Exceptional' },
              ]}
            />
            <Select
              label="Risk Level"
              value={editAltForm.risk_level}
              onChange={(e) => setEditAltForm({ ...editAltForm, risk_level: e.target.value })}
              options={[
                { value: 'Low', label: 'Low' },
                { value: 'Medium', label: 'Medium' },
                { value: 'High', label: 'High' },
              ]}
            />
          </div>
          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem', marginTop: '1.25rem' }}>
            <Button variant="secondary" onClick={() => setShowEditAltModal(false)} disabled={processingAction}>
              Cancel
            </Button>
            <Button type="submit" variant="primary" disabled={processingAction}>
              {processingAction ? 'Saving...' : 'Update Alternative'}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
};
