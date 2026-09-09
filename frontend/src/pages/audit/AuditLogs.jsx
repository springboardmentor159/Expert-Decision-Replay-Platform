import { useEffect, useState } from "react";
import { getAuditLogs, getSecurityLogs, getAccessLogs } from "../../api/audit";
import Card from "../../components/ui/Card";
import Table from "../../components/ui/Table";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import Pagination from "../../components/ui/Pagination";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate } from "../../utils/format";

const SUB_TABS = ["Audit Logs", "Security Logs", "Access Logs"];

const AUDIT_ACTIONS = ["CREATE", "UPDATE", "DELETE", "APPROVE", "REJECT", "SUBMIT", "ARCHIVE", "ASSIGN", "LOGIN", "LOGOUT", "ACCESS"];
const ENTITY_TYPES = ["Decision", "Alternative", "Comment", "DiscussionThread", "MeetingNote", "Approval", "User", "AuditLog"];

export default function AuditLogs() {
  const [tab, setTab] = useState("Audit Logs");
  const [filters, setFilters] = useState({ user_id: "", action: "", entity_type: "" });
  const [page, setPage] = useState(1);
  const pageSize = 20;

  const [result, setResult] = useState({ items: [], total: 0 });
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  async function load() {
    setState("loading");
    try {
      const params = {
        user_id: filters.user_id || undefined,
        page,
        page_size: pageSize,
      };
      let res;
      if (tab === "Audit Logs") {
        res = await getAuditLogs({ ...params, action: filters.action || undefined, entity_type: filters.entity_type || undefined });
      } else if (tab === "Security Logs") {
        res = await getSecurityLogs(params);
      } else {
        res = await getAccessLogs(params);
      }
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
  }, [tab, page]);

  function applyFilters() {
    setPage(1);
    load();
  }

  return (
    <div>
      <div className="page-header">
        <h1>Audit & Activity</h1>
      </div>

      <div className="tabs">
        {SUB_TABS.map((t) => (
          <button
            key={t}
            className={`tab ${tab === t ? "tab-active" : ""}`}
            onClick={() => {
              setTab(t);
              setPage(1);
            }}
          >
            {t}
          </button>
        ))}
      </div>

      <Card>
        <div className="filter-bar">
          <Input
            label="User ID"
            value={filters.user_id}
            onChange={(e) => setFilters((f) => ({ ...f, user_id: e.target.value }))}
          />
          {tab === "Audit Logs" && (
            <>
              <Select
                label="Action"
                placeholder="All actions"
                options={AUDIT_ACTIONS}
                value={filters.action}
                onChange={(e) => setFilters((f) => ({ ...f, action: e.target.value }))}
              />
              <Select
                label="Entity Type"
                placeholder="All entities"
                options={ENTITY_TYPES}
                value={filters.entity_type}
                onChange={(e) => setFilters((f) => ({ ...f, entity_type: e.target.value }))}
              />
            </>
          )}
          <div className="field">
            <label>&nbsp;</label>
            <button className="btn btn-secondary" onClick={applyFilters}>
              Apply Filters
            </button>
          </div>
        </div>
      </Card>

      <Card>
        {state === "loading" && <LoadingState label="Loading logs…" />}
        {state === "error" && <ErrorState message={errorMsg} onRetry={load} />}
        {state === "ready" && result.items.length === 0 && <EmptyState title="No log entries found" />}
        {state === "ready" && result.items.length > 0 && tab === "Audit Logs" && (
          <>
            <Table columns={["User", "Action", "Entity", "Description", "IP", "Date"]}>
              {result.items.map((log) => (
                <tr key={log.id}>
                  <td>#{log.user_id}</td>
                  <td>{log.action}</td>
                  <td>
                    {log.entity_type} #{log.entity_id}
                  </td>
                  <td>{log.description}</td>
                  <td>{log.ip_address || "-"}</td>
                  <td>{formatDate(log.created_at)}</td>
                </tr>
              ))}
            </Table>
            <Pagination page={page} pageSize={pageSize} total={result.total} onPageChange={setPage} />
          </>
        )}
        {state === "ready" && result.items.length > 0 && tab === "Security Logs" && (
          <>
            <Table columns={["User", "Identifier", "Event", "Description", "IP", "Date"]}>
              {result.items.map((log) => (
                <tr key={log.id}>
                  <td>{log.user_id ? `#${log.user_id}` : "-"}</td>
                  <td>{log.identifier || "-"}</td>
                  <td>{log.event_type}</td>
                  <td>{log.description || "-"}</td>
                  <td>{log.ip_address || "-"}</td>
                  <td>{formatDate(log.created_at)}</td>
                </tr>
              ))}
            </Table>
            <Pagination page={page} pageSize={pageSize} total={result.total} onPageChange={setPage} />
          </>
        )}
        {state === "ready" && result.items.length > 0 && tab === "Access Logs" && (
          <>
            <Table columns={["User", "Resource", "Action", "IP", "Date"]}>
              {result.items.map((log) => (
                <tr key={log.id}>
                  <td>#{log.user_id}</td>
                  <td>
                    {log.resource_type} {log.resource_id ? `#${log.resource_id}` : ""}
                  </td>
                  <td>{log.action}</td>
                  <td>{log.ip_address || "-"}</td>
                  <td>{formatDate(log.created_at)}</td>
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
