import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";

function KnowledgeRepository() {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState([]);
  const [tags, setTags] = useState([]);
  const [tagName, setTagName] = useState("");

  const [searchText, setSearchText] = useState("");
  const [category, setCategory] = useState("");
  const [decisionStatus, setDecisionStatus] = useState("");

  const [loading, setLoading] = useState(false);
  const [tagsLoading, setTagsLoading] = useState(false);

  const [error, setError] = useState("");
  const [tagError, setTagError] = useState("");
  const [tagMessage, setTagMessage] = useState("");

  const categories = [
    "Technology",
    "Finance",
    "Operations",
    "Human Resources",
    "Security",
    "Product",
    "Infrastructure",
    "Strategy",
  ];

  const statuses = [
    "Draft",
    "Under Review",
    "Approved",
    "Rejected",
  ];

  const fetchDecisions = async () => {
    try {
      setLoading(true);
      setError("");

      let response;

      if (searchText.trim()) {
        response = await api.get("/decisions/search", {
          params: {
            q: searchText.trim(),
          },
        });
      } else {
        response = await api.get("/decisions/discover", {
          params: {
            ...(category && { category }),
            ...(decisionStatus && {
              status: decisionStatus,
            }),
          },
        });
      }

      setDecisions(response.data);
    } catch (err) {
      console.error("Knowledge Repository error:", err);

      if (err.response?.data?.detail) {
        setError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to load decisions."
        );
      } else {
        setError("Unable to load decisions.");
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchTags = async () => {
    try {
      setTagsLoading(true);
      setTagError("");

      const response = await api.get("/tags");

      console.log("Tags response:", response.data);

      setTags(response.data);
    } catch (err) {
      console.error("Tags error:", err);

      if (err.response?.data?.detail) {
        setTagError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to load tags."
        );
      } else {
        setTagError("Unable to load tags.");
      }
    } finally {
      setTagsLoading(false);
    }
  };

  useEffect(() => {
    fetchDecisions();
    fetchTags();
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchDecisions();
  };

  const handleAddTag = async (e) => {
    e.preventDefault();

    setTagError("");
    setTagMessage("");

    if (!tagName.trim()) {
      setTagError("Tag name is required.");
      return;
    }

    try {
      const response = await api.post("/tags", {
        name: tagName.trim(),
      });

      setTags((current) => [...current, response.data]);

      setTagName("");

      setTagMessage("Tag added successfully.");
    } catch (err) {
      console.error("Add tag error:", err);

      if (err.response?.data?.detail) {
        setTagError(
          typeof err.response.data.detail === "string"
            ? err.response.data.detail
            : "Unable to add tag."
        );
      } else {
        setTagError("Unable to add tag.");
      }
    }
  };

  const handleClear = () => {
    setSearchText("");
    setCategory("");
    setDecisionStatus("");

    setTimeout(() => {
      fetchDecisions();
    }, 0);
  };

  return (
    <div>
      <h1>Knowledge Repository</h1>

      <p>
        Search and discover organizational decisions.
      </p>

      <hr />

      <h2>Search Decisions</h2>

      <form onSubmit={handleSearch}>
        <input
          type="text"
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
          placeholder="Search by title, problem or category"
        />

        <button
          type="submit"
          style={{ marginLeft: "10px" }}
        >
          Search
        </button>
      </form>

      <br />

      <div>
        <label>
          <strong>Category:</strong>
        </label>

        <br />

        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="">All Categories</option>

          {categories.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <br />

      <div>
        <label>
          <strong>Status:</strong>
        </label>

        <br />

        <select
          value={decisionStatus}
          onChange={(e) =>
            setDecisionStatus(e.target.value)
          }
        >
          <option value="">All Statuses</option>

          {statuses.map((item) => (
            <option key={item} value={item}>
              {item}
            </option>
          ))}
        </select>
      </div>

      <br />

      <button onClick={fetchDecisions}>
        Apply Filters
      </button>

      <button
        onClick={handleClear}
        style={{ marginLeft: "10px" }}
      >
        Clear
      </button>

      <hr />

      <h2>Tags</h2>

      <form onSubmit={handleAddTag}>
        <input
          type="text"
          value={tagName}
          onChange={(e) => setTagName(e.target.value)}
          placeholder="Enter tag name"
        />

        <button
          type="submit"
          style={{ marginLeft: "10px" }}
        >
          Add Tag
        </button>
      </form>

      {tagMessage && (
        <p>
          <strong>{tagMessage}</strong>
        </p>
      )}

      {tagError && <p>{tagError}</p>}

      <br />

      {tagsLoading ? (
        <p>Loading tags...</p>
      ) : tags.length === 0 ? (
        <p>No tags found.</p>
      ) : (
        <table border="1" cellPadding="10">
          <thead>
            <tr>
              <th>ID</th>
              <th>Tag Name</th>
            </tr>
          </thead>

          <tbody>
            {tags.map((tag) => (
              <tr key={tag.id}>
                <td>{tag.id}</td>
                <td>{tag.name}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      <hr />

      {loading && <p>Loading decisions...</p>}

      {error && <p>{error}</p>}

      {!loading &&
        !error &&
        decisions.length === 0 && (
          <p>No decisions found.</p>
        )}

      {!loading &&
        !error &&
        decisions.length > 0 && (
          <>
            <h2>Decision Repository</h2>

            <table border="1" cellPadding="10">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Problem Statement</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Created By</th>
                  <th>Created At</th>
                  <th>Updated At</th>
                  <th>Action</th>
                </tr>
              </thead>

              <tbody>
                {decisions.map((decision) => (
                  <tr key={decision.id}>
                    <td>{decision.id}</td>
                    <td>{decision.title}</td>
                    <td>{decision.problem_statement}</td>
                    <td>{decision.category}</td>
                    <td>{decision.status}</td>
                    <td>{decision.created_by}</td>
                    <td>
                      {decision.created_at
                        ? new Date(
                            decision.created_at
                          ).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      {decision.updated_at
                        ? new Date(
                            decision.updated_at
                          ).toLocaleString()
                        : "-"}
                    </td>
                    <td>
                      <button
                        onClick={() =>
                          navigate(
                            `/decisions/${decision.id}`
                          )
                        }
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </>
        )}

      <br />

      <button
        onClick={() => navigate("/dashboard")}
      >
        Back to Dashboard
      </button>
    </div>
  );
}

export default KnowledgeRepository;