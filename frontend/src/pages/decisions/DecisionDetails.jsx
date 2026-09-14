import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import axiosClient from "../../api/axiosClient";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import StatusBadge from "../../components/StatusBadge";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";
import { useAuth } from "../../context/AuthContext";

const DecisionDetails = () => {
  const { decisionId } = useParams();
  const navigate = useNavigate();
  const { user, role } = useAuth();

  const [decision, setDecision] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [tags, setTags] = useState([]);
  const [availableTags, setAvailableTags] = useState([]);

  // --------------------------------------------------
  // STATUS STATE
  // --------------------------------------------------

  const [selectedStatus, setSelectedStatus] = useState("");
  const [statusUpdating, setStatusUpdating] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [statusError, setStatusError] = useState("");

  // --------------------------------------------------
  // TAG STATE
  // --------------------------------------------------

  const [selectedTag, setSelectedTag] = useState("");
  const [tagAdding, setTagAdding] = useState(false);
  const [tagMessage, setTagMessage] = useState("");
  const [tagError, setTagError] = useState("");

  const [newTagName, setNewTagName] = useState("");
  const [tagCreating, setTagCreating] = useState(false);

  // --------------------------------------------------
  // LOADING / ERROR STATE
  // --------------------------------------------------

  const [loading, setLoading] = useState(true);
  const [timelineLoading, setTimelineLoading] = useState(false);
  const [error, setError] = useState("");
  const [timelineError, setTimelineError] = useState("");

  // --------------------------------------------------
  // LOAD ALL AVAILABLE TAGS
  // --------------------------------------------------

  const loadAvailableTags = async () => {
    try {
      const response = await axiosClient.get("/tags");

      const data = response.data;

      setAvailableTags(
        Array.isArray(data)
          ? data
          : data?.items || data?.tags || []
      );
    } catch (err) {
      console.error("Available tags loading error:", err);

      setAvailableTags([]);
    }
  };

  // --------------------------------------------------
  // LOAD ASSIGNED TAGS
  // --------------------------------------------------

  const loadAssignedTags = async () => {
    try {
      const response = await axiosClient.get(
        `/decisions/${decisionId}/tags`
      );

      const data = response.data;

      setTags(
        Array.isArray(data)
          ? data
          : data?.tags || data?.items || []
      );
    } catch (err) {
      console.warn(
        "Assigned tags could not be loaded:",
        err
      );

      setTags([]);
    }
  };

  // --------------------------------------------------
  // LOAD DECISION DETAILS
  // --------------------------------------------------

  const loadDetails = async () => {
    try {
      setLoading(true);
      setError("");

      // ----------------------------------------------
      // LOAD MAIN DECISION
      // ----------------------------------------------

      const decisionResponse = await axiosClient.get(
        `/decisions/${decisionId}`
      );

      setDecision(decisionResponse.data);

      setSelectedStatus(
        decisionResponse.data?.status || ""
      );

      // ----------------------------------------------
      // LOAD TIMELINE
      // ----------------------------------------------

      await loadTimeline();

      // ----------------------------------------------
      // LOAD ASSIGNED TAGS
      // ----------------------------------------------

      await loadAssignedTags();

      // ----------------------------------------------
      // LOAD AVAILABLE TAGS
      // ----------------------------------------------

      await loadAvailableTags();

    } catch (err) {
      console.error(
        "Decision details error:",
        err
      );

      const status = err.response?.status;

      if (status === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (status === 403) {
        setError(
          "You do not have permission to view this decision."
        );
      } else if (status === 404) {
        setError("Decision not found.");
      } else if (status === 422) {
        setError("Invalid decision ID.");
      } else if (status >= 500) {
        setError(
          "Server error. Please try again later."
        );
      } else if (err.request) {
        setError(
          "Unable to connect to the backend. Please make sure FastAPI is running."
        );
      } else {
        setError(
          "Failed to load decision details."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // LOAD TIMELINE
  // --------------------------------------------------

  const loadTimeline = async () => {
    try {
      setTimelineLoading(true);
      setTimelineError("");

      const response = await axiosClient.get(
        `/decisions/${decisionId}/timeline`
      );

      console.log(
        "Timeline API response:",
        response.data
      );

      const data = response.data;

      let activities = [];

      if (Array.isArray(data)) {
        activities = data;
      } else if (Array.isArray(data?.activities)) {
        activities = data.activities;
      } else if (Array.isArray(data?.items)) {
        activities = data.items;
      } else if (Array.isArray(data?.timeline)) {
        activities = data.timeline;
      }

      setTimeline(activities);

    } catch (err) {
      console.error(
        "Timeline loading error:",
        err
      );

      const status = err.response?.status;

      if (status === 401) {
        setTimelineError(
          "You are not authenticated. Please login again."
        );
      } else if (status === 403) {
        setTimelineError(
          "You do not have permission to view this timeline."
        );
      } else if (status === 404) {
        setTimelineError(
          "Timeline endpoint was not found."
        );
      } else if (status === 422) {
        setTimelineError(
          "Invalid decision ID for timeline."
        );
      } else if (status >= 500) {
        setTimelineError(
          "Server error while loading timeline."
        );
      } else {
        setTimelineError(
          "Failed to load decision timeline."
        );
      }

      setTimeline([]);

    } finally {
      setTimelineLoading(false);
    }
  };

  // --------------------------------------------------
  // UPDATE DECISION STATUS
  // --------------------------------------------------

  const handleStatusUpdate = async () => {
    if (!decision) {
      return;
    }

    if (!selectedStatus) {
      setStatusError("Please select a status.");
      return;
    }

    if (selectedStatus === decision.status) {
      setStatusError(
        "Please select a different status."
      );
      return;
    }

    try {
      setStatusUpdating(true);
      setStatusMessage("");
      setStatusError("");

      const response = await axiosClient.patch(
        `/decisions/${decisionId}/status`,
        {
          status: selectedStatus,
        }
      );

      const updatedDecision = response.data;

      setDecision((previousDecision) => ({
        ...previousDecision,
        ...(updatedDecision || {}),
        status:
          updatedDecision?.status ||
          selectedStatus,
      }));

      setSelectedStatus(
        updatedDecision?.status ||
          selectedStatus
      );

      setStatusMessage(
        `Decision status updated to "${updatedDecision?.status || selectedStatus}".`
      );

      await loadTimeline();

    } catch (err) {
      console.error(
        "Status update error:",
        err
      );

      const status = err.response?.status;

      if (status === 401) {
        setStatusError(
          "Your session has expired. Please login again."
        );
      } else if (status === 403) {
        setStatusError(
          "You do not have permission to change this decision status."
        );
      } else if (status === 404) {
        setStatusError(
          "Decision not found."
        );
      } else if (status === 422) {
        setStatusError(
          err.response?.data?.detail ||
            "Invalid status value."
        );
      } else if (status >= 500) {
        setStatusError(
          "Server error while updating the decision status."
        );
      } else if (err.request) {
        setStatusError(
          "Unable to connect to the backend. Please make sure FastAPI is running."
        );
      } else {
        setStatusError(
          err.response?.data?.detail ||
            "Failed to update decision status."
        );
      }

      setSelectedStatus(
        decision.status || ""
      );

    } finally {
      setStatusUpdating(false);
    }
  };

  // --------------------------------------------------
  // ADD EXISTING TAG
  // --------------------------------------------------

  const handleAddTag = async () => {
    if (!selectedTag) {
      setTagError("Please select a tag.");
      return;
    }

    const tagId = Number(selectedTag);

    // Prevent duplicate assignment
    const alreadyAssigned = tags.some(
      (tag) => Number(tag.id) === tagId
    );

    if (alreadyAssigned) {
      setTagError(
        "This tag is already assigned to the decision."
      );
      return;
    }

    try {
      setTagAdding(true);
      setTagMessage("");
      setTagError("");

      await axiosClient.post(
        `/decisions/${decisionId}/tags`,
        {
          tag_ids: [tagId],
        }
      );

      setSelectedTag("");

      setTagMessage(
        "Tag added successfully."
      );

      await loadAssignedTags();
      await loadAvailableTags();
      await loadTimeline();

    } catch (err) {
      console.error(
        "Add tag error:",
        err
      );

      const status = err.response?.status;

      if (status === 401) {
        setTagError(
          "Your session has expired. Please login again."
        );
      } else if (status === 403) {
        setTagError(
          "You do not have permission to add tags."
        );
      } else if (status === 404) {
        setTagError(
          "Decision or tag was not found."
        );
      } else if (status === 422) {
        setTagError(
          err.response?.data?.detail ||
            "Invalid tag data."
        );
      } else if (status >= 500) {
        setTagError(
          "Server error while adding the tag."
        );
      } else if (err.request) {
        setTagError(
          "Unable to connect to the backend."
        );
      } else {
        setTagError(
          err.response?.data?.detail ||
            "Failed to add tag."
        );
      }

    } finally {
      setTagAdding(false);
    }
  };

  // --------------------------------------------------
  // CREATE NEW TAG
  // --------------------------------------------------

  const handleCreateTag = async () => {
    const trimmedName = newTagName.trim();

    if (!trimmedName) {
      setTagError(
        "Please enter a tag name."
      );
      return;
    }

    try {
      setTagCreating(true);
      setTagMessage("");
      setTagError("");

      const response = await axiosClient.post(
        "/tags",
        {
          name: trimmedName,
        }
      );

      const createdTag = response.data;

      setNewTagName("");

      setTagMessage(
        `Tag "${createdTag?.name || trimmedName}" created successfully.`
      );

      await loadAvailableTags();

      // Automatically select the newly created tag
      if (createdTag?.id) {
        setSelectedTag(
          String(createdTag.id)
        );
      }

    } catch (err) {
      console.error(
        "Create tag error:",
        err
      );

      const status = err.response?.status;

      if (status === 400) {
        setTagError(
          err.response?.data?.detail ||
            "Tag already exists."
        );
      } else if (status === 401) {
        setTagError(
          "Your session has expired. Please login again."
        );
      } else if (status === 403) {
        setTagError(
          "You do not have permission to create tags."
        );
      } else if (status === 422) {
        setTagError(
          "Invalid tag name."
        );
      } else if (status >= 500) {
        setTagError(
          "Server error while creating the tag."
        );
      } else if (err.request) {
        setTagError(
          "Unable to connect to the backend."
        );
      } else {
        setTagError(
          err.response?.data?.detail ||
            "Failed to create tag."
        );
      }

    } finally {
      setTagCreating(false);
    }
  };

  // --------------------------------------------------
  // REMOVE TAG
  // --------------------------------------------------

  const handleRemoveTag = async (tagId) => {
    try {
      setTagMessage("");
      setTagError("");

      await axiosClient.delete(
        `/decisions/${decisionId}/tags/${tagId}`
      );

      setTagMessage(
        "Tag removed successfully."
      );

      await loadAssignedTags();
      await loadAvailableTags();
      await loadTimeline();

    } catch (err) {
      console.error(
        "Remove tag error:",
        err
      );

      const status = err.response?.status;

      if (status === 401) {
        setTagError(
          "Your session has expired. Please login again."
        );
      } else if (status === 403) {
        setTagError(
          "You do not have permission to remove this tag."
        );
      } else if (status === 404) {
        setTagError(
          "Tag assignment was not found."
        );
      } else if (status >= 500) {
        setTagError(
          "Server error while removing the tag."
        );
      } else {
        setTagError(
          err.response?.data?.detail ||
            "Failed to remove tag."
        );
      }
    }
  };

  // --------------------------------------------------
  // LOAD WHEN DECISION ID CHANGES
  // --------------------------------------------------

  useEffect(() => {
    if (decisionId) {
      loadDetails();
    }
  }, [decisionId]);

  // --------------------------------------------------
  // FORMAT DATE
  // --------------------------------------------------

  const formatDate = (date) => {
    if (!date) {
      return "-";
    }

    const parsedDate = new Date(date);

    if (Number.isNaN(parsedDate.getTime())) {
      return date;
    }

    return parsedDate.toLocaleString();
  };

  // --------------------------------------------------
  // LOADING STATE
  // --------------------------------------------------

  if (loading) {
    return (
      <div className="decision-details-page">

        <PageHeader
          title="Decision Details"
          subtitle="Loading decision information..."
        />

        <div className="dashboard-loading">

          <div className="loading-spinner"></div>

          <p>
            Loading decision details...
          </p>

        </div>

      </div>
    );
  }

  // --------------------------------------------------
  // ERROR STATE
  // --------------------------------------------------

  if (error) {
    return (
      <div className="decision-details-page">

        <PageHeader
          title="Decision Details"
          subtitle="Unable to load the requested decision"
        />

        <Alert
          message={error}
          type="error"
        />

        <div className="decision-details-actions">

          <Button
            variant="secondary"
            onClick={() =>
              navigate("/decisions")
            }
          >
            ← Back to Decisions
          </Button>

          <Button onClick={loadDetails}>
            Try Again
          </Button>

        </div>

      </div>
    );
  }

  // --------------------------------------------------
  // NO DECISION
  // --------------------------------------------------

  if (!decision) {
    return (
      <div className="decision-details-page">

        <PageHeader
          title="Decision Details"
        />

        <EmptyState
          title="No decision information"
          message="The requested decision could not be loaded."
          action={
            <Button
              onClick={() =>
                navigate("/decisions")
              }
            >
              Back to Decisions
            </Button>
          }
        />

      </div>
    );
  }

  // --------------------------------------------------
  // MAIN PAGE
  // --------------------------------------------------

  return (
    <div className="decision-details-page">

      {/* =========================================
          PAGE HEADER
          ========================================= */}

      <PageHeader
        title="Decision Details"
        subtitle="View and manage decision information"
        action={
          <div className="decision-details-header-actions">

            <Button
              variant="secondary"
              onClick={() =>
                navigate("/decisions")
              }
            >
              ← Back
            </Button>

            <Button
              onClick={() =>
                navigate(
                  `/decisions/${decisionId}/edit`
                )
              }
            >
              Edit Decision
            </Button>

          </div>
        }
      />

      {/* =========================================
          DECISION OVERVIEW
          ========================================= */}

      <Card
        title="Decision Overview"
        className="decision-details-card"
      >

        <div className="decision-overview">

          <div className="decision-main-title">

            <h2>
              {decision.title ||
                "Untitled Decision"}
            </h2>

            <StatusBadge
              status={decision.status}
            />

          </div>

          <p className="decision-category">

            <strong>Category:</strong>{" "}

            {decision.category || "-"}

          </p>

        </div>

        <div className="decision-info-grid">

          <div className="decision-info-item">

            <span className="decision-info-label">
              Decision ID
            </span>

            <strong>
              {decision.id}
            </strong>

          </div>

          <div className="decision-info-item">

            <span className="decision-info-label">
              Created By
            </span>

            <strong>
              {decision.created_by || "-"}
            </strong>

          </div>

          <div className="decision-info-item">

            <span className="decision-info-label">
              Created At
            </span>

            <strong>
              {formatDate(
                decision.created_at
              )}
            </strong>

          </div>

          <div className="decision-info-item">

            <span className="decision-info-label">
              Last Updated
            </span>

            <strong>
              {formatDate(
                decision.updated_at
              )}
            </strong>

          </div>

        </div>

      </Card>

      {/* =========================================
          STATUS MANAGEMENT
          ========================================= */}

      <Card
        title="Decision Status"
        className="decision-details-card"
      >

        <div className="decision-feature-row">

          <div>

            <h3>
              Update Decision Status
            </h3>

            <p>
              Move the decision through the
              decision workflow.
            </p>

          </div>

          <div
            className="decision-status-controls"
            style={{
              display: "flex",
              alignItems: "center",
              gap: "10px",
              flexWrap: "wrap",
            }}
          >

            <select
              value={selectedStatus}
              onChange={(event) =>
                setSelectedStatus(
                  event.target.value
                )
              }
              disabled={statusUpdating}
              style={{
                padding: "10px 12px",
                borderRadius: "6px",
                border: "1px solid #ccc",
                minWidth: "160px",
                background: "#fff",
              }}
            >

              <option value="Draft">
                Draft
              </option>

              <option value="Under Review">
                Under Review
              </option>

              {(role === "Reviewer" ||
                role === "Manager" ||
                role === "Administrator") && (
                <>
                  <option value="Approved">
                    Approved
                  </option>

                  <option value="Rejected">
                    Rejected
                  </option>

                  <option value="Archived">
                    Archived
                  </option>
                </>
              )}

            </select>

            <Button
              onClick={handleStatusUpdate}
              disabled={
                statusUpdating ||
                selectedStatus ===
                  decision.status
              }
            >
              {statusUpdating
                ? "Updating..."
                : "Update Status"}
            </Button>

          </div>

        </div>

        {statusMessage && (
          <div
            style={{
              marginTop: "15px",
              padding: "10px 12px",
              borderRadius: "6px",
              background: "#e8f5e9",
              color: "#2e7d32",
            }}
          >
            {statusMessage}
          </div>
        )}

        {statusError && (
          <div
            style={{
              marginTop: "15px",
              padding: "10px 12px",
              borderRadius: "6px",
              background: "#ffebee",
              color: "#c62828",
            }}
          >
            {statusError}
          </div>
        )}

      </Card>

      {/* =========================================
          PROBLEM STATEMENT
          ========================================= */}

      <Card
        title="Problem Statement"
        className="decision-details-card"
      >

        <div className="decision-text-content">

          {decision.problem_statement ? (

            <p>
              {decision.problem_statement}
            </p>

          ) : (

            <p className="muted-text">
              No problem statement available.
            </p>

          )}

        </div>

      </Card>

      {/* =========================================
          RATIONALE
          ========================================= */}

      <Card
        title="Rationale"
        className="decision-details-card"
      >

        <div className="decision-text-content">

          {decision.rationale ? (

            <p>
              {decision.rationale}
            </p>

          ) : (

            <p className="muted-text">
              No rationale has been added yet.
            </p>

          )}

        </div>

        <div className="decision-section-actions">

          <Button
            variant="secondary"
            onClick={() =>
              navigate(
                `/decisions/${decisionId}/edit`
              )
            }
          >
            Edit Rationale
          </Button>

        </div>

      </Card>

      {/* =========================================
          TAGS
          ========================================= */}

      <Card
        title="Tags"
        className="decision-details-card"
      >

        {/* ASSIGNED TAGS */}

        <div>

          <h3>
            Assigned Tags
          </h3>

          {tags.length === 0 ? (

            <p className="muted-text">
              No tags have been assigned to this
              decision yet.
            </p>

          ) : (

            <div
              className="decision-tags"
              style={{
                display: "flex",
                flexWrap: "wrap",
                gap: "8px",
                marginBottom: "20px",
              }}
            >

              {tags.map((tag, index) => (

                <span
                  key={
                    tag.id ||
                    tag.name ||
                    index
                  }
                  className="decision-tag"
                  style={{
                    display: "inline-flex",
                    alignItems: "center",
                    gap: "6px",
                    padding: "7px 10px",
                    borderRadius: "16px",
                  }}
                >

                  {tag.name || tag}

                  {tag.id && (
                    <button
                      type="button"
                      onClick={() =>
                        handleRemoveTag(
                          tag.id
                        )
                      }
                      style={{
                        border: "none",
                        background: "transparent",
                        cursor: "pointer",
                        fontSize: "15px",
                        lineHeight: 1,
                        padding: 0,
                      }}
                      title="Remove tag"
                    >
                      ×
                    </button>
                  )}

                </span>

              ))}

            </div>

          )}

        </div>

        {/* ADD EXISTING TAG */}

        <div
          style={{
            marginTop: "15px",
            paddingTop: "15px",
            borderTop: "1px solid #eee",
          }}
        >

          <h3>
            Add Existing Tag
          </h3>

          <p>
            Select an existing tag and assign it
            to this decision.
          </p>

          <div
            style={{
              display: "flex",
              gap: "10px",
              alignItems: "center",
              flexWrap: "wrap",
              marginTop: "10px",
            }}
          >

            <select
              value={selectedTag}
              onChange={(event) => {
                setSelectedTag(
                  event.target.value
                );
                setTagError("");
                setTagMessage("");
              }}
              disabled={tagAdding}
              style={{
                padding: "10px 12px",
                borderRadius: "6px",
                border: "1px solid #ccc",
                minWidth: "220px",
                background: "#fff",
              }}
            >

              <option value="">
                Select a tag
              </option>

              {availableTags.map((tag) => (

                <option
                  key={tag.id}
                  value={tag.id}
                >
                  {tag.name}
                </option>

              ))}

            </select>

            <Button
              onClick={handleAddTag}
              disabled={
                tagAdding ||
                !selectedTag
              }
            >
              {tagAdding
                ? "Adding..."
                : "Add Tag"}
            </Button>

          </div>

        </div>

        {/* CREATE NEW TAG */}

        <div
          style={{
            marginTop: "20px",
            paddingTop: "15px",
            borderTop: "1px solid #eee",
          }}
        >

          <h3>
            Create New Tag
          </h3>

          <p>
            Create a new reusable tag and then
            assign it to this decision.
          </p>

          <div
            style={{
              display: "flex",
              gap: "10px",
              alignItems: "center",
              flexWrap: "wrap",
              marginTop: "10px",
            }}
          >

            <input
              type="text"
              value={newTagName}
              onChange={(event) => {
                setNewTagName(
                  event.target.value
                );
                setTagError("");
                setTagMessage("");
              }}
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleCreateTag();
                }
              }}
              placeholder="Enter new tag name"
              disabled={tagCreating}
              style={{
                padding: "10px 12px",
                borderRadius: "6px",
                border: "1px solid #ccc",
                minWidth: "220px",
                fontSize: "14px",
              }}
            />

            <Button
              variant="secondary"
              onClick={handleCreateTag}
              disabled={
                tagCreating ||
                !newTagName.trim()
              }
            >
              {tagCreating
                ? "Creating..."
                : "Create Tag"}
            </Button>

          </div>

        </div>

        {/* TAG SUCCESS MESSAGE */}

        {tagMessage && (
          <div
            style={{
              marginTop: "15px",
              padding: "10px 12px",
              borderRadius: "6px",
              background: "#e8f5e9",
              color: "#2e7d32",
            }}
          >
            {tagMessage}
          </div>
        )}

        {/* TAG ERROR MESSAGE */}

        {tagError && (
          <div
            style={{
              marginTop: "15px",
              padding: "10px 12px",
              borderRadius: "6px",
              background: "#ffebee",
              color: "#c62828",
            }}
          >
            {tagError}
          </div>
        )}

      </Card>

      {/* =========================================
          ALTERNATIVES
          ========================================= */}

      <Card
        title="Alternatives"
        className="decision-details-card"
      >

        <div className="decision-feature-row">

          <div>

            <h3>
              Alternative Analysis
            </h3>

            <p>
              Add, edit and compare alternatives
              for this decision.
            </p>

          </div>

          <Button
            onClick={() =>
              navigate(
                `/decisions/${decisionId}/alternatives`
              )
            }
          >
            Manage Alternatives
          </Button>

        </div>

      </Card>

      {/* =========================================
          DISCUSSION
          ========================================= */}

      <Card
        title="Discussion"
        className="decision-details-card"
      >

        <div className="decision-feature-row">

          <div>

            <h3>
              Decision Discussion
            </h3>

            <p>
              View comments, threads and meeting
              notes related to this decision.
            </p>

          </div>

          <Button
            onClick={() =>
              navigate(
                `/decisions/${decisionId}/discussion`
              )
            }
          >
            Open Discussion
          </Button>

        </div>

      </Card>

      {/* =========================================
          APPROVAL
          ========================================= */}

      <Card
        title="Approval"
        className="decision-details-card"
      >

        <div className="decision-feature-row">

          <div>

            <h3>
              Approval Workflow
            </h3>

            <p>
              View approval status and workflow
              information for this decision.
            </p>

          </div>

          <Button
            variant="secondary"
            onClick={() =>
              navigate("/approvals")
            }
          >
            View Approvals
          </Button>

        </div>

      </Card>

      {/* =========================================
          TIMELINE
          ========================================= */}

      <Card
        title="Decision Timeline"
        className="decision-details-card"
      >

        {/* TIMELINE ERROR */}

        {timelineError && (
          <Alert
            message={timelineError}
            type="error"
          />
        )}

        {/* TIMELINE LOADING */}

        {timelineLoading ? (

          <div className="dashboard-loading">

            <div className="loading-spinner"></div>

            <p>
              Loading timeline...
            </p>

          </div>

        ) : timeline.length === 0 ? (

          <EmptyState
            title="No timeline activities"
            message={
              timelineError
                ? "The timeline could not be loaded."
                : "No activity history is available for this decision."
            }
          />

        ) : (

          <div className="decision-timeline">

            {timeline.map(
              (activity, index) => (

                <div
                  className="decision-timeline-item"
                  key={
                    activity.id ||
                    index
                  }
                >

                  <div className="timeline-dot">
                    ●
                  </div>

                  <div className="timeline-content">

                    <strong>
                      {activity.activity_type ||
                        activity.type ||
                        activity.action ||
                        "Activity"}
                    </strong>

                    <p>
                      {activity.description ||
                        activity.message ||
                        activity.details ||
                        "Decision activity recorded."}
                    </p>

                    <div className="timeline-meta">

                      {(activity.created_by ||
                        activity.user_id ||
                        activity.user_name) && (

                        <span className="timeline-user">

                          <strong>
                            By:
                          </strong>{" "}

                          {activity.user_name ||
                            activity.created_by ||
                            activity.user_id}

                        </span>

                      )}

                      <span className="timeline-date">

                        {formatDate(
                          activity.created_at ||
                            activity.timestamp ||
                            activity.date
                        )}

                      </span>

                    </div>

                  </div>

                </div>

              )
            )}

          </div>

        )}

        <div className="decision-section-actions">

          <Button
            variant="secondary"
            onClick={loadTimeline}
            disabled={timelineLoading}
          >
            {timelineLoading
              ? "Refreshing..."
              : "Refresh Timeline"}
          </Button>

        </div>

      </Card>

      {/* =========================================
          BOTTOM ACTIONS
          ========================================= */}

      <div className="decision-details-actions">

        <Button
          variant="secondary"
          onClick={() =>
            navigate("/decisions")
          }
        >
          ← Back to Decisions
        </Button>

        <Button
          onClick={() =>
            navigate(
              `/decisions/${decisionId}/edit`
            )
          }
        >
          Edit Decision
        </Button>

      </div>

    </div>
  );
};

export default DecisionDetails;