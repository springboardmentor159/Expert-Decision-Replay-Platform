import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getEmployeeDashboard } from "../../api/dashboard";
import StatCard from "../../components/ui/StatCard";
import Card from "../../components/ui/Card";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate } from "../../utils/format";

export default function EmployeeDashboard() {
  const [data, setData] = useState(null);
  const [state, setState] = useState("loading"); // loading | ready | error
  const [errorMsg, setErrorMsg] = useState("");

  async function load() {
    setState("loading");
    try {
      const res = await getEmployeeDashboard();
      setData(res);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === "loading") return <LoadingState label="Loading your dashboard…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div>
      <div className="page-header">
        <h1>My Dashboard</h1>
        <Link className="btn btn-primary" to="/decisions/new">
          + Create Decision
        </Link>
      </div>

      <div className="stat-grid">
        <StatCard label="Total Decisions" value={data.total_decisions} />
        <StatCard label="Draft" value={data.draft_decisions} tone="gray" />
        <StatCard label="Under Review" value={data.under_review} tone="blue" />
        <StatCard label="Approved" value={data.approved_decisions} tone="green" />
        <StatCard label="Rejected" value={data.rejected_decisions} tone="red" />
        <StatCard label="Pending Reviews" value={data.pending_reviews} tone="blue" />
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
