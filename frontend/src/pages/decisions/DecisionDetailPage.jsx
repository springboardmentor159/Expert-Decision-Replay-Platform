import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { decisionService } from '../../services/decisionService';
import { alternativeService } from '../../services/alternativeService';
import { discussionService } from '../../services/discussionService';
import { approvalService } from '../../services/approvalService';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../components/common/Toast';
import { StatusBadge, RiskBadge } from '../../components/common/StatusBadge';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';
import { EmptyState } from '../../components/common/EmptyState';
import { AlternativeModal } from '../../components/decisions/AlternativeModal';
import { CompareModal } from '../../components/decisions/CompareModal';
import { SubmitApprovalModal } from '../../components/decisions/SubmitApprovalModal';
import {
  FileText,
  ArrowLeft,
  Edit,
  Trash2,
  Send,
  PlusCircle,
  Columns3,
  MessageSquare,
  FileSpreadsheet,
  CheckCircle2,
  XCircle,
  Clock,
  History,
  User,
  Star,
  DollarSign,
  AlertTriangle,
  Calendar,
  Layers,
  Sparkles,
} from 'lucide-react';

export const DecisionDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user, isAdmin, isManager, isReviewer } = useAuth();
  const { addToast } = useToast();

  const [decision, setDecision] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [threads, setThreads] = useState([]);
  const [meetingNotes, setMeetingNotes] = useState([]);
  const [approvals, setApprovals] = useState([]);
  const [timelineEvents, setTimelineEvents] = useState([]);
  const [versions, setVersions] = useState([]);

  const [activeTab, setActiveTab] = useState('overview');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Modals state
  const [isAltModalOpen, setIsAltModalOpen] = useState(false);
  const [editingAlternative, setEditingAlternative] = useState(null);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);
  const [isSubmitModalOpen, setIsSubmitModalOpen] = useState(false);

  // Thread creation state
  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadContent, setNewThreadContent] = useState('');
  const [isCreatingThread, setIsCreatingThread] = useState(false);

  // Active expanded thread for comments
  const [expandedThreadId, setExpandedThreadId] = useState(null);
  const [threadComments, setThreadComments] = useState({});
  const [replyText, setReplyText] = useState({});

  // Meeting notes state
  const [isAddingNote, setIsAddingNote] = useState(false);
  const [noteForm, setNoteForm] = useState({ title: '', attendees: '', notes: '', action_items: '' });

  // Approval review action state (Approve / Reject)
  const [reviewComments, setReviewComments] = useState('');
  const [isProcessingAction, setIsProcessingAction] = useState(false);

  // Fetch complete decision details
  const fetchAllData = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const [decData, altsData, threadsData, notesData, apprvData, timelineData, versData] =
        await Promise.all([
          decisionService.getDecisionById(id),
          alternativeService.getAlternatives(id),
          discussionService.getThreads(id),
          discussionService.getMeetingNotes(id),
          approvalService.getDecisionApprovals(id),
          decisionService.getTimeline(id),
          decisionService.getVersions(id),
        ]);

      setDecision(decData);
      setAlternatives(altsData);
      setThreads(threadsData);
      setMeetingNotes(notesData);
      setApprovals(apprvData);
      setTimelineEvents(timelineData.events || []);
      setVersions(versData);
    } catch (err) {
      setError(err.userMessage || 'Failed to load decision details');
    } finally {
      setIsLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Load thread comments when expanding thread
  const toggleThread = async (threadId) => {
    if (expandedThreadId === threadId) {
      setExpandedThreadId(null);
      return;
    }
    setExpandedThreadId(threadId);
    try {
      const comments = await discussionService.getThreadComments(threadId);
      setThreadComments((prev) => ({ ...prev, [threadId]: comments }));
    } catch (err) {
      console.error('Failed to load comments:', err);
    }
  };

  const handlePostReply = async (threadId) => {
    const text = replyText[threadId];
    if (!text || !text.trim()) return;

    try {
      await discussionService.addThreadComment(threadId, { comment: text.trim() });
      setReplyText((prev) => ({ ...prev, [threadId]: '' }));
      const updatedComments = await discussionService.getThreadComments(threadId);
      setThreadComments((prev) => ({ ...prev, [threadId]: updatedComments }));
      addToast('Reply added', 'success');
    } catch (err) {
      addToast(err.userMessage || 'Failed to add reply', 'error');
    }
  };

  const handleCreateThread = async (e) => {
    e.preventDefault();
    if (!newThreadTitle.trim() || !newThreadContent.trim()) return;

    try {
      await discussionService.createThread(id, {
        title: newThreadTitle.trim(),
        initial_comment: newThreadContent.trim(),
      });
      setNewThreadTitle('');
      setNewThreadContent('');
      setIsCreatingThread(false);
      const updatedThreads = await discussionService.getThreads(id);
      setThreads(updatedThreads);
      addToast('Discussion thread started', 'success');
    } catch (err) {
      addToast(err.userMessage || 'Failed to start thread', 'error');
    }
  };

  const handleCreateNote = async (e) => {
    e.preventDefault();
    if (!noteForm.title.trim() || !noteForm.notes.trim()) return;

    try {
      await discussionService.createMeetingNote(id, {
        title: noteForm.title.trim(),
        meeting_date: new Date().toISOString(),
        attendees: noteForm.attendees.trim() || undefined,
        key_points: noteForm.notes.trim(),
        action_items: noteForm.action_items.trim() || undefined,
      });
      setNoteForm({ title: '', attendees: '', notes: '', action_items: '' });
      setIsAddingNote(false);
      const updatedNotes = await discussionService.getMeetingNotes(id);
      setMeetingNotes(updatedNotes);
      addToast('Meeting note added', 'success');
    } catch (err) {
      addToast(err.userMessage || 'Failed to add meeting note', 'error');
    }
  };

  const handleDeleteAlternative = async (altId, altName) => {
    if (!window.confirm(`Delete alternative "${altName}"?`)) return;
    try {
      await alternativeService.deleteAlternative(altId);
      addToast('Alternative removed', 'success');
      const updated = await alternativeService.getAlternatives(id);
      setAlternatives(updated);
    } catch (err) {
      addToast(err.userMessage || 'Failed to delete alternative', 'error');
    }
  };

  // Process Approve or Reject
  const handleApprovalAction = async (status) => {
    const pendingApproval = approvals.find((a) => a.status === 'Pending');
    if (!pendingApproval) return;

    setIsProcessingAction(true);
    try {
      await approvalService.processAction(pendingApproval.id, {
        status,
        comments: reviewComments.trim() || undefined,
      });
      addToast(`Decision has been ${status.toLowerCase()}!`, status === 'Approved' ? 'success' : 'info');
      setReviewComments('');
      await fetchAllData();
    } catch (err) {
      addToast(err.userMessage || `Failed to ${status.toLowerCase()} decision`, 'error');
    } finally {
      setIsProcessingAction(false);
    }
  };

  if (isLoading) return <LoadingSpinner message="Loading decision workspace..." />;

  if (error || !decision) {
    return (
      <div style={{ margin: '2rem' }}>
        <div className="alert alert-error">
          <span>{error || 'Decision not found.'}</span>
        </div>
        <Link to="/decisions" className="btn btn-secondary">
          <ArrowLeft size={16} /> Back to Decisions
        </Link>
      </div>
    );
  }

  // Permissions
  const isOwner = decision.created_by === user?.id;
  const canEdit = isOwner || isAdmin || isManager;
  const canSubmit = (decision.status === 'Draft' || decision.status === 'Rejected') && canEdit;

  // Check if current user is the assigned reviewer or manager/admin for pending approval
  const pendingApproval = approvals.find((a) => a.status === 'Pending');
  const isAssignedReviewer = pendingApproval && (pendingApproval.reviewer_id === user?.id || isAdmin || isManager);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.75rem' }}>
      {/* Top Breadcrumb & Actions Bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '1rem',
        }}
      >
        <div>
          <Link
            to="/decisions"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '0.85rem',
              color: 'var(--text-muted)',
              marginBottom: '0.5rem',
            }}
          >
            <ArrowLeft size={16} /> Back to Decision Repository
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <h1 style={{ fontSize: '1.75rem', color: 'var(--text-primary)', fontWeight: 800 }}>{decision.title}</h1>
            <StatusBadge status={decision.status} />
            <span className="badge badge-category">{decision.category}</span>
          </div>
          <p className="text-muted" style={{ fontSize: '0.85rem', marginTop: '0.35rem' }}>
            Decision ID: <span className="font-mono">#{decision.id}</span> • Created on{' '}
            {new Date(decision.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Header Action Buttons */}
        <div style={{ display: 'flex', gap: '0.65rem', flexWrap: 'wrap' }}>
          {canSubmit && (
            <button id="btn-open-submit-approval" className="btn btn-primary" onClick={() => setIsSubmitModalOpen(true)}>
              <Send size={16} />
              <span>Submit for Review</span>
            </button>
          )}

          {canEdit && (
            <Link to={`/decisions/${id}/edit`} id="btn-edit-decision" className="btn btn-secondary">
              <Edit size={16} />
              <span>Edit</span>
            </Link>
          )}

          <button id="btn-open-compare" className="btn btn-secondary" onClick={() => setIsCompareModalOpen(true)}>
            <Columns3 size={16} />
            <span>Compare Alternatives</span>
          </button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="tabs-container">
        <button
          id="tab-overview"
          className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          <FileText size={16} /> Overview
        </button>

        <button
          id="tab-alternatives"
          className={`tab-btn ${activeTab === 'alternatives' ? 'active' : ''}`}
          onClick={() => setActiveTab('alternatives')}
        >
          <Columns3 size={16} /> Alternatives ({alternatives.length})
        </button>

        <button
          id="tab-discussions"
          className={`tab-btn ${activeTab === 'discussions' ? 'active' : ''}`}
          onClick={() => setActiveTab('discussions')}
        >
          <MessageSquare size={16} /> Discussions & Notes ({threads.length + meetingNotes.length})
        </button>

        <button
          id="tab-approvals"
          className={`tab-btn ${activeTab === 'approvals' ? 'active' : ''}`}
          onClick={() => setActiveTab('approvals')}
        >
          <CheckCircle2 size={16} /> Approvals ({approvals.length})
        </button>

        <button
          id="tab-history"
          className={`tab-btn ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <History size={16} /> Timeline & History ({versions.length} versions)
        </button>
      </div>

      {/* TAB 1: OVERVIEW */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Problem Statement & Background</h3>
              </div>
              <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                {decision.problem_statement}
              </p>
            </div>

            {decision.rationale && (
              <div className="card">
                <div className="card-header">
                  <h3 className="card-title">Evaluation Criteria, Objectives & Rationale</h3>
                </div>
                <p style={{ fontSize: '0.95rem', color: 'var(--text-secondary)', lineHeight: 1.7, whiteSpace: 'pre-wrap' }}>
                  {decision.rationale}
                </p>
              </div>
            )}
          </div>

          {/* Sidebar Metadata Card */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Decision Metadata</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
                <div>
                  <span className="text-dim" style={{ fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    Current State
                  </span>
                  <div style={{ marginTop: '4px' }}>
                    <StatusBadge status={decision.status} />
                  </div>
                </div>

                <div>
                  <span className="text-dim" style={{ fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    Domain Category
                  </span>
                  <div style={{ marginTop: '4px', fontWeight: 600 }}>{decision.category}</div>
                </div>

                <div>
                  <span className="text-dim" style={{ fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    Created By
                  </span>
                  <div style={{ marginTop: '4px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <User size={15} color="var(--primary-light)" />
                    <span>User #{decision.created_by}</span>
                  </div>
                </div>

                <div>
                  <span className="text-dim" style={{ fontSize: '0.78rem', textTransform: 'uppercase' }}>
                    Last Updated
                  </span>
                  <div style={{ marginTop: '4px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                    {new Date(decision.updated_at || decision.created_at).toLocaleString()}
                  </div>
                </div>

                {decision.tags && decision.tags.length > 0 && (
                  <div>
                    <span className="text-dim" style={{ fontSize: '0.78rem', textTransform: 'uppercase' }}>
                      Repository Tags
                    </span>
                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                      {decision.tags.map((tag, i) => (
                        <span key={i} className="badge badge-category">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB 2: ALTERNATIVES */}
      {activeTab === 'alternatives' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <p className="text-muted" style={{ fontSize: '0.9rem' }}>
              Add, score, and evaluate competing options before issuing a recommendation.
            </p>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              {alternatives.length > 1 && (
                <button className="btn btn-secondary btn-sm" onClick={() => setIsCompareModalOpen(true)}>
                  <Columns3 size={15} /> Compare Side-by-Side
                </button>
              )}
              {canEdit && (
                <button
                  id="btn-open-add-alternative"
                  className="btn btn-primary btn-sm"
                  onClick={() => {
                    setEditingAlternative(null);
                    setIsAltModalOpen(true);
                  }}
                >
                  <PlusCircle size={15} /> Add Alternative
                </button>
              )}
            </div>
          </div>

          {alternatives.length === 0 ? (
            <EmptyState
              title="No alternatives added yet"
              description="Propose alternative solutions, evaluate feasibility scores (1-5), and analyze cost & risk."
              actionText={canEdit ? 'Add Alternative' : undefined}
              onAction={
                canEdit
                  ? () => {
                      setEditingAlternative(null);
                      setIsAltModalOpen(true);
                    }
                  : undefined
              }
            />
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
                gap: '1.25rem',
              }}
            >
              {alternatives.map((alt) => (
                <div key={alt.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h4 style={{ fontSize: '1.1rem', color: 'var(--text-primary)' }}>{alt.name}</h4>
                    <RiskBadge risk={alt.risk_level} />
                  </div>

                  <p className="text-muted" style={{ fontSize: '0.85rem', margin: '0.75rem 0', flexGrow: 1 }}>
                    {alt.description}
                  </p>

                  <div
                    style={{
                      background: 'var(--bg-elevated)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '0.75rem 1rem',
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginBottom: '1rem',
                    }}
                  >
                    <div>
                      <span className="text-dim" style={{ fontSize: '0.75rem' }}>Feasibility</span>
                      <div style={{ fontWeight: 700, display: 'flex', alignItems: 'center', gap: '3px' }}>
                        <Star size={14} fill="#fbbf24" color="#fbbf24" />
                        {alt.feasibility_score} / 5
                      </div>
                    </div>
                    <div>
                      <span className="text-dim" style={{ fontSize: '0.75rem' }}>Estimated Cost</span>
                      <div style={{ fontWeight: 700, color: '#047857', fontFamily: 'var(--font-mono)' }}>
                        ${Number(alt.estimated_cost || 0).toLocaleString()}
                      </div>
                    </div>
                  </div>

                  {/* Pros & Cons summary */}
                  {alt.pros && (
                    <div style={{ fontSize: '0.8rem', color: '#065f46', marginBottom: '0.5rem' }}>
                      <strong>Pros:</strong> {alt.pros}
                    </div>
                  )}
                  {alt.cons && (
                    <div style={{ fontSize: '0.8rem', color: '#991b1b', marginBottom: '1rem' }}>
                      <strong>Cons:</strong> {alt.cons}
                    </div>
                  )}

                  {canEdit && (
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'flex-end',
                        gap: '0.5rem',
                        paddingTop: '0.75rem',
                        borderTop: '1px solid var(--border-subtle)',
                      }}
                    >
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => {
                          setEditingAlternative(alt);
                          setIsAltModalOpen(true);
                        }}
                      >
                        <Edit size={14} /> Edit
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => handleDeleteAlternative(alt.id, alt.name)}
                        style={{ color: '#f87171' }}
                      >
                        <Trash2 size={14} /> Delete
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* TAB 3: DISCUSSIONS & MEETING NOTES */}
      {activeTab === 'discussions' && (
        <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
          {/* Discussion Threads */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', fontWeight: 700 }}>Discussion Threads</h3>
              <button
                className="btn btn-primary btn-sm"
                onClick={() => setIsCreatingThread(!isCreatingThread)}
              >
                <PlusCircle size={15} /> {isCreatingThread ? 'Cancel' : 'Start Thread'}
              </button>
            </div>

            {/* Create Thread Form */}
            {isCreatingThread && (
              <div className="card" style={{ border: '1px solid var(--primary)' }}>
                <form onSubmit={handleCreateThread}>
                  <div className="form-group">
                    <label className="form-label form-label-required">Thread Topic</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g., Performance benchmarks between Option A and Option B"
                      value={newThreadTitle}
                      onChange={(e) => setNewThreadTitle(e.target.value)}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label form-label-required">Initial Comment</label>
                    <textarea
                      className="form-textarea"
                      placeholder="Share questions, preliminary data, or observations..."
                      value={newThreadContent}
                      onChange={(e) => setNewThreadContent(e.target.value)}
                      rows={3}
                      required
                    />
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                    <button
                      type="button"
                      className="btn btn-secondary btn-sm"
                      onClick={() => setIsCreatingThread(false)}
                    >
                      Cancel
                    </button>
                    <button type="submit" className="btn btn-primary btn-sm">
                      Post Thread
                    </button>
                  </div>
                </form>
              </div>
            )}

            {threads.length === 0 ? (
              <EmptyState
                icon={MessageSquare}
                title="No discussions yet"
                description="Start a discussion thread to gather feedback from architects and engineers."
              />
            ) : (
              threads.map((thread) => (
                <div key={thread.id} className="card">
                  <div
                    style={{ display: 'flex', justifyContent: 'space-between', cursor: 'pointer' }}
                    onClick={() => toggleThread(thread.id)}
                  >
                    <div>
                      <h4 style={{ fontSize: '1.05rem', color: 'var(--text-primary)' }}>{thread.title}</h4>
                      <p className="text-dim" style={{ fontSize: '0.78rem', marginTop: '2px' }}>
                        Created by {thread.creator?.full_name || 'Team Member'} on{' '}
                        {new Date(thread.created_at).toLocaleDateString()}
                      </p>
                    </div>
                    <button className="btn btn-secondary btn-sm">
                      {expandedThreadId === thread.id ? 'Hide Replies' : 'View Replies'}
                    </button>
                  </div>

                  {/* Expanded Thread Replies */}
                  {expandedThreadId === thread.id && (
                    <div
                      style={{
                        marginTop: '1.25rem',
                        paddingTop: '1rem',
                        borderTop: '1px solid var(--border-subtle)',
                      }}
                    >
                      {/* Comments List */}
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1rem' }}>
                        {(threadComments[thread.id] || []).map((c) => (
                          <div
                            key={c.id}
                            style={{
                              background: 'var(--bg-elevated)',
                              padding: '0.75rem 1rem',
                              borderRadius: 'var(--radius-sm)',
                              border: '1px solid var(--border-subtle)',
                            }}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--primary-light)' }}>
                                {c.user?.full_name || 'Team Member'}
                              </span>
                              <span className="text-dim" style={{ fontSize: '0.72rem' }}>
                                {new Date(c.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>{c.comment}</p>
                          </div>
                        ))}
                      </div>

                      {/* Reply Input */}
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <input
                          type="text"
                          className="form-input"
                          placeholder="Type your reply..."
                          value={replyText[thread.id] || ''}
                          onChange={(e) =>
                            setReplyText({ ...replyText, [thread.id]: e.target.value })
                          }
                          onKeyDown={(e) => {
                            if (e.key === 'Enter') handlePostReply(thread.id);
                          }}
                        />
                        <button
                          className="btn btn-primary btn-sm"
                          onClick={() => handlePostReply(thread.id)}
                        >
                          Reply
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          {/* Meeting Notes */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', fontWeight: 700 }}>Meeting Notes</h3>
              <button
                className="btn btn-secondary btn-sm"
                onClick={() => setIsAddingNote(!isAddingNote)}
              >
                <PlusCircle size={15} /> {isAddingNote ? 'Cancel' : 'Add Note'}
              </button>
            </div>

            {isAddingNote && (
              <div className="card" style={{ border: '1px solid var(--primary)' }}>
                <form onSubmit={handleCreateNote}>
                  <div className="form-group">
                    <label className="form-label form-label-required">Meeting Title</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="e.g. Architecture Review Sync"
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
                      placeholder="Jane, John, Alex"
                      value={noteForm.attendees}
                      onChange={(e) => setNoteForm({ ...noteForm, attendees: e.target.value })}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label form-label-required">Key Discussion Points</label>
                    <textarea
                      className="form-textarea"
                      placeholder="Summary of decisions, consensus reached..."
                      value={noteForm.notes}
                      onChange={(e) => setNoteForm({ ...noteForm, notes: e.target.value })}
                      rows={3}
                      required
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Action Items</label>
                    <input
                      type="text"
                      className="form-input"
                      placeholder="1. Benchmark latency; 2. Request quote"
                      value={noteForm.action_items}
                      onChange={(e) => setNoteForm({ ...noteForm, action_items: e.target.value })}
                    />
                  </div>
                  <button type="submit" className="btn btn-primary btn-sm" style={{ width: '100%' }}>
                    Save Note
                  </button>
                </form>
              </div>
            )}

            {meetingNotes.length === 0 ? (
              <p className="text-muted" style={{ fontSize: '0.88rem' }}>
                No meeting notes recorded for this decision.
              </p>
            ) : (
              meetingNotes.map((note) => (
                <div key={note.id} className="card" style={{ padding: '1.25rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <h4 style={{ fontSize: '0.98rem', color: 'var(--text-primary)' }}>{note.title}</h4>
                    <span className="text-dim" style={{ fontSize: '0.75rem' }}>
                      {new Date(note.meeting_date).toLocaleDateString()}
                    </span>
                  </div>
                  {note.attendees && (
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>
                      <strong>Attendees:</strong> {note.attendees}
                    </div>
                  )}
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
                    {note.key_points}
                  </p>
                  {note.action_items && (
                    <div
                      style={{
                        marginTop: '0.5rem',
                        fontSize: '0.8rem',
                        background: 'var(--bg-elevated)',
                        padding: '0.4rem 0.65rem',
                        borderRadius: 'var(--radius-xs)',
                        color: 'var(--accent-cyan)',
                      }}
                    >
                      <strong>Action Items:</strong> {note.action_items}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      )}

      {/* TAB 4: APPROVAL WORKFLOW */}
      {activeTab === 'approvals' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {/* Approval Stepper Banner */}
          <div className="card" style={{ padding: '2rem' }}>
            <h3 style={{ fontSize: '1.15rem', color: 'var(--text-primary)', marginBottom: '1.5rem', fontWeight: 700 }}>
              Decision Approval Stepper
            </h3>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'relative' }}>
              {/* Step 1: Draft */}
              <div style={{ textAlign: 'center', zIndex: 2 }}>
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: '#10b981',
                    color: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 0.5rem',
                  }}
                >
                  <CheckCircle2 size={20} />
                </div>
                <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Draft Created</span>
              </div>

              {/* Connector line 1 */}
              <div
                style={{
                  flex: 1,
                  height: '2px',
                  background: decision.status !== 'Draft' ? '#10b981' : 'var(--border-default)',
                  margin: '0 1rem -1.2rem',
                }}
              ></div>

              {/* Step 2: Under Review */}
              <div style={{ textAlign: 'center', zIndex: 2 }}>
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background:
                      decision.status === 'Under Review'
                        ? '#f59e0b'
                        : decision.status === 'Approved'
                        ? '#10b981'
                        : decision.status === 'Rejected'
                        ? '#ef4444'
                        : '#f1f5f9',
                    color: decision.status === 'Draft' ? 'var(--text-dim)' : 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 0.5rem',
                    border: '2px solid var(--border-default)',
                  }}
                >
                  <Clock size={20} />
                </div>
                <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Under Review</span>
              </div>

              {/* Connector line 2 */}
              <div
                style={{
                  flex: 1,
                  height: '2px',
                  background:
                    decision.status === 'Approved'
                      ? '#10b981'
                      : decision.status === 'Rejected'
                      ? '#ef4444'
                      : 'var(--border-default)',
                  margin: '0 1rem -1.2rem',
                }}
              ></div>

              {/* Step 3: Resolution */}
              <div style={{ textAlign: 'center', zIndex: 2 }}>
                <div
                  style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background:
                      decision.status === 'Approved'
                        ? '#10b981'
                        : decision.status === 'Rejected'
                        ? '#ef4444'
                        : '#f1f5f9',
                    color: (decision.status === 'Approved' || decision.status === 'Rejected') ? 'white' : 'var(--text-dim)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 0.5rem',
                    border: '2px solid var(--border-default)',
                  }}
                >
                  {decision.status === 'Approved' ? (
                    <CheckCircle2 size={20} />
                  ) : decision.status === 'Rejected' ? (
                    <XCircle size={20} />
                  ) : (
                    <FileText size={20} />
                  )}
                </div>
                <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>
                  {decision.status === 'Approved'
                    ? 'Approved'
                    : decision.status === 'Rejected'
                    ? 'Rejected'
                    : 'Awaiting Resolution'}
                </span>
              </div>
            </div>
          </div>

          {/* Conditional Action Box: Reviewer Approve/Reject */}
          {pendingApproval && isAssignedReviewer && (
            <div
              className="card"
              style={{
                border: '2px solid var(--warning)',
                background: 'linear-gradient(145deg, var(--bg-card) 0%, rgba(245, 158, 11, 0.05) 100%)',
              }}
            >
              <h3 style={{ fontSize: '1.2rem', color: 'var(--text-primary)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <Clock size={22} color="var(--warning)" /> Reviewer Action Required
              </h3>
              <p className="text-muted" style={{ fontSize: '0.88rem', marginBottom: '1.25rem' }}>
                You are authorized to review this proposal. Please provide evaluation feedback before approving or rejecting.
              </p>

              <div className="form-group">
                <label className="form-label">Review Remarks / Justification</label>
                <textarea
                  id="textarea-review-comments"
                  className="form-textarea"
                  placeholder="State technical reasons, trade-offs evaluated, conditions of approval, or necessary improvements if rejecting..."
                  value={reviewComments}
                  onChange={(e) => setReviewComments(e.target.value)}
                  rows={3}
                />
              </div>

              <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
                <button
                  id="btn-reject-decision"
                  className="btn btn-danger"
                  onClick={() => handleApprovalAction('Rejected')}
                  disabled={isProcessingAction}
                >
                  <XCircle size={18} />
                  <span>Reject Decision</span>
                </button>
                <button
                  id="btn-approve-decision"
                  className="btn btn-success"
                  onClick={() => handleApprovalAction('Approved')}
                  disabled={isProcessingAction}
                >
                  <CheckCircle2 size={18} />
                  <span>Approve Decision</span>
                </button>
              </div>
            </div>
          )}

          {/* Approval History List */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Approval Audit Trail</h3>
            </div>

            {approvals.length === 0 ? (
              <EmptyState
                title="No approval history"
                description="This decision has not been submitted for review yet."
                actionText={canSubmit ? 'Submit for Review' : undefined}
                onAction={canSubmit ? () => setIsSubmitModalOpen(true) : undefined}
              />
            ) : (
              <div className="table-container" style={{ border: 'none' }}>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Status</th>
                      <th>Level</th>
                      <th>Reviewer</th>
                      <th>Submitted Date</th>
                      <th>Completed Date</th>
                      <th>Review Comments</th>
                    </tr>
                  </thead>
                  <tbody>
                    {approvals.map((apprv) => (
                      <tr key={apprv.id}>
                        <td>
                          <StatusBadge status={apprv.status} />
                        </td>
                        <td>Level {apprv.approval_level}</td>
                        <td>{apprv.reviewer_name || `Reviewer #${apprv.reviewer_id}`}</td>
                        <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                          {new Date(apprv.created_at).toLocaleString()}
                        </td>
                        <td style={{ fontSize: '0.82rem', color: 'var(--text-dim)' }}>
                          {apprv.completed_at ? new Date(apprv.completed_at).toLocaleString() : 'Pending'}
                        </td>
                        <td style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                          {apprv.comments || '—'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 5: TIMELINE & VERSION HISTORY */}
      {activeTab === 'history' && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
          {/* Visual Event Timeline */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Decision Event Timeline</h3>
            </div>
            {timelineEvents.length === 0 ? (
              <p className="text-muted" style={{ padding: '1rem' }}>No events recorded.</p>
            ) : (
              <div className="timeline">
                {timelineEvents.map((event, idx) => (
                  <div key={idx} className="timeline-item">
                    <div className="timeline-dot">
                      <div className="timeline-dot-inner"></div>
                    </div>
                    <div className="timeline-content">
                      <div className="timeline-meta">
                        <span className="timeline-title">{event.event_type.replace('_', ' ').toUpperCase()}</span>
                        <span className="timeline-time">
                          {new Date(event.timestamp).toLocaleString()}
                        </span>
                      </div>
                      <p className="timeline-desc">{event.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Version Snapshots */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Version History Snapshots</h3>
            </div>
            {versions.length === 0 ? (
              <p className="text-muted" style={{ padding: '1rem' }}>No version history recorded.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {versions.map((ver) => (
                  <div
                    key={ver.id}
                    style={{
                      background: 'var(--bg-elevated)',
                      border: '1px solid var(--border-subtle)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '1rem',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                      <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                        Version {ver.version_number}
                      </span>
                      <span className="text-dim" style={{ fontSize: '0.78rem' }}>
                        {new Date(ver.created_at).toLocaleString()}
                      </span>
                    </div>
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                      Status: <StatusBadge status={ver.status} /> • Author: {ver.created_by_name || `User #${ver.created_by}`}
                    </div>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '0.5rem' }}>
                      {ver.problem_statement}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Alternative Modal (Add / Edit) */}
      <AlternativeModal
        isOpen={isAltModalOpen}
        onClose={() => setIsAltModalOpen(false)}
        decisionId={id}
        alternative={editingAlternative}
        onSuccess={fetchAllData}
      />

      {/* Compare Side-by-Side Modal */}
      <CompareModal
        isOpen={isCompareModalOpen}
        onClose={() => setIsCompareModalOpen(false)}
        alternatives={alternatives}
      />

      {/* Submit for Review Modal */}
      <SubmitApprovalModal
        isOpen={isSubmitModalOpen}
        onClose={() => setIsSubmitModalOpen(false)}
        decisionId={decision.id}
        decisionTitle={decision.title}
        onSuccess={fetchAllData}
      />
    </div>
  );
};
