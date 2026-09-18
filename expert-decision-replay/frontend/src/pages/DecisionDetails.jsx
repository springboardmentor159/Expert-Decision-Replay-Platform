import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api";

import "./DecisionDetails.css";

function DecisionDetails() {
  const { decisionId } = useParams();
  const navigate = useNavigate();

  const id = decisionId;

  const [decision, setDecision] = useState(null);
  const [alternatives, setAlternatives] = useState([]);
  const [comments, setComments] = useState([]);

  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  const [isEditing, setIsEditing] = useState(false);
  const [saving, setSaving] = useState(false);

  const [commentText, setCommentText] = useState("");
  const [addingComment, setAddingComment] = useState(false);

  const [showAlternativeForm, setShowAlternativeForm] = useState(false);
  const [addingAlternative, setAddingAlternative] = useState(false);

  const [alternativeForm, setAlternativeForm] = useState({
    name: "",
    description: "",
    pros: "",
    cons: "",
    estimated_cost: "",
    feasibility_score: 1,
    risk_level: "Low",
  });

  const [editForm, setEditForm] = useState({
    title: "",
    problem_statement: "",
    category: "",
    status: "",
    rationale: "",
  });

  // --------------------------------------------------
  // LOAD DECISION DETAILS
  // --------------------------------------------------

  useEffect(() => {
    if (!id) {
      setMessage("Decision ID is missing.");
      setLoading(false);
      return;
    }

    fetchDecisionDetails();
  }, [id]);

  const fetchDecisionDetails = async () => {
    try {
      setLoading(true);
      setMessage("");

      console.log("Loading decision ID:", id);

      // Main decision
      const decisionResponse = await api.get(`/decisions/${id}`);

      console.log(
        "Decision details response:",
        decisionResponse.data
      );

      const decisionData = decisionResponse.data;

      // Sometimes backend may return { decision: {...} }
      const actualDecision =
        decisionData?.decision || decisionData;

      setDecision(actualDecision);

      setEditForm({
        title: actualDecision.title || "",
        problem_statement:
          actualDecision.problem_statement ||
          actualDecision.description ||
          "",
        category: actualDecision.category || "",
        status: actualDecision.status || "",
        rationale: actualDecision.rationale || "",
      });

      // --------------------------------------------------
      // FETCH ALTERNATIVES
      // --------------------------------------------------

      try {
        const alternativesResponse = await api.get(
          `/decisions/${id}/alternatives/compare`
        );

        console.log(
          "Alternatives response:",
          alternativesResponse.data
        );

        const alternativesData = alternativesResponse.data;

        if (Array.isArray(alternativesData)) {
          setAlternatives(alternativesData);
        } else if (
          Array.isArray(alternativesData?.alternatives)
        ) {
          setAlternatives(alternativesData.alternatives);
        } else if (
          Array.isArray(alternativesData?.data)
        ) {
          setAlternatives(alternativesData.data);
        } else {
          setAlternatives([]);
        }
      } catch (error) {
        console.error(
          "Error fetching alternatives:",
          error
        );

        // Don't stop the main decision page
        setAlternatives([]);
      }

      // --------------------------------------------------
      // FETCH COMMENTS
      // --------------------------------------------------

      try {
        const commentsResponse = await api.get(
          `/decisions/${id}/comments`
        );

        console.log(
          "Comments response:",
          commentsResponse.data
        );

        const commentsData = commentsResponse.data;

        if (Array.isArray(commentsData)) {
          setComments(commentsData);
        } else if (
          Array.isArray(commentsData?.comments)
        ) {
          setComments(commentsData.comments);
        } else if (
          Array.isArray(commentsData?.data)
        ) {
          setComments(commentsData.data);
        } else {
          setComments([]);
        }
      } catch (error) {
        console.error(
          "Error fetching comments:",
          error
        );

        // Don't stop the main decision page
        setComments([]);
      }
    } catch (error) {
      console.error(
        "Error fetching decision:",
        error
      );

      const detail = error.response?.data?.detail;

      if (Array.isArray(detail)) {
        setMessage(
          detail
            .map((item) => item.msg)
            .join(", ")
        );
      } else if (typeof detail === "object") {
        setMessage(
          detail?.message ||
            "Unable to load decision details."
        );
      } else {
        setMessage(
          detail ||
            "Unable to load decision details."
        );
      }

      setDecision(null);
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // EDIT DECISION
  // --------------------------------------------------

  const handleEditChange = (event) => {
    const { name, value } = event.target;

    setEditForm((previousForm) => ({
      ...previousForm,
      [name]: value,
    }));
  };

  const handleUpdateDecision = async (event) => {
    event.preventDefault();

    try {
      setSaving(true);
      setMessage("");

      const response = await api.put(
        `/decisions/${id}`,
        {
          title: editForm.title,
          problem_statement:
            editForm.problem_statement,
          category: editForm.category,
          status: editForm.status,
          rationale: editForm.rationale,
        }
      );

      console.log(
        "Updated decision:",
        response.data
      );

      const updatedDecision =
        response.data?.decision ||
        response.data;

      setDecision(updatedDecision);

      setEditForm({
        title: updatedDecision.title || "",
        problem_statement:
          updatedDecision.problem_statement ||
          updatedDecision.description ||
          "",
        category:
          updatedDecision.category || "",
        status:
          updatedDecision.status || "",
        rationale:
          updatedDecision.rationale || "",
      });

      setIsEditing(false);
      setMessage(
        "Decision updated successfully."
      );
    } catch (error) {
      console.error(
        "Error updating decision:",
        error
      );

      const detail =
        error.response?.data?.detail;

      if (Array.isArray(detail)) {
        setMessage(
          detail
            .map((item) => item.msg)
            .join(", ")
        );
      } else if (typeof detail === "object") {
        setMessage(
          detail?.message ||
            "Unable to update decision."
        );
      } else {
        setMessage(
          detail ||
            "Unable to update decision."
        );
      }
    } finally {
      setSaving(false);
    }
  };

  // --------------------------------------------------
  // ADD COMMENT
  // --------------------------------------------------

  const handleAddComment = async (event) => {
    event.preventDefault();

    if (!commentText.trim()) {
      setMessage("Please enter a comment.");
      return;
    }

    try {
      setAddingComment(true);
      setMessage("");

      await api.post(
        `/decisions/${id}/comments`,
        {
          content: commentText.trim(),
        }
      );

      setCommentText("");

      setMessage(
        "Comment added successfully."
      );

      // Reload comments
      const commentsResponse = await api.get(
        `/decisions/${id}/comments`
      );

      const commentsData =
        commentsResponse.data;

      if (Array.isArray(commentsData)) {
        setComments(commentsData);
      } else if (
        Array.isArray(commentsData?.comments)
      ) {
        setComments(
          commentsData.comments
        );
      } else if (
        Array.isArray(commentsData?.data)
      ) {
        setComments(commentsData.data);
      } else {
        setComments([]);
      }
    } catch (error) {
      console.error(
        "Error adding comment:",
        error
      );

      const detail =
        error.response?.data?.detail;

      if (Array.isArray(detail)) {
        setMessage(
          detail
            .map((item) => item.msg)
            .join(", ")
        );
      } else {
        setMessage(
          detail ||
            "Unable to add comment."
        );
      }
    } finally {
      setAddingComment(false);
    }
  };

  // --------------------------------------------------
  // ALTERNATIVE FORM
  // --------------------------------------------------

  const handleAlternativeChange = (event) => {
    const { name, value } = event.target;

    setAlternativeForm(
      (previousForm) => ({
        ...previousForm,
        [name]: value,
      })
    );
  };

  const handleAddAlternative = async (
    event
  ) => {
    event.preventDefault();

    if (!alternativeForm.name.trim()) {
      setMessage(
        "Please enter alternative name."
      );
      return;
    }

    if (!alternativeForm.description.trim()) {
      setMessage(
        "Please enter alternative description."
      );
      return;
    }

    if (!alternativeForm.pros.trim()) {
      setMessage(
        "Please enter alternative pros."
      );
      return;
    }

    if (!alternativeForm.cons.trim()) {
      setMessage(
        "Please enter alternative cons."
      );
      return;
    }

    if (
      alternativeForm.estimated_cost === ""
    ) {
      setMessage(
        "Please enter estimated cost."
      );
      return;
    }

    try {
      setAddingAlternative(true);
      setMessage("");

      await api.post(
        "/alternatives/",
        {
          decision_id: Number(id),
          name: alternativeForm.name.trim(),
          description:
            alternativeForm.description.trim(),
          pros: alternativeForm.pros.trim(),
          cons: alternativeForm.cons.trim(),
          estimated_cost: Number(
            alternativeForm.estimated_cost
          ),
          feasibility_score: Number(
            alternativeForm.feasibility_score
          ),
          risk_level:
            alternativeForm.risk_level,
        }
      );

      setAlternativeForm({
        name: "",
        description: "",
        pros: "",
        cons: "",
        estimated_cost: "",
        feasibility_score: 1,
        risk_level: "Low",
      });

      setShowAlternativeForm(false);

      setMessage(
        "Alternative added successfully."
      );

      // Reload alternatives
      try {
        const alternativesResponse =
          await api.get(
            `/decisions/${id}/alternatives/compare`
          );

        const alternativesData =
          alternativesResponse.data;

        if (Array.isArray(alternativesData)) {
          setAlternatives(
            alternativesData
          );
        } else if (
          Array.isArray(
            alternativesData?.alternatives
          )
        ) {
          setAlternatives(
            alternativesData.alternatives
          );
        } else if (
          Array.isArray(
            alternativesData?.data
          )
        ) {
          setAlternatives(
            alternativesData.data
          );
        } else {
          setAlternatives([]);
        }
      } catch (error) {
        console.error(
          "Error reloading alternatives:",
          error
        );
      }
    } catch (error) {
      console.error(
        "Error adding alternative:",
        error
      );

      const detail =
        error.response?.data?.detail;

      if (Array.isArray(detail)) {
        setMessage(
          detail
            .map((item) => item.msg)
            .join(", ")
        );
      } else if (
        typeof detail === "object"
      ) {
        setMessage(
          detail?.message ||
            "Unable to add alternative."
        );
      } else {
        setMessage(
          detail ||
            "Unable to add alternative."
        );
      }
    } finally {
      setAddingAlternative(false);
    }
  };

  // --------------------------------------------------
  // LOADING
  // --------------------------------------------------

  if (loading) {
    return (
      <div className="decision-details-page">
        <div className="loading-message">
          Loading decision details...
        </div>
      </div>
    );
  }

  // --------------------------------------------------
  // DECISION NOT FOUND
  // --------------------------------------------------

  if (!decision) {
    return (
      <div className="decision-details-page">
        <div className="error-message">
          {message ||
            "Decision not found."}
        </div>

        <button
          type="button"
          className="back-button"
          onClick={() =>
            navigate("/decisions")
          }
        >
          Back to Decisions
        </button>
      </div>
    );
  }

  const problemStatement =
    decision.problem_statement ||
    decision.description ||
    "Not available";

  // --------------------------------------------------
  // MAIN UI
  // --------------------------------------------------

  return (
    <div className="decision-details-page">
      <div className="decision-details-container">

        {/* PAGE HEADER */}

        <div className="page-header">
          <div>
            <h1>Decision Details</h1>

            <p>
              View and manage the selected
              decision.
            </p>
          </div>

          <button
            type="button"
            className="back-button"
            onClick={() =>
              navigate("/decisions")
            }
          >
            Back to Decisions
          </button>
        </div>

        {/* MESSAGE */}

        {message && (
          <div className="message-box">
            {message}
          </div>
        )}

        {/* DECISION INFORMATION */}

        <div className="decision-card">
          <div className="decision-card-header">
            <h2>
              Decision Information
            </h2>

            {!isEditing && (
              <button
                type="button"
                className="edit-button"
                onClick={() =>
                  setIsEditing(true)
                }
              >
                Edit Decision
              </button>
            )}
          </div>

          {isEditing ? (
            <form
              className="decision-edit-form"
              onSubmit={
                handleUpdateDecision
              }
            >
              <div className="form-group">
                <label htmlFor="title">
                  Title
                </label>

                <input
                  id="title"
                  name="title"
                  type="text"
                  value={editForm.title}
                  onChange={
                    handleEditChange
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="problem_statement">
                  Problem Statement
                </label>

                <textarea
                  id="problem_statement"
                  name="problem_statement"
                  rows="4"
                  value={
                    editForm.problem_statement
                  }
                  onChange={
                    handleEditChange
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="category">
                  Category
                </label>

                <input
                  id="category"
                  name="category"
                  type="text"
                  value={editForm.category}
                  onChange={
                    handleEditChange
                  }
                />
              </div>

              <div className="form-group">
                <label htmlFor="status">
                  Status
                </label>

                <select
                  id="status"
                  name="status"
                  value={editForm.status}
                  onChange={
                    handleEditChange
                  }
                >
                  <option value="">
                    Select Status
                  </option>

                  <option value="Draft">
                    Draft
                  </option>

                  <option value="Pending">
                    Pending
                  </option>

                  <option value="Approved">
                    Approved
                  </option>

                  <option value="Rejected">
                    Rejected
                  </option>

                  <option value="Completed">
                    Completed
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="rationale">
                  Rationale
                </label>

                <textarea
                  id="rationale"
                  name="rationale"
                  rows="4"
                  value={editForm.rationale}
                  onChange={
                    handleEditChange
                  }
                />
              </div>

              <div className="form-actions">
                <button
                  type="submit"
                  className="save-button"
                  disabled={saving}
                >
                  {saving
                    ? "Saving..."
                    : "Save Changes"}
                </button>

                <button
                  type="button"
                  className="cancel-button"
                  onClick={() =>
                    setIsEditing(false)
                  }
                  disabled={saving}
                >
                  Cancel
                </button>
              </div>
            </form>
          ) : (
            <div className="decision-information">

              <div className="detail-row">
                <span className="detail-label">
                  Decision ID
                </span>

                <span className="detail-value">
                  {decision.id}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">
                  Title
                </span>

                <span className="detail-value">
                  {decision.title ||
                    "Not available"}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">
                  Problem Statement
                </span>

                <span className="detail-value">
                  {problemStatement}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">
                  Category
                </span>

                <span className="detail-value">
                  {decision.category ||
                    "Not available"}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">
                  Status
                </span>

                <span className="status-badge">
                  {decision.status ||
                    "Not available"}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">
                  Rationale
                </span>

                <span className="detail-value">
                  {decision.rationale ||
                    "Not available"}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">
                  Created At
                </span>

                <span className="detail-value">
                  {decision.created_at
                    ? new Date(
                        decision.created_at
                      ).toLocaleString()
                    : "Not available"}
                </span>
              </div>

              <div className="detail-row">
                <span className="detail-label">
                  Updated At
                </span>

                <span className="detail-value">
                  {decision.updated_at
                    ? new Date(
                        decision.updated_at
                      ).toLocaleString()
                    : "Not available"}
                </span>
              </div>

            </div>
          )}
        </div>

        {/* ALTERNATIVES */}

        <div className="alternatives-section">
          <div className="section-header">
            <h2>Alternatives</h2>

            <div>
              <span className="section-count">
                {alternatives.length} alternatives
              </span>

              <button
                type="button"
                className="edit-button"
                onClick={() =>
                  setShowAlternativeForm(
                    !showAlternativeForm
                  )
                }
              >
                {showAlternativeForm
                  ? "Cancel"
                  : "Add Alternative"}
              </button>
            </div>
          </div>

          {/* ADD ALTERNATIVE FORM */}

          {showAlternativeForm && (
            <form
              className="decision-edit-form"
              onSubmit={
                handleAddAlternative
              }
            >
              <div className="form-group">
                <label htmlFor="alternative-name">
                  Alternative Name
                </label>

                <input
                  id="alternative-name"
                  name="name"
                  type="text"
                  value={
                    alternativeForm.name
                  }
                  onChange={
                    handleAlternativeChange
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="alternative-description">
                  Description
                </label>

                <textarea
                  id="alternative-description"
                  name="description"
                  rows="3"
                  value={
                    alternativeForm.description
                  }
                  onChange={
                    handleAlternativeChange
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="alternative-pros">
                  Pros
                </label>

                <textarea
                  id="alternative-pros"
                  name="pros"
                  rows="2"
                  value={
                    alternativeForm.pros
                  }
                  onChange={
                    handleAlternativeChange
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="alternative-cons">
                  Cons
                </label>

                <textarea
                  id="alternative-cons"
                  name="cons"
                  rows="2"
                  value={
                    alternativeForm.cons
                  }
                  onChange={
                    handleAlternativeChange
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="estimated-cost">
                  Estimated Cost
                </label>

                <input
                  id="estimated-cost"
                  name="estimated_cost"
                  type="number"
                  min="0"
                  value={
                    alternativeForm.estimated_cost
                  }
                  onChange={
                    handleAlternativeChange
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="feasibility-score">
                  Feasibility Score
                </label>

                <select
                  id="feasibility-score"
                  name="feasibility_score"
                  value={
                    alternativeForm.feasibility_score
                  }
                  onChange={
                    handleAlternativeChange
                  }
                  required
                >
                  <option value="1">
                    1
                  </option>

                  <option value="2">
                    2
                  </option>

                  <option value="3">
                    3
                  </option>

                  <option value="4">
                    4
                  </option>

                  <option value="5">
                    5
                  </option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="risk-level">
                  Risk Level
                </label>

                <select
                  id="risk-level"
                  name="risk_level"
                  value={
                    alternativeForm.risk_level
                  }
                  onChange={
                    handleAlternativeChange
                  }
                  required
                >
                  <option value="Low">
                    Low
                  </option>

                  <option value="Medium">
                    Medium
                  </option>

                  <option value="High">
                    High
                  </option>
                </select>
              </div>

              <div className="form-actions">
                <button
                  type="submit"
                  className="save-button"
                  disabled={
                    addingAlternative
                  }
                >
                  {addingAlternative
                    ? "Adding..."
                    : "Save Alternative"}
                </button>

                <button
                  type="button"
                  className="cancel-button"
                  onClick={() =>
                    setShowAlternativeForm(
                      false
                    )
                  }
                  disabled={
                    addingAlternative
                  }
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* ALTERNATIVE LIST */}

          {alternatives.length === 0 ? (
            <div className="empty-message">
              No alternatives available for
              this decision.
            </div>
          ) : (
            <div className="alternatives-grid">
              {alternatives.map(
                (alternative) => (
                  <div
                    className="alternative-card"
                    key={alternative.id}
                  >
                    <h3>
                      {alternative.name ||
                        alternative.title ||
                        `Alternative ${alternative.id}`}
                    </h3>

                    <p>
                      {alternative.description ||
                        "No description available."}
                    </p>

                    {alternative.feasibility_score !==
                      undefined && (
                      <div className="alternative-detail">
                        <strong>
                          Feasibility Score:
                        </strong>{" "}
                        {
                          alternative.feasibility_score
                        }
                      </div>
                    )}

                    {alternative.risk_level && (
                      <div className="alternative-detail">
                        <strong>
                          Risk:
                        </strong>{" "}
                        {
                          alternative.risk_level
                        }
                      </div>
                    )}

                    {alternative.estimated_cost !==
                      undefined && (
                      <div className="alternative-detail">
                        <strong>
                          Estimated Cost:
                        </strong>{" "}
                        {
                          alternative.estimated_cost
                        }
                      </div>
                    )}

                    {alternative.pros && (
                      <div className="alternative-detail">
                        <strong>
                          Pros:
                        </strong>{" "}
                        {alternative.pros}
                      </div>
                    )}

                    {alternative.cons && (
                      <div className="alternative-detail">
                        <strong>
                          Cons:
                        </strong>{" "}
                        {alternative.cons}
                      </div>
                    )}
                  </div>
                )
              )}
            </div>
          )}
        </div>

        {/* COMMENTS */}

        <div className="comments-section">
          <div className="section-header">
            <h2>Comments</h2>

            <span className="section-count">
              {comments.length} comments
            </span>
          </div>

          {/* ADD COMMENT */}

          <form
            className="comment-form"
            onSubmit={handleAddComment}
          >
            <label htmlFor="comment">
              Add a Comment
            </label>

            <textarea
              id="comment"
              rows="4"
              placeholder="Write your comment here..."
              value={commentText}
              onChange={(event) =>
                setCommentText(
                  event.target.value
                )
              }
            />

            <button
              type="submit"
              className="comment-submit-button"
              disabled={addingComment}
            >
              {addingComment
                ? "Adding..."
                : "Add Comment"}
            </button>
          </form>

          {/* COMMENTS LIST */}

          {comments.length === 0 ? (
            <div className="empty-message">
              No comments available for this
              decision.
            </div>
          ) : (
            <div className="comments-list">
              {comments.map((comment) => (
                <div
                  className="comment-card"
                  key={comment.id}
                >
                  <div className="comment-header">
                    <span className="comment-user">
                      User ID:{" "}
                      {comment.user_id}
                    </span>

                    <span className="comment-date">
                      {comment.created_at
                        ? new Date(
                            comment.created_at
                          ).toLocaleString()
                        : ""}
                    </span>
                  </div>

                  <p className="comment-content">
                    {comment.content}
                  </p>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}

export default DecisionDetails;