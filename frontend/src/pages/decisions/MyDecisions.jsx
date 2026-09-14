import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getDecisions } from "../../services/decisionService";
import { useAuth } from "../../context/AuthContext";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import Card from "../../components/Card";
import StatusBadge from "../../components/StatusBadge";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const MyDecisions = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  const [decisions, setDecisions] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [category, setCategory] = useState("");

  // SORTING
  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");

  const [page, setPage] = useState(1);

  const limit = 10;

  // --------------------------------------------------
  // LOAD MY DECISIONS
  // --------------------------------------------------
  const loadDecisions = async (overrideValues = {}) => {
    if (!user?.id) {
      setError("Unable to identify the logged-in user.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await getDecisions({
        // IMPORTANT:
        // Only fetch decisions created by the logged-in user
        created_by: user.id,

        search:
          overrideValues.search !== undefined
            ? overrideValues.search
            : search.trim() || undefined,

        status:
          overrideValues.status !== undefined
            ? overrideValues.status
            : status || undefined,

        category:
          overrideValues.category !== undefined
            ? overrideValues.category
            : category.trim() || undefined,

        page:
          overrideValues.page !== undefined
            ? overrideValues.page
            : page,

        limit,

        sort_by:
          overrideValues.sort_by !== undefined
            ? overrideValues.sort_by
            : sortBy,

        sort_order:
          overrideValues.sort_order !== undefined
            ? overrideValues.sort_order
            : sortOrder,
      });

      const decisionList = Array.isArray(data)
        ? data
        : data?.decisions || [];

      setDecisions(decisionList);
    } catch (err) {
      console.error("Failed to load my decisions:", err);

      const code = err.response?.status;

      if (code === 401) {
        setError(
          "Your session has expired. Please login again."
        );
      } else if (code === 403) {
        setError(
          "You are not authorized to view your decisions."
        );
      } else if (code === 404) {
        setError(
          "Decision endpoint was not found."
        );
      } else if (code === 422) {
        setError(
          "Invalid search, filter or sorting values."
        );
      } else if (code >= 500) {
        setError(
          "Server error. Please try again later."
        );
      } else if (err.request) {
        setError(
          "Unable to connect to the backend. Please make sure FastAPI is running."
        );
      } else {
        setError(
          "Unable to load your decisions."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  // --------------------------------------------------
  // LOAD WHEN USER / PAGE CHANGES
  // --------------------------------------------------
  useEffect(() => {
    if (user?.id) {
      loadDecisions();
    }
  }, [user?.id, page]);

  // --------------------------------------------------
  // SEARCH
  // --------------------------------------------------
  const handleSearch = () => {
    if (page !== 1) {
      setPage(1);
      return;
    }

    loadDecisions({
      page: 1,
    });
  };

  // --------------------------------------------------
  // RESET FILTERS + SORTING
  // --------------------------------------------------
  const handleReset = () => {
    setSearch("");
    setStatus("");
    setCategory("");

    setSortBy("created_at");
    setSortOrder("desc");

    if (page !== 1) {
      setPage(1);
      return;
    }

    loadDecisions({
      search: undefined,
      status: undefined,
      category: undefined,
      page: 1,
      sort_by: "created_at",
      sort_order: "desc",
    });
  };

  // --------------------------------------------------
  // OPEN DECISION DETAILS
  // --------------------------------------------------
  const openDecisionDetails = (decisionId) => {
    navigate(`/decisions/${decisionId}`);
  };

  // --------------------------------------------------
  // RENDER
  // --------------------------------------------------
  return (
    <div className="decision-page">

      <PageHeader
        title="My Decisions"
        subtitle="View, search, filter and manage decisions created by you"
        action={
          <Button
            onClick={() =>
              navigate("/decisions/create")
            }
          >
            + Create Decision
          </Button>
        }
      />

      {/* ERROR MESSAGE */}
      {error && (
        <Alert
          message={error}
          type="error"
          onClose={() => setError("")}
        />
      )}

      {/* SEARCH & FILTERS */}
      <Card title="Search & Filters">

        <div className="decision-filters">

          {/* SEARCH */}
          <div className="filter-group search-filter">
            <label htmlFor="my-decision-search">
              Search
            </label>

            <input
              id="my-decision-search"
              type="text"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search title or problem statement"
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSearch();
                }
              }}
            />
          </div>

          {/* STATUS */}
          <div className="filter-group">
            <label htmlFor="my-decision-status">
              Status
            </label>

            <select
              id="my-decision-status"
              value={status}
              onChange={(event) =>
                setStatus(event.target.value)
              }
            >
              <option value="">
                All Statuses
              </option>

              <option value="Draft">
                Draft
              </option>

              <option value="Under Review">
                Under Review
              </option>

              <option value="Approved">
                Approved
              </option>

              <option value="Rejected">
                Rejected
              </option>

              <option value="Archived">
                Archived
              </option>
            </select>
          </div>

          {/* CATEGORY */}
          <div className="filter-group">
            <label htmlFor="my-decision-category">
              Category
            </label>

            <input
              id="my-decision-category"
              type="text"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value)
              }
              placeholder="Category"
              onKeyDown={(event) => {
                if (event.key === "Enter") {
                  handleSearch();
                }
              }}
            />
          </div>

          {/* SORT BY */}
          <div className="filter-group">
            <label htmlFor="my-decision-sort-by">
              Sort By
            </label>

            <select
              id="my-decision-sort-by"
              value={sortBy}
              onChange={(event) =>
                setSortBy(event.target.value)
              }
            >
              <option value="created_at">
                Created Date
              </option>

              <option value="updated_at">
                Last Updated
              </option>

              <option value="title">
                Title
              </option>

              <option value="status">
                Status
              </option>

              <option value="category">
                Category
              </option>
            </select>
          </div>

          {/* SORT ORDER */}
          <div className="filter-group">
            <label htmlFor="my-decision-sort-order">
              Sort Order
            </label>

            <select
              id="my-decision-sort-order"
              value={sortOrder}
              onChange={(event) =>
                setSortOrder(event.target.value)
              }
            >
              <option value="desc">
                Descending
              </option>

              <option value="asc">
                Ascending
              </option>
            </select>
          </div>

          {/* ACTIONS */}
          <div className="filter-actions">

            <Button
              onClick={handleSearch}
              disabled={loading}
            >
              Search
            </Button>

            <Button
              variant="secondary"
              onClick={handleReset}
              disabled={loading}
            >
              Reset
            </Button>

          </div>

        </div>

      </Card>

      {/* LOADING */}
      {loading ? (

        <div className="dashboard-loading">
          <div className="loading-spinner"></div>

          <p>
            Loading your decisions...
          </p>
        </div>

      ) : decisions.length === 0 ? (

        <EmptyState
          title="No decisions found"
          message="You have not created any decisions matching your current search or filters."
          action={
            <Button
              onClick={() =>
                navigate("/decisions/create")
              }
            >
              Create Decision
            </Button>
          }
        />

      ) : (

        /* DECISION TABLE */
        <Card title="My Decisions">

          <div className="decision-table-wrapper">

            <table className="decision-table">

              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Status</th>
                  <th>Created By</th>
                  <th>Created At</th>
                </tr>
              </thead>

              <tbody>

                {decisions.map((decision) => (

                  <tr
                    key={decision.id}
                    onDoubleClick={() =>
                      openDecisionDetails(
                        decision.id
                      )
                    }
                    title="Double-click to open decision details"
                  >

                    {/* ID */}
                    <td>
                      {decision.id}
                    </td>

                    {/* TITLE */}
                    <td className="decision-title">

                      <button
                        type="button"
                        className="decision-title-button"
                        onClick={() =>
                          openDecisionDetails(
                            decision.id
                          )
                        }
                        title="Open decision details"
                      >
                        {decision.title ||
                          "Untitled Decision"}
                      </button>

                    </td>

                    {/* CATEGORY */}
                    <td>
                      {decision.category || "-"}
                    </td>

                    {/* STATUS */}
                    <td>
                      <StatusBadge
                        status={decision.status}
                      />
                    </td>

                    {/* CREATED BY */}
                    <td>
                      {decision.created_by || "-"}
                    </td>

                    {/* CREATED AT */}
                    <td>
                      {decision.created_at
                        ? new Date(
                            decision.created_at
                          ).toLocaleString()
                        : "-"}
                    </td>

                  </tr>

                ))}

              </tbody>

            </table>

          </div>

          {/* PAGINATION */}
          <div className="decision-pagination">

            <Button
              variant="secondary"
              disabled={
                page === 1 || loading
              }
              onClick={() =>
                setPage(
                  (currentPage) =>
                    currentPage - 1
                )
              }
            >
              Previous
            </Button>

            <span>
              Page {page}
            </span>

            <Button
              variant="secondary"
              disabled={
                decisions.length < limit ||
                loading
              }
              onClick={() =>
                setPage(
                  (currentPage) =>
                    currentPage + 1
                )
              }
            >
              Next
            </Button>

          </div>

        </Card>

      )}

    </div>
  );
};

export default MyDecisions;