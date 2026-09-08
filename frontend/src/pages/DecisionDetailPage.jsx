import React, { useEffect, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ArrowLeft, Plus, Save, GitCompare, Pencil, MessageSquare, Upload, Download, Trash2 } from 'lucide-react';
import apiClient from '../api/client';
import { useAuth, UserRole } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';
import Alert from '../components/common/Alert';
import LoadingSpinner from '../components/common/LoadingSpinner';
import FormField from '../components/common/FormField';
import Input from '../components/common/Input';
import Select from '../components/common/Select';
import Textarea from '../components/common/Textarea';
import Table from '../components/common/Table';

const tabs = ['Overview', 'Alternatives', 'Discussion', 'Meeting Notes', 'Documents', 'History'];
const statuses = ['Draft', 'Under Review', 'Approved', 'Rejected', 'Archived'];

const dateText = (value) => (value ? new Date(value).toLocaleString() : 'Not recorded');

export const DecisionDetailPage = () => {
  const { decisionId } = useParams();
  const { user, hasRole } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();
  const [decision, setDecision] = useState(null);
  const [tab, setTab] = useState('Overview');
  const [related, setRelated] = useState({ alternatives: [], comments: [], threads: [], notes: [], history: [], compare: [], documents: [] });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [edit, setEdit] = useState({ title: '', problem_statement: '', category: '', rationale: '' });
  const [comment, setComment] = useState('');
  const [alternative, setAlternative] = useState({ name: '', description: '', pros: '', cons: '', estimated_cost: '', feasibility_score: 3, risk_level: 'Medium' });
  const [editingAlternative, setEditingAlternative] = useState(null);
  const [thread, setThread] = useState({ title: '', description: '' });
  const [threadReply, setThreadReply] = useState({});
  const [note, setNote] = useState({ title: '', content: '', meeting_date: '' });
  const canEdit = decision && (decision.created_by === user?.id || hasRole(UserRole.ADMINISTRATOR));

  const load = async () => {
    setLoading(true);
    try {
      const [decisionResponse, alternatives, compare, comments, threads, notes, history] = await Promise.all([
        apiClient.get(`/decisions/${decisionId}`),
        apiClient.get(`/decisions/${decisionId}/alternatives`),
        apiClient.get(`/decisions/${decisionId}/alternatives/compare`),
        apiClient.get(`/decisions/${decisionId}/comments`),
        apiClient.get(`/decisions/${decisionId}/threads`),
        apiClient.get(`/decisions/${decisionId}/meeting-notes`),
          apiClient.get(`/decisions/${decisionId}/documents`).catch(() => ({ data: [] })),
        apiClient.get(`/decisions/${decisionId}/history`),
      ]);
      const record = decisionResponse.data;
      setDecision(record);
      setEdit({ title: record.title || '', problem_statement: record.problem_statement || '', category: record.category || '', rationale: record.rationale || '' });
      setRelated({ alternatives: alternatives.data || [], compare: compare.data?.alternatives || [], comments: comments.data || [], threads: threads.data || [], notes: notes.data || [], documents: documents.data || [], history: history.data?.items || [] });
    } catch (error) {
      toast.error(error.formattedMessage || 'Unable to load this decision');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(); }, [decisionId]);

  const saveDecision = async (event) => {
    event.preventDefault();
    setSaving(true);
    try {
      const response = await apiClient.put(`/decisions/${decisionId}`, {
        title: edit.title,
        problem_statement: edit.problem_statement,
        category: edit.category,
      });
      if (edit.rationale !== (decision.rationale || '')) await apiClient.put(`/decisions/${decisionId}/rationale`, { rationale: edit.rationale });
      setDecision(response.data);
      toast.success('Decision details saved');
    } catch (error) {
      toast.error(error.formattedMessage || 'Unable to save decision');
    } finally { setSaving(false); }
  };

  const changeStatus = async (event) => {
    try {
      const response = await apiClient.patch(`/decisions/${decisionId}/status`, { status: event.target.value });
      setDecision(response.data);
      toast.success(`Status changed to ${event.target.value}`);
    } catch (error) { toast.error(error.formattedMessage || 'Unable to change status'); }
  };

  const addComment = async (event) => {
    event.preventDefault();
    if (!comment.trim()) return;
    try { await apiClient.post(`/decisions/${decisionId}/comments`, { content: comment }); setComment(''); await load(); toast.success('Comment added'); }
    catch (error) { toast.error(error.formattedMessage || 'Unable to add comment'); }
  };

  const addAlternative = async (event) => {
    event.preventDefault();
    if (!alternative.name.trim()) return;
    try {
      const payload = { ...alternative, estimated_cost: alternative.estimated_cost ? Number(alternative.estimated_cost) : null, feasibility_score: Number(alternative.feasibility_score) };
      if (editingAlternative) await apiClient.put(`/alternatives/${editingAlternative.id}`, payload);
      else await apiClient.post(`/decisions/${decisionId}/alternatives`, payload);
      setAlternative({ name: '', description: '', pros: '', cons: '', estimated_cost: '', feasibility_score: 3, risk_level: 'Medium' }); setEditingAlternative(null); await load(); toast.success(editingAlternative ? 'Alternative updated' : 'Alternative added');
    }
    catch (error) { toast.error(error.formattedMessage || 'Unable to add alternative'); }
  };

  const addThread = async (event) => {
    event.preventDefault();
    if (!thread.title.trim()) return;
    try { await apiClient.post(`/decisions/${decisionId}/threads`, thread); setThread({ title: '', description: '' }); await load(); toast.success('Discussion thread created'); }
    catch (error) { toast.error(error.formattedMessage || 'Unable to create thread'); }
  };

  const replyToThread = async (event, threadId) => {
    event.preventDefault();
    if (!threadReply[threadId]?.trim()) return;
    try { await apiClient.post(`/threads/${threadId}/comments`, { content: threadReply[threadId] }); setThreadReply({ ...threadReply, [threadId]: '' }); await load(); toast.success('Reply added'); }
    catch (error) { toast.error(error.formattedMessage || 'Unable to add reply'); }
  };

  const addNote = async (event) => {
    event.preventDefault();
    if (!note.title.trim() || !note.content.trim() || !note.meeting_date) return;
    try { await apiClient.post(`/decisions/${decisionId}/meeting-notes`, { ...note, meeting_date: new Date(note.meeting_date).toISOString() }); setNote({ title: '', content: '', meeting_date: '' }); await load(); toast.success('Meeting note added'); }
    catch (error) { toast.error(error.formattedMessage || 'Unable to add meeting note'); }
  };

  const uploadDocument = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    try {
      await apiClient.post(`/decisions/${decisionId}/documents`, formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      await load();
      toast.success('Document uploaded');
    } catch (error) { toast.error(error.formattedMessage || 'Unable to upload document'); }
  };

  const deleteDocument = async (documentId) => {
    try {
      await apiClient.delete(`/decisions/documents/${documentId}`);
      setRelated((current) => ({ ...current, documents: current.documents.filter((item) => item.id !== documentId) }));
      toast.success('Document deleted');
    } catch (error) { toast.error(error.formattedMessage || 'Unable to delete document'); }
  };

  const downloadDocument = async (document) => {
    try {
      const response = await apiClient.get(document.download_url, { responseType: 'blob' });
      const url = URL.createObjectURL(response.data);
      const anchor = window.document.createElement('a');
      anchor.href = url;
      anchor.download = document.filename;
      anchor.click();
      URL.revokeObjectURL(url);
    } catch (error) { toast.error(error.formattedMessage || 'Unable to download document'); }
  };

  if (loading) return <LoadingSpinner size="large" text="Loading decision..." />;
  if (!decision) return <Alert type="error" title="Decision unavailable">The requested decision could not be loaded.</Alert>;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <Link to="/decisions" style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '14px' }}><ArrowLeft size={16} /> Back to decisions</Link>
      <div className="apple-card" style={{ display: 'flex', justifyContent: 'space-between', gap: '16px', flexWrap: 'wrap' }}>
        <div><Badge variant={decision.status}>{decision.status}</Badge><h1 style={{ marginTop: '10px', fontSize: '28px' }}>{decision.title}</h1><p style={{ color: 'var(--color-ink-muted-48)', marginTop: '6px' }}>{decision.category} · Updated {dateText(decision.updated_at)}</p></div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}><Select value={decision.status} options={statuses} onChange={changeStatus} /><Button variant="pearl" icon={Save} onClick={saveDecision} loading={saving}>Save</Button></div>
      </div>
      <div role="tablist" style={{ display: 'flex', gap: '6px', overflowX: 'auto', borderBottom: '1px solid var(--color-hairline)' }}>{tabs.map((item) => <button key={item} role="tab" aria-selected={tab === item} onClick={() => setTab(item)} style={{ padding: '10px 14px', color: tab === item ? 'var(--color-primary)' : 'var(--color-ink-muted-48)', borderBottom: tab === item ? '2px solid var(--color-primary)' : '2px solid transparent', whiteSpace: 'nowrap' }}>{item}</button>)}</div>

      {tab === 'Overview' && <form className="apple-card" onSubmit={saveDecision} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <FormField label="Title"><Input value={edit.title} onChange={(event) => setEdit({ ...edit, title: event.target.value })} disabled={!canEdit} /></FormField>
        <FormField label="Category"><Input value={edit.category} onChange={(event) => setEdit({ ...edit, category: event.target.value })} disabled={!canEdit} /></FormField>
        <FormField label="Problem statement"><Textarea rows={5} value={edit.problem_statement} onChange={(event) => setEdit({ ...edit, problem_statement: event.target.value })} disabled={!canEdit} /></FormField>
        <FormField label="Rationale"><Textarea rows={4} value={edit.rationale} onChange={(event) => setEdit({ ...edit, rationale: event.target.value })} disabled={!canEdit} /></FormField>
        {canEdit && <Button type="submit" variant="primary" icon={Save} loading={saving}>Save changes</Button>}
      </form>}

      {tab === 'Alternatives' && <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}><form className="apple-card" onSubmit={addAlternative} style={{ display: 'grid', gap: '12px' }}><h2>{editingAlternative ? 'Edit alternative' : 'Add alternative'}</h2><Input placeholder="Alternative name" value={alternative.name} onChange={(event) => setAlternative({ ...alternative, name: event.target.value })} /><Textarea placeholder="Description" rows={3} value={alternative.description} onChange={(event) => setAlternative({ ...alternative, description: event.target.value })} /><div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, minmax(0, 1fr))', gap: '12px' }}><Input placeholder="Pros" value={alternative.pros} onChange={(event) => setAlternative({ ...alternative, pros: event.target.value })} /><Input placeholder="Cons" value={alternative.cons} onChange={(event) => setAlternative({ ...alternative, cons: event.target.value })} /><Input type="number" min="0" placeholder="Estimated cost" value={alternative.estimated_cost} onChange={(event) => setAlternative({ ...alternative, estimated_cost: event.target.value })} /><Input type="number" min="1" max="5" placeholder="Feasibility (1-5)" value={alternative.feasibility_score} onChange={(event) => setAlternative({ ...alternative, feasibility_score: event.target.value })} /><Select options={['Low', 'Medium', 'High', 'Critical']} value={alternative.risk_level} onChange={(event) => setAlternative({ ...alternative, risk_level: event.target.value })} /></div><Button type="submit" variant="primary" icon={editingAlternative ? Save : Plus}>{editingAlternative ? 'Save alternative' : 'Add alternative'}</Button></form><Table columns={[{ key: 'name', header: 'Name' }, { key: 'feasibility_score', header: 'Feasibility' }, { key: 'risk_level', header: 'Risk' }, { key: 'estimated_cost', header: 'Cost' }, { key: 'actions', header: 'Actions', render: (_, row) => <Button variant="pearl" size="small" icon={Pencil} onClick={() => { setEditingAlternative(row); setAlternative({ ...row, estimated_cost: row.estimated_cost || '', feasibility_score: row.feasibility_score || 3, risk_level: row.risk_level || 'Medium' }); }}>Edit</Button> }]} data={related.alternatives} emptyTitle="No alternatives yet" /><div className="apple-card"><h2><GitCompare size={18} /> Comparison</h2><Table columns={[{ key: 'name', header: 'Name' }, { key: 'estimated_cost', header: 'Cost' }, { key: 'feasibility_score', header: 'Feasibility' }, { key: 'risk_level', header: 'Risk' }]} data={related.compare} emptyTitle="Add alternatives to compare" /></div></div>}

      {tab === 'Discussion' && <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}><form className="apple-card" onSubmit={addThread} style={{ display: 'grid', gap: '10px' }}><h2><MessageSquare size={18} /> Start a thread</h2><Input placeholder="Thread title" value={thread.title} onChange={(event) => setThread({ ...thread, title: event.target.value })} /><Textarea placeholder="What needs discussion?" rows={3} value={thread.description} onChange={(event) => setThread({ ...thread, description: event.target.value })} /><Button type="submit" variant="primary" icon={Plus}>Start thread</Button></form><form className="apple-card" onSubmit={addComment} style={{ display: 'flex', gap: '10px' }}><Input placeholder="Add a decision comment" value={comment} onChange={(event) => setComment(event.target.value)} /><Button type="submit" variant="primary">Comment</Button></form><div className="apple-card">{related.threads.map((item) => <div key={item.id} style={{ padding: '12px 0', borderBottom: '1px solid var(--color-divider-soft)' }}><strong>{item.title}</strong><p>{item.description}</p><form onSubmit={(event) => replyToThread(event, item.id)} style={{ display: 'flex', gap: '8px', marginTop: '8px' }}><Input placeholder="Reply to thread" value={threadReply[item.id] || ''} onChange={(event) => setThreadReply({ ...threadReply, [item.id]: event.target.value })} /><Button type="submit" variant="pearl" size="small">Reply</Button></form></div>)}{related.comments.map((item) => <div key={item.id} style={{ padding: '12px 0', borderBottom: '1px solid var(--color-divider-soft)' }}><p>{item.content}</p><small>{dateText(item.created_at)}</small></div>)}{!related.comments.length && !related.threads.length && <p style={{ color: 'var(--color-ink-muted-48)' }}>No discussion activity yet.</p>}</div></div>}

      {tab === 'Meeting Notes' && <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}><form className="apple-card" onSubmit={addNote} style={{ display: 'grid', gap: '12px' }}><h2>Add meeting note</h2><Input placeholder="Meeting title" value={note.title} onChange={(event) => setNote({ ...note, title: event.target.value })} /><Input type="datetime-local" value={note.meeting_date} onChange={(event) => setNote({ ...note, meeting_date: event.target.value })} /><Textarea placeholder="Notes" rows={4} value={note.content} onChange={(event) => setNote({ ...note, content: event.target.value })} /><Button type="submit" variant="primary" icon={Plus}>Add note</Button></form><Table columns={[{ key: 'title', header: 'Meeting' }, { key: 'meeting_date', header: 'Date' }, { key: 'content', header: 'Notes' }]} data={related.notes} emptyTitle="No meeting notes yet" /></div>}
      {tab === 'Documents' && <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {canEdit && <div className="apple-card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
          <div><h2 style={{ fontSize: '18px' }}>Supporting documents</h2><p style={{ color: 'var(--color-ink-muted-48)', fontSize: '13px', marginTop: '4px' }}>PDF, Office, text, CSV, or image files up to 10 MB.</p></div>
          <label style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', background: 'var(--color-primary)', color: 'var(--color-on-primary)', borderRadius: 'var(--radius-pill)', cursor: 'pointer', fontSize: '15px' }}><Upload size={16} /> Upload document<input type="file" onChange={uploadDocument} accept=".pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.csv,.png,.jpg,.jpeg" style={{ position: 'absolute', width: '1px', height: '1px', opacity: 0 }} /></label>
        </div>}
        <div className="apple-card"><Table columns={[{ key: 'filename', header: 'File' }, { key: 'size_bytes', header: 'Size', render: (value) => `${Math.ceil(value / 1024)} KB` }, { key: 'created_at', header: 'Uploaded', render: dateText }, { key: 'actions', header: 'Actions', render: (_, item) => <div style={{ display: 'flex', gap: '6px' }}><Button variant="pearl" size="small" icon={Download} aria-label={`Download ${item.filename}`} onClick={() => downloadDocument(item)} />{(item.uploaded_by === user?.id || hasRole(UserRole.ADMINISTRATOR)) && <Button variant="pearl" size="small" icon={Trash2} aria-label={`Delete ${item.filename}`} onClick={() => deleteDocument(item.id)} />}</div> }]} data={related.documents} emptyTitle="No supporting documents yet" /></div>
      </div>}
      {tab === 'History' && <Table columns={[{ key: 'action', header: 'Action' }, { key: 'description', header: 'Description' }, { key: 'created_at', header: 'When', render: dateText }]} data={related.history} emptyTitle="No history recorded" />}
    </div>
  );
};

export default DecisionDetailPage;
