import { useEffect, useState } from "react";
import { assignApproval, actOnApproval } from "../../api/approvals";
import { listUsers } from "../../api/users";
import Card from "../../components/ui/Card";
import Table from "../../components/ui/Table";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import Select from "../../components/ui/Select";
import Textarea from "../../components/ui/Textarea";
import Alert from "../../components/ui/Alert";
import EmptyState from "../../components/ui/EmptyState";
import { formatDate } from "../../utils/format";
import { useAuth } from "../../context/AuthContext";
import { canAssignApprovals, canActOnApprovals } from "../../utils/roles";

// The backend does not expose "list approvals for a decision" directly, so
// this panel is driven by the decision's timeline/history for display, plus
// the assign/act actions. The parent (DecisionDetail) passes down the
// decision so we know its current status.
export default function ApprovalPanel({ decisionId, decision, onChanged }) {
  const { user } = useAuth();
  const [reviewers, setReviewers] = useState([]);
  const [showAssign, setShowAssign] = useState(false);
  const [assignForm, setAssignForm] = useState({ reviewer_id: "", level: 1 });
  const [assignError, setAssignError] = useState("");
  const [assigning, setAssigning] = useState(false);

  const [actionError, setActionError] = useState("");
  const [approvalIdInput, setApprovalIdInput] = useState("");
  const [comments, setComments] = useState("");
  const [acting, setActing] = useState(false);

  useEffect(() => {
    if (canAssignApprovals(user?.role)) {
      listUsers()
        .then((all) => setReviewers(all.filter((u) => u.role === "Reviewer")))
        .catch(() => setReviewers([]));
    }
  }, [user]);

  async function handleAssign(e) {
    e.preventDefault();
    if (!assignForm.reviewer_id) {
      setAssignError("Select a reviewer.");
      return;
    }
    setAssigning(true);
    setAssignError("");
    try {
      await assignApproval(decisionId, Number(assignForm.reviewer_id), Number(assignForm.level) || 1);
      setShowAssign(false);
      onChanged();
    } catch (err) {
      setAssignError(err.message);
    } finally {
      setAssigning(false);
    }
  }

  async function act(decisionValue) {
    if (!approvalIdInput) {
      setActionError("Enter the Approval ID (visible in your Assigned Reviews list).");
      return;
    }
    setActing(true);
    setActionError("");
    try {
      await actOnApproval(Number(approvalIdInput), decisionValue, comments);
      setComments("");
      onChanged();
    } catch (err) {
      setActionError(err.message);
    } finally {
      setActing(false);
    }
  }

  return (
    <div>
      <Card
        title="Approval Status"
        actions={
          canAssignApprovals(user?.role) &&
          decision.status === "Draft" && (
            <Button size="sm" onClick={() => setShowAssign(true)}>
              Submit for Approval
            </Button>
          )
        }
      >
        <div className="approval-status-row">
          <span>Current status:</span>
          <Badge>{decision.status}</Badge>
        </div>

        {decision.status === "Draft" && (
          <EmptyState
            title="Not yet submitted"
            description="This decision has not been assigned to a reviewer yet."
          />
        )}
      </Card>

      {canActOnApprovals(user?.role) && (
        <Card title="Take Action on an Approval">
          <p className="form-note">
            Enter the Approval ID from your Assigned Reviews list to approve or reject it.
          </p>
          <Alert type="error">{actionError}</Alert>
          <div className="form-grid">
            <input
              className="input"
              placeholder="Approval ID"
              value={approvalIdInput}
              onChange={(e) => setApprovalIdInput(e.target.value)}
            />
          </div>
          <Textarea
            label="Comments (optional)"
            rows={2}
            value={comments}
            onChange={(e) => setComments(e.target.value)}
          />
          <div className="form-actions">
            <Button variant="danger" loading={acting} onClick={() => act("Rejected")}>
              Reject
            </Button>
            <Button variant="success" loading={acting} onClick={() => act("Approved")}>
              Approve
            </Button>
          </div>
        </Card>
      )}

      {showAssign && (
        <Modal title="Assign Reviewer" onClose={() => setShowAssign(false)}>
          <form onSubmit={handleAssign} className="stacked-form" noValidate>
            <Alert type="error">{assignError}</Alert>
            <Select
              label="Reviewer"
              required
              placeholder="Select reviewer"
              options={reviewers.map((r) => ({ value: r.id, label: `${r.full_name} (${r.email})` }))}
              value={assignForm.reviewer_id}
              onChange={(e) => setAssignForm({ ...assignForm, reviewer_id: e.target.value })}
            />
            <input
              className="input"
              type="number"
              min="1"
              placeholder="Approval level (default 1)"
              value={assignForm.level}
              onChange={(e) => setAssignForm({ ...assignForm, level: e.target.value })}
            />
            <div className="form-actions">
              <Button type="button" variant="secondary" onClick={() => setShowAssign(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={assigning}>
                Assign
              </Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
