import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../services/api";

function DecisionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [decision, setDecision] = useState(null);
  const [attachments, setAttachments] = useState([]);
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadingAttachment, setUploadingAttachment] = useState(false);

  const [loading, setLoading] = useState(true);
  const [loadingAttachments, setLoadingAttachments] = useState(false);

  const [meetingNotes, setMeetingNotes] = useState([]);
const [loadingMeetingNotes, setLoadingMeetingNotes] = useState(false);

const [newNoteTitle, setNewNoteTitle] = useState("");
const [newNoteContent, setNewNoteContent] = useState("");
const [newNoteDate, setNewNoteDate] = useState("");

const [editingNoteId, setEditingNoteId] = useState(null);
const [editingNoteTitle, setEditingNoteTitle] = useState("");
const [editingNoteContent, setEditingNoteContent] = useState("");
const [editingNoteDate, setEditingNoteDate] = useState("");

  const [error, setError] = useState("");

  useEffect(() => {
    const fetchDecision = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get(`/decisions/${id}`);
        setDecision(response.data);
      } catch (error) {
        console.error("Failed to load decision:", error);

        if (error.response?.status === 404) {
          setError("Decision not found.");
        } else if (error.response?.status === 401) {
          setError("Your session has expired. Please login again.");
        } else if (error.response?.status === 403) {
          setError("You are not authorized to view this decision.");
        } else {
          setError("Unable to load decision. Please try again.");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchDecision();
  }, [id]);

  useEffect(() => {
    const fetchAttachments = async () => {
      try {
        setLoadingAttachments(true);

        const response = await api.get(
          `/decisions/${id}/attachments`
        );

        setAttachments(response.data);
      } catch (error) {
        console.error("Failed to load attachments:", error);

        if (error.response?.status === 401) {
          setError("Your session has expired. Please login again.");
        } else if (error.response?.status === 403) {
          setError("You are not authorized to view attachments.");
        } else if (error.response?.status === 404) {
          setError("Decision not found.");
        } else {
          setError("Unable to load attachments.");
        }
      } finally {
        setLoadingAttachments(false);
      }
    };

    fetchAttachments();
  }, [id]);

  useEffect(() => {
  const fetchMeetingNotes = async () => {
    try {
      setLoadingMeetingNotes(true);

      const response = await api.get(
        `/decisions/${id}/meeting-notes`
      );

      setMeetingNotes(response.data);
    } catch (error) {
      console.error("Failed to load meeting notes:", error);

      if (error.response?.status === 401) {
        setError("Your session has expired. Please login again.");
      } else if (error.response?.status === 403) {
        setError("You are not authorized to view meeting notes.");
      } else if (error.response?.status === 404) {
        setError("Decision not found.");
      } else {
        setError("Unable to load meeting notes.");
      }
    } finally {
      setLoadingMeetingNotes(false);
    }
  };

  fetchMeetingNotes();
}, [id]);

  const handleUploadAttachment = async (event) => {
  event.preventDefault();

  if (!selectedFile) {
    setError("Please select a file.");
    return;
  }

  try {
    setUploadingAttachment(true);
    setError("");

    const formData = new FormData();
    formData.append("file", selectedFile);

    const response = await api.post(
  `/decisions/${id}/attachments`,
  formData,
  {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  }
);

    setAttachments((previous) => [
      ...previous,
      response.data,
    ]);

    setSelectedFile(null);

    event.target.reset();

  } catch (error) {
    console.error(
      "Failed to upload attachment:",
      error
    );

    if (error.response?.status === 401) {
      setError(
        "Your session has expired. Please login again."
      );
    } else if (error.response?.status === 403) {
      setError(
        "You are not authorized to upload attachments."
      );
    } else if (error.response?.status === 404) {
      setError("Decision not found.");
   } else if (error.response?.status === 422) {
  setError(
    error.response?.data?.detail ||
      "Please select a valid file."
  );
} else {
      setError(
        error.response?.data?.detail ||
          "Unable to upload attachment."
      );
    }
  } finally {
    setUploadingAttachment(false);
  }
};

const handleDeleteAttachment = async (attachmentId) => {
  const confirmed = window.confirm(
    "Are you sure you want to delete this attachment?"
  );

  if (!confirmed) {
    return;
  }

  try {
    setError("");

    await api.delete(`/attachments/${attachmentId}`);

    setAttachments((previous) =>
      previous.filter(
        (attachment) => attachment.id !== attachmentId
      )
    );
  } catch (error) {
    console.error(
      "Failed to delete attachment:",
      error
    );

    if (error.response?.status === 401) {
      setError(
        "Your session has expired. Please login again."
      );
    } else if (error.response?.status === 403) {
      setError(
        "You can only delete your own attachments."
      );
    } else if (error.response?.status === 404) {
      setError("Attachment not found.");
    } else {
      setError(
        error.response?.data?.detail ||
          "Unable to delete attachment."
      );
    }
  }
};

const handleCreateMeetingNote = async (event) => {
  event.preventDefault();

  if (!newNoteTitle.trim()) {
    setError("Meeting note title cannot be empty.");
    return;
  }

  if (!newNoteContent.trim()) {
    setError("Meeting note content cannot be empty.");
    return;
  }

  if (!newNoteDate) {
    setError("Please select a meeting date.");
    return;
  }

  try {
    setError("");

    const response = await api.post(
      `/decisions/${id}/meeting-notes`,
      {
        title: newNoteTitle.trim(),
        content: newNoteContent.trim(),
        meeting_date: newNoteDate,
      }
    );

    setMeetingNotes((previous) => [
      ...previous,
      response.data,
    ]);

    setNewNoteTitle("");
    setNewNoteContent("");
    setNewNoteDate("");
  } catch (error) {
    console.error(
      "Failed to create meeting note:",
      error
    );

    setError(
      error.response?.data?.detail ||
        "Unable to create meeting note."
    );
  }
};

const handleEditMeetingNote = (note) => {
  setEditingNoteId(note.id);
  setEditingNoteTitle(note.title);
  setEditingNoteContent(note.content);
  setEditingNoteDate(
    note.meeting_date
      ? note.meeting_date.substring(0, 10)
      : ""
  );

  setError("");
};

const handleCancelMeetingNoteEdit = () => {
  setEditingNoteId(null);
  setEditingNoteTitle("");
  setEditingNoteContent("");
  setEditingNoteDate("");
};

const handleUpdateMeetingNote = async (noteId) => {
  if (!editingNoteTitle.trim()) {
    setError("Meeting note title cannot be empty.");
    return;
  }

  if (!editingNoteContent.trim()) {
    setError("Meeting note content cannot be empty.");
    return;
  }

  if (!editingNoteDate) {
    setError("Please select a meeting date.");
    return;
  }

  try {
    setError("");

    const response = await api.put(
      `/meeting-notes/${noteId}`,
      {
        title: editingNoteTitle.trim(),
        content: editingNoteContent.trim(),
        meeting_date: editingNoteDate,
      }
    );

    setMeetingNotes((previous) =>
      previous.map((note) =>
        note.id === noteId
          ? response.data
          : note
      )
    );

    handleCancelMeetingNoteEdit();
  } catch (error) {
    console.error(
      "Failed to update meeting note:",
      error
    );

    if (error.response?.status === 403) {
      setError(
        "You can only update your own meeting notes."
      );
    } else {
      setError(
        error.response?.data?.detail ||
          "Unable to update meeting note."
      );
    }
  }
};

const handleDeleteMeetingNote = async (noteId) => {
  const confirmed = window.confirm(
    "Are you sure you want to delete this meeting note?"
  );

  if (!confirmed) {
    return;
  }

  try {
    setError("");

    await api.delete(`/meeting-notes/${noteId}`);

    setMeetingNotes((previous) =>
      previous.filter(
        (note) => note.id !== noteId
      )
    );
  } catch (error) {
    console.error(
      "Failed to delete meeting note:",
      error
    );

    if (error.response?.status === 403) {
      setError(
        "You can only delete your own meeting notes."
      );
    } else {
      setError(
        error.response?.data?.detail ||
          "Unable to delete meeting note."
      );
    }
  }
};

  if (loading) {
    return (
      <div className="page-container">
        <h2>Decision Details</h2>
        <p>Loading decision...</p>
      </div>
    );
  }

  if (error && !decision) {
    return (
      <div className="page-container">
        <h2>Decision Details</h2>

        <div className="error-message">
          {error}
        </div>

        <button onClick={() => navigate("/decisions")}>
          Back to My Decisions
        </button>
      </div>
    );
  }

  if (!decision) {
    return null;
  }

  return (
    <div className="page-container">

      <div className="page-header">
        <div>
          <h1>{decision.title}</h1>
          <p>Decision #{decision.id}</p>
        </div>

        <button onClick={() => navigate("/decisions")}>
          ← Back
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="details-card">
        <h2>Decision Information</h2>

        <div className="details-grid">

          <div>
            <strong>Category</strong>
            <p>{decision.category || "N/A"}</p>
          </div>

          <div>
            <strong>Status</strong>
            <p>{decision.status || "N/A"}</p>
          </div>

          <div>
            <strong>Created By</strong>
            <p>{decision.created_by || "N/A"}</p>
          </div>

          <div>
            <strong>Created At</strong>
            <p>
              {decision.created_at
                ? new Date(decision.created_at).toLocaleString()
                : "N/A"}
            </p>
          </div>

          <div>
            <strong>Updated At</strong>
            <p>
              {decision.updated_at
                ? new Date(decision.updated_at).toLocaleString()
                : "N/A"}
            </p>
          </div>

        </div>
      </div>

      <div className="details-card">
        <h2>Problem Statement</h2>

        <p>
          {decision.problem_statement ||
            "No problem statement provided."}
        </p>
      </div>

      <div className="details-card">
        <h2>Rationale</h2>

        <p>
          {decision.rationale ||
            "No rationale provided."}
        </p>
      </div>

  <div className="details-card">
  <h2>Attachments</h2>

  <form onSubmit={handleUploadAttachment}>
    <input
      type="file"
      onChange={(event) =>
        setSelectedFile(event.target.files[0] || null)
      }
    />

    <button
      type="submit"
      disabled={uploadingAttachment}
    >
      {uploadingAttachment
        ? "Uploading..."
        : "Upload Attachment"}
    </button>
  </form>

  {loadingAttachments ? (
    <p>Loading attachments...</p>
  ) : attachments.length === 0 ? (
    <p>No attachments uploaded yet.</p>
  ) : (
  <ul>
  {attachments.map((attachment) => (
    <li key={attachment.id}>
      <span>
        {attachment.file_name ||
          attachment.filename ||
          attachment.original_filename ||
          `Attachment #${attachment.id}`}
      </span>

      <button
        type="button"
        className="action-button delete-button"
        onClick={() =>
          handleDeleteAttachment(attachment.id)
        }
      >
        Delete
      </button>
    </li>
  ))}
</ul>
  )}
</div>

<div className="details-card">
  <h2>Meeting Notes</h2>

  <form onSubmit={handleCreateMeetingNote}>
    <input
      type="text"
      placeholder="Meeting title"
      value={newNoteTitle}
      onChange={(event) =>
        setNewNoteTitle(event.target.value)
      }
    />

    <textarea
      rows="4"
      placeholder="Meeting notes..."
      value={newNoteContent}
      onChange={(event) =>
        setNewNoteContent(event.target.value)
      }
    />

    <input
      type="date"
      value={newNoteDate}
      onChange={(event) =>
        setNewNoteDate(event.target.value)
      }
    />

    <button type="submit">
      Add Meeting Note
    </button>
  </form>

  <hr />

  {loadingMeetingNotes ? (
    <p>Loading meeting notes...</p>
  ) : meetingNotes.length === 0 ? (
    <p>No meeting notes yet.</p>
  ) : (
    <div className="comments-list">
      {meetingNotes.map((note) => (
        <div
          key={note.id}
          className="comment-card"
        >
          {editingNoteId === note.id ? (
            <>
              <input
                type="text"
                value={editingNoteTitle}
                onChange={(event) =>
                  setEditingNoteTitle(
                    event.target.value
                  )
                }
              />

              <textarea
                rows="4"
                value={editingNoteContent}
                onChange={(event) =>
                  setEditingNoteContent(
                    event.target.value
                  )
                }
              />

              <input
                type="date"
                value={editingNoteDate}
                onChange={(event) =>
                  setEditingNoteDate(
                    event.target.value
                  )
                }
              />

              <div className="decision-actions">
                <button
                  type="button"
                  className="action-button edit-button"
                  onClick={() =>
                    handleUpdateMeetingNote(note.id)
                  }
                >
                  Save
                </button>

                <button
                  type="button"
                  className="action-button"
                  onClick={handleCancelMeetingNoteEdit}
                >
                  Cancel
                </button>
              </div>
            </>
          ) : (
            <>
              <h3>{note.title}</h3>

              <p>{note.content}</p>

              <small>
                Meeting Date:{" "}
                {note.meeting_date
                  ? new Date(
                      note.meeting_date
                    ).toLocaleDateString()
                  : "N/A"}
              </small>

              <div className="decision-actions">
                <button
                  type="button"
                  className="action-button edit-button"
                  onClick={() =>
                    handleEditMeetingNote(note)
                  }
                >
                  Edit
                </button>

                <button
                  type="button"
                  className="action-button delete-button"
                  onClick={() =>
                    handleDeleteMeetingNote(note.id)
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
</div>

      <div className="details-card">

        <h2>Alternatives</h2>

        {decision.alternatives?.length > 0 ? (
          <ul>
            {decision.alternatives.map((alternative) => (
              <li key={alternative.id}>
                {alternative.name ||
                  alternative.title ||
                  `Alternative #${alternative.id}`}
              </li>
            ))}
          </ul>
        ) : (
          <p>No alternatives added yet.</p>
        )}

        <button
          type="button"
          onClick={() =>
            navigate(`/decisions/${id}/alternatives`)
          }
        >
          Open Alternative Analysis
        </button>

      </div>

    </div>
  );
}

export default DecisionDetails;