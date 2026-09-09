import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyPendingApprovals } from "../../api/approvals";
import Card from "../../components/ui/Card";
import StatCard from "../../components/ui/StatCard";
import Table from "../../components/ui/Table";
import Badge from "../../components/ui/Badge";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate } from "../../utils/format";

// The backend does not expose a dedicated /dashboard/reviewer endpoint,
// so this view is built from the reviewer's own pending-approvals queue.
export default function ReviewerDashboard() {
  const [approvals, setApprovals] = useState([]);
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  async function load() {
    setState("loading");
    try {
      const res = await getMyPendingApprovals();
      setApprovals(res);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
  }, []);

  if (state === "loading") return <LoadingState label="Loading your review queue…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  const pending = approvals.filter((a) => a.status === "Pending");

  return (
    <div>
      <div className="page-header">
        <h1>Reviewer Dashboard</h1>
        <Link className="btn btn-primary" to="/approvals">
          Go to Assigned Reviews
        </Link>
      </div>

      <div className="stat-grid">
        <StatCard label="Assigned to Me" value={approvals.length} />
        <StatCard label="Pending Reviews" value={pending.length} tone="blue" />
      </div>

      <Card title="Pending Reviews">
        {pending.length ? (
          <Table columns={["Decision", "Level", "Status", "Assigned"]}>
            {pending.map((a) => (
              <tr key={a.id}>
                <td>
                  <Link to={`/decisions/${a.decision_id}`}>Decision #{a.decision_id}</Link>
                </td>
                <td>{a.level}</td>
                <td>
                  <Badge>{a.status}</Badge>
                </td>
                <td>{formatDate(a.created_at)}</td>
              </tr>
            ))}
          </Table>
        ) : (
          <EmptyState title="No pending reviews" description="You're all caught up." />
        )}
      </Card>
    </div>
  );
}
