import { useState } from "react";
import {
  getDecisionReport,
  getApprovalReport,
  getTeamReport,
  getAuditReport,
  exportDecisionReportPdf,
  exportDecisionReportExcel,
  exportApprovalReportPdf,
  exportApprovalReportExcel,
  exportTeamReportPdf,
  exportTeamReportExcel,
  exportAuditReportPdf,
  exportAuditReportExcel,
} from "../../api/reports";
import Card from "../../components/ui/Card";
import Table from "../../components/ui/Table";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Select from "../../components/ui/Select";
import StatCard from "../../components/ui/StatCard";
import Alert from "../../components/ui/Alert";
import LoadingState from "../../components/ui/LoadingState";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate, DECISION_STATUSES } from "../../utils/format";
import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";

const REPORT_TABS = ["Decisions", "Approvals", "Teams", "Audit"];

export default function Reports() {
  const { user } = useAuth();
  const [tab, setTab] = useState("Decisions");
  const [filters, setFilters] = useState({ category: "", status: "", team: "" });
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState("");

  const availableTabs = user?.role === ROLES.ADMINISTRATOR ? REPORT_TABS : REPORT_TABS.filter((t) => t !== "Audit");

  function buildParams() {
    return {
      category: filters.category || undefined,
      status: filters.status || undefined,
      team: filters.team || undefined,
    };
  }

  async function generate() {
    setLoading(true);
    setError("");
    setData(null);
    try {
      const params = buildParams();
      let res;
      if (tab === "Decisions") res = await getDecisionReport(params);
      else if (tab === "Approvals") res = await getApprovalReport({ status: filters.status || undefined });
      else if (tab === "Teams") res = await getTeamReport({ team: filters.team || undefined });
      else res = await getAuditReport({});
      setData(res);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleExport(kind) {
    setExporting(kind);
    setError("");
    try {
      const params = buildParams();
      if (tab === "Decisions") kind === "pdf" ? await exportDecisionReportPdf(params) : await exportDecisionReportExcel(params);
      else if (tab === "Approvals") kind === "pdf" ? await exportApprovalReportPdf(params) : await exportApprovalReportExcel(params);
      else if (tab === "Teams") kind === "pdf" ? await exportTeamReportPdf(params) : await exportTeamReportExcel(params);
      else kind === "pdf" ? await exportAuditReportPdf(params) : await exportAuditReportExcel(params);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting("");
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Reports</h1>
      </div>

      <div className="tabs">
        {availableTabs.map((t) => (
          <button
            key={t}
            className={`tab ${tab === t ? "tab-active" : ""}`}
            onClick={() => {
              setTab(t);
              setData(null);
            }}
          >
            {t}
          </button>
        ))}
      </div>

      <Card>
        <div className="filter-bar">
          {(tab === "Decisions" || tab === "Approvals") && (
            <Select
              label="Status"
              placeholder="All statuses"
              options={tab === "Decisions" ? DECISION_STATUSES : ["Pending", "Approved", "Rejected"]}
              value={filters.status}
              onChange={(e) => setFilters((f) => ({ ...f, status: e.target.value }))}
            />
          )}
          {tab === "Decisions" && (
            <Input label="Category" value={filters.category} onChange={(e) => setFilters((f) => ({ ...f, category: e.target.value }))} />
          )}
          {tab === "Teams" && (
            <Input label="Team / Department" value={filters.team} onChange={(e) => setFilters((f) => ({ ...f, team: e.target.value }))} />
          )}
          <div className="field">
            <label>&nbsp;</label>
            <Button onClick={generate} loading={loading}>
              Generate Report
            </Button>
          </div>
        </div>
        <Alert type="error">{error}</Alert>
        {data && (
          <div className="form-actions">
            <Button variant="secondary" loading={exporting === "pdf"} onClick={() => handleExport("pdf")}>
              Export PDF
            </Button>
            <Button variant="secondary" loading={exporting === "excel"} onClick={() => handleExport("excel")}>
              Export Excel
            </Button>
          </div>
        )}
      </Card>

      {loading && <LoadingState label="Generating report…" />}

      {data && tab === "Decisions" && (
        <>
          <div className="stat-grid">
            <StatCard label="Total" value={data.summary.total_decisions} />
            <StatCard label="Draft" value={data.summary.draft_decisions} tone="gray" />
            <StatCard label="Under Review" value={data.summary.under_review} tone="blue" />
            <StatCard label="Approved" value={data.summary.approved_decisions} tone="green" />
            <StatCard label="Rejected" value={data.summary.rejected_decisions} tone="red" />
            <StatCard label="Archived" value={data.summary.archived_decisions} tone="purple" />
          </div>
          <Card>
            {data.items.length === 0 ? (
              <EmptyState title="No decisions match these filters" />
            ) : (
              <Table columns={["Title", "Category", "Status", "Created By", "Alternatives", "Approvals"]}>
                {data.items.map((d) => (
                  <tr key={d.decision_id}>
                    <td>{d.title}</td>
                    <td>{d.category}</td>
                    <td>{d.status}</td>
                    <td>{d.created_by_name || `#${d.created_by}`}</td>
                    <td>{d.alternatives_count}</td>
                    <td>{d.approvals_count}</td>
                  </tr>
                ))}
              </Table>
            )}
          </Card>
        </>
      )}

      {data && tab === "Approvals" && (
        <>
          <div className="stat-grid">
            <StatCard label="Total" value={data.summary.total_approvals} />
            <StatCard label="Pending" value={data.summary.pending_approvals} tone="blue" />
            <StatCard label="Approved" value={data.summary.approved_approvals} tone="green" />
            <StatCard label="Rejected" value={data.summary.rejected_approvals} tone="red" />
            <StatCard label="Avg Turnaround (hrs)" value={data.summary.average_turnaround_hours?.toFixed?.(1) ?? "-"} />
          </div>
          <Card>
            {data.items.length === 0 ? (
              <EmptyState title="No approvals match these filters" />
            ) : (
              <Table columns={["Decision", "Reviewer", "Level", "Status", "Assigned", "Completed"]}>
                {data.items.map((a) => (
                  <tr key={a.approval_id}>
                    <td>{a.decision_title}</td>
                    <td>{a.reviewer_name || `#${a.reviewer_id}`}</td>
                    <td>{a.approval_level}</td>
                    <td>{a.approval_status}</td>
                    <td>{formatDate(a.assigned_date)}</td>
                    <td>{a.completed_date ? formatDate(a.completed_date) : "-"}</td>
                  </tr>
                ))}
              </Table>
            )}
          </Card>
        </>
      )}

      {data && tab === "Teams" && (
        <Card>
          {data.items.length === 0 ? (
            <EmptyState title="No team data available" />
          ) : (
            <Table columns={["Team", "Members", "Total", "Approved", "Rejected", "Pending"]}>
              {data.items.map((t) => (
                <tr key={t.team_name}>
                  <td>{t.team_name}</td>
                  <td>{t.member_count}</td>
                  <td>{t.total_decisions}</td>
                  <td>{t.approved_decisions}</td>
                  <td>{t.rejected_decisions}</td>
                  <td>{t.pending_decisions}</td>
                </tr>
              ))}
            </Table>
          )}
        </Card>
      )}

      {data && tab === "Audit" && (
        <Card>
          {data.items.length === 0 ? (
            <EmptyState title="No audit entries match these filters" />
          ) : (
            <Table columns={["User", "Action", "Entity", "Description", "Date"]}>
              {data.items.map((a) => (
                <tr key={a.id}>
                  <td>{a.user_name || `#${a.user_id}`}</td>
                  <td>{a.action}</td>
                  <td>
                    {a.entity_type} #{a.entity_id}
                  </td>
                  <td>{a.description}</td>
                  <td>{formatDate(a.timestamp)}</td>
                </tr>
              ))}
            </Table>
          )}
        </Card>
      )}
    </div>
  );
}
