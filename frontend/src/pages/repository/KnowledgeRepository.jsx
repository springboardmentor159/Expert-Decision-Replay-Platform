import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { searchDecisions } from "../../api/decisions";
import Card from "../../components/ui/Card";
import Table from "../../components/ui/Table";
import Badge from "../../components/ui/Badge";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Pagination from "../../components/ui/Pagination";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate, DECISION_STATUSES } from "../../utils/format";

export default function KnowledgeRepository() {
  const [query, setQuery] = useState("");
  const [filters, setFilters] = useState({ status: "", category: "", tag: "" });
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const [result, setResult] = useState({ items: [], total: 0 });
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  async function load() {
    setState("loading");
    try {
      const res = await searchDecisions({
        q: query || undefined,
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
    const timeout = setTimeout(load, 300); // light debounce on keyword search
    return () => clearTimeout(timeout);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query, filters.status, filters.category, filters.tag, page]);

  return (
    <div>
      <div className="page-header">
        <h1>Knowledge Repository</h1>
      </div>

      <Card>
        <div className="filter-bar">
          <Input
            label="Search"
            placeholder="Search title, problem statement, rationale…"
            value={query}
            onChange={(e) => {
              setPage(1);
              setQuery(e.target.value);
            }}
          />
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
            value={filters.category}
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, category: e.target.value }));
            }}
          />
          <Input
            label="Tag"
            value={filters.tag}
            onChange={(e) => {
              setPage(1);
              setFilters((f) => ({ ...f, tag: e.target.value }));
            }}
          />
        </div>
      </Card>

      <Card>
        {state === "loading" && <LoadingState label="Searching…" />}
        {state === "error" && <ErrorState message={errorMsg} onRetry={load} />}
        {state === "ready" && result.items.length === 0 && (
          <EmptyState title="No decisions found" description="Try a different search term or filter." />
        )}
        {state === "ready" && result.items.length > 0 && (
          <>
            <Table columns={["Title", "Category", "Status", "Tags", "Updated"]}>
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
