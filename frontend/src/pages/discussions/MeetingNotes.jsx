import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axiosClient from "../../api/axiosClient";

const MeetingNotes = () => {
  const { decisionId } = useParams();

  const [notes, setNotes] = useState([]);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [meetingDate, setMeetingDate] = useState("");

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadNotes = async () => {
    try {
      const response = await axiosClient.get(
        `/decisions/${decisionId}/meeting-notes`
      );

      setNotes(response.data || []);
    } catch (err) {
      console.error(err);
      setError("Failed to load meeting notes.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadNotes();
  }, [decisionId]);

  const createNote = async (event) => {
    event.preventDefault();

    if (!title.trim()) {
      setError("Meeting title is required.");
      return;
    }

    if (!content.trim()) {
      setError("Meeting content is required.");
      return;
    }

    if (!meetingDate) {
      setError("Meeting date is required.");
      return;
    }

    try {
      await axiosClient.post(
        `/decisions/${decisionId}/meeting-notes`,
        {
          title,
          content,
          meeting_date: meetingDate,
        }
      );

      setTitle("");
      setContent("");
      setMeetingDate("");
      setError("");

      loadNotes();
    } catch (err) {
      console.error(err);
      setError("Failed to create meeting note.");
    }
  };

  if (loading) {
    return <p>Loading meeting notes...</p>;
  }

  return (
    <div>
      <h1>Meeting Notes</h1>

      {error && <p>{error}</p>}

      <h2>Add Meeting Note</h2>

      <form onSubmit={createNote}>
        <label>Title *</label>
        <br />

        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <br />
        <br />

        <label>Meeting Date *</label>
        <br />

        <input
          type="date"
          value={meetingDate}
          onChange={(e) =>
            setMeetingDate(e.target.value)
          }
        />

        <br />
        <br />

        <label>Content *</label>
        <br />

        <textarea
          value={content}
          onChange={(e) =>
            setContent(e.target.value)
          }
          rows="6"
          cols="50"
        />

        <br />

        <button type="submit">
          Save Meeting Note
        </button>
      </form>

      <hr />

      <h2>Previous Meeting Notes</h2>

      {notes.length === 0 ? (
        <p>No meeting notes available.</p>
      ) : (
        notes.map((note) => (
          <div
            key={note.id}
            style={{
              border: "1px solid #ccc",
              padding: "10px",
              marginBottom: "10px",
            }}
          >
            <h3>{note.title}</h3>

            <p>{note.content}</p>

            <p>
              Meeting Date: {note.meeting_date}
            </p>
          </div>
        ))
      )}
    </div>
  );
};

export default MeetingNotes;