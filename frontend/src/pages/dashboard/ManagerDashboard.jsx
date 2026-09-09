import { useEffect, useState } from "react";
import { getManagerDashboard, getManagerStatistics } from "../../api/dashboard";
import StatCard from "../../components/ui/StatCard";
import Card from "../../components/ui/Card";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import { Link } from "react-router-dom";

export default function ManagerDashboard() {
  const [overview, setOverview] = useState(null);
  const [stats, setStats] = useState(null);
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  async function load() {
    setState("loading");
    try {
      const [o, s] = await Promise.all([getManagerDashboard(), getManagerStatistics()]);
      setOverview(o);
      setStats(s);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === "loading") return <LoadingState label="Loading team dashboard…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div>
      <div className="page-header">
        <h1>Manager Dashboard</h1>
        <Link className="btn btn-secondary" to="/reports">
          View Reports
        </Link>
      </div>

      <div className="stat-grid">
        <StatCard label="Team Decisions" value={overview.team_decisions} />
        <StatCard label="Pending Approvals" value={overview.pending_approvals} tone="blue" />
        <StatCard label="Under Review" value={overview.under_review} tone="blue" />
        <StatCard label="Approved" value={overview.approved_decisions} tone="green" />
        <StatCard label="Rejected" value={overview.rejected_decisions} tone="red" />
      </div>

      <Card title="Decision Analytics">
        <div className="stat-grid">
          <StatCard label="Total" value={stats.total_decisions} />
          <StatCard label="Draft" value={stats.draft_decisions} tone="gray" />
          <StatCard label="Under Review" value={stats.under_review} tone="blue" />
          <StatCard label="Approved" value={stats.approved_decisions} tone="green" />
          <StatCard label="Rejected" value={stats.rejected_decisions} tone="red" />
          <StatCard label="Archived" value={stats.archived_decisions} tone="purple" />
        </div>
      </Card>
    </div>
  );
}
