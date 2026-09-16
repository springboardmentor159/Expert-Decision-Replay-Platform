import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";

import {
  AlertCircle,
  ArrowLeft,
  BarChart3,
  CheckCircle2,
  DollarSign,
  Gauge,
  Loader2,
  ShieldAlert,
  Target,
} from "lucide-react";

import apiClient from "../api/apiClient";


function formatCost(value) {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return "—";
  }

  const number = Number(value);

  if (Number.isNaN(number)) {
    return String(value);
  }

  return number.toLocaleString(undefined, {
    maximumFractionDigits: 2,
  });
}


function getRiskClass(riskLevel) {
  switch (riskLevel) {
    case "Low":
      return "ac-risk-low";

    case "Medium":
      return "ac-risk-medium";

    case "High":
      return "ac-risk-high";

    case "Critical":
      return "ac-risk-critical";

    default:
      return "ac-risk-default";
  }
}


function extractAlternatives(data) {
  if (Array.isArray(data)) {
    return data;
  }

  if (Array.isArray(data?.alternatives)) {
    return data.alternatives;
  }

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  if (Array.isArray(data?.results)) {
    return data.results;
  }

  return [];
}


function getErrorMessage(error) {
  const status =
    error?.response?.status;

  const detail =
    error?.response?.data?.detail;

  if (status === 400) {
    return (
      detail ||
      "The comparison request is invalid."
    );
  }

  if (status === 401) {
    return (
      "Your session has expired. Please log in again."
    );
  }

  if (status === 403) {
    return (
      detail ||
      "You do not have permission to compare these alternatives."
    );
  }

  if (status === 404) {
    return (
      detail ||
      "The decision or alternatives were not found."
    );
  }

  if (status === 422) {
    return (
      detail ||
      "The comparison request contains invalid information."
    );
  }

  if (status >= 500) {
    return (
      "A server error occurred while loading the comparison."
    );
  }

  return (
    detail ||
    error?.message ||
    "Unable to load the alternative comparison."
  );
}


function getStatusClass(status) {
  switch (status) {
    case "Approved":
      return "ac-status-approved";

    case "Under Review":
      return "ac-status-review";

    case "Rejected":
      return "ac-status-rejected";

    case "Archived":
      return "ac-status-archived";

    default:
      return "ac-status-draft";
  }
}


export default function AlternativeComparison() {
  const {
    decisionId,
  } = useParams();


  const [decision, setDecision] =
    useState(null);

  const [alternatives, setAlternatives] =
    useState([]);


  const [loading, setLoading] =
    useState(true);

  const [errorMessage, setErrorMessage] =
    useState("");


  useEffect(() => {
    loadComparison();
  }, [decisionId]);


  async function loadComparison() {
    try {
      setLoading(true);
      setErrorMessage("");

      const [
        decisionResponse,
        alternativesResponse,
      ] = await Promise.all([
        apiClient.get(
          `/decisions/${decisionId}`
        ),

        apiClient.get(
          `/alternatives/decision/${decisionId}`
        ),
      ]);


      setDecision(
        decisionResponse.data
      );

      setAlternatives(
        extractAlternatives(
          alternativesResponse.data
        )
      );

    } catch (error) {
      console.error(
        "Failed to load alternative comparison:",
        error
      );

      setErrorMessage(
        getErrorMessage(error)
      );

    } finally {
      setLoading(false);
    }
  }


  if (loading) {
    return (
      <div className="ac-page">

        <style>{`
          .ac-page {
            width: 100%;
          }

          .ac-loading {
            min-height: 420px;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 12px;
            color: #64748b;
            font-size: 13px;
          }

          .ac-spin {
            animation: acSpin 1s linear infinite;
          }

          @keyframes acSpin {
            from {
              transform: rotate(0deg);
            }

            to {
              transform: rotate(360deg);
            }
          }
        `}</style>

        <div className="ac-loading">

          <Loader2
            size={28}
            className="ac-spin"
          />

          <span>
            Loading alternative comparison...
          </span>

        </div>

      </div>
    );
  }


  if (errorMessage) {
    return (
      <div className="ac-page">

        <style>{`
          .ac-page {
            width: 100%;
          }

          .ac-error-card {
            max-width: 600px;
            margin: 70px auto;
            padding: 32px;
            border: 1px solid #fecaca;
            border-radius: 17px;
            background: #fff;
            text-align: center;
            box-shadow:
              0 10px 30px
              rgba(15,23,42,.06);
          }

          .ac-error-icon {
            width: 54px;
            height: 54px;
            margin: 0 auto 16px;
            border-radius: 15px;
            background: #fef2f2;
            color: #dc2626;
            display: flex;
            align-items: center;
            justify-content: center;
          }

          .ac-error-card h2 {
            margin: 0 0 7px;
            color: #0f172a;
            font-size: 19px;
          }

          .ac-error-card p {
            margin: 0 0 20px;
            color: #64748b;
            font-size: 13px;
            line-height: 1.6;
          }

          .ac-button {
            min-height: 40px;
            padding: 0 14px;
            border-radius: 8px;
            border: 1px solid #cbd5e1;
            background: #fff;
            color: #475569;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            font-family: inherit;
            font-size: 11px;
            font-weight: 750;
            text-decoration: none;
            cursor: pointer;
          }

          .ac-button:hover {
            background: #f8fafc;
          }
        `}</style>

        <div className="ac-error-card">

          <div className="ac-error-icon">
            <AlertCircle size={26} />
          </div>

          <h2>
            Unable to Load Comparison
          </h2>

          <p>
            {errorMessage}
          </p>

          <button
            type="button"
            className="ac-button"
            onClick={loadComparison}
          >
            Try Again
          </button>

        </div>

      </div>
    );
  }


  return (
    <div className="ac-page">

      <style>{`
        .ac-page {
          width: 100%;
          max-width: 1200px;
          margin: 0 auto;
          padding: 4px 0 40px;
        }

        .ac-header {
          display: flex;
          align-items: flex-start;
          justify-content: space-between;
          gap: 20px;
          margin-bottom: 22px;
        }

        .ac-header-main {
          display: flex;
          align-items: flex-start;
          gap: 14px;
        }

        .ac-header-icon {
          width: 49px;
          height: 49px;
          min-width: 49px;
          border-radius: 14px;
          background: #eaf2ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ac-back {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          margin-bottom: 6px;
          color: #64748b;
          text-decoration: none;
          font-size: 11px;
          font-weight: 700;
        }

        .ac-back:hover {
          color: #2563eb;
        }

        .ac-eyebrow {
          margin-bottom: 4px;
          color: #64748b;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: .1em;
          text-transform: uppercase;
        }

        .ac-header h1 {
          margin: 0;
          color: #0f172a;
          font-size: 28px;
          line-height: 1.2;
        }

        .ac-header-description {
          max-width: 680px;
          margin: 6px 0 0;
          color: #64748b;
          font-size: 13px;
          line-height: 1.5;
        }

        .ac-header-actions {
          display: flex;
          align-items: center;
          gap: 8px;
          flex-shrink: 0;
        }

        .ac-button-primary {
          border-color: #2563eb;
          background: #2563eb;
          color: #fff;
        }

        .ac-button-primary:hover {
          background: #1d4ed8;
        }

        .ac-decision-card {
          overflow: hidden;
          margin-bottom: 20px;
          border: 1px solid #dbeafe;
          border-radius: 16px;
          background: #fff;
          box-shadow:
            0 7px 25px
            rgba(15,23,42,.05);
        }

        .ac-decision-top {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 15px;
          padding: 20px 22px;
          background: #f8fbff;
          border-bottom: 1px solid #e2e8f0;
        }

        .ac-decision-label {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 5px;
          color: #2563eb;
          font-size: 10px;
          font-weight: 800;
          letter-spacing: .08em;
          text-transform: uppercase;
        }

        .ac-decision-title {
          margin: 0;
          color: #0f172a;
          font-size: 18px;
          line-height: 1.3;
        }

        .ac-decision-problem {
          margin: 0;
          padding: 18px 22px;
          color: #64748b;
          font-size: 12px;
          line-height: 1.65;
        }

        .ac-status {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 6px 9px;
          border-radius: 999px;
          font-size: 10px;
          font-weight: 800;
          white-space: nowrap;
        }

        .ac-status-approved {
          background: #dcfce7;
          color: #166534;
        }

        .ac-status-review {
          background: #fef3c7;
          color: #92400e;
        }

        .ac-status-rejected {
          background: #fee2e2;
          color: #991b1b;
        }

        .ac-status-archived {
          background: #e2e8f0;
          color: #475569;
        }

        .ac-status-draft {
          background: #dbeafe;
          color: #1d4ed8;
        }

        .ac-comparison-card {
          overflow: hidden;
          margin-bottom: 20px;
          border: 1px solid #e2e8f0;
          border-radius: 16px;
          background: #fff;
          box-shadow:
            0 7px 25px
            rgba(15,23,42,.05);
        }

        .ac-card-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          gap: 15px;
          padding: 19px 22px;
          border-bottom: 1px solid #e2e8f0;
          background: #f8fafc;
        }

        .ac-card-heading {
          display: flex;
          align-items: center;
          gap: 10px;
        }

        .ac-card-icon {
          width: 35px;
          height: 35px;
          border-radius: 9px;
          background: #dbeafe;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ac-card-header h2 {
          margin: 0;
          color: #0f172a;
          font-size: 16px;
        }

        .ac-card-header p {
          margin: 4px 0 0;
          color: #64748b;
          font-size: 11px;
        }

        .ac-count {
          padding: 6px 9px;
          border-radius: 999px;
          background: #e2e8f0;
          color: #475569;
          font-size: 10px;
          font-weight: 800;
        }

        .ac-table-wrap {
          width: 100%;
          overflow-x: auto;
        }

        .ac-table {
          width: 100%;
          min-width: 820px;
          border-collapse: collapse;
        }

        .ac-table th,
        .ac-table td {
          padding: 15px 17px;
          border-bottom: 1px solid #e2e8f0;
          text-align: left;
          vertical-align: top;
        }

        .ac-table thead th {
          background: #f8fafc;
          color: #475569;
          font-size: 10px;
          font-weight: 800;
          text-transform: uppercase;
          letter-spacing: .04em;
        }

        .ac-table thead th:first-child {
          width: 175px;
          color: #64748b;
        }

        .ac-table thead th:not(:first-child) {
          color: #0f172a;
          font-size: 12px;
          text-transform: none;
          letter-spacing: 0;
        }

        .ac-table tbody tr:last-child td {
          border-bottom: none;
        }

        .ac-criteria {
          display: flex;
          align-items: center;
          gap: 8px;
          color: #334155;
          font-size: 11px;
          font-weight: 800;
        }

        .ac-criteria-icon {
          width: 27px;
          height: 27px;
          min-width: 27px;
          border-radius: 7px;
          background: #f1f5f9;
          color: #64748b;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ac-table td {
          color: #475569;
          font-size: 12px;
          line-height: 1.6;
        }

        .ac-alt-name {
          color: #0f172a;
          font-weight: 750;
        }

        .ac-alt-id {
          display: block;
          margin-top: 3px;
          color: #94a3b8;
          font-size: 9px;
          font-weight: 650;
        }

        .ac-text {
          max-width: 310px;
          white-space: pre-wrap;
        }

        .ac-cost {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          color: #0f172a;
          font-weight: 750;
        }

        .ac-feasibility {
          display: inline-flex;
          align-items: center;
          gap: 7px;
        }

        .ac-feasibility-score {
          color: #0f172a;
          font-size: 13px;
          font-weight: 800;
        }

        .ac-score-bar {
          width: 65px;
          height: 6px;
          overflow: hidden;
          border-radius: 999px;
          background: #e2e8f0;
        }

        .ac-score-fill {
          height: 100%;
          border-radius: inherit;
          background: #2563eb;
        }

        .ac-risk {
          display: inline-flex;
          align-items: center;
          gap: 5px;
          padding: 5px 9px;
          border-radius: 999px;
          font-size: 10px;
          font-weight: 800;
        }

        .ac-risk-low {
          background: #dcfce7;
          color: #166534;
        }

        .ac-risk-medium {
          background: #fef3c7;
          color: #92400e;
        }

        .ac-risk-high,
        .ac-risk-critical {
          background: #fee2e2;
          color: #991b1b;
        }

        .ac-risk-default {
          background: #f1f5f9;
          color: #64748b;
        }

        .ac-empty {
          padding: 55px 25px;
          text-align: center;
        }

        .ac-empty-icon {
          width: 52px;
          height: 52px;
          margin: 0 auto 14px;
          border-radius: 14px;
          background: #f1f5f9;
          color: #64748b;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ac-empty h2 {
          margin: 0 0 7px;
          color: #0f172a;
          font-size: 18px;
        }

        .ac-empty p {
          max-width: 480px;
          margin: 0 auto 18px;
          color: #64748b;
          font-size: 12px;
          line-height: 1.6;
        }

        .ac-guidance-card {
          overflow: hidden;
          border: 1px solid #e2e8f0;
          border-radius: 16px;
          background: #fff;
          box-shadow:
            0 7px 25px
            rgba(15,23,42,.05);
        }

        .ac-guidance-grid {
          display: grid;
          grid-template-columns:
            repeat(3, minmax(0, 1fr));
          gap: 0;
        }

        .ac-guidance-item {
          padding: 20px 22px;
          border-right: 1px solid #e2e8f0;
        }

        .ac-guidance-item:last-child {
          border-right: none;
        }

        .ac-guidance-icon {
          width: 32px;
          height: 32px;
          margin-bottom: 10px;
          border-radius: 8px;
          background: #eff6ff;
          color: #2563eb;
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .ac-guidance-item strong {
          display: block;
          margin-bottom: 5px;
          color: #0f172a;
          font-size: 12px;
        }

        .ac-guidance-item p {
          margin: 0;
          color: #64748b;
          font-size: 11px;
          line-height: 1.6;
        }

        .ac-footer {
          display: flex;
          justify-content: flex-start;
          margin-top: 18px;
        }

        @media (max-width: 800px) {
          .ac-header {
            flex-direction: column;
          }

          .ac-header-actions {
            width: 100%;
          }

          .ac-header-actions .ac-button {
            flex: 1;
          }

          .ac-guidance-grid {
            grid-template-columns: 1fr;
          }

          .ac-guidance-item {
            border-right: none;
            border-bottom: 1px solid #e2e8f0;
          }

          .ac-guidance-item:last-child {
            border-bottom: none;
          }
        }

        @media (max-width: 520px) {
          .ac-header-main {
            gap: 10px;
          }

          .ac-header-icon {
            width: 43px;
            height: 43px;
            min-width: 43px;
          }

          .ac-header h1 {
            font-size: 23px;
          }

          .ac-header-actions {
            flex-direction: column;
          }

          .ac-header-actions .ac-button {
            width: 100%;
          }

          .ac-decision-top {
            align-items: flex-start;
            flex-direction: column;
          }

          .ac-card-header {
            align-items: flex-start;
          }
        }
      `}</style>


      {/* HEADER */}
      <div className="ac-header">

        <div className="ac-header-main">

          <div className="ac-header-icon">
            <BarChart3 size={23} />
          </div>

          <div>

            <Link
              to={`/decisions/${decisionId}/alternatives`}
              className="ac-back"
            >
              <ArrowLeft size={13} />
              Back to Alternatives
            </Link>

            <div className="ac-eyebrow">
              Decision Analysis
            </div>

            <h1>
              Alternative Comparison
            </h1>

            <p className="ac-header-description">
              Compare available alternatives side by
              side across cost, feasibility, risk,
              strengths, and weaknesses.
            </p>

          </div>

        </div>


        <div className="ac-header-actions">

          <Link
            to={`/decisions/${decisionId}/alternatives`}
            className="ac-button"
          >
            <ArrowLeft size={14} />
            Alternatives
          </Link>

          <Link
            to={`/decisions/${decisionId}`}
            className="ac-button ac-button-primary"
          >
            View Decision
          </Link>

        </div>

      </div>


      {/* DECISION SUMMARY */}
      {decision && (
        <div className="ac-decision-card">

          <div className="ac-decision-top">

            <div>

              <div className="ac-decision-label">
                <Target size={12} />
                Decision Being Evaluated
              </div>

              <h2 className="ac-decision-title">
                {decision.title ||
                  `Decision #${decisionId}`}
              </h2>

            </div>


            {decision.status && (
              <span
                className={`ac-status ${getStatusClass(
                  decision.status
                )}`}
              >
                {decision.status ===
                  "Approved" && (
                  <CheckCircle2 size={12} />
                )}

                {decision.status}
              </span>
            )}

          </div>


          <p className="ac-decision-problem">
            {decision.problem_statement ||
              "No problem statement available."}
          </p>

        </div>
      )}


      {/* COMPARISON */}
      {alternatives.length === 0 ? (
        <div className="ac-comparison-card">

          <div className="ac-empty">

            <div className="ac-empty-icon">
              <BarChart3 size={25} />
            </div>

            <h2>
              No Alternatives Available
            </h2>

            <p>
              This decision does not have any
              alternatives available for comparison
              yet. Add alternatives first to use the
              comparison view.
            </p>

            <Link
              to={`/decisions/${decisionId}/alternatives`}
              className="ac-button ac-button-primary"
            >
              Manage Alternatives
            </Link>

          </div>

        </div>
      ) : (
        <div className="ac-comparison-card">

          <div className="ac-card-header">

            <div className="ac-card-heading">

              <div className="ac-card-icon">
                <BarChart3 size={17} />
              </div>

              <div>

                <h2>
                  Side-by-Side Comparison
                </h2>

                <p>
                  Evaluate each available alternative
                  using the same criteria.
                </p>

              </div>

            </div>


            <span className="ac-count">
              {alternatives.length}{" "}
              alternative
              {alternatives.length !== 1
                ? "s"
                : ""}
            </span>

          </div>


          <div className="ac-table-wrap">

            <table className="ac-table">

              <thead>

                <tr>

                  <th>
                    Criteria
                  </th>

                  {alternatives.map(
                    (alternative) => (
                      <th
                        key={
                          alternative.id
                        }
                      >

                        <div className="ac-alt-name">
                          {alternative.name ||
                            `Alternative #${alternative.id}`}
                        </div>

                        <span className="ac-alt-id">
                          Alternative #
                          {alternative.id}
                        </span>

                      </th>
                    )
                  )}

                </tr>

              </thead>


              <tbody>

                {/* DESCRIPTION */}
                <tr>

                  <td>

                    <div className="ac-criteria">

                      <span className="ac-criteria-icon">
                        <FileDescriptionIcon />
                      </span>

                      Description

                    </div>

                  </td>


                  {alternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                      >
                        <div className="ac-text">
                          {alternative.description ||
                            "—"}
                        </div>
                      </td>
                    )
                  )}

                </tr>


                {/* PROS */}
                <tr>

                  <td>

                    <div className="ac-criteria">

                      <span className="ac-criteria-icon">
                        <CheckCircle2 size={14} />
                      </span>

                      Pros

                    </div>

                  </td>


                  {alternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                      >
                        <div className="ac-text">
                          {alternative.pros ||
                            "—"}
                        </div>
                      </td>
                    )
                  )}

                </tr>


                {/* CONS */}
                <tr>

                  <td>

                    <div className="ac-criteria">

                      <span className="ac-criteria-icon">
                        <ShieldAlert size={14} />
                      </span>

                      Cons

                    </div>

                  </td>


                  {alternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                      >
                        <div className="ac-text">
                          {alternative.cons ||
                            "—"}
                        </div>
                      </td>
                    )
                  )}

                </tr>


                {/* COST */}
                <tr>

                  <td>

                    <div className="ac-criteria">

                      <span className="ac-criteria-icon">
                        <DollarSign size={14} />
                      </span>

                      Estimated Cost

                    </div>

                  </td>


                  {alternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                      >

                        <span className="ac-cost">
                          <DollarSign
                            size={13}
                          />

                          {formatCost(
                            alternative.estimated_cost
                          )}
                        </span>

                      </td>
                    )
                  )}

                </tr>


                {/* FEASIBILITY */}
                <tr>

                  <td>

                    <div className="ac-criteria">

                      <span className="ac-criteria-icon">
                        <Gauge size={14} />
                      </span>

                      Feasibility

                    </div>

                  </td>


                  {alternatives.map(
                    (alternative) => {

                      const score =
                        Number(
                          alternative.feasibility_score
                        );

                      const validScore =
                        !Number.isNaN(
                          score
                        );

                      const percentage =
                        validScore
                          ? Math.max(
                              0,
                              Math.min(
                                100,
                                score * 20
                              )
                            )
                          : 0;

                      return (
                        <td
                          key={
                            alternative.id
                          }
                        >

                          <div className="ac-feasibility">

                            <span className="ac-feasibility-score">
                              {validScore
                                ? `${score} / 5`
                                : "—"}
                            </span>

                            {validScore && (
                              <div className="ac-score-bar">

                                <div
                                  className="ac-score-fill"
                                  style={{
                                    width: `${percentage}%`,
                                  }}
                                />

                              </div>
                            )}

                          </div>

                        </td>
                      );
                    }
                  )}

                </tr>


                {/* RISK */}
                <tr>

                  <td>

                    <div className="ac-criteria">

                      <span className="ac-criteria-icon">
                        <ShieldAlert size={14} />
                      </span>

                      Risk Level

                    </div>

                  </td>


                  {alternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                      >

                        <span
                          className={`ac-risk ${getRiskClass(
                            alternative.risk_level
                          )}`}
                        >
                          <ShieldAlert
                            size={12}
                          />

                          {alternative.risk_level ||
                            "—"}
                        </span>

                      </td>
                    )
                  )}

                </tr>


                {/* ID */}
                <tr>

                  <td>

                    <div className="ac-criteria">

                      <span className="ac-criteria-icon">
                        <Target size={14} />
                      </span>

                      Alternative ID

                    </div>

                  </td>


                  {alternatives.map(
                    (alternative) => (
                      <td
                        key={
                          alternative.id
                        }
                      >
                        #{alternative.id}
                      </td>
                    )
                  )}

                </tr>

              </tbody>

            </table>

          </div>

        </div>
      )}


      {/* GUIDANCE */}
      <div className="ac-guidance-card">

        <div className="ac-card-header">

          <div className="ac-card-heading">

            <div className="ac-card-icon">
              <ShieldAlert size={17} />
            </div>

            <div>

              <h2>
                Comparison Guidance
              </h2>

              <p>
                Use consistent criteria when reviewing
                the available options.
              </p>

            </div>

          </div>

        </div>


        <div className="ac-guidance-grid">

          <div className="ac-guidance-item">

            <div className="ac-guidance-icon">
              <Gauge size={16} />
            </div>

            <strong>
              Feasibility
            </strong>

            <p>
              Higher feasibility scores indicate
              that an alternative is easier to
              implement.
            </p>

          </div>


          <div className="ac-guidance-item">

            <div className="ac-guidance-icon">
              <ShieldAlert size={16} />
            </div>

            <strong>
              Risk
            </strong>

            <p>
              Consider risk together with expected
              benefits, implementation complexity,
              and estimated cost.
            </p>

          </div>


          <div className="ac-guidance-item">

            <div className="ac-guidance-icon">
              <CheckCircle2 size={16} />
            </div>

            <strong>
              Pros & Cons
            </strong>

            <p>
              Review the advantages and
              disadvantages before making a
              final decision.
            </p>

          </div>

        </div>

      </div>


      {/* FOOTER */}
      <div className="ac-footer">

        <Link
          to={`/decisions/${decisionId}/alternatives`}
          className="ac-button"
        >
          <ArrowLeft size={14} />
          Back to Alternatives
        </Link>

      </div>

    </div>
  );
}


/*
 * Small local icon wrapper.
 * Kept separate so the comparison table
 * remains readable.
 */
function FileDescriptionIcon() {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: "13px",
        fontWeight: 800,
      }}
    >
      ≡
    </span>
  );
}