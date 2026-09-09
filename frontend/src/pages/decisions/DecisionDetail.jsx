import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import {
  getDecision,
  updateDecision,
  updateDecisionStatus,
  getDecisionRationale,
  updateDecisionRationale,
} from "../../api/decisions";
import Card from "../../components/ui/Card";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import Input from "../../components/ui/Input";
import Textarea from "../../components/ui/Textarea";
import Alert from "../../components/ui/Alert";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import { formatDate } from "../../utils/format";
import { useAuth } from "../../context/AuthContext";
import { ROLES } from "../../utils/roles";
import AlternativesPanel from "../alternatives/AlternativesPanel";
import DiscussionsPanel from "../discussions/DiscussionsPanel";
import ApprovalPanel from "../approvals/ApprovalPanel";
import HistoryPanel from "./HistoryPanel";
import TagsPanel from "./TagsPanel";

const TABS = ["Overview", "Alternatives", "Discussions", "Approval", "History"];

export default function DecisionDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [decision, setDecision] = useState(null);
  const [rationale, setRationale] = useState("");
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");
  const [tab, setTab] = useState("Overview");

  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState({ title: "", problem_statement: "", category: "" });
  const [editError, setEditError] = useState("");
  const [saving, setSaving] = useState(false);

  const [rationaleDraft, setRationaleDraft] = useState("");
  const [savingRationale, setSavingRationale] = useState(false);
  const [statusError, setStatusError] = useState("");

  const isOwner = decision && user && decision.created_by === user.id;
  const canEditDecision = isOwner || user?.role === ROLES.ADMINISTRATOR;

  async function load() {
    setState("loading");
    try {
      const d = await getDecision(id);
      setDecision(d);
      setEditForm({ title: d.title, problem_statement: d.problem_statement, category: d.category });
      try {
        const r = await getDecisionRationale(id);
        setRationale(r.rationale || "");
        setRationaleDraft(r.rationale || "");
      } catch {
        // rationale endpoint failing shouldn't block the whole page
      }
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  async function handleEditSave(e) {
    e.preventDefault();
    setEditError("");
    if (!editForm.title.trim() || !editForm.problem_statement.trim() || !editForm.category.trim()) {
      setEditError("All fields are required.");
      return;
    }
    setSaving(true);
    try {
      await updateDecision(id, editForm);
      setEditing(false);
      load();
    } catch (err) {
      setEditError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function handleSubmitForReview() {
    setStatusError("");
    try {
      await updateDecisionStatus(id, "Under Review");
      load();
    } catch (err) {
      setStatusError(err.message);
    }
  }

  async function handleArchive() {
    setStatusError("");
    try {
      await updateDecisionStatus(id, "Archived");
      load();
    } catch (err) {
      setStatusError(err.message);
    }
  }

  async function handleSaveRationale() {
    setSavingRationale(true);
    try {
      await updateDecisionRationale(id, rationaleDraft);
      setRationale(rationaleDraft);
    } catch (err) {
      setStatusError(err.message);
    } finally {
      setSavingRationale(false);
    }
  }

  if (state === "loading") return <LoadingState label="Loading decision…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div>
      <div className="page-header">
        <div>
          <button className="link-button" onClick={() => navigate("/decisions")}>
            ← Back to Decisions
          </button>
          <h1>{decision.title}</h1>
          <div className="decision-meta-row">
            <Badge>{decision.status}</Badge>
            <span>Category: {decision.category}</span>
            <span>Created {formatDate(decision.created_at)}</span>
            <span>Updated {formatDate(decision.updated_at)}</span>
          </div>
        </div>
        <div className="page-header-actions">
          {canEditDecision && decision.status === "Draft" && (
            <Button variant="secondary" onClick={() => setEditing(true)}>
              Edit
            </Button>
          )}
          {canEditDecision && decision.status === "Draft" && (
            <Button onClick={handleSubmitForReview}>Submit for Review</Button>
          )}
          {canEditDecision && (decision.status === "Approved" || decision.status === "Rejected") && (
            <Button variant="secondary" onClick={handleArchive}>
              Archive
            </Button>
          )}
        </div>
      </div>

      <Alert type="error">{statusError}</Alert>

      <div className="tabs">
        {TABS.map((t) => (
          <button key={t} className={`tab ${tab === t ? "tab-active" : ""}`} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </div>

      {tab === "Overview" && (
        <div>
          <Card title="Problem Statement">
            <p>{decision.problem_statement}</p>
          </Card>
          <Card title="Rationale">
            {canEditDecision ? (
              <div>
                <Textarea
                  rows={4}
                  value={rationaleDraft}
                  onChange={(e) => setRationaleDraft(e.target.value)}
                  placeholder="Explain the reasoning behind this decision…"
                />
                <div className="form-actions">
                  <Button size="sm" loading={savingRationale} onClick={handleSaveRationale}>
                    Save Rationale
                  </Button>
                </div>
              </div>
            ) : (
              <p>{rationale || "No rationale recorded yet."}</p>
            )}
          </Card>
          <TagsPanel decisionId={id} canEdit={canEditDecision} />
        </div>
      )}

      {tab === "Alternatives" && <AlternativesPanel decisionId={id} canEdit={canEditDecision} />}
      {tab === "Discussions" && <DiscussionsPanel decisionId={id} />}
      {tab === "Approval" && <ApprovalPanel decisionId={id} decision={decision} onChanged={load} />}
      {tab === "History" && <HistoryPanel decisionId={id} />}

      {editing && (
        <div className="modal-overlay" onClick={() => setEditing(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Edit Decision</h3>
              <button className="modal-close" onClick={() => setEditing(false)}>
                ×
              </button>
            </div>
            <div className="modal-body">
              <form onSubmit={handleEditSave} className="stacked-form" noValidate>
                <Alert type="error">{editError}</Alert>
                <Input
                  label="Title"
                  required
                  value={editForm.title}
                  onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                />
                <Textarea
                  label="Problem Statement"
                  required
                  rows={4}
                  value={editForm.problem_statement}
                  onChange={(e) => setEditForm({ ...editForm, problem_statement: e.target.value })}
                />
                <Input
                  label="Category"
                  required
                  value={editForm.category}
                  onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                />
                <div className="form-actions">
                  <Button type="button" variant="secondary" onClick={() => setEditing(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" loading={saving}>
                    Save Changes
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
