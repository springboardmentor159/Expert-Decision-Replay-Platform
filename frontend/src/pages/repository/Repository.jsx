import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  getRepositoryDecisions,
  getTags,
} from "../../services/repositoryService";

import PageHeader from "../../components/PageHeader";
import Button from "../../components/Button";
import StatusBadge from "../../components/StatusBadge";
import Alert from "../../components/Alert";
import EmptyState from "../../components/EmptyState";

const Repository = () => {
  const navigate = useNavigate();

  // =========================
  // DATA
  // =========================

  const [decisions, setDecisions] = useState([]);
  const [tags, setTags] = useState([]);

  // =========================
  // FILTERS
  // =========================

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [status, setStatus] = useState("");
  const [tag, setTag] = useState("");

  // =========================
  // SORTING
  // =========================

  const [sortBy, setSortBy] = useState("created_at");
  const [sortOrder, setSortOrder] = useState("desc");

  // =========================
  // PAGINATION
  // =========================

  const [page, setPage] = useState(1);
  const limit = 10;

  // =========================
  // STATES
  // =========================

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [tagError, setTagError] = useState("");

  // =========================
  // LOAD REPOSITORY
  // =========================

  const loadRepository = async (overrideValues = {}) => {
    try {
      setLoading(true);
      setError("");

      const response = await getRepositoryDecisions({
        search:
          overrideValues.search !== undefined
            ? overrideValues.search
            : search.trim() || undefined,

        category:
          overrideValues.category !== undefined
            ? overrideValues.category
            : category || undefined,

        status:
          overrideValues.status !== undefined
            ? overrideValues.status
            : status || undefined,

        tag:
          overrideValues.tag !== undefined
            ? overrideValues.tag
            : tag || undefined,

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

      setDecisions(
        Array.isArray(response)
          ? response
          : response?.decisions || response?.items || []
      );
    } catch (err) {
      console.error(
        "Repository loading error:",
        err
      );

      const statusCode = err.response?.status;

      if (statusCode === 401) {
        setError(
          "You are not authenticated. Please login again."
        );
      } else if (statusCode === 403) {
        setError(
          "You do not have permission to access the repository."
        );
      } else if (statusCode === 404) {
        setError(
          "Repository service was not found."
        );
      } else if (statusCode === 422) {
        setError(
          "Invalid repository filters or sorting values."
        );
      } else if (statusCode === 500) {
        setError(
          "Server error. Please try again later."
        );
      } else {
        setError(
          "Failed to load the Knowledge Repository."
        );
      }

      setDecisions([]);
    } finally {
      setLoading(false);
    }
  };

  // =========================
  // LOAD TAGS
  // =========================

  const loadTags = async () => {
    try {
      setTagError("");

      const response = await getTags();

      setTags(
        Array.isArray(response)
          ? response
          : response?.tags || response?.items || []
      );
    } catch (err) {
      console.error(
        "Tag loading error:",
        err
      );

      const statusCode = err.response?.status;

      if (statusCode === 404) {
        setTagError(
          "Tags could not be loaded."
        );
      }
    }
  };

  // =========================
  // INITIAL LOAD
  // =========================

  useEffect(() => {
    loadTags();
  }, []);

  // =========================
  // LOAD REPOSITORY
  // =========================

  useEffect(() => {
    loadRepository();
  }, [page]);

  // =========================
  // SEARCH
  // =========================

  const handleSearch = (event) => {
    event.preventDefault();

    if (page !== 1) {
      setPage(1);
    } else {
      loadRepository({
        page: 1,
      });
    }
  };

  // =========================
  // SORT CHANGE
  // =========================

  const handleSortByChange = (event) => {
    const newSortBy = event.target.value;

    setSortBy(newSortBy);

    if (page !== 1) {
      setPage(1);
    } else {
      loadRepository({
        sort_by: newSortBy,
        sort_order: sortOrder,
        page: 1,
      });
    }
  };

  const handleSortOrderChange = (event) => {
    const newSortOrder = event.target.value;

    setSortOrder(newSortOrder);

    if (page !== 1) {
      setPage(1);
    } else {
      loadRepository({
        sort_by: sortBy,
        sort_order: newSortOrder,
        page: 1,
      });
    }
  };

  // =========================
  // CLEAR FILTERS
  // =========================

  const clearFilters = () => {
    setSearch("");
    setCategory("");
    setStatus("");
    setTag("");

    // Reset sorting
    setSortBy("created_at");
    setSortOrder("desc");

    if (page !== 1) {
      setPage(1);
      return;
    }

    loadRepository({
      search: undefined,
      category: undefined,
      status: undefined,
      tag: undefined,
      page: 1,
      sort_by: "created_at",
      sort_order: "desc",
    });
  };

  // =========================
  // REFRESH
  // =========================

  const handleRefresh = () => {
    loadRepository();
    loadTags();
  };

  // =========================
  // CATEGORY OPTIONS
  // =========================

  const categories = [
    ...new Set(
      decisions
        .map((decision) => decision.category)
        .filter(Boolean)
    ),
  ];

  // =========================
  // LOADING
  // =========================

  if (loading) {
    return (
      <div className="repository-page">

        <PageHeader
          title="Knowledge Repository"
          subtitle="Search and explore stored organizational decisions."
        />

        <div className="repository-loading">

          <div className="repository-loading-spinner">
            Loading...
          </div>

          <p>
            Loading Knowledge Repository...
          </p>

        </div>

      </div>
    );
  }

  // =========================
  // PAGE
  // =========================

  return (
    <div className="repository-page">

      {/* =========================
          HEADER
      ========================== */}

      <PageHeader
        title="Knowledge Repository"
        subtitle="Search and explore stored organizational decisions."
      >

        <Button
          type="button"
          variant="secondary"
          onClick={handleRefresh}
        >
          Refresh
        </Button>

      </PageHeader>


      {/* =========================
          FILTER CARD
      ========================== */}

      <section className="repository-filter-card">

        <div className="repository-filter-header">

          <div>

            <h2>
              Search & Filters
            </h2>

            <p>
              Find decisions using keywords, category,
              status, or tags.
            </p>

          </div>

        </div>


        <form
          className="repository-filter-form"
          onSubmit={handleSearch}
        >

          {/* SEARCH */}

          <div className="repository-filter-group repository-search-group">

            <label htmlFor="repository-search">
              Search
            </label>

            <input
              id="repository-search"
              type="text"
              placeholder="Search decisions..."
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
            />

          </div>


          {/* CATEGORY */}

          <div className="repository-filter-group">

            <label htmlFor="repository-category">
              Category
            </label>

            <select
              id="repository-category"
              value={category}
              onChange={(event) =>
                setCategory(event.target.value)
              }
            >

              <option value="">
                All Categories
              </option>

              {categories.map((item) => (

                <option
                  key={item}
                  value={item}
                >
                  {item}
                </option>

              ))}

            </select>

          </div>


          {/* STATUS */}

          <div className="repository-filter-group">

            <label htmlFor="repository-status">
              Status
            </label>

            <select
              id="repository-status"
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


          {/* TAG */}

          <div className="repository-filter-group">

            <label htmlFor="repository-tag">
              Tag
            </label>

            <select
              id="repository-tag"
              value={tag}
              onChange={(event) =>
                setTag(event.target.value)
              }
            >

              <option value="">
                All Tags
              </option>

              {tags.map((item) => (

                <option
                  key={item.id}
                  value={item.name}
                >
                  {item.name}
                </option>

              ))}

            </select>

          </div>


          {/* SORT BY */}

          <div className="repository-filter-group">

            <label htmlFor="repository-sort-by">
              Sort By
            </label>

            <select
              id="repository-sort-by"
              value={sortBy}
              onChange={handleSortByChange}
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

          <div className="repository-filter-group">

            <label htmlFor="repository-sort-order">
              Sort Order
            </label>

            <select
              id="repository-sort-order"
              value={sortOrder}
              onChange={handleSortOrderChange}
            >

              <option value="desc">
                Descending
              </option>

              <option value="asc">
                Ascending
              </option>

            </select>

          </div>


          {/* BUTTONS */}

          <div className="repository-filter-actions">

            <Button type="submit">
              Search
            </Button>

            <Button
              type="button"
              variant="secondary"
              onClick={clearFilters}
            >
              Clear Filters
            </Button>

          </div>

        </form>


        {tagError && (

          <div className="repository-tag-warning">
            {tagError}
          </div>

        )}

      </section>


      {/* =========================
          ERROR
      ========================== */}

      {error && (

        <div className="repository-error-wrapper">

          <Alert>
            {error}
          </Alert>

          <Button
            type="button"
            onClick={loadRepository}
          >
            Try Again
          </Button>

        </div>

      )}


      {/* =========================
          RESULTS
      ========================== */}

      {!error && (

        <section className="repository-results-card">

          <div className="repository-results-header">

            <div>

              <h2>
                Decision Repository
              </h2>

              <p>
                Showing decisions from the knowledge repository.
              </p>

            </div>

            <span className="repository-result-count">

              {decisions.length} result
              {decisions.length !== 1
                ? "s"
                : ""}

            </span>

          </div>


          {/* EMPTY */}

          {decisions.length === 0 ? (

            <EmptyState
              title="No Decisions Found"
              message="No decisions match the selected search criteria."
            />

          ) : (

            <div className="repository-table-wrapper">

              <table className="repository-table">

                <thead>

                  <tr>

                    <th>
                      ID
                    </th>

                    <th>
                      Decision
                    </th>

                    <th>
                      Category
                    </th>

                    <th>
                      Status
                    </th>

                    <th>
                      Created By
                    </th>

                    <th>
                      Created At
                    </th>

                    <th>
                      Action
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {decisions.map(
                    (decision) => (

                      <tr
                        key={decision.id}
                      >

                        {/* ID */}

                        <td>

                          <span className="repository-id">
                            #{decision.id}
                          </span>

                        </td>


                        {/* TITLE */}

                        <td>

                          <button
                            type="button"
                            className="repository-title-button"
                            onClick={() =>
                              navigate(
                                `/decisions/${decision.id}`
                              )
                            }
                          >

                            {decision.title}

                          </button>


                          {decision.problem_statement && (

                            <div className="repository-problem-preview">

                              {decision
                                .problem_statement
                                .length > 100
                                ? `${decision.problem_statement.substring(
                                    0,
                                    100
                                  )}...`
                                : decision.problem_statement}

                            </div>

                          )}

                        </td>


                        {/* CATEGORY */}

                        <td>

                          <span className="repository-category">
                            {decision.category || "—"}
                          </span>

                        </td>


                        {/* STATUS */}

                        <td>

                          <StatusBadge
                            status={decision.status}
                          />

                        </td>


                        {/* CREATED BY */}

                        <td>

                          {decision.created_by || "—"}

                        </td>


                        {/* CREATED AT */}

                        <td>

                          {decision.created_at
                            ? new Date(
                                decision.created_at
                              ).toLocaleString()
                            : "—"}

                        </td>


                        {/* ACTION */}

                        <td>

                          <Button
                            type="button"
                            onClick={() =>
                              navigate(
                                `/decisions/${decision.id}`
                              )
                            }
                          >
                            View Details
                          </Button>

                        </td>

                      </tr>

                    )
                  )}

                </tbody>

              </table>

            </div>

          )}

        </section>

      )}


      {/* =========================
          PAGINATION
      ========================== */}

      {!error && (

        <div className="repository-pagination">

          <Button
            type="button"
            variant="secondary"
            disabled={
              page === 1
            }
            onClick={() =>
              setPage(
                (previousPage) =>
                  previousPage - 1
              )
            }
          >
            ← Previous
          </Button>


          <div className="repository-page-number">

            Page <strong>{page}</strong>

          </div>


          <Button
            type="button"
            variant="secondary"
            disabled={
              decisions.length < limit
            }
            onClick={() =>
              setPage(
                (previousPage) =>
                  previousPage + 1
              )
            }
          >
            Next →

          </Button>

        </div>

      )}

    </div>
  );
};

export default Repository;