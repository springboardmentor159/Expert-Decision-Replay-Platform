import { useEffect, useState } from "react";
import {
  listThreads,
  createThread,
  listThreadReplies,
  createThreadReply,
  listDecisionComments,
  createDecisionComment,
  listMeetingNotes,
  createMeetingNote,
} from "../../api/discussions";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Textarea from "../../components/ui/Textarea";
import Modal from "../../components/ui/Modal";
import Alert from "../../components/ui/Alert";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import Badge from "../../components/ui/Badge";
import { formatDate } from "../../utils/format";

function ThreadReplies({ threadId }) {
  const [replies, setReplies] = useState([]);
  const [state, setState] = useState("loading");
  const [text, setText] = useState("");
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState("");

  async function load() {
    setState("loading");
    try {
      const res = await listThreadReplies(threadId);
      setReplies(res);
      setState("ready");
    } catch (err) {
      setError(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [threadId]);

  async function handleReply(e) {
    e.preventDefault();
    if (!text.trim()) return;
    setPosting(true);
    setError("");
    try {
      await createThreadReply(threadId, text);
      setText("");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setPosting(false);
    }
  }

  if (state === "loading") return <LoadingState label="Loading replies…" />;
  if (state === "error") return <ErrorState message={error} onRetry={load} />;

  return (
    <div className="thread-replies">
      {replies.length === 0 ? (
        <EmptyState title="No replies yet" />
      ) : (
        <ul className="comment-list">
          {replies.map((c) => (
            <li key={c.id}>
              <div className="comment-meta">
                <span>User #{c.user_id}</span>
                <span>{formatDate(c.created_at)}</span>
              </div>
              <p>{c.content}</p>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={handleReply} className="inline-form">
        <Alert type="error">{error}</Alert>
        <Input placeholder="Write a reply…" value={text} onChange={(e) => setText(e.target.value)} />
        <Button type="submit" size="sm" loading={posting}>
          Reply
        </Button>
      </form>
    </div>
  );
}

export default function DiscussionsPanel({ decisionId }) {
  const [threads, setThreads] = useState([]);
  const [comments, setComments] = useState([]);
  const [notes, setNotes] = useState([]);
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [expandedThread, setExpandedThread] = useState(null);

  const [showThreadForm, setShowThreadForm] = useState(false);
  const [threadForm, setThreadForm] = useState({ title: "", description: "" });
  const [threadError, setThreadError] = useState("");
  const [savingThread, setSavingThread] = useState(false);

  const [commentText, setCommentText] = useState("");
  const [commentError, setCommentError] = useState("");
  const [postingComment, setPostingComment] = useState(false);

  const [showNoteForm, setShowNoteForm] = useState(false);
  const [noteForm, setNoteForm] = useState({ title: "", content: "", meeting_date: "" });
  const [noteError, setNoteError] = useState("");
  const [savingNote, setSavingNote] = useState(false);

  async function load() {
    setState("loading");
    try {
      const [t, c, n] = await Promise.all([
        listThreads(decisionId),
        listDecisionComments(decisionId),
        listMeetingNotes(decisionId),
      ]);
      setThreads(t);
      setComments(c);
      setNotes(n);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [decisionId]);

  async function handleCreateThread(e) {
    e.preventDefault();
    if (!threadForm.title.trim()) {
      setThreadError("Title is required.");
      return;
    }
    setSavingThread(true);
    setThreadError("");
    try {
      await createThread(decisionId, threadForm);
      setShowThreadForm(false);
      setThreadForm({ title: "", description: "" });
      load();
    } catch (err) {
      setThreadError(err.message);
    } finally {
      setSavingThread(false);
    }
  }

  async function handlePostComment(e) {
    e.preventDefault();
    if (!commentText.trim()) return;
    setPostingComment(true);
    setCommentError("");
    try {
      await createDecisionComment(decisionId, commentText);
      setCommentText("");
      load();
    } catch (err) {
      setCommentError(err.message);
    } finally {
      setPostingComment(false);
    }
  }

  async function handleCreateNote(e) {
    e.preventDefault();
    if (!noteForm.title.trim() || !noteForm.content.trim() || !noteForm.meeting_date) {
      setNoteError("Title, content, and meeting date are required.");
      return;
    }
    setSavingNote(true);
    setNoteError("");
    try {
      await createMeetingNote(decisionId, {
        ...noteForm,
        meeting_date: new Date(noteForm.meeting_date).toISOString(),
      });
      setShowNoteForm(false);
      setNoteForm({ title: "", content: "", meeting_date: "" });
      load();
    } catch (err) {
      setNoteError(err.message);
    } finally {
      setSavingNote(false);
    }
  }

  if (state === "loading") return <LoadingState label="Loading discussion…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div className="discussion-panel">
      <Card
        title="General Comments"
      >
        {comments.length === 0 ? (
          <EmptyState title="No comments yet" />
        ) : (
          <ul className="comment-list">
            {comments
              .filter((c) => !c.thread_id)
              .map((c) => (
                <li key={c.id}>
                  <div className="comment-meta">
                    <span>User #{c.user_id}</span>
                    <span>{formatDate(c.created_at)}</span>
                  </div>
                  <p>{c.content}</p>
                </li>
              ))}
          </ul>
        )}
        <form onSubmit={handlePostComment} className="inline-form">
          <Alert type="error">{commentError}</Alert>
          <Input placeholder="Add a comment…" value={commentText} onChange={(e) => setCommentText(e.target.value)} />
          <Button type="submit" size="sm" loading={postingComment}>
            Comment
          </Button>
        </form>
      </Card>

      <Card
        title="Discussion Threads"
        actions={
          <Button size="sm" onClick={() => setShowThreadForm(true)}>
            + New Thread
          </Button>
        }
      >
        {threads.length === 0 ? (
          <EmptyState title="No discussion threads yet" description="Start a thread to discuss a specific topic." />
        ) : (
          <ul className="thread-list">
            {threads.map((t) => (
              <li key={t.id} className="thread-item">
                <div
                  className="thread-summary"
                  onClick={() => setExpandedThread(expandedThread === t.id ? null : t.id)}
                >
                  <div>
                    <strong>{t.title}</strong>
                    {t.description && <p className="thread-desc">{t.description}</p>}
                  </div>
                  <Badge>{t.status}</Badge>
                </div>
                {expandedThread === t.id && <ThreadReplies threadId={t.id} />}
              </li>
            ))}
          </ul>
        )}
      </Card>

      <Card
        title="Meeting Notes"
        actions={
          <Button size="sm" onClick={() => setShowNoteForm(true)}>
            + Add Note
          </Button>
        }
      >
        {notes.length === 0 ? (
          <EmptyState title="No meeting notes yet" />
        ) : (
          <ul className="comment-list">
            {notes.map((n) => (
              <li key={n.id}>
                <div className="comment-meta">
                  <strong>{n.title}</strong>
                  <span>{formatDate(n.meeting_date)}</span>
                </div>
                <p>{n.content}</p>
              </li>
            ))}
          </ul>
        )}
      </Card>

      {showThreadForm && (
        <Modal title="New Discussion Thread" onClose={() => setShowThreadForm(false)}>
          <form onSubmit={handleCreateThread} className="stacked-form" noValidate>
            <Alert type="error">{threadError}</Alert>
            <Input
              label="Title"
              required
              value={threadForm.title}
              onChange={(e) => setThreadForm({ ...threadForm, title: e.target.value })}
            />
            <Textarea
              label="Description"
              rows={3}
              value={threadForm.description}
              onChange={(e) => setThreadForm({ ...threadForm, description: e.target.value })}
            />
            <div className="form-actions">
              <Button type="button" variant="secondary" onClick={() => setShowThreadForm(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={savingThread}>
                Create Thread
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {showNoteForm && (
        <Modal title="Add Meeting Note" onClose={() => setShowNoteForm(false)}>
          <form onSubmit={handleCreateNote} className="stacked-form" noValidate>
            <Alert type="error">{noteError}</Alert>
            <Input
              label="Title"
              required
              value={noteForm.title}
              onChange={(e) => setNoteForm({ ...noteForm, title: e.target.value })}
            />
            <Input
              label="Meeting Date"
              type="datetime-local"
              required
              value={noteForm.meeting_date}
              onChange={(e) => setNoteForm({ ...noteForm, meeting_date: e.target.value })}
            />
            <Textarea
              label="Content"
              required
              rows={4}
              value={noteForm.content}
              onChange={(e) => setNoteForm({ ...noteForm, content: e.target.value })}
            />
            <div className="form-actions">
              <Button type="button" variant="secondary" onClick={() => setShowNoteForm(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={savingNote}>
                Save Note
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
