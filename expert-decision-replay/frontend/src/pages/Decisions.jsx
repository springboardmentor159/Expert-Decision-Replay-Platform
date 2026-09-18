import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

import "./Decisions.css";

function Decisions() {
  const navigate = useNavigate();

  const [decisions, setDecisions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchDecisions();
  }, []);

  const fetchDecisions = async () => {
    try {
      setLoading(true);
      setMessage("");

      const response = await api.get("/decisions");

      const responseData = response.data;

      if (Array.isArray(responseData)) {
        setDecisions(responseData);
      } else if (Array.isArray(responseData?.decisions)) {
        setDecisions(responseData.decisions);
      } else if (Array.isArray(responseData?.data)) {
        setDecisions(responseData.data);
      } else {
        setDecisions([]);
        console.error(
          "Unexpected decisions response:",
          responseData
        );
      }
    } catch (error) {
      console.error("Error fetching decisions:", error);

      setMessage(
        error.response?.data?.detail ||
          "Unable to load decisions."
      );

      setDecisions([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewDecision = (decisionId) => {
    console.log("Clicked decision ID:", decisionId);

    if (!decisionId) {
      console.error("Decision ID is missing:", decisionId);
      setMessage("Unable to open decision: Decision ID is missing.");
      return;
    }

    navigate(`/decisions/${decisionId}`);
  };

  if (loading) {
    return (
      <div className="decisions-page">
        <div className="decisions-container">
          <p className="loading-message">
            Loading decisions...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="decisions-page">
      <div className="decisions-container">

        <div className="decisions-header">
          <div>
            <h1>All Decisions</h1>
            <p>
              View and manage your recorded decisions.
            </p>
          </div>

          <button
            className="refresh-button"
            onClick={fetchDecisions}
          >
            Refresh
          </button>
        </div>

        {message && (
          <div className="message-box">
            {message}
          </div>
        )}

        {decisions.length === 0 ? (
          <div className="empty-message">
            No decisions found.
          </div>
        ) : (
          <div className="decisions-grid">
            {decisions.map((decision) => (
              <div
                className="decision-list-card"
                key={decision.id}
              >
                <div className="decision-list-card-header">
                  <h2>
                    {decision.title ||
                      `Decision ${decision.id}`}
                  </h2>

                  <span className="status-badge">
                    {decision.status || "Unknown"}
                  </span>
                </div>

                <p className="decision-description">
                  {decision.description ||
                    "No description available."}
                </p>

                <div className="decision-meta">
                  <span>
                    <strong>ID:</strong>{" "}
                    {decision.id}
                  </span>

                  {decision.category && (
                    <span>
                      <strong>Category:</strong>{" "}
                      {decision.category}
                    </span>
                  )}
                </div>

                <button
                  type="button"
                  className="view-button"
                  onClick={() =>
                    handleViewDecision(decision.id)
                  }
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}

export default Decisions;