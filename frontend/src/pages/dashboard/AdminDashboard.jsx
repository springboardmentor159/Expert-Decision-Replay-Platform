import { useEffect, useState } from "react";
import { getAdminDashboard, getAdminApprovalStatistics, getAdminCompletionRate } from "../../api/dashboard";
import StatCard from "../../components/ui/StatCard";
import Card from "../../components/ui/Card";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate } from "../../utils/format";
import { Link } from "react-router-dom";

export default function AdminDashboard() {
  const [data, setData] = useState(null);
  const [approvalStats, setApprovalStats] = useState(null);
  const [completion, setCompletion] = useState(null);
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  async function load() {
    setState("loading");
    try {
      const [d, a, c] = await Promise.all([
        getAdminDashboard(),
        getAdminApprovalStatistics(),
        getAdminCompletionRate(),
      ]);
      setData(d);
      setApprovalStats(a);
      setCompletion(c);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === "loading") return <LoadingState label="Loading admin dashboard…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div>
      <div className="page-header">
        <h1>Admin Dashboard</h1>
        <div className="page-header-actions">
          <Link className="btn btn-secondary" to="/users">
            User Management
          </Link>
          <Link className="btn btn-secondary" to="/audit">
            Audit Logs
          </Link>
          <Link className="btn btn-primary" to="/reports">
            Reports
          </Link>
        </div>
      </div>

      <div className="stat-grid">
        <StatCard label="Total Users" value={data.total_users} />
        <StatCard label="Total Decisions" value={data.total_decisions} />
        <StatCard label="Total Approvals" value={data.total_approvals} />
        <StatCard label="Pending Approvals" value={data.pending_approvals} tone="blue" />
        <StatCard label="Approved" value={data.approved_decisions} tone="green" />
        <StatCard label="Rejected" value={data.rejected_decisions} tone="red" />
        <StatCard label="Under Review" value={data.under_review} tone="blue" />
        <StatCard label="Draft" value={data.draft_decisions} tone="gray" />
        <StatCard label="Archived" value={data.archived_decisions} tone="purple" />
      </div>

      <div className="two-col">
        <Card title="Approval Performance">
          <div className="stat-grid">
            <StatCard label="Avg Turnaround (hrs)" value={approvalStats.average_approval_time_hours?.toFixed?.(1) ?? "-"} />
            <StatCard label="Fastest (hrs)" value={approvalStats.fastest_approval_hours?.toFixed?.(1) ?? "-"} />
            <StatCard label="Slowest (hrs)" value={approvalStats.slowest_approval_hours?.toFixed?.(1) ?? "-"} />
            <StatCard label="Pending" value={approvalStats.pending_approvals} tone="blue" />
          </div>
        </Card>
        <Card title="Completion Rate">
          <div className="stat-grid">
            <StatCard label="Total Approvals" value={completion.total_approvals} />
            <StatCard label="Completed" value={completion.completed_approvals} tone="green" />
            <StatCard label="Rate" value={`${completion.completion_rate?.toFixed?.(1) ?? 0}%`} />
          </div>
        </Card>
      </div>

      <Card title="Recent Activity">
        {data.recent_activities?.length ? (
          <ul className="activity-list">
            {data.recent_activities.map((a) => (
              <li key={a.id}>
                <span>{a.description}</span>
                <span className="activity-date">{formatDate(a.created_at)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState title="No recent activity" />
        )}
      </Card>
    </div>
  );
}
