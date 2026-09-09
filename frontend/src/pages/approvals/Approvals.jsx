import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyPendingApprovals, actOnApproval } from "../../api/approvals";
import Card from "../../components/ui/Card";
import Table from "../../components/ui/Table";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import Textarea from "../../components/ui/Textarea";
import Alert from "../../components/ui/Alert";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate } from "../../utils/format";
import { useAuth } from "../../context/AuthContext";
import { canActOnApprovals } from "../../utils/roles";

export default function Approvals() {
  const { user } = useAuth();
  const [approvals, setApprovals] = useState([]);
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  const [activeApproval, setActiveApproval] = useState(null);
  const [decisionValue, setDecisionValue] = useState("Approved");
  const [comments, setComments] = useState("");
  const [actionError, setActionError] = useState("");
  const [acting, setActing] = useState(false);

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

  function openAction(approval, value) {
    setActiveApproval(approval);
    setDecisionValue(value);
    setComments("");
    setActionError("");
  }

  async function submitAction() {
    setActing(true);
    setActionError("");
    try {
      await actOnApproval(activeApproval.id, decisionValue, comments);
      setActiveApproval(null);
      load();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActing(false);
    }
  }

  if (state === "loading") return <LoadingState label="Loading your review queue…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div>
      <div className="page-header">
        <h1>Assigned Reviews</h1>
      </div>

      <Card>
        {approvals.length === 0 ? (
          <EmptyState title="No approvals assigned" description="You have nothing to review right now." />
        ) : (
          <Table columns={["Decision", "Level", "Status", "Assigned", "Actions"]}>
            {approvals.map((a) => (
              <tr key={a.id}>
                <td>
                  <Link to={`/decisions/${a.decision_id}`}>Decision #{a.decision_id}</Link>
                </td>
                <td>{a.level}</td>
                <td>
                  <Badge>{a.status}</Badge>
                </td>
                <td>{formatDate(a.created_at)}</td>
                <td className="row-actions">
                  {a.status === "Pending" && canActOnApprovals(user?.role) && (
                    <>
                      <Button size="sm" variant="danger" onClick={() => openAction(a, "Rejected")}>
                        Reject
                      </Button>
                      <Button size="sm" variant="success" onClick={() => openAction(a, "Approved")}>
                        Approve
                      </Button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </Table>
        )}
      </Card>

      {activeApproval && (
        <Modal
          title={`${decisionValue === "Approved" ? "Approve" : "Reject"} Approval #${activeApproval.id}`}
          onClose={() => setActiveApproval(null)}
          footer={
            <>
              <Button variant="secondary" onClick={() => setActiveApproval(null)}>
                Cancel
              </Button>
              <Button variant={decisionValue === "Approved" ? "success" : "danger"} loading={acting} onClick={submitAction}>
                Confirm {decisionValue}
              </Button>
            </>
          }
        >
          <Alert type="error">{actionError}</Alert>
          <Textarea
            label="Comments (optional)"
            rows={3}
            value={comments}
            onChange={(e) => setComments(e.target.value)}
          />
        </Modal>
      )}
    </div>
  );
}
