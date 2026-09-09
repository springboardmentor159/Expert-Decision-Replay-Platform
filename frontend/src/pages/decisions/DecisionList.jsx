import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listDecisions, updateDecisionStatus } from "../../api/decisions";
import Card from "../../components/ui/Card";
import Table from "../../components/ui/Table";
import Badge from "../../components/ui/Badge";
import Select from "../../components/ui/Select";
import Input from "../../components/ui/Input";
import Button from "../../components/ui/Button";
import Pagination from "../../components/ui/Pagination";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import Alert from "../../components/ui/Alert";
import { formatDate, DECISION_STATUSES } from "../../utils/format";
import { useAuth } from "../../context/AuthContext";

export default function DecisionList() {
  const { user } = useAuth();
  const [filters, setFilters] = useState({ status: "", category: "", tag: "" });
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const [result, setResult] = useState({ items: [], total: 0 });
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [actionError, setActionError] = useState("");

  async function load() {
    setState("loading");
    try {
      const res = await listDecisions({
        status: filters.status || undefined,
        category: filters.category || undefined,
        tag: filters.tag || undefined,
        page,
        page_size: pageSize,
      });
      setResult(res);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters.status, filters.category, filters.tag]);

  async function submitForReview(decisionId) {
    setActionError("");
    try {
      await updateDecisionStatus(decisionId, "Under Review");
      load();
    } catch (err) {
      setActionError(err.message);
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Decisions</h1>
        <Link className="btn btn-primary" to="/decisions/new">
          + Create Decision
        </Link>
      </div>

      <Card>
        <div className="filter-bar">
          <Select
            label="Status"
            placeholder="All statuses"
            options={DECISION_STATUSES}
            value={filters.status}
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, status: e.target.value }));
            }}
          />
          <Input
            label="Category"
            placeholder="e.g. Finance"
            value={filters.category}
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, category: e.target.value }));
            }}
          />
          <Input
            label="Tag"
            placeholder="e.g. urgent"
            value={filters.tag}
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, tag: e.target.value }));
            }}
          />
        </div>
      </Card>

      <Alert type="error" onClose={() => setActionError("")}>
        {actionError}
      </Alert>

      <Card>
        {state === "loading" && <LoadingState label="Loading decisions…" />}
        {state === "error" && <ErrorState message={errorMsg} onRetry={load} />}
        {state === "ready" && result.items.length === 0 && (
          <EmptyState title="No decisions found" description="Try adjusting your filters or create a new decision." />
        )}
        {state === "ready" && result.items.length > 0 && (
          <>
            <Table columns={["Title", "Category", "Status", "Tags", "Updated", "Actions"]}>
              {result.items.map((d) => (
                <tr key={d.id}>
                  <td>
                    <Link to={`/decisions/${d.id}`}>{d.title}</Link>
                  </td>
                  <td>{d.category}</td>
                  <td>
                    <Badge>{d.status}</Badge>
                  </td>
                  <td>{d.tags?.join(", ") || "-"}</td>
                  <td>{formatDate(d.updated_at)}</td>
                  <td className="row-actions">
                    <Link className="btn btn-secondary btn-sm" to={`/decisions/${d.id}`}>
                      View
                    </Link>
                    {d.status === "Draft" && (
                      <Button size="sm" variant="secondary" onClick={() => submitForReview(d.id)}>
                        Submit for Review
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </Table>
            <Pagination page={page} pageSize={pageSize} total={result.total} onPageChange={setPage} />
          </>
        )}
      </Card>
    </div>
  );
}
