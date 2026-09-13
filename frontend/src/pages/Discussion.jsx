import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { getThreads, createThread, getComments, createComment, getDecision } from '../services/api';
import Layout from '../components/Layout';

export default function Discussion() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [decision, setDecision] = useState(null);
  const [threads, setThreads] = useState([]);
  const [selectedThread, setSelectedThread] = useState(null);
  const [comments, setComments] = useState([]);
  const [newThread, setNewThread] = useState({ title: '', content: '' });
  const [newComment, setNewComment] = useState('');
  const [showThreadForm, setShowThreadForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => { fetchData(); }, [id]);
  useEffect(() => { if (selectedThread) fetchComments(selectedThread.id); }, [selectedThread]);

  const fetchData = async () => {
    try {
      const [decRes, thrRes] = await Promise.all([
        getDecision(id), getThreads(id),
      ]);
      setDecision(decRes.data);
      setThreads(thrRes.data);
      if (thrRes.data.length > 0) setSelectedThread(thrRes.data[0]);
    } catch (err) {
      setError('Failed to load discussions');
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async (threadId) => {
    try {
      const response = await getComments(threadId);
      setComments(response.data);
    } catch (err) {
      setComments([]);
    }
  };

  const handleCreateThread = async (e) => {
    e.preventDefault();
    if (!newThread.title || !newThread.content) {
      alert('Title and content are required');
      return;
    }
    try {
      await createThread(id, newThread);
      setNewThread({ title: '', content: '' });
      setShowThreadForm(false);
      fetchData();
    } catch (err) {
      alert('Failed to create thread');
    }
  };

  const handleCreateComment = async (e) => {
    e.preventDefault();
    if (!newComment.trim()) {
      alert('Comment cannot be empty');
      return;
    }
    try {
      await createComment(selectedThread.id, { content: newComment });
      setNewComment('');
      fetchComments(selectedThread.id);
    } catch (err) {
      alert('Failed to add comment');
    }
  };

  if (loading) return <Layout><div style={styles.center}>Loading discussions...</div></Layout>;
  if (error) return <Layout><div style={styles.center}>{error}</div></Layout>;

  return (
    <Layout>
      {/* Header */}
      <div style={styles.header}>
        <button style={styles.backBtn}
          onClick={() => navigate(`/decisions/${id}`)}>← Back to Decision</button>
        <h2 style={styles.title}>💬 Discussions</h2>
        <p style={styles.subtitle}>Decision: <strong>{decision?.title}</strong></p>
      </div>

      <div style={styles.layout}>
        {/* Threads List */}
        <div style={styles.threadsList}>
          <div style={styles.threadsHeader}>
            <h3 style={styles.threadsTitle}>Threads ({threads.length})</h3>
            <button style={styles.addThreadBtn}
              onClick={() => setShowThreadForm(!showThreadForm)}>
              + New
            </button>
          </div>

          {/* New Thread Form */}
          {showThreadForm && (
            <div style={styles.threadForm}>
              <form onSubmit={handleCreateThread}>
                <div style={styles.field}>
                  <label style={styles.label}>Title *</label>
                  <input value={newThread.title}
                    onChange={(e) => setNewThread({...newThread, title: e.target.value})}
                    style={styles.input} placeholder="Thread title" />
                </div>
                <div style={styles.field}>
                  <label style={styles.label}>Content *</label>
                  <textarea value={newThread.content}
                    onChange={(e) => setNewThread({...newThread, content: e.target.value})}
                    style={styles.textarea} placeholder="Thread content" rows={3} />
                </div>
                <div style={styles.formBtns}>
                  <button type="button" style={styles.cancelBtn}
                    onClick={() => setShowThreadForm(false)}>Cancel</button>
                  <button type="submit" style={styles.submitBtn}>Create</button>
                </div>
              </form>
            </div>
          )}

          {threads.length === 0 ? (
            <p style={styles.empty}>No threads yet.</p>
          ) : (
            threads.map(thread => (
              <div key={thread.id}
                style={{
                  ...styles.threadItem,
                  ...(selectedThread?.id === thread.id ? styles.activeThread : {})
                }}
                onClick={() => setSelectedThread(thread)}>
                <h4 style={styles.threadItemTitle}>{thread.title}</h4>
                <p style={styles.threadItemContent}>{thread.content}</p>
                <span style={styles.threadDate}>
                  {new Date(thread.created_at).toLocaleDateString()}
                </span>
              </div>
            ))
          )}
        </div>

        {/* Comments Section */}
        <div style={styles.commentsSection}>
          {!selectedThread ? (
            <div style={styles.noThread}>
              <p>Select a thread to view comments</p>
            </div>
          ) : (
            <>
              <div style={styles.commentsHeader}>
                <h3 style={styles.commentsTitle}>{selectedThread.title}</h3>
                <p style={styles.commentsSubtitle}>{selectedThread.content}</p>
              </div>

              <div style={styles.commentsList}>
                {comments.length === 0 ? (
                  <p style={styles.empty}>No comments yet. Be the first!</p>
                ) : (
                  comments.map(comment => (
                    <div key={comment.id} style={styles.commentCard}>
                      <div style={styles.commentHeader}>
                        <div style={styles.commentAvatar}>
                          {comment.user_id}
                        </div>
                        <div>
                          <span style={styles.commentUser}>User #{comment.user_id}</span>
                          <span style={styles.commentDate}>
                            {new Date(comment.created_at).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <p style={styles.commentContent}>{comment.content}</p>
                    </div>
                  ))
                )}
              </div>

              {/* Add Comment */}
              <div style={styles.addComment}>
                <h4 style={styles.addCommentTitle}>Add Comment</h4>
                <form onSubmit={handleCreateComment}>
                  <textarea value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    style={styles.commentInput}
                    placeholder="Write your comment..." rows={3} />
                  <button type="submit" style={styles.submitCommentBtn}>
                    Post Comment
                  </button>
                </form>
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
}

const styles = {
  header: { marginBottom: '24px' },
  backBtn: { padding: '8px 16px', backgroundColor: '#ecf0f1', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px', marginBottom: '12px', display: 'block' },
  title: { color: '#2C3E50', fontSize: '24px', margin: '8px 0 4px' },
  subtitle: { color: '#7f8c8d', fontSize: '14px', margin: 0 },
  layout: { display: 'grid', gridTemplateColumns: '300px 1fr', gap: '24px' },
  threadsList: { backgroundColor: 'white', borderRadius: '12px', padding: '16px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)', height: 'fit-content' },
  threadsHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' },
  threadsTitle: { color: '#2C3E50', fontSize: '16px', margin: 0 },
  addThreadBtn: { padding: '6px 12px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' },
  threadForm: { backgroundColor: '#f8f9fa', padding: '16px', borderRadius: '8px', marginBottom: '16px' },
  field: { marginBottom: '12px' },
  label: { display: 'block', marginBottom: '4px', color: '#2C3E50', fontWeight: '600', fontSize: '13px' },
  input: { width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '13px', boxSizing: 'border-box' },
  textarea: { width: '100%', padding: '8px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '13px', boxSizing: 'border-box', resize: 'vertical' },
  formBtns: { display: 'flex', gap: '8px', justifyContent: 'flex-end' },
  cancelBtn: { padding: '6px 14px', backgroundColor: '#ecf0f1', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' },
  submitBtn: { padding: '6px 14px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '13px' },
  threadItem: { padding: '12px', borderRadius: '8px', cursor: 'pointer', marginBottom: '8px', border: '1px solid #eee' },
  activeThread: { backgroundColor: '#EBF5FB', borderColor: '#2980b9' },
  threadItemTitle: { color: '#2C3E50', fontSize: '14px', margin: '0 0 4px' },
  threadItemContent: { color: '#7f8c8d', fontSize: '12px', margin: '0 0 4px' },
  threadDate: { color: '#95a5a6', fontSize: '11px' },
  commentsSection: { backgroundColor: 'white', borderRadius: '12px', padding: '24px', boxShadow: '0 2px 8px rgba(0,0,0,0.05)' },
  commentsHeader: { marginBottom: '20px', paddingBottom: '16px', borderBottom: '1px solid #eee' },
  commentsTitle: { color: '#2C3E50', fontSize: '18px', margin: '0 0 8px' },
  commentsSubtitle: { color: '#7f8c8d', fontSize: '14px', margin: 0 },
  commentsList: { marginBottom: '24px' },
  commentCard: { border: '1px solid #eee', borderRadius: '8px', padding: '16px', marginBottom: '12px' },
  commentHeader: { display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' },
  commentAvatar: { width: '36px', height: '36px', borderRadius: '50%', backgroundColor: '#2C3E50', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 'bold' },
  commentUser: { color: '#2C3E50', fontWeight: '600', fontSize: '13px', display: 'block' },
  commentDate: { color: '#95a5a6', fontSize: '12px' },
  commentContent: { color: '#2C3E50', fontSize: '14px', margin: 0, lineHeight: '1.5' },
  addComment: { borderTop: '1px solid #eee', paddingTop: '20px' },
  addCommentTitle: { color: '#2C3E50', fontSize: '16px', marginBottom: '12px' },
  commentInput: { width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid #ddd', fontSize: '14px', boxSizing: 'border-box', resize: 'vertical', marginBottom: '12px' },
  submitCommentBtn: { padding: '10px 20px', backgroundColor: '#2C3E50', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '14px' },
  noThread: { display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px', color: '#7f8c8d' },
  empty: { color: '#7f8c8d', fontStyle: 'italic', textAlign: 'center', padding: '20px' },
  center: { display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' },
};