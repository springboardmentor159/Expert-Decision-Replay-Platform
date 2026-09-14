import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getDecisionComments,
  createDecisionComment,
  updateComment,
  deleteComment,
  getMeetingNotes,
  createMeetingNote,
  updateMeetingNote,
  deleteMeetingNote,
  getDecisionRationale,
  updateDecisionRationale,
} from "../../services/discussionService";

const Discussion = () => {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  // =========================================================
  // STATE
  // =========================================================

  const [comments, setComments] = useState([]);
  const [meetingNotes, setMeetingNotes] = useState([]);
  const [rationale, setRationale] = useState("");

  const [commentText, setCommentText] = useState("");

  const [editingCommentId, setEditingCommentId] = useState(null);
  const [editingCommentText, setEditingCommentText] = useState("");

  const [meetingNoteForm, setMeetingNoteForm] = useState({
    title: "",
    content: "",
    meeting_date: "",
  });

  const [editingNoteId, setEditingNoteId] = useState(null);

  const [rationaleText, setRationaleText] = useState("");

  const [loading, setLoading] = useState(true);
  const [commentsLoading, setCommentsLoading] = useState(false);
  const [notesLoading, setNotesLoading] = useState(false);

  const [savingComment, setSavingComment] = useState(false);
  const [savingNote, setSavingNote] = useState(false);
  const [savingRationale, setSavingRationale] = useState(false);

  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  // =========================================================
  // LOAD ALL DISCUSSION DATA
  // =========================================================

  useEffect(() => {
    loadDiscussion();
  }, [decisionId]);

  const loadDiscussion = async () => {
    setLoading(true);
    setError("");

    await Promise.all([
      loadComments(),
      loadMeetingNotes(),
      loadRationale(),
    ]);

    setLoading(false);
  };

  // =========================================================
  // COMMENTS
  // =========================================================

  const loadComments = async () => {
    setCommentsLoading(true);

    try {
      const data = await getDecisionComments(decisionId);

      setComments(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load comments:", err);

      if (!error) {
        handleError(err, "Unable to load comments.");
      }
    } finally {
      setCommentsLoading(false);
    }
  };

  const handleAddComment = async (event) => {
    event.preventDefault();

    if (!commentText.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    setSavingComment(true);
    setError("");
    setSuccessMessage("");

    try {
      await createDecisionComment(
        decisionId,
        commentText.trim()
      );

      setCommentText("");

      await loadComments();

      setSuccessMessage("Comment added successfully.");
    } catch (err) {
      console.error("Failed to add comment:", err);
      handleError(err, "Unable to add comment.");
    } finally {
      setSavingComment(false);
    }
  };

  const startEditComment = (comment) => {
    setEditingCommentId(comment.id);
    setEditingCommentText(comment.content);
    setError("");
    setSuccessMessage("");
  };

  const cancelEditComment = () => {
    setEditingCommentId(null);
    setEditingCommentText("");
  };

  const handleUpdateComment = async (commentId) => {
    if (!editingCommentText.trim()) {
      setError("Comment cannot be empty.");
      return;
    }

    setSavingComment(true);
    setError("");
    setSuccessMessage("");

    try {
      await updateComment(
        commentId,
        editingCommentText.trim()
      );

      cancelEditComment();

      await loadComments();

      setSuccessMessage("Comment updated successfully.");
    } catch (err) {
      console.error("Failed to update comment:", err);
      handleError(err, "Unable to update comment.");
    } finally {
      setSavingComment(false);
    }
  };

  const handleDeleteComment = async (commentId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this comment?"
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccessMessage("");

    try {
      await deleteComment(commentId);

      await loadComments();

      setSuccessMessage("Comment deleted successfully.");
    } catch (err) {
      console.error("Failed to delete comment:", err);
      handleError(err, "Unable to delete comment.");
    }
  };

  // =========================================================
  // MEETING NOTES
  // =========================================================

  const loadMeetingNotes = async () => {
    setNotesLoading(true);

    try {
      const data = await getMeetingNotes(decisionId);

      setMeetingNotes(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load meeting notes:", err);

      if (!error) {
        handleError(err, "Unable to load meeting notes.");
      }
    } finally {
      setNotesLoading(false);
    }
  };

  const handleMeetingNoteChange = (event) => {
    const { name, value } = event.target;

    setMeetingNoteForm((previous) => ({
      ...previous,
      [name]: value,
    }));
  };

  const resetMeetingNoteForm = () => {
    setMeetingNoteForm({
      title: "",
      content: "",
      meeting_date: "",
    });

    setEditingNoteId(null);
  };

  const handleSaveMeetingNote = async (event) => {
    event.preventDefault();

    if (!meetingNoteForm.title.trim()) {
      setError("Meeting note title is required.");
      return;
    }

    if (!meetingNoteForm.content.trim()) {
      setError("Meeting note content is required.");
      return;
    }

    if (!meetingNoteForm.meeting_date) {
      setError("Meeting date is required.");
      return;
    }

    setSavingNote(true);
    setError("");
    setSuccessMessage("");

    try {
      const payload = {
        title: meetingNoteForm.title.trim(),
        content: meetingNoteForm.content.trim(),
        meeting_date: new Date(
          meetingNoteForm.meeting_date
        ).toISOString(),
      };

      if (editingNoteId) {
        await updateMeetingNote(
          editingNoteId,
          payload
        );

        setSuccessMessage(
          "Meeting note updated successfully."
        );
      } else {
        await createMeetingNote(
          decisionId,
          payload
        );

        setSuccessMessage(
          "Meeting note added successfully."
        );
      }

      resetMeetingNoteForm();

      await loadMeetingNotes();
    } catch (err) {
      console.error("Failed to save meeting note:", err);
      handleError(err, "Unable to save meeting note.");
    } finally {
      setSavingNote(false);
    }
  };

  const startEditMeetingNote = (note) => {
    setEditingNoteId(note.id);

    setMeetingNoteForm({
      title: note.title || "",
      content: note.content || "",
      meeting_date: note.meeting_date
        ? formatDateTimeLocalValue(note.meeting_date)
        : "",
    });

    setError("");
    setSuccessMessage("");
  };

  const handleDeleteMeetingNote = async (noteId) => {
    const confirmed = window.confirm(
      "Are you sure you want to delete this meeting note?"
    );

    if (!confirmed) {
      return;
    }

    setError("");
    setSuccessMessage("");

    try {
      await deleteMeetingNote(noteId);

      if (editingNoteId === noteId) {
        resetMeetingNoteForm();
      }

      await loadMeetingNotes();

      setSuccessMessage(
        "Meeting note deleted successfully."
      );
    } catch (err) {
      console.error("Failed to delete meeting note:", err);
      handleError(err, "Unable to delete meeting note.");
    }
  };

  // =========================================================
  // RATIONALE
  // =========================================================

  const loadRationale = async () => {
    try {
      const data = await getDecisionRationale(decisionId);

      const currentRationale = data?.rationale || "";

      setRationale(currentRationale);
      setRationaleText(currentRationale);
    } catch (err) {
      console.error("Failed to load rationale:", err);

      if (!error) {
        handleError(err, "Unable to load rationale.");
      }
    }
  };

  const handleSaveRationale = async (event) => {
    event.preventDefault();

    setSavingRationale(true);
    setError("");
    setSuccessMessage("");

    try {
      await updateDecisionRationale(
        decisionId,
        rationaleText.trim()
      );

      setRationale(rationaleText.trim());

      setSuccessMessage(
        "Decision rationale updated successfully."
      );
    } catch (err) {
      console.error("Failed to update rationale:", err);
      handleError(
        err,
        "Unable to update decision rationale."
      );
    } finally {
      setSavingRationale(false);
    }
  };

  // =========================================================
  // ERROR HANDLING
  // =========================================================

  const handleError = (err, defaultMessage) => {
    const status = err?.response?.status;

    if (status === 400) {
      setError(
        err.response?.data?.detail ||
          "Invalid request."
      );
    } else if (status === 401) {
      setError(
        "Your session has expired. Please log in again."
      );
    } else if (status === 403) {
      setError(
        "You do not have permission to perform this action."
      );
    } else if (status === 404) {
      setError(
        "The requested discussion item was not found."
      );
    } else if (status === 422) {
      setError(
        "Please check the entered information."
      );
    } else if (status >= 500) {
      setError(
        "A server error occurred. Please try again."
      );
    } else if (!err?.response) {
      setError(
        "Unable to connect to the backend server."
      );
    } else {
      setError(
        err.response?.data?.detail ||
          defaultMessage
      );
    }
  };

  // =========================================================
  // HELPERS
  // =========================================================

  const formatDate = (value) => {
    if (!value) {
      return "—";
    }

    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return value;
    }

    return date.toLocaleString();
  };

  const formatDateTimeLocalValue = (value) => {
    const date = new Date(value);

    if (Number.isNaN(date.getTime())) {
      return "";
    }

    const year = date.getFullYear();
    const month = String(
      date.getMonth() + 1
    ).padStart(2, "0");
    const day = String(
      date.getDate()
    ).padStart(2, "0");
    const hours = String(
      date.getHours()
    ).padStart(2, "0");
    const minutes = String(
      date.getMinutes()
    ).padStart(2, "0");

    return `${year}-${month}-${day}T${hours}:${minutes}`;
  };

  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="discussion-page">
        <div className="page-header">
          <div>
            <h1>Discussion</h1>
            <p>
              Comments, threads, meeting notes and rationale
            </p>
          </div>
        </div>

        <div className="discussion-loading">
          Loading discussion...
        </div>
      </div>
    );
  }

  // =========================================================
  // UI
  // =========================================================

  return (
    <div className="discussion-page">

      {/* PAGE HEADER */}
      <div className="page-header">
        <div>
          <h1>Discussion</h1>
          <p>
            Comments, threads, meeting notes and decision
            rationale
          </p>
        </div>

        <div className="discussion-header-actions">
          <button
            type="button"
            className="app-button secondary"
            onClick={() =>
              navigate(
                `/decisions/${decisionId}`
              )
            }
          >
            Back to Decision
          </button>

          <button
            type="button"
            className="app-button secondary"
            onClick={() =>
              navigate(
                `/decisions/${decisionId}/threads`
              )
            }
          >
            Threads
          </button>
        </div>
      </div>

      {/* ERROR */}
      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {/* SUCCESS */}
      {successMessage && (
        <div className="alert alert-success">
          {successMessage}
        </div>
      )}

      {/* =====================================================
          COMMENTS
          ===================================================== */}

      <section className="discussion-section">
        <div className="discussion-section-header">
          <div>
            <h2>Comments</h2>
            <p>
              Discuss the decision with other users.
            </p>
          </div>

          <span className="discussion-count">
            {comments.length}
          </span>
        </div>

        <div className="discussion-card">

          {commentsLoading ? (
            <div className="discussion-loading-small">
              Loading comments...
            </div>
          ) : comments.length === 0 ? (
            <div className="discussion-empty">
              <strong>No comments yet</strong>
              <p>
                Be the first to add a comment.
              </p>
            </div>
          ) : (
            <div className="comment-list">
              {comments.map((comment) => (
                <div
                  className="comment-card"
                  key={comment.id}
                >
                  <div className="comment-card-header">
                    <div>
                      <strong>
                        User #{comment.user_id}
                      </strong>

                      <span>
                        {formatDate(
                          comment.created_at
                        )}
                      </span>
                    </div>
                  </div>

                  {editingCommentId ===
                  comment.id ? (
                    <div className="comment-edit-area">
                      <textarea
                        value={
                          editingCommentText
                        }
                        onChange={(event) =>
                          setEditingCommentText(
                            event.target.value
                          )
                        }
                        rows={4}
                        placeholder="Enter your comment"
                      />

                      <div className="discussion-form-actions">
                        <button
                          type="button"
                          className="app-button secondary"
                          onClick={
                            cancelEditComment
                          }
                        >
                          Cancel
                        </button>

                        <button
                          type="button"
                          className="app-button primary"
                          disabled={
                            savingComment
                          }
                          onClick={() =>
                            handleUpdateComment(
                              comment.id
                            )
                          }
                        >
                          {savingComment
                            ? "Saving..."
                            : "Save Changes"}
                        </button>
                      </div>
                    </div>
                  ) : (
                    <>
                      <p className="comment-content">
                        {comment.content}
                      </p>

                      <div className="comment-actions">
                        <button
                          type="button"
                          className="text-button"
                          onClick={() =>
                            startEditComment(
                              comment
                            )
                          }
                        >
                          Edit
                        </button>

                        <button
                          type="button"
                          className="text-button danger-text"
                          onClick={() =>
                            handleDeleteComment(
                              comment.id
                            )
                          }
                        >
                          Delete
                        </button>
                      </div>
                    </>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* ADD COMMENT */}
          <form
            className="discussion-form"
            onSubmit={handleAddComment}
          >
            <label htmlFor="comment">
              Add Comment
            </label>

            <textarea
              id="comment"
              value={commentText}
              onChange={(event) =>
                setCommentText(
                  event.target.value
                )
              }
              rows={4}
              placeholder="Write a comment..."
            />

            <div className="discussion-form-actions">
              <button
                type="submit"
                className="app-button primary"
                disabled={savingComment}
              >
                {savingComment
                  ? "Adding..."
                  : "Add Comment"}
              </button>
            </div>
          </form>
        </div>
      </section>

      {/* =====================================================
          THREADS
          ===================================================== */}

      <section className="discussion-section">
        <div className="discussion-section-header">
          <div>
            <h2>Threads</h2>
            <p>
              Organize longer discussions into separate
              discussion threads.
            </p>
          </div>
        </div>

        <div className="discussion-card discussion-link-card">
          <p>
            Use the Threads page to create, edit, delete
            and reply to discussion threads.
          </p>

          <button
            type="button"
            className="app-button primary"
            onClick={() =>
              navigate(
                `/decisions/${decisionId}/threads`
              )
            }
          >
            Open Threads
          </button>
        </div>
      </section>

      {/* =====================================================
          MEETING NOTES
          ===================================================== */}

      <section className="discussion-section">
        <div className="discussion-section-header">
          <div>
            <h2>Meeting Notes</h2>
            <p>
              Record important information from decision
              meetings.
            </p>
          </div>

          <span className="discussion-count">
            {meetingNotes.length}
          </span>
        </div>

        <div className="discussion-card">

          {/* MEETING NOTE FORM */}

          <form
            className="discussion-form meeting-note-form"
            onSubmit={handleSaveMeetingNote}
          >
            <h3>
              {editingNoteId
                ? "Edit Meeting Note"
                : "Add Meeting Note"}
            </h3>

            <div className="discussion-form-grid">

              <div className="form-group">
                <label htmlFor="meeting-title">
                  Title
                </label>

                <input
                  id="meeting-title"
                  name="title"
                  type="text"
                  value={
                    meetingNoteForm.title
                  }
                  onChange={
                    handleMeetingNoteChange
                  }
                  placeholder="Enter meeting title"
                />
              </div>

              <div className="form-group">
                <label htmlFor="meeting-date">
                  Meeting Date
                </label>

                <input
                  id="meeting-date"
                  name="meeting_date"
                  type="datetime-local"
                  value={
                    meetingNoteForm.meeting_date
                  }
                  onChange={
                    handleMeetingNoteChange
                  }
                />
              </div>

            </div>

            <div className="form-group">
              <label htmlFor="meeting-content">
                Content
              </label>

              <textarea
                id="meeting-content"
                name="content"
                rows={5}
                value={
                  meetingNoteForm.content
                }
                onChange={
                  handleMeetingNoteChange
                }
                placeholder="Enter meeting notes..."
              />
            </div>

            <div className="discussion-form-actions">

              {editingNoteId && (
                <button
                  type="button"
                  className="app-button secondary"
                  onClick={
                    resetMeetingNoteForm
                  }
                >
                  Cancel
                </button>
              )}

              <button
                type="submit"
                className="app-button primary"
                disabled={savingNote}
              >
                {savingNote
                  ? "Saving..."
                  : editingNoteId
                  ? "Update Meeting Note"
                  : "Add Meeting Note"}
              </button>

            </div>
          </form>

          {/* MEETING NOTE LIST */}

          <div className="discussion-subsection">

            <h3>Saved Meeting Notes</h3>

            {notesLoading ? (
              <div className="discussion-loading-small">
                Loading meeting notes...
              </div>
            ) : meetingNotes.length === 0 ? (
              <div className="discussion-empty">
                <strong>
                  No meeting notes yet
                </strong>
                <p>
                  Add a meeting note using the form above.
                </p>
              </div>
            ) : (
              <div className="meeting-note-list">

                {meetingNotes.map((note) => (
                  <article
                    className="meeting-note-card"
                    key={note.id}
                  >
                    <div className="meeting-note-header">
                      <div>
                        <h4>
                          {note.title}
                        </h4>

                        <span>
                          Meeting:{" "}
                          {formatDate(
                            note.meeting_date
                          )}
                        </span>
                      </div>

                      <span className="meeting-note-id">
                        #{note.id}
                      </span>
                    </div>

                    <p className="meeting-note-content">
                      {note.content}
                    </p>

                    <div className="meeting-note-meta">
                      <span>
                        Created by User #
                        {note.created_by}
                      </span>

                      <span>
                        Created:{" "}
                        {formatDate(
                          note.created_at
                        )}
                      </span>
                    </div>

                    <div className="meeting-note-actions">
                      <button
                        type="button"
                        className="text-button"
                        onClick={() =>
                          startEditMeetingNote(
                            note
                          )
                        }
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="text-button danger-text"
                        onClick={() =>
                          handleDeleteMeetingNote(
                            note.id
                          )
                        }
                      >
                        Delete
                      </button>
                    </div>
                  </article>
                ))}

              </div>
            )}
          </div>
        </div>
      </section>

      {/* =====================================================
          RATIONALE
          ===================================================== */}

      <section className="discussion-section">
        <div className="discussion-section-header">
          <div>
            <h2>Decision Rationale</h2>
            <p>
              Record the reasoning behind the decision.
            </p>
          </div>
        </div>

        <div className="discussion-card">

          {rationale && (
            <div className="current-rationale">
              <strong>Current Rationale</strong>
              <p>{rationale}</p>
            </div>
          )}

          <form
            className="discussion-form"
            onSubmit={handleSaveRationale}
          >
            <label htmlFor="rationale">
              Rationale
            </label>

            <textarea
              id="rationale"
              rows={6}
              value={rationaleText}
              onChange={(event) =>
                setRationaleText(
                  event.target.value
                )
              }
              placeholder="Explain why this decision was made..."
            />

            <div className="discussion-form-actions">
              <button
                type="submit"
                className="app-button primary"
                disabled={savingRationale}
              >
                {savingRationale
                  ? "Saving..."
                  : "Save Rationale"}
              </button>
            </div>
          </form>
        </div>
      </section>

    </div>
  );
};

export default Discussion;