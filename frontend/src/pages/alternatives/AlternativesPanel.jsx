import { useEffect, useState } from "react";
import { listAlternatives, createAlternative, updateAlternative, compareAlternatives, RISK_LEVELS } from "../../api/alternatives";
import Card from "../../components/ui/Card";
import Table from "../../components/ui/Table";
import Badge from "../../components/ui/Badge";
import Button from "../../components/ui/Button";
import Modal from "../../components/ui/Modal";
import Input from "../../components/ui/Input";
import Textarea from "../../components/ui/Textarea";
import Select from "../../components/ui/Select";
import Alert from "../../components/ui/Alert";
import LoadingState from "../../components/ui/LoadingState";
import ErrorState from "../../components/ui/ErrorState";
import EmptyState from "../../components/ui/EmptyState";
import { formatCurrency } from "../../utils/format";

const EMPTY = {
  name: "",
  description: "",
  pros: "",
  cons: "",
  estimated_cost: "",
  feasibility_score: "",
  risk_level: "",
};

export default function AlternativesPanel({ decisionId, canEdit }) {
  const [alternatives, setAlternatives] = useState([]);
  const [state, setState] = useState("loading");
  const [errorMsg, setErrorMsg] = useState("");

  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null); // alternative being edited, or null for "new"
  const [form, setForm] = useState(EMPTY);
  const [formErrors, setFormErrors] = useState({});
  const [formError, setFormError] = useState("");
  const [saving, setSaving] = useState(false);

  const [compareMode, setCompareMode] = useState(false);
  const [compareData, setCompareData] = useState(null);
  const [compareError, setCompareError] = useState("");

  async function load() {
    setState("loading");
    try {
      const res = await listAlternatives(decisionId);
      setAlternatives(res);
      setState("ready");
    } catch (err) {
      setErrorMsg(err.message);
      setState("error");
    }
  }

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [decisionId]);

  function openCreate() {
    setEditing(null);
    setForm(EMPTY);
    setFormErrors({});
    setFormError("");
    setShowForm(true);
  }

  function openEdit(alt) {
    setEditing(alt);
    setForm({
      name: alt.name,
      description: alt.description,
      pros: alt.pros,
      cons: alt.cons,
      estimated_cost: alt.estimated_cost,
      feasibility_score: alt.feasibility_score,
      risk_level: alt.risk_level,
    });
    setFormErrors({});
    setFormError("");
    setShowForm(true);
  }

  function validate() {
    const next = {};
    if (!form.name.trim()) next.name = "Name is required.";
    if (!form.description.trim()) next.description = "Description is required.";
    if (!form.pros.trim()) next.pros = "List at least one pro.";
    if (!form.cons.trim()) next.cons = "List at least one con.";
    if (form.estimated_cost === "" || Number(form.estimated_cost) < 0) next.estimated_cost = "Enter a valid cost.";
    const score = Number(form.feasibility_score);
    if (!score || score < 1 || score > 5) next.feasibility_score = "Feasibility score must be between 1 and 5.";
    if (!form.risk_level) next.risk_level = "Select a risk level.";
    setFormErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSave(e) {
    e.preventDefault();
    setFormError("");
    if (!validate()) return;

    const payload = {
      ...form,
      estimated_cost: Number(form.estimated_cost),
      feasibility_score: Number(form.feasibility_score),
    };

    setSaving(true);
    try {
      if (editing) {
        await updateAlternative(editing.id, payload);
      } else {
        await createAlternative(decisionId, payload);
      }
      setShowForm(false);
      load();
    } catch (err) {
      setFormError(err.message);
    } finally {
      setSaving(false);
    }
  }

  async function openCompare() {
    setCompareMode(true);
    setCompareError("");
    try {
      const res = await compareAlternatives(decisionId);
      setCompareData(res);
    } catch (err) {
      setCompareError(err.message);
    }
  }

  if (state === "loading") return <LoadingState label="Loading alternatives…" />;
  if (state === "error") return <ErrorState message={errorMsg} onRetry={load} />;

  return (
    <div>
      <div className="panel-header">
        <h3>Alternatives</h3>
        <div className="page-header-actions">
          {alternatives.length > 1 && (
            <Button variant="secondary" size="sm" onClick={openCompare}>
              Compare
            </Button>
          )}
          {canEdit && (
            <Button size="sm" onClick={openCreate}>
              + Add Alternative
            </Button>
          )}
        </div>
      </div>

      {alternatives.length === 0 ? (
        <EmptyState title="No alternatives yet" description="Add alternatives to start comparing options." />
      ) : (
        <Table columns={["Name", "Cost", "Feasibility", "Risk", "Actions"]}>
          {alternatives.map((a) => (
            <tr key={a.id}>
              <td>{a.name}</td>
              <td>{formatCurrency(a.estimated_cost)}</td>
              <td>{a.feasibility_score} / 5</td>
              <td>
                <Badge>{a.risk_level}</Badge>
              </td>
              <td>
                {canEdit && (
                  <Button size="sm" variant="secondary" onClick={() => openEdit(a)}>
                    Edit
                  </Button>
                )}
              </td>
            </tr>
          ))}
        </Table>
      )}

      {alternatives.map((a) => (
        <details key={a.id} className="alt-details">
          <summary>{a.name} — pros / cons</summary>
          <div className="two-col">
            <div>
              <strong>Pros</strong>
              <p>{a.pros}</p>
            </div>
            <div>
              <strong>Cons</strong>
              <p>{a.cons}</p>
            </div>
          </div>
        </details>
      ))}

      {showForm && (
        <Modal title={editing ? "Edit Alternative" : "Add Alternative"} onClose={() => setShowForm(false)}>
          <form onSubmit={handleSave} className="stacked-form" noValidate>
            <Alert type="error">{formError}</Alert>
            <Input label="Name" required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} error={formErrors.name} />
            <Textarea label="Description" required rows={3} value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} error={formErrors.description} />
            <Textarea label="Pros" required rows={2} value={form.pros} onChange={(e) => setForm({ ...form, pros: e.target.value })} error={formErrors.pros} />
            <Textarea label="Cons" required rows={2} value={form.cons} onChange={(e) => setForm({ ...form, cons: e.target.value })} error={formErrors.cons} />
            <div className="form-grid">
              <Input
                label="Estimated Cost"
                type="number"
                min="0"
                step="0.01"
                required
                value={form.estimated_cost}
                onChange={(e) => setForm({ ...form, estimated_cost: e.target.value })}
                error={formErrors.estimated_cost}
              />
              <Input
                label="Feasibility Score (1-5)"
                type="number"
                min="1"
                max="5"
                required
                value={form.feasibility_score}
                onChange={(e) => setForm({ ...form, feasibility_score: e.target.value })}
                error={formErrors.feasibility_score}
              />
              <Select
                label="Risk Level"
                required
                placeholder="Select risk level"
                options={RISK_LEVELS}
                value={form.risk_level}
                onChange={(e) => setForm({ ...form, risk_level: e.target.value })}
                error={formErrors.risk_level}
              />
            </div>
            <div className="form-actions">
              <Button type="button" variant="secondary" onClick={() => setShowForm(false)}>
                Cancel
              </Button>
              <Button type="submit" loading={saving}>
                Save
              </Button>
            </div>
          </form>
        </Modal>
      )}

      {compareMode && (
        <Modal title="Compare Alternatives" onClose={() => setCompareMode(false)}>
          <Alert type="error">{compareError}</Alert>
          {compareData ? (
            <Table columns={["Name", "Cost", "Feasibility", "Risk"]}>
              {compareData.alternatives.map((a) => (
                <tr key={a.name}>
                  <td>{a.name}</td>
                  <td>{formatCurrency(a.estimated_cost)}</td>
                  <td>{a.feasibility_score} / 5</td>
                  <td>
                    <Badge>{a.risk_level}</Badge>
                  </td>
                </tr>
              ))}
            </Table>
          ) : (
            !compareError && <LoadingState label="Loading comparison…" />
          )}
        </Modal>
      )}
    </div>
  );
}
